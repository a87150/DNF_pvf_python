'''背包编辑器主窗口：GUI 主体按功能拆到 dnfpkgtool/gui*.py 的 mixin，这里只做组合、提供 run() 入口与 cxv 包生成'''
import dnfpkgtool.appCommon as _appCommon
from dnfpkgtool.appCommon import *
from dnfpkgtool.guiInit import GuiAppInit
from dnfpkgtool.guiTabMain import GuiAppTabMain
from dnfpkgtool.guiTabCharac import GuiAppTabCharac
from dnfpkgtool.guiTabGM import GuiAppTabGM
from dnfpkgtool.guiTabSsh import GuiAppTabSsh
from dnfpkgtool.guiActions import GuiAppActions


class GuiApp(GuiAppInit, GuiAppTabMain, GuiAppTabCharac, GuiAppTabGM, GuiAppTabSsh, GuiAppActions):
    '''主界面：方法体见各 mixin 模块'''


def run(finCallBackFunc=lambda:None,root_:tk.Tk=None):
    #from ttkthemes import themed_tk
    lastTitleTimeStamp = time.time()
    global print2title
    @inThread
    def resetTitle():
        while True:
            if time.time()-lastTitleTimeStamp>5:
                try:
                    runOnUi(root.title,app.titleString)
                except:
                    pass
            time.sleep(5)

    @inThread
    def print2title(*args):
        '''输出到title和日志'''
        if len(args)==1:
            runOnUi(root.title,str(args[0]))
        else:
            runOnUi(root.title,str(args))
        nonlocal lastTitleTimeStamp
        lastTitleTimeStamp = time.time()
        log(*args)
    # appCommon 里的 print() 取的是 appCommon 自己的全局名；只在本模块 global 赋值等于没赋值，
    # 结果就是 print2title 一直是那个 no-op lambda —— 标题永远不更新、log() 只剩显式调用。
    _appCommon.print2title = print2title

    global root
    W = 720
    H = 520
    if platform.system().lower() == 'linux':
        W = 800
        H = 700

    
    theme = cacheM.config.get('THEME','默认主题')
    style = None
    if theme!='默认主题':
        W = 920
        H = 640
    if root_ is None:
        if theme =='默认主题':
            root = tk.Tk()
        else:
            
            style = Style() #darkly cyborg minty
            root = style.master
            style.theme_use(theme)        
    else:
        root = root_
    
    startUiPump(root)   # 主线程泵：必须在下面任何后台线程（resetTitle/connectSQL…）之前启动
    root.title('背包编辑工具')
    resetTitle()

    try:
        import ctypes
        #获取屏幕的缩放因子
        ScaleFactor=ctypes.windll.shcore.GetScaleFactorForDevice(0)
        if ScaleFactor!=100:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
            root.tk.call('tk', 'scaling', ScaleFactor/75)
            W = int(W + W*(ScaleFactor-100)*0.8//100)
            H = int(H + H*(ScaleFactor-100)*0.6//100)
            s=ttk.Style()

            s.configure('Treeview', rowheight=20*ScaleFactor//100)
    except:
        print('高清缩放失败')
    
    W, H = cacheM.config.get('RESOLUTION',f'{W}x{H}').split('x')
    #老配置的分辨率偏小，这里抬到下限，同时不超出屏幕
    W = min(max(int(W),1200),root.winfo_screenwidth()-60)
    H = min(max(int(H),800),root.winfo_screenheight()-80)
    root.geometry(f'{W}x{H}+{root.winfo_screenwidth()//2-W//2}+{root.winfo_screenheight()//2-H//2}')
    def fixed_map(option):
        return [elm for elm in style2.map('Treeview', query_opt=option) if
        elm[:2] != ('!disabled', '!selected')]
    style2 = ttk.Style()
    style2.map('Treeview', foreground=fixed_map('foreground'),
    background=fixed_map('background'))
    app = GuiApp(root,style=style)
    if cacheM.config.get('PVF_PATH')!='':
        app.w.after(2000,lambda:app.load_PVF(cacheM.config.get('PVF_PATH')))
    
    app.w.after(200,app.connectSQL)
    #print(ScaleFactor)
    root.deiconify()
    root.overrideredirect(False)
    #move root to center
    configBtnPack(root,2,'padx')
    configBtnPack(root,2,'pady')
    root.update()
    root.update_idletasks()
    #root.geometry(f'+{int((root.winfo_screenwidth()-W)/2)}+{int((root.winfo_screenheight()-H)/2)}')
    root.focus_force()
    finCallBackFunc()
    #configFrame(root,'yellow','bg')
    #configFrame(root,'yellow','background')
    
    app.run()
    for localVar,localValue in locals().items():
        globals()[localVar] = localValue
