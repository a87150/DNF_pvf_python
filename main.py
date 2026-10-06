# -*- coding: utf-8 -*-
"""打包入口：把工作目录切到 exe 所在目录，并保证 config/ 就位。

开发时直接跑：.venv\\Scripts\\python.exe main.py
"""
import os
import shutil
import sys
from pathlib import Path

# --- PyMySQL 1.0.2 的 Windows 启动地雷 ---------------------------------------------
# pymysql/connections.py 在 import 时算了一次 getpass.getuser()。
# getuser() 先查 LOGNAME / USER / LNAME / USERNAME，查不到就 import pwd（Windows 没有），
# 于是抛 OSError: No username set in the environment。
# 打包成 exe 后环境里可能没有这些变量（本次就是这样），结果**主程序还没建窗口就退出**，
# 连 log/ 都不会生成 —— 排查时看起来像"什么都没发生"。
# 这里补一个假的 pwd 模块：getpass 只会用它拿用户名，拿不到会自动回退到环境变量。
if 'pwd' not in sys.modules:
    import types as _types
    _pwd = _types.ModuleType('pwd')
    def _user():
        return (os.environ.get('USERNAME')
                or os.environ.get('LOGNAME')
                or os.environ.get('USER')
                or os.environ.get('USERPROFILE', '').replace('\\', '/').rsplit('/', 1)[-1]
                or 'user')
    _pwd.getpwuid = lambda _uid: (_user(), '*', 0, 0, '', '', '')
    _pwd.getpwnam = lambda _name: (_name, '*', 0, 0, '', '', '')
    _pwd.struct_passwd = ()
    sys.modules['pwd'] = _pwd
    # getpass 还会走 pwd.getpwuid(os.getuid())，而 Windows 上 os.getuid 根本不存在
    # （py3.13 起 getuser 只接住 ImportError/KeyError，AttributeError 会直接抛出去）。
    if not hasattr(os, 'getuid'):
        os.getuid = lambda: 0
if not (os.environ.get('LOGNAME') or os.environ.get('USER')):
    _u = os.environ.get('USERNAME') or os.environ.get('USERPROFILE', '').replace('\\', '/').rsplit('/', 1)[-1]
    if _u:
        os.environ.setdefault('LOGNAME', _u)
# ----------------------------------------------------------------------------------

FROZEN = getattr(sys, 'frozen', False)
if FROZEN:
    BASE = Path(sys.executable).resolve().parent      # exe 同级目录（config/ 放这里）
    BUNDLE = Path(getattr(sys, '_MEIPASS', BASE))     # 打包进去的只读资源
else:
    BASE = Path(__file__).resolve().parent
    BUNDLE = BASE

os.chdir(BASE)

# 首次运行：把打包进去的默认配置复制到 exe 同级（config 会被程序改写，不能留在只读包内）
if FROZEN and not (BASE / 'config').exists() and (BUNDLE / 'config').exists():
    shutil.copytree(BUNDLE / 'config', BASE / 'config')

if __name__ == '__main__':
    # 冻结成 exe 后必须调用，否则 pvfReader 的多进程解析子进程起不来，加载 PVF 会一直无响应
    import multiprocessing
    multiprocessing.freeze_support()

    # 自检：DNF背包编辑工具.exe --loadpvf <Script.pvf>  （结果写进 log/，用于验证打包是否完整）
    if len(sys.argv) > 2 and sys.argv[1] == '--loadpvf':
        import traceback
        from dnfpkgtool.__main__ import log
        from dnfpkgtool import cacheManager as cacheM
        try:
            info = cacheM.loadItems2(True, sys.argv[2], encode='big5')
            log('PVF自检完成：%s' % info)
        except Exception:
            log('PVF自检失败：%s' % traceback.format_exc())
        sys.exit(0)

    from dnfpkgtool.__main__ import run
    run()
