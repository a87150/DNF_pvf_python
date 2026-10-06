# -*- coding: utf-8 -*-
r'''角色表页自检：headless 建 Tk root → 建页面 → 喂假角色行 → 断言列名/按钮/线程纪律。

写操作全部被替换成"只记录"，不动任何真实数据库；真库那一段只做 select count(*)，连不上打印 SKIP 不算失败。
跑法：.venv\Scripts\python.exe tests\charac_table_check.py
'''
import collections
import io
import os
import pickle
import shutil
import sys
import tempfile
import threading
import time
import tkinter as tk
import tkinter.ttk as ttk
import zlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import dnfpkgtool.appCommon as appCommon
from dnfpkgtool import cacheManager as cacheM
from dnfpkgtool import characTableFrame as CT
from dnfpkgtool import sqlManager2 as sqlM

failed = []


def check(name, cond):
    print(('PASS  ' if cond else 'FAIL  ') + name)
    if not cond:
        failed.append(name)


FAKE_ROWS = [   # m_id, charac_no, 角色名, 等级, 职业, 成长类型, delete_flag, 觉醒
    (1, 1, '阿修罗', 46, 0, 4, 0, 0),
    (1, 2, '已删角色', 10, 1, 1, 1, 0),
]

errs = []
threading.excepthook = lambda a: errs.append((a.exc_type.__name__, str(a.exc_value)))

root = tk.Tk()
root.withdraw()
appCommon.startUiPump(root)

uiCalls = collections.Counter()
_realRunOnUi = appCommon.runOnUi


def spyRunOnUi(func, *a, **kw):
    uiCalls[getattr(func, '__name__', str(func))] += 1
    return _realRunOnUi(func, *a, **kw)


CT.runOnUi = spyRunOnUi      # 只换角色表模块里的那个名字；主线程泵、超时逻辑都还是真的

writes = []
_origFetch = sqlM.execute_and_fetch

CV_CNOS = {1, 2}       # 假的 charac_view 缓存里已缓存的角色号（角色3 故意不在里面 -> 「隐藏」）


def cvBlob(cNos):      # charac_view.info = u32(解压后长度) + zlib(36 个 148 字节槽位，槽首是角色号)
    raw = bytearray(CT.CV_SLOT * 36)
    for i, cNo in enumerate(sorted(cNos)):
        raw[i * CT.CV_SLOT:i * CT.CV_SLOT + 4] = int(cNo).to_bytes(4, 'little')
    return len(raw).to_bytes(4, 'little') + zlib.compress(bytes(raw))


def fakeFetch(db, sql, args=None, charset='utf8'):
    s = sql.lower()
    if 'information_schema.columns' in s:
        return [('m_id',), ('charac_no',), ('charac_name',), ('lev',), ('job',),
                ('grow_type',), ('delete_flag',), ('expert_job',)]
    if 'max(charac_no)' in s:
        return [(9,)]
    if 'max(ui_id)' in s:
        return [(50,)]
    if 'charac_name=%s' in s:
        return []
    if 'from charac_view' in s:
        return [(1, cvBlob(CV_CNOS))]
    if s.startswith('select * from') and 'where charac_no=' in s:
        return list(FAKE_ROWS)
    if 'from charac_info' in s:
        return list(FAKE_ROWS)
    return []


sqlM.execute_and_fetch = fakeFetch
sqlM.execute_and_commit = lambda db, sql, args=None, charset='utf8': writes.append(sql)
sqlM.del_cNos = lambda cNos: writes.append(('del_cNos', list(cNos)))
sqlM.recover_cNos = lambda cNos: writes.append(('recover_cNos', list(cNos)))


class MsgStub:
    def __init__(self):
        self.calls = []

    def askokcancel(self, *a):
        self.calls.append(a)
        return True

    def askyesnocancel(self, *a):
        self.calls.append(a)
        return True

    def showinfo(self, *a):
        self.calls.append(a)

    def showerror(self, *a):
        self.calls.append(a)


msg = MsgStub()
CT.messagebox = msg
CT.BAK_DIR = os.path.join(tempfile.gettempdir(), 'charac_table_check_bak')
bakFile = []


class FdStub:
    def askopenfilename(self, **kw):
        return bakFile[0] if bakFile else ''


