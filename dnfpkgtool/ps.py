import  os,psutil,json,shlex,subprocess,traceback
from tkinter import messagebox
from tkinter.filedialog import asksaveasfilename
from pathlib import Path
import threading
import time
ICON_PATH = r'.\config\DNF.ico'
B2E_PATH = r'config\b2e.exe'
workingFlg = False
# 兜底查进程：Get-CimInstance 能读到管理员进程的 ProcessId/Name/ExecutablePath/CommandLine
WMI_PS = ('[Console]::OutputEncoding=[Text.Encoding]::UTF8;'
          'Get-CimInstance Win32_Process -Filter "Name like \'%dnf%\'" |'
          ' Select-Object ProcessId,Name,ExecutablePath,CommandLine | ConvertTo-Json -Compress')


def getDNF():
    '''找正在运行的 DNF 进程，返回候选列表（统一成 dict：{'pid','name','exe','args'}）。
    psutil 读不到时（如游戏以管理员身份运行，name() 静默给 None）才用 WMI 兜底，
    即只有 psutil 一个都没找到才会去跑一次 powershell。'''
    procs = []
    for proc in psutil.process_iter():
        try:
            name = proc.name() or ''
            if 'dnf' in name.lower():
                procs.append({'pid':proc.pid,'name':name,'exe':proc.exe(),'args':proc.cmdline()[1:]})
        except:
            pass
    if procs:
        return procs
    return _wmiDNF()

def _wmiDNF():
    '''psutil 的兜底。CommandLine 为 None（读不到）时退化成只 start "" "<exe>"（args=[]）。'''
    try:
        out = subprocess.run(['powershell','-NoProfile','-NonInteractive','-Command',WMI_PS],
                             capture_output=True,timeout=20).stdout
        data = json.loads(out.decode('utf-8',errors='replace') or '[]')
    except Exception:
        traceback.print_exc()
        return []
    if isinstance(data,dict):    # 只有一个进程时 ConvertTo-Json 给对象而不是数组
        data = [data]
    procs = []
    for d in data:
        if not d or not d.get('Name'):
            continue
        try:
            args = shlex.split(d.get('CommandLine') or '',posix=False)[1:]
        except ValueError:
            args = []
        procs.append({'pid':d.get('ProcessId'),'name':d['Name'],
                      'exe':str(d.get('ExecutablePath') or '').strip('"'),'args':args})
    return procs

def _build_launcher_cmds(exePath,args,outPath,outPath_bat,b2ePath=None,iconPath=ICON_PATH):
    '''纯函数：算出一键启动器要写的 bat 内容与 b2e 命令（不碰磁盘、不弹框，便于测试）。
    bat 统一成 start "" "<exe>" <args>：b2e 是 Bat To Exe Converter，转换时就把 bat 嵌进 exe，
    所以转换前写的那份才是真正会跑的；原写法 start <exe>（无引号）在游戏目录带空格时会废。'''
    bat = 'start "" "%s"%s' % (exePath,''.join(' '+a for a in args))
    b2e = f'"{b2ePath or os.path.join(os.getcwd(),B2E_PATH)}" /bat "{outPath_bat}" /exe "{outPath}" /icon "{iconPath}" /invisible'
    return bat,b2e

NOT_FOUND = '未找到 DNF 游戏进程：请先启动游戏；若游戏以管理员身份运行，请同样以管理员身份运行本工具。'

def _fail(runOnUi,log,text):
    '''失败必须看得见：日志 + 弹窗。原来只 print，界面上毫无反馈，用户只会觉得"点了没反应"。'''
    print(text)
    try:
        log(text)
    except Exception:
        traceback.print_exc()
    try:
        runOnUi(messagebox.showwarning,'生成一键启动器',text)
    except Exception:
        traceback.print_exc()

def saveStart(runFunc=lambda:...):
    global workingFlg
    if workingFlg:      # 防重入：必须在起线程前置位，否则连点两次会跑两遍
        return False
    workingFlg = True
    def inner():
        global workingFlg
        from dnfpkgtool.appCommon import runOnUi,log   # inner 跑在后台线程：文件框/弹窗必须回主线程（py3.14）
        try:
            print('搜寻DNF进程中...')
            procs = getDNF()
            dnf = next((p for p in procs if p['exe']),None)
            if dnf is None:
                _fail(runOnUi,log,NOT_FOUND if not procs else
                      '找到 DNF 进程（pid=%s, %s）但读不到它的 exe 路径：请以管理员身份运行本工具。'
                      % (procs[0]['pid'],procs[0]['name']))
                runFunc()
                return False
            print(procs)
            dnfPath = Path(dnf['exe'])
            b2ePath = os.path.join(os.getcwd(),B2E_PATH)
            outPath = Path(runOnUi(asksaveasfilename,title=f'请保存至DNF.exe同级游戏目录',filetypes=[('可执行文件',f'*.exe')],initialfile=f'DNF一键登录.exe',initialdir=dnfPath.parent))
            if len(str(outPath))<2:
                return False
            if str(outPath)[-4:]!='.exe':
                outPath = Path(str(outPath)+'.exe')
            outPath_bat = Path(str(outPath)[:-3] + 'bat')
            startCMD,cmd = _build_launcher_cmds(str(dnfPath),dnf['args'],outPath,outPath_bat,b2ePath)
            with open(outPath_bat,'w') as f:
                f.write(startCMD)
            print(outPath_bat)
            print(cmd)
            pi = subprocess.Popen(cmd,shell=False,cwd=os.getcwd(),stdout=subprocess.PIPE)
            blankLineNum = 0
            for i in iter(pi.stdout.readline,'b'):
                ret = i.decode('gbk',errors='ignore').strip()
                if ret=='':
                    blankLineNum+=1
                    if blankLineNum>4:
                        pi.kill()
                        break
                else:
                    print(ret) #编码问题
            with open(outPath_bat,'w') as f:    # 与上面同一份（bat 内容在转换时已被 b2e 嵌进 exe）
                f.write(startCMD)
            if outPath.exists():
                openDirCMD = f'explorer.exe /select,{str(outPath)}'
                subprocess.Popen(openDirCMD,shell=False)
                print('保存结束')
            else:
                print('保存失败')
            runFunc()
            return True
        except BaseException:
            _fail(runOnUi,log,'生成一键启动器失败：'+chr(10)+traceback.format_exc())
            return False
        finally:
            workingFlg = False
    t = threading.Thread(target=inner)
    t.daemon = True
    t.start()

if __name__=='__main__':
    saveStart()
