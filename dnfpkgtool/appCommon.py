import sys
import platform
import tkinter as tk
import tkinter.ttk as ttk
from ttkbootstrap import Style
from tkinter import ttk, messagebox
from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory
import ipaddress
import os
if __name__=='__main__':
    import sys 
    sys.path.append(os.getcwd())
    sys.path.append(os.path.join(os.getcwd(),'dnfpkgtool'))
from dnfpkgtool import itemSlotFrame
from dnfpkgtool import creatureFeame
from dnfpkgtool import avatarFrame
from dnfpkgtool import mailFrame
from dnfpkgtool import characFrame
import threading
import queue
import traceback

# ---- 主线程调度：后台线程只跑 DB/网络/耗时活，控件更新统一交回主线程 ----
# 必须定义在下面那些 dnfpkgtool 子模块 import 之前：子模块用 from dnfpkgtool.appCommon import *
# 取 inThread/runOnUi，appCommon 又反过来 import 它们，循环导入时这里还没执行到就会 AttributeError。
_uiQueue = queue.Queue()
_uiRoot = None
UI_CALL_TIMEOUT = 60    # runOnUi 阻塞上限（秒）

def _uiLog(text):
    """泵自己的错误出口：写日志文件 + 打一份到 stderr（打包成 --windowed 时 stderr 是 None）。
    不能用 appCommon.log()：它内部会调 runOnUi，泵出错时正好是 runOnUi 最可能死锁的时刻。"""
    try:
        import time as _time
        tm = _time.localtime()
        line = '[%s-%s %s:%s:%s] [UI泵] %s' % ('%02d' % tm.tm_mon, '%02d' % tm.tm_mday, '%02d' % tm.tm_hour, '%02d' % tm.tm_min, '%02d' % tm.tm_sec, text)
        with open(LOGFile,'a+',encoding='utf-8') as f:
            f.write(line + chr(10))
    except BaseException:
        pass
    if sys.stderr is not None:      # --windowed 下是 None，print_exc/print 自己会抛
        try:
            print(line, file=sys.stderr)
        except BaseException:
            pass

def runOnUi(func,*args,**kw):
    """在主线程执行 func 并返回结果。
    主线程自己调用时直接执行；泵没启动（独立小工具）时退回原行为，直接在当前线程执行。
    泵死了也不允许永久挂起：最多等 UI_CALL_TIMEOUT 秒，超时先记录一条明确错误再抛 RuntimeError。"""
    if _uiRoot is None or threading.current_thread() is threading.main_thread():
        return func(*args,**kw)
    box = [None,None]
    done = threading.Event()
    _uiQueue.put((func,args,kw,box,done))
    if not done.wait(UI_CALL_TIMEOUT):
        _uiLog('等待主线程执行 %s 超过 %ss，主线程 UI 泵可能已停止' % (getattr(func,'__name__',func), UI_CALL_TIMEOUT))
        raise RuntimeError('runOnUi 超时 %ss：主线程未响应（UI 泵可能已停止）：%s' % (UI_CALL_TIMEOUT, getattr(func,'__name__',func)))
    if box[1] is not None:
        raise box[1]
    return box[0]

def startUiPump(root):
    """建好 root、起任何线程之前调用一次；每 30ms 在主线程清一次队列。
    异常只记录（写日志文件）绝不逃出回调：一旦逃出，root.after 不再 re-arm，之后所有
    worker 线程的 runOnUi 就永久卡死——这正是连接流程连一句日志都没有的那种故障。"""
    global _uiRoot
    if _uiRoot is not None:
        return
    _uiRoot = root
    def pump():
        try:
            while True:
                try:
                    func,args,kw,box,done = _uiQueue.get_nowait()
                except queue.Empty:
                    break
                try:
                    box[0] = func(*args,**kw)
                except BaseException as e:
                    box[1] = e     # 回抛给调用线程
                    _uiLog('执行 %s 出错：%s' % (getattr(func,'__name__',func), traceback.format_exc()))
                finally:
                    done.set()     # 无论如何都要放行等待中的线程
        except BaseException:
            _uiLog('泵异常（已继续运行）：%s' % traceback.format_exc())
        finally:
            try:
                root.after(30,pump)    # re-arm 必须在 finally：root 销毁后这里会抛，属正常退出路径
            except BaseException:
                pass
    root.after(30,pump)

from dnfpkgtool.pvfJson import loadJsonFile   # 兼容读取 config/*.json（UTF-8 / GBK），无循环 import

def inThread(func):
    def inner(*args,**kw):
        t = threading.Thread(target=lambda:func(*args,**kw))
        t.daemon = True
        t.start()
        return t
    return inner

from dnfpkgtool import cacheManager as cacheM

