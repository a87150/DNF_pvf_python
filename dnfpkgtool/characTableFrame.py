'''角色表页：按原版（Cython 编译版 dnf_pkg_tool V.23.09.15 的 dnfpkgtool.characRecFrame）复刻。

左「角色操作」：账号ID 查询（角色列表来自「查询」页签）+ 状态/角色ID/角色名/等级/职业/UID + 删除/恢复/拷贝/备份/读取恢复数据
右「角色转移」：账号ID + 查找账号 + 角色ID/角色名/等级/职业 + 转移角色到右侧账号

「状态」列取自 taiwan_cain.charac_info.delete_flag（1=已删除，0=正常时留空）：
    删除选中角色 = update charac_info set delete_flag=1 where charac_no=...   -> sqlManager2.del_cNos
    恢复选中角色 = update charac_info set delete_flag=0 where charac_no=...   -> sqlManager2.recover_cNos
这两条与原版 pyd 里抠出来的 SQL 一字不差。

后台线程只碰 DB；控件读写与弹窗一律经 appCommon.runOnUi 回主线程（py3.14 里非主线程调控件会 RuntimeError）。
'''
import os
import zlib
import pickle

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox

from dnfpkgtool import cacheManager as cacheM
from dnfpkgtool import sqlManager2 as sqlM
from dnfpkgtool.appCommon import inThread, log, runOnUi

BAK_DIR = 'charac_bak'    # 「备份选中角色」写 .cbak 的目录（一个角色一个文件）

# 一个角色散落在这些表里（原版 copyCharac.py 的清单）：(库, 表, 主键是不是 ui_id)
CHARAC_TABLES = (
    ('taiwan_cain', 'charac_info', False),
    ('taiwan_cain', 'charac_stat', False),
    ('taiwan_cain', 'new_charac_quest', False),
    ('taiwan_cain', 'charac_achievement', False),
    ('taiwan_cain', 'charac_expert_job', False),
    ('taiwan_cain', 'charac_item_stat', False),
    ('taiwan_cain', 'charac_npc', False),
    ('taiwan_cain', 'charac_option', False),
    ('taiwan_cain', 'charac_quest_shop', False),
    ('taiwan_cain', 'charac_titlebook', False),
    ('taiwan_cain_2nd', 'inventory', False),
    ('taiwan_cain_2nd', 'skill', False),
    ('taiwan_cain_2nd', 'charac_inven_expand', False),
    ('taiwan_cain_2nd', 'user_items', True),
    ('taiwan_cain_2nd', 'creature_items', True),
)

# .cbak 备份/恢复的表清单：表 -> (库, 角色键列)。
# 原版 dnfpkgtool.copyCharac 的 tList（从 dnfpkgtool.cp36-win_amd64.pyd 里抠出）就是这个顺序；
# 注意 postal 没有 charac_no，真库里按 receive_charac_no 取。
BAK_TABLES = {
    'charac_info': ('taiwan_cain', 'charac_no'),
    'new_charac_quest': ('taiwan_cain', 'charac_no'),
    'charac_achievement': ('taiwan_cain', 'charac_no'),
    'charac_expert_job': ('taiwan_cain', 'charac_no'),
    'charac_item_stat': ('taiwan_cain', 'charac_no'),
    'charac_npc': ('taiwan_cain', 'charac_no'),
    'charac_option': ('taiwan_cain', 'charac_no'),
    'charac_quest_shop': ('taiwan_cain', 'charac_no'),
    'charac_stat': ('taiwan_cain', 'charac_no'),
    'charac_titlebook': ('taiwan_cain', 'charac_no'),
    'inventory': ('taiwan_cain_2nd', 'charac_no'),
    'postal': ('taiwan_cain_2nd', 'receive_charac_no'),
    'skill': ('taiwan_cain_2nd', 'charac_no'),
    'user_items': ('taiwan_cain_2nd', 'charac_no'),
    'creature_items': ('taiwan_cain_2nd', 'charac_no'),
    'charac_inven_expand': ('taiwan_cain_2nd', 'charac_no'),
}

