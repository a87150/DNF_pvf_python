r'''运行期连接自检：按真实启动方式（__main__.run）建出主窗口，点一次「连接数据库」，
断言：数据库用户树 6 行、在线角色/角色表有行、连接器下拉已填充、后台线程零异常、
CONNECTING_FLG 复位（没卡死），以及日志文件真的记下了整个连接过程。

为什么要按 __main__.run() 启动：print() 的日志/标题通道是 appCommon.print2title，
只有 run() 里会把它从 no-op lambda 换成真实实现。以前这个赋值只写在本模块的 global 里，
绑错了模块（print() 在 appCommon 里查自己的全局），于是日志永远停在"欢迎使用背包编辑器!"一行
——正是用户看到的那个 47 字节日志。这里把它作为断言钉住。

跑法：.venv\Scripts\python.exe tests\conn_flow_check.py（需要 config/config.json 里可连的库）
'''
import sys, os, io, re, time, threading, tkinter as tk
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import dnfpkgtool.__main__ as M
from dnfpkgtool import appCommon

# 这个脚本需要真实数据库；连不上就跳过（不算失败），其余 7 个套件都是离线的
import socket
_cfg = appCommon.cacheM.config
try:
    socket.create_connection((_cfg['DB_IP'], int(_cfg['DB_PORT'])), 3).close()
except OSError as _e:
    print('SKIP  连不上 %s:%s（%s），本次跳过；本套件需要真实数据库' % (_cfg['DB_IP'], _cfg['DB_PORT'], _e))
    sys.exit(0)

failed = []
def check(name, cond, extra=''):
    print(('PASS  ' if cond else 'FAIL  ') + name + (('  ' + str(extra)) if extra else ''))
    if not cond:
        failed.append(name)

errs = []
threading.excepthook = lambda a: errs.append((a.exc_type.__name__, str(a.exc_value)))

holder = {}
_orig = M.GuiApp.__init__
def _patched(self, *a, **kw):
    _orig(self, *a, **kw)
    holder['app'] = self
M.GuiApp.__init__ = _patched

root = tk.Tk()
root.geometry('1200x800+20+20')

def run_checks():
    app = holder.get('app')
    tabs = [app.tabView.tab(i, 'text').strip() for i in app.tabView.tabs()] if app else []
    check('主窗口构造完成，12 个页签且含「角色表」', app is not None and len(tabs) == 12 and '角色表' in tabs, tabs)
    check('页签顺序 封停→角色表→其它',
          tabs[tabs.index('封停'):tabs.index('封停') + 3] == ['封停', '角色表', '其它']
          if '封停' in tabs else False, tabs)
    if app is None:
        root.destroy(); return

    # 启动前是模块里那个 no-op lambda；run() 必须把它换成真实实现（inThread 的 inner）
    check('run() 已把真实 print2title 装进 appCommon（否则日志只有一行欢迎语）',
          getattr(appCommon.print2title, '__name__', '') != '<lambda>',
          appCommon.print2title)

    app.db_conBTN.config(state='normal')
    if not app.CONNECTING_FLG:                 # 自动连接可能已经跑过了
        app.db_conBTN.invoke()                 # 真实触发连接流程
    check('连接流程已启动', app.CONNECTING_FLG is True)

    def wait_done():
        if app.CONNECTING_FLG and time.time() < wait_done.deadline:
            root.after(100, wait_done); return
        for _ in range(20):                    # 再等 fill_db_bak / 事件日志刷新跑完
            root.update(); time.sleep(0.05)
        report(app)
    wait_done.deadline = time.time() + 60
    root.after(100, wait_done)

def charac_trees(app):
    """在线角色/角色表可能落在查询页的 characTreeV，也可能落在独立的「角色表」页；两个都算。"""
    out = []
    for name in ('characTreeV',):
        w = getattr(app, name, None)
        if w is not None:
            out.append((name, w))
    w = getattr(app, 'characTableFrame', None)
    if w is not None:
        out.append(('角色表页', getattr(w, 'characTreeV', None)))
    return [(n, w) for n, w in out if w is not None]

def report(app):
    users = app.sqlUserManageF.sqlUserTree
    userRows = [tuple(users.item(i)['values']) for i in users.get_children()]
    characRows = []
    for name, tree in charac_trees(app):
        rows = tree.get_children()
        print('%s 行数 = %d  前几行 = %s' % (name, len(rows),
              [tree.item(i)['values'] for i in rows[:5]]))
        characRows += list(rows)
    print('数据库用户树行数 =', len(userRows))
    print('数据库用户 =', userRows)
    print('连接器 =', app.connectorE.get(), '| 事件树行数 =', len(app.eventTreeNow.get_children()),
          '| 封停树行数 =', len(app.banedTreeV.get_children()), '| 远端库列表行数 =', len(app.remoteSqlTree.get_children()))
    check('数据库用户树有 6 行', len(userRows) == 6, len(userRows))
    check('数据库用户首行形如 (user, host)', bool(userRows) and len(userRows[0]) == 2, userRows[:1])
    logText = ''
    try:
        with open(appCommon.LOGFile, 'r', encoding='utf-8') as f:
            logText = f.read()
    except BaseException as e:
        logText = '<读日志失败 %s>' % e
    # 日志就是判据：连接流程里会 print「当前在线角色已加载(N)」。N=0 说明用户此刻没在游戏里，
    # 这时候树里 0 行是环境如此，不是接线坏了 —— 打 SKIP，不算失败。
    print('--- 日志 %s (%d 字节) ---' % (appCommon.LOGFile, len(logText.encode('utf-8'))))
    print(logText.strip()[:600])
    m = re.search(r'当前在线角色已加载\((\d+)\)', logText)
    online = int(m.group(1)) if m else None
    if len(characRows) > 0:
        check('在线角色 / 角色表有行', True, len(characRows))
    elif online == 0:
        print('SKIP  在线角色（当前无人在线）')
    else:
        check('在线角色 / 角色表有行', False, '日志在线角色数=%s，树里 %d 行' % (online, len(characRows)))
    check('连接器下拉已填充（connectorE）', app.connectorE.get().startswith('0-'), app.connectorE.get())
    check('后台线程无异常', errs == [], errs)
    check('CONNECTING_FLG 已复位（流程走完，没卡死）', app.CONNECTING_FLG is False)

    check('日志里有"正在连接数据库"', '正在连接数据库' in logText)
    check('日志里有"数据库连接成功"', '数据库连接成功' in logText)
    check('日志不再只有那一行欢迎语', len(logText.encode('utf-8')) > 200, len(logText.encode('utf-8')))

    root.destroy()

def wait_window(deadline=None):
    if 'app' not in holder and time.time() < (deadline or time.time() + 30):
        root.after(200, lambda: wait_window(deadline or time.time() + 30)); return
    run_checks()
root.after(1000, wait_window)      # 等 run() 把窗口建好（GuiApp 构造完成后接管）
root.after(60000, lambda: (print('TIMEOUT: 60s 兜底退出'), root.destroy()))
M.run(root_=root)          # 与真实启动同一路径：建窗口 -> 泵 -> 自动连接 -> mainloop
if failed:
    print('CONN_FLOW_CHECK FAILED:', failed)
    sys.exit(1)
print('CONN_FLOW_CHECK PASSED')