CT.filedialog = FdStub()


def pump(n=60):
    for _ in range(n):
        root.update()
        time.sleep(0.02)


def descendants(w):
    out = []
    for c in w.winfo_children():
        out.append(c)
        out.extend(descendants(c))
    return out


def cols_of(tree):
    c = tree.cget('columns')
    return c.split() if isinstance(c, str) else list(c)


def heads_of(tree, n):
    return [tree.heading(f'#{i + 1}')['text'] for i in range(n)]


# ---------------- 1. 控件结构 ----------------
frame = CT.CharactableframeWidget(root)
btns = [w for w in descendants(frame) if isinstance(w, ttk.Button)]
check('按钮文案与顺序（8 个）', [b['text'] for b in btns] == [
    '查找账号', '删除选中角色', '恢复选中角色', '拷贝选中角色', '备份选中角色', '读取恢复数据',
    '转移角色到右侧账号', '查找账号'])
check('「查找角色」按钮不存在', not hasattr(frame, 'searchCnoBtn') and not any('查找角色' in str(b['text']) for b in btns))
check('「角色名」输入框与 label 不存在',
      not hasattr(frame, 'cNameE')
      and not any(isinstance(w, ttk.Label) and '角色名' in str(w['text']) for w in descendants(frame)))
check('左树列数=6', len(cols_of(frame.characTreeV)) == 6)
check('左树列头=状态/角色ID/角色名/等级/职业/UID',
      heads_of(frame.characTreeV, 6) == ['状态', '角色ID', '角色名', '等级', '职业', 'UID'])
check('右树列数=4', len(cols_of(frame.targetTree)) == 4)
check('右树列头=角色ID/角色名/等级/职业', heads_of(frame.targetTree, 4) == ['角色ID', '角色名', '等级', '职业'])
check('转移按钮初始禁用', str(frame.moveCharacBtn['state']) == 'disabled')
check('按钮处理函数跑在后台线程（@inThread 返回 Thread）',
      isinstance(frame._reload(), threading.Thread))
pump(10)

# ---------------- 2. 左栏数据源 = 「查询」页签同一个函数 ----------------
sharedCalls = []
_realGetCharacterInfo = sqlM.getCharacterInfo
sqlM.getCharacterInfo = lambda **kw: (sharedCalls.append(kw), list(FAKE_ROWS))[1]
try:
    frame.uidE.delete(0, tk.END)
    frame.uidE.insert(0, '1')
    frame.search_account_1()
    pump()
finally:
    sqlM.getCharacterInfo = _realGetCharacterInfo
check('左栏查询走 sqlM.getCharacterInfo（和「查询」页签 guiTabMain.searchCharac 同一个函数）',
      sharedCalls == [{'uid': 1}])
rows = [tuple(frame.characTreeV.item(i)['values']) for i in frame.characTreeV.get_children()]
check('共享函数返回的行进了左栏 tree',
      len(rows) == 2 and [int(r[1]) for r in rows] == [1, 2]
      and str(rows[1][0]) == '已删除' and [int(r[5]) for r in rows] == [1, 1])

# ---------------- 3. 假数据填左树 ----------------
frame.uidE.delete(0, tk.END)      # uidE 为空 = 加载全部
frame.search_account_1()
pump()
items = list(frame.characTreeV.get_children())
rows = [tuple(frame.characTreeV.item(i)['values']) for i in items]
check('左树填了 2 行', len(rows) == 2)
check('状态列取 delete_flag（1 -> 已删除）', str(rows[1][0]) == '已删除')
check('状态列 delete_flag=0 留空', str(rows[0][0]) == '')
check('角色ID 列', [int(r[1]) for r in rows] == [1, 2])
check('UID 列 = 账号ID', [int(r[5]) for r in rows] == [1, 1])
check('填树经 runOnUi', uiCalls['_ui_fill_charac_tree'] >= 1)
check('后台线程没有直接碰控件（无线程异常）', errs == [])

