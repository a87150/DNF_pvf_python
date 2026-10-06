# tkinter 跨线程自检：Python 3.14 下后台线程直接操作控件会抛 RuntimeError: main thread is not in main loop
# （旧版 py3.6 能容忍，所以升级后才暴露：数据库页"连上了但看不到内容"就是这个原因）
#
# 另外盯三件曾经真出过故障的事：
#   1. 泵回调里抛异常后必须还能 re-arm——否则 root.after 不再重排，之后所有后台线程的 runOnUi 永久卡死，
#      表现是"点了连接数据库，日志里连一句正在连接都没有"（打包成 --windowed 时泵里的 traceback.print_exc()
#      自己会抛，就是这条路）。
#   2. runOnUi 必须有超时，任何原因导致主线程不响应都要抛错而不是永久挂起。
#   3. 泵的异常出口必须写日志文件，不能只打 stderr（--windowed 下 stderr 是 None）。
import sys, os, io, time, threading, tkinter as tk
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import dnfpkgtool.appCommon as appCommon
from dnfpkgtool import sqlManager2 as sqlM, cacheManager as cacheM, sqlUserManager as UM

def check(name, cond):
    print(('PASS  ' if cond else 'FAIL  ') + name)
    if not cond:
        sys.exit(1)

FAKE = [('root', '%'), ('game', '127.0.0.1'), ('game', 'localhost'),
        ('mysql.session', 'localhost'), ('mysql.sys', 'localhost'), ('zageku', '%')]
seenThread = []
def fakeFetch(db, sql, *a, **k):
    seenThread.append(threading.current_thread().name)
    return list(FAKE)
sqlM.execute_and_fetch = fakeFetch          # 不依赖真实数据库

errs = []
threading.excepthook = lambda a: errs.append((a.exc_type.__name__, str(a.exc_value)))

root = tk.Tk(); root.withdraw()
appCommon.startUiPump(root)

# --- 正常业务：后台取用户列表回主线程填树 ---
w = UM.SqluserframeWidget(root)
w.get_all_users()                            # 走 @inThread，DB 查询在后台线程
for _ in range(60):
    root.update(); time.sleep(0.05)

check('后台取用户后列表被填充（6 行）', len(w.sqlUserTree.get_children()) == 6)
check('线程里没有异常（控件更新已回到主线程）', errs == [])
first = tuple(w.sqlUserTree.item(w.sqlUserTree.get_children()[0])['values'])
check('首行是 root/%', first == ('root', '%'))
check('DB 查询确实跑在后台线程（没退化回主线程阻塞）', seenThread and seenThread[0] != 'MainThread')
check('runOnUi 在主线程调用时直通执行（否则会自锁）', appCommon.runOnUi(lambda: 42) == 42)

# --- 泵被回调异常撞过之后必须还活着（本次故障的机制）---
def boom():
    raise ValueError('__pump_must_survive__')
th = threading.Thread(target=lambda: appCommon.runOnUi(boom), daemon=True)
th.start()
deadline = time.time() + 10
while th.is_alive() and time.time() < deadline:
    root.update(); time.sleep(0.02)
check('泵把回调异常回抛给调用线程（而不是自己停）', not th.is_alive())

box = {}
th2 = threading.Thread(target=lambda: box.setdefault('r', appCommon.runOnUi(lambda: 'alive')), daemon=True)
th2.start()
deadline = time.time() + 10
while th2.is_alive() and time.time() < deadline:
    root.update(); time.sleep(0.02)
check('回调抛异常之后泵仍在 re-arm，后续 runOnUi 照常返回', box.get('r') == 'alive')

# --- 泵的异常出口必须落进日志文件（--windowed 下 stderr 为 None）---
logFile = appCommon.LOGFile
before = os.path.getsize(logFile) if os.path.exists(logFile) else 0
appCommon._uiLog('__uiLog_to_file__')
after = os.path.getsize(logFile) if os.path.exists(logFile) else 0
check('泵错误出口写进日志文件而不是只看 stderr', after > before)

# --- 主线程不响应时 runOnUi 必须超时抛错，不能永久 wait ---
# 模拟"泵死了"：_uiRoot 指向一个不会再被泵处理的假 root，任务只入队没人取。
old_timeout = appCommon.UI_CALL_TIMEOUT
old_root = appCommon._uiRoot
appCommon.UI_CALL_TIMEOUT = 0.5
appCommon._uiRoot = object()
res = {}
def _waiter():
    t0 = time.time()
    try:
        appCommon.runOnUi(lambda: 'never')
        res['raised'] = None
    except RuntimeError as e:
        res['raised'] = e
    res['cost'] = time.time() - t0
tw = threading.Thread(target=_waiter, daemon=True); tw.start(); tw.join(10)
appCommon.UI_CALL_TIMEOUT = old_timeout
appCommon._uiRoot = old_root
check('泵停住时 runOnUi 超时抛 RuntimeError（不再永久挂起）',
      isinstance(res.get('raised'), RuntimeError) and res.get('cost', 99) < 5)
for _ in range(40):        # 让恢复后的泵把那条超时任务排掉，保持队列干净
    root.update(); time.sleep(0.02)

root.destroy()
print('UI_THREAD_CHECK PASSED')