_colsCache = {}


def _columns(db, table):
    '''列名（按 ordinal_position，和 select * 的顺序一致）'''
    key = (db, table)
    if key not in _colsCache:
        sql = ('select column_name from information_schema.columns '
               'where table_schema=%s and table_name=%s order by ordinal_position')
        _colsCache[key] = [r[0] for r in sqlM.execute_and_fetch('taiwan_cain', sql, (db, table))]
    return _colsCache[key]


def _rows_of(db, table, cNo):
    '''按角色号整行取出（只读）。字符集用默认 utf8：读进来是库里真正的字符，写回同一字符集不会二次编码。'''
    cols = _columns(db, table)
    rows = sqlM.execute_and_fetch(db, f'select * from `{table}` where charac_no={int(cNo)};')
    return [dict(zip(cols, r)) for r in rows]


def _insert_rows(db, table, rows):
    '''整行写回（字典列表）。主键冲突交给 INSERT IGNORE，免得一行冲突把整批回滚。'''
    if not rows:
        return 0
    cols = _columns(db, table)
    sql = (f'insert ignore into `{table}` (' + ','.join(f'`{c}`' for c in cols) + ') values '
           + ','.join(['(' + ','.join(['%s'] * len(cols)) + ')'] * len(rows)))
    args = [row.get(c) for row in rows for c in cols]
    sqlM.execute_and_commit(db, sql, args)
    return len(rows)


def _next_ui_id(db, table):
    res = sqlM.execute_and_fetch(db, f'select ifnull(max(ui_id),0)+1 from `{table}`;')
    return int(res[0][0]) if res else 0


def _free_charac_name(name):
    '''charac_name 上有唯一索引：重名时按 名字+序号 找空位（varchar(20) 截断）'''
    name = name[:20]
    for i in range(100):
        cand = (name if i == 0 else f'{name}{i}')[:20]
        if not sqlM.execute_and_fetch('taiwan_cain',
                                      'select charac_no from charac_info where charac_name=%s;', (cand,)):
            return cand
    raise RuntimeError(f'角色名[{name}]的副本名已用满')


def _all_characs():
    '''全部角色（含已删除）。sqlM.get_all_charac 会把 delete_flag=1 的行滤掉，
    角色表页正好要显示它们，所以这里保留原版 get_charac_view 用的那条 SQL。'''
    sql = 'select m_id, charac_no, charac_name, lev, job, grow_type, delete_flag, expert_job from charac_info;'
    return sqlM.decode_charac_list(sqlM.execute_and_fetch('taiwan_cain', sql))


CV_SLOT = 148    # charac_view.info 解压后是 36 个等长槽位，槽首 u32 = 角色号（0 = 空槽）


def _view_c_nos(rows):
    '''账号缓存表 charac_view 里已缓存（客户端角色选择界面看得见）的角色号，按 m_id 分组。
    解法照原版 get_charac_view：info = u32(解压后长度) + zlib，解压出来是一条条 148 字节槽位。
    取不到该账号的 charac_view 行就是空集 —— 原版对这种账号也全部判「隐藏」。'''
    view = {}
    m_ids = sorted({int(r[0]) for r in rows})
    if m_ids:
        sql = 'select m_id, info from charac_view where m_id in (' + ','.join(['%s'] * len(m_ids)) + ');'
        for m_id, info in sqlM.execute_and_fetch('taiwan_cain', sql, m_ids):
            view[int(m_id)] = set()
            try:
                raw = zlib.decompress(bytes(info)[4:])
            except Exception:
                continue     # 解不开的缓存当空：宁可显示「隐藏」，也别让整页查询失败
            cNos = (int.from_bytes(raw[o:o + 4], 'little') for o in range(0, len(raw), CV_SLOT))
            view[int(m_id)] = {cNo for cNo in cNos if cNo}      # 空槽是 0，不算角色
    return view


def _descendants(w):
    for c in w.winfo_children():
        yield c
        yield from _descendants(c)