# ---------------- 3b. 状态第三档「隐藏」= 不在账号缓存 charac_view 里 ----------------
check('charac_view 解出该账号已缓存的角色号', CT._view_c_nos([FAKE_ROWS[0]]) == {1: {1, 2}})
frame._ui_fill_charac_tree([(1, 3, '不在缓存里', 10, 1, 1, 0, 0)], {1: {1, 2}})
rows = [tuple(frame.characTreeV.item(i)['values']) for i in frame.characTreeV.get_children()]
check('缓存里没有、delete_flag=0 的角色 -> 状态「隐藏」', [str(r[0]) for r in rows] == ['隐藏'])
frame.uidE.delete(0, tk.END)
frame.search_account_1()       # 复原成 2 行，后面的用例按行号取
pump()
items = list(frame.characTreeV.get_children())

# ---------------- 4. 删除 / 恢复 ----------------
frame.characTreeV.selection_set(items[1])
frame.del_sel_charac()
pump()
check('删除 = sqlM.del_cNos（置 delete_flag=1）', ('del_cNos', [2]) in writes)
check('读选中行经 runOnUi', uiCalls['_ui_sel_rows'] >= 1)
check('确认框经 runOnUi', uiCalls['askokcancel'] >= 1)

items = list(frame.characTreeV.get_children())
frame.characTreeV.selection_set(items[1])
frame.rec_sel_charac()
pump()
check('恢复 = sqlM.recover_cNos（清 delete_flag）', ('recover_cNos', [2]) in writes)

# ---------------- 5. 右侧查账号 -> 转移 ----------------
frame.uidE2.delete(0, tk.END)
frame.uidE2.insert(0, '1')
frame.search_account_2()
pump()
check('右树填了 2 行', len(frame.targetTree.get_children()) == 2)
check('查到目标账号', frame.targetUID == 1)
check('查到后转移按钮解禁', str(frame.moveCharacBtn['state']) == 'normal')
frame.characTreeV.selection_set(frame.characTreeV.get_children()[1])
frame.move_charac_to_account()
pump()
moveSql = [w for w in writes if isinstance(w, str) and 'update charac_info set m_id' in w]
check('转移 = 一条 update charac_info set m_id=', len(moveSql) == 1)
check('转移 SQL 带 where charac_no in', bool(moveSql) and 'where charac_no in' in moveSql[0])

# ---------------- 6. 拷贝 / 备份 / 读取恢复数据 ----------------
frame.characTreeV.selection_set(frame.characTreeV.get_children()[1])
n0 = len(writes)
frame.copy_sel_charac()
pump()
copySql = [w for w in writes[n0:] if isinstance(w, str) and 'insert ignore into' in w]
check('拷贝对多张表写 INSERT IGNORE', len(copySql) >= 10)
check('拷贝包含 charac_info 整行复制', any('insert ignore into `charac_info`' in w for w in copySql))
check('拷贝过程无线程异常', errs == [])

if os.path.exists(CT.BAK_DIR):
    shutil.rmtree(CT.BAK_DIR, ignore_errors=True)
frame.characTreeV.selection_set(frame.characTreeV.get_children()[1])
frame.backup_sel_charac()
pump()
bakPath = os.path.join(CT.BAK_DIR, '2-1-已删角色.cbak')
check('备份文件名 = 角色ID-账号ID-角色名.cbak', os.path.exists(bakPath))
if os.path.exists(bakPath):
    bakFile.append(bakPath)

n0 = len(writes)
frame.load_bak_data()
pump()
restoreSql = [w for w in writes[n0:] if isinstance(w, str)]
check('恢复数据先 delete 再 insert',
      any(w.startswith('delete from') for w in restoreSql) and any('insert ignore into' in w for w in restoreSql))
check('恢复完成有提示', any(len(a) > 1 and a[0] == '提示' and '恢复完成' in str(a[1]) for a in msg.calls))
check('三段式文件名解析出角色ID=2', any(len(a) > 1 and '角色[2]' in str(a[1]) for a in msg.calls))
check('全程无线程异常', errs == [])

# ---------------- 7. 真库只读抽查（连不上 SKIP） ----------------
sqlM.execute_and_fetch = _origFetch
CT._colsCache.clear()      # 上面拿假 sqlM 填过假列名，这里换回真库必须清缓存
liveCur = None
try:
    import pymysql
    cfg = cacheM.config
    conn = pymysql.connect(host=cfg['DB_IP'], port=int(cfg['DB_PORT']), user=cfg['DB_USER'],
                           password=cfg['DB_PWD'], charset='utf8', connect_timeout=5, read_timeout=5)
    liveCur = conn.cursor()
    liveCur.execute('select count(*) from taiwan_cain.charac_info')
    n = int(liveCur.fetchone()[0])
    check(f'真实库 charac_info 行数 > 0（{n} 行）', n > 0)