from dnfpkgtool import sqlManager2 as sqlM
from pathlib import Path
import time
from copy import deepcopy
import struct
from dnfpkgtool.widgets.toolTip import CreateToolTip, CreateOnceToolTip, ToolTip
from dnfpkgtool import ps
from dnfpkgtool.widgets.titleBar import TitleBarFrame
from dnfpkgtool import pvfEditorGUI
#from dnfpkgtool import findServerFrame
from dnfpkgtool import questFrame
from dnfpkgtool import sqlUserManager
import pyperclip
import pickle
import json
import base64
import datetime

WIDTH = 1

oldPrint = print
logFunc = [oldPrint]
print2title = lambda x:...
def print(*args,**kw):
    try:
        if len(args)==1:
            text = str(args[0])
            print2title(text)
        else:
            text = str(args)
    except BaseException:
        pass    # print2title 只是日志/标题通道，坏掉不能影响正常 print 落到日志文件
    logFunc[-1](*args,**kw)

logPath = Path('log/')
IconPath = 'config/ico.png'
if not logPath.exists():
    logPath.mkdir()
tm = time.localtime()
LOGFile = f'./log/{"%02d" % tm.tm_mon}-{"%02d" % tm.tm_mday} {"%02d" % tm.tm_hour}_{"%02d" % tm.tm_min}_{"%02d" % tm.tm_sec}.log'

LOG_WIDGET = None   #主窗口下方的全局日志控件，界面建好后赋值

def log(text):
    tm = time.localtime()
    log = '[%s-%s %s:%s:%s] %s' % ('%02d' % tm.tm_mon, '%02d' % tm.tm_mday, '%02d' % tm.tm_hour, '%02d' % tm.tm_min, '%02d' % tm.tm_sec, text)
    log += chr(10)
    with open(LOGFile,'a+',encoding='utf-8') as f:
        f.write(log)
    if LOG_WIDGET is not None:   #背包编辑器 + PVF 编辑器的日志都汇总到这里
        # log() 会被各后台线程调用（PVF加载、选角色、SQL连接…），控件写入回主线程
        runOnUi(LOG_WIDGET.insert,tk.END,log)
        runOnUi(LOG_WIDGET.see,tk.END)

def str2bytes(s)->bytes:
    i = 0
    length = len(s)
    nums = []
    while i<length:
        nums.append(int(s[i:i+2],base=16))
        i+=2
    return struct.pack('B'*len(nums),*nums)

expert_jobMap={
    0:'无职业',
    1:'附魔师',
    2:'炼金术师',
    3:'分解师',
    4:'控偶师'
}

globalBlobs_map = {
        '物品栏':'inventory',
        '穿戴栏':'equipslot',
        '宠物栏':'creature',
        ' 仓库 ':'cargo',
        '账号金库':'account_cargo'
    }
globalNonBlobs_map = {
    ' 宠物 ':'creature_items',
    ' 时装 ':'user_items',
    ' 邮件 ':'user_postals'
    }

tabIDDict = {}

rarityMap = cacheM.rarityMap
rarityMapRev = cacheM.rarityMapRev

def configFrame(frame:tk.Frame,value='disable',attr='state'):
    try:
        frame[attr] = value
    except:
        pass
    for widget in frame.children.values():
        if type(widget) in [tk.Frame,tk.LabelFrame,ttk.Frame,ttk.Treeview,ttk.Notebook,ttk.Labelframe]:
            configFrame(widget,value,attr)
        else:
            try:
                widget[attr] = value
            except:
                continue

def configBtnPack(frame:tk.Frame,value=1,attr='padx'):
    for widget in frame.children.values():
        if isinstance(widget,ttk.Button):
            try:
                widget.pack_configure({attr:value})
            except:
                
                try:
                    widget.grid_configure({attr:value})
                except:
                    print('配置失败')
                    continue
        else:
            configBtnPack(widget,value,attr)

letter_send_dict = {}

def setLogWidget(w):
    '''界面构建完成后调用，把主窗口底部的事件日志控件交给 log()'''
    global LOG_WIDGET
    LOG_WIDGET = w