def _query_tab_rows(frame):
    '''「查询」页签当前的结果行（同一 Notebook 里的兄弟页签），形如
    (角色ID, 角色名, 等级, 职业, UID, 是否已删除)。找不到那个页签就返回 []（自检里单独建页时就是这样）。'''
    nb = frame.master
    if not isinstance(nb, ttk.Notebook):
        return []
    for tabId in nb.tabs():
        if str(nb.tab(tabId, 'text')).strip() != '查询':
            continue
        for w in _descendants(nb.nametowidget(tabId)):
            if isinstance(w, ttk.Treeview):
                rows = []
                for i in w.get_children():
                    item = w.item(i)
                    rows.append(tuple(item['values']) + ('deleted' in item['tags'],))
                return rows
    return []


def _move_characs(cNos, uid):
    '''转移角色：只改 charac_info.m_id（原版 move_charac_uid 就是 update charac_info set m_id=）'''
    cNos = [int(c) for c in cNos]
    sql = 'update charac_info set m_id=%s where charac_no in (' + ','.join(['%s'] * len(cNos)) + ');'
    sqlM.execute_and_commit('taiwan_cain', sql, [int(uid)] + cNos)


def _copy_charac(cNo):
    '''拷贝一个角色：换新 charac_no、重名自动改名、ui_id 换新号。返回 (新角色号, 新角色名)'''
    info = _rows_of('taiwan_cain', 'charac_info', cNo)
    if not info:
        return None
    res = sqlM.execute_and_fetch('taiwan_cain', 'select ifnull(max(charac_no),0)+1 from charac_info;')
    newCNo = int(res[0][0])
    info[0]['charac_name'] = _free_charac_name(str(info[0].get('charac_name') or ''))
    for db, table, has_ui_id in CHARAC_TABLES:
        rows = info if table == 'charac_info' else _rows_of(db, table, cNo)
        if not rows:
            continue
        for row in rows:
            row['charac_no'] = newCNo
        if has_ui_id:
            uiID = _next_ui_id(db, table)
            for row in rows:
                row['ui_id'] = uiID
                uiID += 1
        _insert_rows(db, table, rows)
        log(f'拷贝角色{cNo}->{newCNo}: {db}.{table} {len(rows)}行')
    return newCNo, info[0]['charac_name']


def _dump_charac(cNo):
    '''角色快照 {裸表名: DB 原始行元组}；原版 .cbak 就是 zlib(pickle(这个 dict, protocol=3))。
    值是 select * 取回的行元组（datetime/bytes 原样），空表也留键；字符串保持库里的 latin1 形态，
    显示时再走 sqlM.decode。'''
    return {table: sqlM.execute_and_fetch(db, f'select * from `{table}` where {key}={int(cNo)};')
            for table, (db, key) in BAK_TABLES.items()}


def _restore_charac_rows(cNo, data):
    '''读回 .cbak：先按角色键删旧行，再整行写回（原版 recover_charac_stat 的做法）'''
    for table, rows in data.items():
        if table not in BAK_TABLES:
            log(f'跳过 .cbak 里的未知表：{table}')
            continue
        db, key = BAK_TABLES[table]
        cols = _columns(db, table)
        records = []
        for row in rows:
            if len(row) != len(cols):     # 换过版本的库改了表结构：宁可报错，也不静默截断写坏数据
                raise RuntimeError(f'{db}.{table} 列数不符：文件 {len(row)} 列，当前库 {len(cols)} 列')
            record = dict(zip(cols, row))
            record[key] = int(cNo)
            records.append(record)
        sqlM.execute_and_commit(db, f'delete from `{table}` where {key}={int(cNo)};')
        _insert_rows(db, table, records)
        log(f'恢复角色{cNo}: {db}.{table} {len(records)}行')