except Exception as e:
    print(f'SKIP  真实库只读抽查连不上：{e}')

# ---------------- 8. 真文件 .cbak 结构 + 往返（全程只读 select，不写库） ----------------
REAL_CBAK = r'D:\新建文件夹\dnf_package_tool_win64_V.23.09.15\charac_bak\1-1-阿修罗.cbak'
REAL_CNO = 1
if not os.path.exists(REAL_CBAK):
    print(f'SKIP  真文件 .cbak 不在：{REAL_CBAK}')
else:
    with open(REAL_CBAK, 'rb') as f:
        rawReal = f.read()
    real = pickle.loads(zlib.decompress(rawReal))
    check('真文件 = zlib(78 9c) + pickle PROTO 3(80 03)',
          rawReal[:2] == b'\x78\x9c' and zlib.decompress(rawReal)[:2] == b'\x80\x03')
    check('真文件 16 个键、全是裸表名（0 个含点）',
          len(real) == 16 and not any('.' in k for k in real))
    check('真文件键集合 == BAK_TABLES 的表集合', set(real) == set(CT.BAK_TABLES))
    check('真文件 charac_info 第3列 latin1→utf8 == 阿修罗',
          sqlM.decode(real['charac_info'][0][2]) == '阿修罗')
    if liveCur is None:
        print('SKIP  连不上真库，跳过 .cbak 往返对照')
    else:
        dump = CT._dump_charac(REAL_CNO)          # 只读 select *，不动库
        check('往返：dump 键集合与真文件完全相同', set(dump) == set(real) and len(dump) == 16)
        check('往返：dump 键不含点', not any('.' in k for k in dump))
        # 真文件是 10-06 的快照，这角色之后还在被改（值会漂），漂移的表不算格式问题，打印出来
        drift = sorted(t for t in real if list(dump.get(t, ())) != list(real[t]))
        for t in drift:
            print(f'DRIFT {t}：真文件 {len(real[t])} 行 / 现在 {len(dump.get(t, ()))} 行')
        check('往返：未漂移的表每表行数与真文件相同',
              all(len(dump[t]) == len(real[t]) for t in real if t not in drift))
        liveCur.execute(f'select count(*) from taiwan_cain.charac_info where charac_no={REAL_CNO}')
        check('往返：charac_info 行数与真库 SELECT 一致',
              len(dump['charac_info']) == int(liveCur.fetchone()[0]))
        check('往返：charac_info 首行前 8 个标量相同',
              tuple(dump['charac_info'][0][:8]) == tuple(real['charac_info'][0][:8]))
        check('往返：每表行宽 == 真库 information_schema 列数（恢复不会报列数不符）',
              all(len(dump[t][0]) == len(CT._columns(db, t))
                  for t, (db, key) in CT.BAK_TABLES.items() if dump[t]))
        tmpDir = tempfile.mkdtemp(prefix='charac_cbak_rt_')
        try:
            tmpPath = os.path.join(tmpDir, '1-1-阿修罗.cbak')
            with open(tmpPath, 'wb') as f:
                f.write(zlib.compress(pickle.dumps(dump, protocol=3)))
            with open(tmpPath, 'rb') as f:
                rawTmp = f.read()
            check('往返：写出 zlib(78 9c) + pickle PROTO 3(80 03)',
                  rawTmp[:2] == b'\x78\x9c' and zlib.decompress(rawTmp)[:2] == b'\x80\x03')
            check('往返：读回成功且与 dump 一致',
                  pickle.loads(zlib.decompress(rawTmp)) == dump)
        finally:
            shutil.rmtree(tmpDir, ignore_errors=True)
        check('往返：临时文件已删除', not os.path.exists(tmpDir))

if liveCur is not None:
    liveCur.connection.close()
shutil.rmtree(CT.BAK_DIR, ignore_errors=True)
root.destroy()
if failed:
    print('CHARAC_TABLE_CHECK FAILED:', failed)
    sys.exit(1)
print('CHARAC_TABLE_CHECK PASSED')