def creat_cxv_pkg(t:ttk.Treeview,app:'GuiApp',tabName:str):
    def copySel(event=None):
        copyString = ''
        for sel in t.selection():
            copyString += ','.join([str(i) for i in t.item(sel)['values']])+'\n'
        pyperclip.copy(copyString.strip('\n'))
    
    def copyAll(event=None):
        copyString = ''
        for sel in t.get_children():
            copyString += ','.join([str(i) for i in t.item(sel)['values']])+'\n'
        pyperclip.copy(copyString.strip('\n'))
    
    def copyAsCode(event=None):
        sels = t.selection()
        values = [t.item(sel)['values'] for sel in sels]
        indexList = [int(item[0]) for item in values]
        characItemDict = app.selectedCharacItemsDict[tabName]
        selItemSlots = {}
        itemName0 = cacheM.ITEMS_dict.get(characItemDict[indexList[0]].id)
        for index in indexList:
            selItemSlots[index] = characItemDict[index]
        copyStringBytes = pickle.dumps(selItemSlots)
        copyString = base64.b64encode(copyStringBytes).decode('utf-8')
        pyperclip.copy(copyString)
        print(f'[{itemName0}]等{len(indexList)}个物品数据已复制至剪贴板')

    def pasteCode(event=None):
        try:
            b64String = pyperclip.paste()
            copyStringBytes = base64.b64decode(b64String)
            itemDict = pickle.loads(copyStringBytes)
        except:
            itemDict = ''
            print('剪贴板数据读取错误')
            return False
        if type(itemDict) is not dict:
            print(f'剪贴板数据格式错误,{type(itemDict)}')
            return False
        sel = t.selection()[0]
        values = t.item(sel)['values']
        index = int(values[0])
        editedDict = app.editedItemsDict[tabName]
        characItemDict = app.selectedCharacItemsDict[tabName]
        pasteNum = 0
        itemName0 = cacheM.ITEMS_dict.get(list(itemDict.values())[0].id)
        for itemSlot in itemDict.values():
            if characItemDict.get(index) is None:
                print('物品位置超出，已跳过')
                continue
            editedDict[index] = itemSlot
            index += 1
            pasteNum += 1
        #t.selection_set(sel)
        editFrameShowFunc = app.editFrameShowFuncs[tabName]
        editFrameShowFunc(save=False)
        print(f'已粘贴[{itemName0}]等{pasteNum}个物品数据')

    def delSel(event=None):
        sels = t.selection()
        editedDict = app.editedItemsDict[tabName]
        for sel in sels:
            index = int(t.item(sel)['values'][0])
            editedDict[index] = sqlM.DnfItemSlot(b'\x00'*61)
        editFrameShowFunc = app.editFrameShowFuncs[tabName]
        editFrameShowFunc(save=False)
        print(f'已标记{len(sels)}个物品为删除状态')
    def sealSel(event=None):
        sels = t.selection()
        editedDict = app.editedItemsDict[tabName]
        initItemDict = app.selectedCharacItemsDict[tabName]
        for sel in sels:
            index = int(t.item(sel)['values'][0])
            itemSlot:sqlM.DnfItemSlot = initItemDict[index] if editedDict.get(index) is None else editedDict[index]
            itemSlot.isSeal = 1
            editedDict[index] = itemSlot
        editFrameShowFunc = app.editFrameShowFuncs[tabName]
        editFrameShowFunc(save=False)
    
    def unsealSel(event=None):
        sels = t.selection()
        editedDict = app.editedItemsDict[tabName]
        initItemDict = app.selectedCharacItemsDict[tabName]
        for sel in sels:
            index = int(t.item(sel)['values'][0])
            itemSlot:sqlM.DnfItemSlot = initItemDict[index] if editedDict.get(index) is None else editedDict[index]
            itemSlot.isSeal = 0
            itemSlot.sealCnt = 0
            editedDict[index] = itemSlot
        editFrameShowFunc = app.editFrameShowFuncs[tabName]
        editFrameShowFunc(save=False)

    '''创建一个弹出菜单'''
    menu = tk.Menu(t,
                tearoff=False,
                #bg="black",
                )
    
    menu.add_command(label="复制", command=copySel)
    menu.add_command(label="复制为代码", command=copyAsCode)
    menu.add_command(label="粘贴代码", command=pasteCode)
    menu.add_command(label="复制全部", command=copyAll)
    menu.add_command(label="标记为删除", command=delSel)
    menu.add_command(label="标记为封装", command=sealSel)
    menu.add_command(label="取消封装", command=unsealSel)

    def popup(event):
        if len(t.selection())==0:
            menu.entryconfig(0,state='disabled')
            menu.entryconfig(1,state='disabled')
            menu.entryconfig(2,state='disabled')
        else:
            menu.entryconfig(0,state='normal')
            menu.entryconfig(1,state='normal')
            menu.entryconfig(2,state='normal')
        if len(t.get_children())==0:
            menu.entryconfig(3,state='disabled')
        else:
            menu.entryconfig(3,state='normal')
        
        menu.post(event.x_root, event.y_root)   # post在指定的位置显示弹出菜单

    t.bind("<Button-3>", popup,add='')                 # 绑定鼠标右键,执行popup函数


if __name__ == "__main__":
    run()
    


