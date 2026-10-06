# tkinter 跨线程自检：Python 3.14 下后台线程直接操作控件会抛 RuntimeError: main thread is not in main loop
# （旧版 py3.6 能容忍，所以升级后才暴露：数据库页"连上了但看不到内容"就是这个原因）
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
root.destroy()
print('UI_THREAD_CHECK PASSED')
