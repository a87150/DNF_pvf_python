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
from dnfpkgtool import cacheManager as cacheM

from dnfpkgtool import sqlManager2 as sqlM
from pathlib import Path
import time
from copy import deepcopy
import struct
from dnfpkgtool.widgets.toolTip import CreateToolTip, CreateOnceToolTip, ToolTip
from dnfpkgtool import ps
import webbrowser
from dnfpkgtool.widgets.titleBar import TitleBarFrame
from dnfpkgtool import gmTool_resize as gmToolGUI
from dnfpkgtool import pvfEditorGUI
#from dnfpkgtool import findServerFrame
from dnfpkgtool import questFrame
from dnfpkgtool import sqlUserManager
import pyperclip
import pickle
import json
import base64
import datetime
import pyqrcode

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
    except:
        pass
    logFunc[-1](*args,**kw)

def inThread(func):
    def inner(*args,**kw):
        t = threading.Thread(target=lambda:func(*args,**kw))
        t.daemon = True
        t.start()
        return t
    return inner

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
        LOG_WIDGET.insert(tk.END,log)
        LOG_WIDGET.see(tk.END)

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

def openWeb(e=None): 
    webbrowser.open(cacheM.config['TIEBA'])
    webbrowser.open(cacheM.config['GITHUB'])
    #webbrowser.open(cacheM.config['QQ'])
    #webbrowser.open(cacheM.config['PROVIDER'])

class GitHubFrame(tk.Frame):
    def __init__(self,*args,**kw):
        tk.Frame.__init__(self,*args,**kw)
        ttk.Button(self,text='项目地址 / 交流群',command=openWeb).pack()
        CreateToolTip(self,f'点击加入群聊查看最新动态')

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
        copyString = base64.b64encode(copyStringBytes).decode()
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
    