class CharactableframeWidget(ttk.Frame):
    '''角色表页：左「角色操作」右「角色转移」'''
    CHARAC_COLS = ('column6', 'column1', 'column2', 'column3', 'column4', 'column5')
    CHARAC_HEADS = ('状态', '角色ID', '角色名', '等级', '职业', 'UID')
    TARGET_COLS = ('column8', 'column9', 'column10', 'column11')
    TARGET_HEADS = ('角色ID', '角色名', '等级', '职业')

    def __init__(self, master=None, **kw):
        super(CharactableframeWidget, self).__init__(master, **kw)
        self.characRows = {}      # 左树 item -> (角色号, 账号ID, 角色名, delete_flag)
        self.lastSearch = {}      # 上次查询条件，写完数据后照着重查
        self.targetUID = None     # 右侧查到的目标账号
        self.bind('<Map>', self._on_show)   # 本页签显示时搬「查询」页签现在的角色（不查库）
        self._queryRows = None    # 上次从「查询」页签搬过来的行

        # ---------------- 左：角色操作 ----------------
        labelframe1 = ttk.Labelframe(self, text='角色操作')
        labelframe1.configure(height=200, width=200)
        searchFrame = ttk.Frame(labelframe1)
        label = ttk.Label(searchFrame)
        label.configure(text='账号ID：')
        label.pack(side='left')
        self.uidE = ttk.Entry(searchFrame)
        self.uidE.configure(width=12)
        self.uidE.pack(side='left')
        self.searchUIDBtn = ttk.Button(searchFrame)
        self.searchUIDBtn.configure(text='查找账号', width=10, command=self.search_account_1)
        self.searchUIDBtn.pack(expand=False, fill='x', side='left')
        searchFrame.pack(fill='x', side='top')
        treeFrame = ttk.Frame(labelframe1)
        self.characTreeV = ttk.Treeview(treeFrame)
        self.characTreeV.configure(selectmode='extended', show='headings',
                                   columns=self.CHARAC_COLS, displaycolumns=self.CHARAC_COLS)
        for col, head in zip(self.CHARAC_COLS, self.CHARAC_HEADS):
            self.characTreeV.heading(col, anchor='center', text=head)
            self.characTreeV.column(col, anchor='center', stretch=True, width=60, minwidth=20)
        self.characBar = ttk.Scrollbar(treeFrame)
        self.characBar.configure(orient='vertical', command=self.characTreeV.yview)
        self.characTreeV.configure(yscrollcommand=self.characBar.set)
        self.characTreeV.pack(expand=True, fill='both', side='left')
        self.characBar.pack(fill='y', side='right')
        treeFrame.pack(expand=True, fill='both', side='top')
        btnFrame = ttk.Frame(labelframe1)
        self.delSelBtn = ttk.Button(btnFrame)
        self.delSelBtn.configure(text='删除选中角色', command=self.del_sel_charac)
        self.delSelBtn.pack(expand=True, fill='x', side='left')
        self.recSelBtn = ttk.Button(btnFrame)
        self.recSelBtn.configure(text='恢复选中角色', command=self.rec_sel_charac)
        self.recSelBtn.pack(expand=True, fill='x', side='left')
        self.copySelBtn = ttk.Button(btnFrame)
        self.copySelBtn.configure(text='拷贝选中角色', command=self.copy_sel_charac)
        self.copySelBtn.pack(expand=True, fill='x', side='left')
        self.backupSelBtn = ttk.Button(btnFrame)
        self.backupSelBtn.configure(text='备份选中角色', command=self.backup_sel_charac)
        self.backupSelBtn.pack(expand=True, fill='x', side='left')
        self.loadBakBtn = ttk.Button(btnFrame)
        self.loadBakBtn.configure(text='读取恢复数据', command=self.load_bak_data)
        self.loadBakBtn.pack(expand=True, fill='x', side='left')
        btnFrame.pack(fill='x', side='top')
        labelframe1.pack(expand=True, fill='both', side='left')
        # ---------------- 右：角色转移 ----------------
        labelframe2 = ttk.Labelframe(self, text='角色转移')
        labelframe2.configure(height=200, width=200)
        self.moveCharacBtn = ttk.Button(labelframe2)
        self.moveCharacBtn.configure(text='转移角色到右侧账号', state='disabled',
                                     command=self.move_charac_to_account)
        self.moveCharacBtn.pack(expand=False, fill='x', side='bottom')
        targetSearchFrame = ttk.Frame(labelframe2)
        label3 = ttk.Label(targetSearchFrame)
        label3.configure(text='  账号ID：')
        label3.pack(side='left')
        self.uidE2 = ttk.Entry(targetSearchFrame)
        self.uidE2.configure(width=12)
        self.uidE2.pack(side='left')
        self.searchUID2Btn = ttk.Button(targetSearchFrame)
        self.searchUID2Btn.configure(text='查找账号', width=10, command=self.search_account_2)
        self.searchUID2Btn.pack(expand=False, fill='x', side='left')
        targetSearchFrame.pack(fill='x', side='top')
        targetTreeFrame = ttk.Frame(labelframe2)
        self.targetTree = ttk.Treeview(targetTreeFrame)
        self.targetTree.configure(selectmode='extended', show='headings',
                                  columns=self.TARGET_COLS, displaycolumns=self.TARGET_COLS)
        for col, head in zip(self.TARGET_COLS, self.TARGET_HEADS):
            self.targetTree.heading(col, anchor='center', text=head)
            self.targetTree.column(col, anchor='center', stretch=True, width=60, minwidth=20)
        self.targetBar = ttk.Scrollbar(targetTreeFrame)
        self.targetBar.configure(orient='vertical', command=self.targetTree.yview)
        self.targetTree.configure(yscrollcommand=self.targetBar.set)
        self.targetTree.pack(expand=True, fill='both', side='left')
        self.targetBar.pack(fill='y', side='right')
        targetTreeFrame.pack(expand=True, fill='both', side='top')
        labelframe2.pack(expand=True, fill='both', side='left')

    # ---------------- 主线程专属：只有 _ui_ 开头的这些能碰控件 ----------------
    def _ui_fill_charac_tree(self, rows, view=None):
        '''填左树：状态/角色ID/角色名/等级/职业/UID。状态三档照原版：已删除 > 隐藏 > 空。
        「隐藏」= 该角色不在它账号的 charac_view 缓存里（view 由后台线程的 _view_c_nos 算好传进来）。'''
        self.characTreeV.delete(*self.characTreeV.get_children())
        self.characRows = {}
        for m_id, cNo, cName, lev, job, growType, deleteFlag, expert_job in rows:
            jobDict = cacheM.jobDict.get(job)
            jobZh = jobDict.get(growType % 16) if isinstance(jobDict, dict) else growType % 16
            hidden = view is not None and int(cNo) not in view.get(int(m_id), ())   # view=None(没传)时不判隐藏
            state = '已删除' if deleteFlag == 1 else ('隐藏' if hidden else '')
            item = self.characTreeV.insert('', tk.END, values=(state, cNo, cName, lev, jobZh, m_id))
            self.characRows[item] = (int(cNo), int(m_id), cName, deleteFlag)

    def _on_show(self, event=None):
        '''本页签显示：左栏直接用「查询」页签当前的结果行（纯读控件，不再查库）。
        只在「查询」页签的结果变了（或本页还没搬过）时搬，免得写操作后刷出来的真状态被旧行盖掉。'''
        rows = _query_tab_rows(self)
        if rows and rows != self._queryRows:
            self._queryRows = rows
            self._ui_fill_from_query(rows)

    def _ui_fill_from_query(self, rows):
        '''「查询」页签的行 -> 左树（状态从它给已删角色打的 deleted 标签来）。
        「查询」页签的行不带 charac_view 信息，所以这条路上不判「隐藏」。'''
        self.characTreeV.delete(*self.characTreeV.get_children())
        self.characRows = {}
        for cNo, cName, lev, jobZh, m_id, deleted in rows:
            item = self.characTreeV.insert('', tk.END, values=('已删除' if deleted else '', cNo, cName, lev, jobZh, m_id))
            self.characRows[item] = (int(cNo), int(m_id), cName, 1 if deleted else 0)

    def _ui_sel_rows(self):
        '''左树选中行 -> [(角色号, 账号ID, 角色名, delete_flag)]'''
        return [self.characRows[i] for i in self.characTreeV.selection() if i in self.characRows]

    def _ui_fill_target_tree(self, rows):
        '''填右树：角色ID/角色名/等级/职业'''
        self.targetTree.delete(*self.targetTree.get_children())
        for m_id, cNo, cName, lev, job, growType, deleteFlag, expert_job in rows:
            jobDict = cacheM.jobDict.get(job)
            jobZh = jobDict.get(growType % 16) if isinstance(jobDict, dict) else growType % 16
            self.targetTree.insert('', tk.END, values=(cNo, cName, lev, jobZh))

    def _ui_set_move_state(self, state):
        self.moveCharacBtn.configure(state=state)

    def _ui_refresh_after(self, what):
        messagebox.showinfo('提示', f'{what}完成')
        self._reload()

    # ---------------- 后台：查询 ----------------
    def _load_characs(self, **kw):
        '''后台：查角色（含已删除）后把行交回主线程刷树。
        uid 走 sqlM.getCharacterInfo —— 和「查询」页签（guiTabMain.searchCharac）同一个函数。'''
        self.lastSearch = kw
        uid = kw.get('uid') or 0
        try:
            if uid > 0:
                rows = sqlM.getCharacterInfo(uid=uid)
            else:
                rows = _all_characs()
        except Exception as e:
            log(f'角色表查询失败：{e}')
            runOnUi(messagebox.showerror, '错误', f'角色查询失败：{e}')
            return
        runOnUi(self._ui_fill_charac_tree, rows, _view_c_nos(rows))    # 查库算「隐藏」留在后台线程

    @inThread
    def _reload(self):
        self._load_characs(**self.lastSearch)

    @inThread
    def search_account_1(self):
        text = runOnUi(self.uidE.get).strip()
        if text == '':
            self._load_characs()
            return
        try:
            uid = int(text)
        except ValueError:
            runOnUi(messagebox.showerror, '错误', '账号ID必须是数字')
            return
        self._load_characs(uid=uid)

    @inThread
    def search_account_2(self):
        '''右侧：查目标账号的角色，查到才允许转移'''
        text = runOnUi(self.uidE2.get).strip()
        try:
            uid = int(text)
        except ValueError:
            runOnUi(messagebox.showerror, '错误', '账号查找错误')
            runOnUi(self._ui_set_move_state, 'disabled')
            self.targetUID = None
            return
        rows = sqlM.getCharacterInfo(uid=uid)
        if not rows:
            runOnUi(messagebox.showerror, '错误', '账号查找错误')
            runOnUi(self._ui_set_move_state, 'disabled')
            self.targetUID = None
            return
        self.targetUID = uid
        runOnUi(self._ui_fill_target_tree, rows)
        runOnUi(self._ui_set_move_state, 'normal')

    # ---------------- 后台：写操作 ----------------
    @inThread
    def del_sel_charac(self):
        rows = runOnUi(self._ui_sel_rows)
        if not rows:
            runOnUi(messagebox.showinfo, '提示', '请先选择角色')
            return
        if not runOnUi(messagebox.askokcancel, '提示', '确认删除选中角色？'):
            return
        try:
            sqlM.del_cNos([r[0] for r in rows])          # update charac_info set delete_flag=1
        except Exception as e:
            log(f'删除角色失败：{e}')
            runOnUi(messagebox.showerror, '错误', f'删除角色失败：{e}')
            return
        log(f'删除角色{[r[0] for r in rows]}')
        runOnUi(self._ui_refresh_after, '删除选中角色')

    @inThread
    def rec_sel_charac(self):
        rows = runOnUi(self._ui_sel_rows)
        if not rows:
            runOnUi(messagebox.showinfo, '提示', '请先选择角色')
            return
        if not runOnUi(messagebox.askokcancel, '提示', '确认恢复选中角色？'):
            return
        try:
            sqlM.recover_cNos([r[0] for r in rows])      # update charac_info set delete_flag=0
        except Exception as e:
            log(f'恢复角色失败：{e}')
            runOnUi(messagebox.showerror, '错误', f'恢复角色失败：{e}')
            return
        log(f'恢复角色{[r[0] for r in rows]}')
        runOnUi(self._ui_refresh_after, '恢复选中角色')

    @inThread
    def move_charac_to_account(self):
        rows = runOnUi(self._ui_sel_rows)
        uid = self.targetUID
        if uid is None:
            runOnUi(messagebox.showerror, '错误', '无目标账号')
            return
        if not rows:
            runOnUi(messagebox.showinfo, '提示', '请先选择角色')
            return
        if not runOnUi(messagebox.askokcancel, '提示', f'确认转移选中角色到帐号[{uid}]下？'):
            return
        try:
            _move_characs([r[0] for r in rows], uid)
        except Exception as e:
            log(f'转移角色失败：{e}')
            runOnUi(messagebox.showerror, '错误', f'转移角色失败：{e}')
            return
        log(f'角色{[r[0] for r in rows]}转移到账号{uid}')
        runOnUi(self._ui_refresh_after, '转移选中角色')

    @inThread
    def copy_sel_charac(self):
        rows = runOnUi(self._ui_sel_rows)
        if not rows:
            runOnUi(messagebox.showinfo, '提示', '请先选择角色')
            return
        if not runOnUi(messagebox.askokcancel, '提示',
                       f'确认复制选中的{len(rows)}个角色？如果账号内有角色在线可能会造成复制后角色被隐藏。'):
            return
        try:
            for cNo, uid, name, deleteFlag in rows:
                log(f'正在复制角色 {cNo} ...')
                _copy_charac(cNo)
        except Exception as e:
            log(f'复制角色失败：{e}')
            runOnUi(messagebox.showerror, '错误', f'复制角色失败：{e}')
            return
        runOnUi(messagebox.showinfo, '复制完成', '角色复制完成！')
        runOnUi(self._reload)

    @inThread
    def backup_sel_charac(self):
        rows = runOnUi(self._ui_sel_rows)
        if not rows:
            runOnUi(messagebox.showinfo, '提示', '请先选择角色')
            return
        try:
            if not os.path.exists(BAK_DIR):
                os.mkdir(BAK_DIR)
            for cNo, uid, name, deleteFlag in rows:
                path = os.path.join(BAK_DIR, f'{cNo}-{uid}-{name}.cbak')
                with open(path, 'wb') as f:
                    f.write(zlib.compress(pickle.dumps(_dump_charac(cNo), protocol=3)))
                log(f'已备份角色 {cNo} 到文件 {path}')
        except Exception as e:
            log(f'备份角色失败：{e}')
            runOnUi(messagebox.showerror, '错误', f'备份角色失败：{e}')
            return
        runOnUi(messagebox.showinfo, '备份完成',
                f'数据已经备份至{BAK_DIR}目录，请勿修改文件名，否则恢复时会出现错误')

    @inThread
    def load_bak_data(self):
        path = runOnUi(filedialog.askopenfilename, title='恢复数据',
                       filetypes=(('cbak文件', '.cbak'),))
        if not path:
            return
        try:
            cNo, uid = [int(seg) for seg in os.path.basename(path).split('-')[:2]]
        except ValueError:
            runOnUi(messagebox.showerror, '文件名错误',
                    '从文件名中获取角色ID失败！文件名应以 角色ID-账号ID-xxx.cbak命名！')
            return
        try:
            with open(path, 'rb') as f:
                data = pickle.loads(zlib.decompress(f.read()))
        except Exception as e:
            log(f'读取备份文件失败：{e}')
            runOnUi(messagebox.showerror, '错误', f'读取备份文件失败：{e}')
            return
        if not runOnUi(messagebox.askokcancel, '恢复数据', f'将恢复角色[{cNo}]的数据，是否继续？'):
            return
        try:
            runOnUi(messagebox.showinfo, '恢复数据', '正在恢复角色数据...')
            _restore_charac_rows(cNo, data)
        except Exception as e:
            log(f'恢复角色数据失败：{e}')
            runOnUi(messagebox.showerror, '错误', f'恢复角色数据失败：{e}')
            return
        runOnUi(self._reload)
        runOnUi(messagebox.showinfo, '提示', '角色数据恢复完成！')
