# -*- coding: utf-8 -*-
"""打包入口：把工作目录切到 exe 所在目录，并保证 config/ 就位。

开发时直接跑：.venv\\Scripts\\python.exe main.py
"""
import os
import shutil
import sys
from pathlib import Path

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
