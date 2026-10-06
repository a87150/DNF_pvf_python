# -*- coding: utf-8 -*-
'''界面结构自检：确认"去图片"改造没有留下断口。

跑法：.venv\\Scripts\\python.exe tests\\uitree_check.py
程序会建出主窗口（不连数据库）、检查控件树，然后把窗口销毁。
'''
import sys
import tkinter as tk
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import dnfpkgtool.__main__ as M

holder = {}
_orig = M.GuiApp.__init__


def _patched(self, *a, **kw):
    _orig(self, *a, **kw)
    holder['app'] = self


def descendants(w):
    out = []
    for c in w.winfo_children():
        out.append(c)
        out.extend(descendants(c))
    return out


def main():
    M.GuiApp.__init__ = _patched
    root = tk.Tk()
    failed = []

    def check(name, cond):
        print(('  OK   ' if cond else '  FAIL ') + name)
        if not cond:
            failed.append(name)

    def run_checks():
        app = holder['app']
        check('主窗口无 imageFrame1（查询页广告位已删）', not hasattr(app, 'imageFrame1'))
        check('主窗口无 aboutImageLabel（关于页图片已删）', not hasattr(app, 'aboutImageLabel'))
        check('主窗口无 qrLabel/qrCode（关于页二维码已删）', not hasattr(app, 'qrLabel') and not hasattr(app, 'qrCode'))
        check('主窗口无 sponsorFrame 开关（GM 广告页已删）', not hasattr(app, 'sponsorFrame'))
        check('tabViewChangeFuncs 无残留回调', app.tabViewChangeFuncs == [])
        check('其它页已无 gitHubFrame 外链容器', not hasattr(app, 'gitHubFrame'))
        btns = [k for k in descendants(app.aboutFrame) if isinstance(k, tk.ttk.Button)]
        check('关于页不再有「项目地址 / 交流群」按钮', len(btns) == 0)
        links = [k for k in descendants(app.aboutFrame)
                 if isinstance(k, tk.Label) and k.cget('cursor') == 'hand2']
        check('关于页有两条可点击链接',
              len(links) == 2 and all(k.bind('<Button-1>') for k in links))
        check('链接文案是原项目地址 / 本项目地址',
              sorted(k.cget('text') for k in links) == ['原项目地址', '本项目地址'])
        check('两条链接居中摆在关于页空档（place）',
              all(k.winfo_manager() == 'place' for k in links))
        check('主窗口有全局日志区', hasattr(app, 'logTextE') and hasattr(app, 'logFrame'))
        M.log('__全局日志自检__')
        check('全局日志能收到消息', '__全局日志自检__' in app.logTextE.get('1.0', 'end'))
        check('旧GM工具按钮已删除', not hasattr(app, 'GMtoolBtn'))
        check('"启动时打开"复选框已删除', not hasattr(app, 'autoGMVar'))
        check('_open_GM 已删除', not hasattr(app, '_open_GM'))
        check('set_gm_startup 已删除', not hasattr(app, 'set_gm_startup'))
        check('imageLabel 模块已不在包内', not (ROOT / 'dnfpkgtool' / 'widgets' / 'imageLabel.py').exists())
        check('广告图片资源已删', not (ROOT / 'config' / 'gif').exists() and not (ROOT / 'config' / 'gif2').exists())
        print('主窗口标签页：', [app.tabView.tab(i, 'text').strip() for i in app.tabView.tabs()])
        root.destroy()

    root.after(8000, run_checks)
    M.run(root_=root)
    if failed:
        print('UITREE_CHECK FAILED:', failed)
        return 1
    print('UITREE_CHECK PASSED')
    return 0


if __name__ == '__main__':
    sys.exit(main())
