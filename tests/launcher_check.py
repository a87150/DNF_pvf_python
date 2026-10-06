r'''「生成一键启动器」自检：进程检测、启动命令拼装、失败分支必须可见。

为什么要有这个套件：按钮点了没反应的根因是 getDNF() 用 psutil 读不到游戏进程（psutil 对读不到
的进程静默给 name()=None，条件永不匹配），saveStart 只 print 一句就 return False，界面零反馈。
这里钉住：a) 真实环境能拿到正在运行的 DNF 进程（本进程被降权/游戏没开就 SKIP，不假 FAIL）；
b) exe 路径+参数能拼出 start "" "<exe>" <args>；c) 零进程/读不到路径时走弹窗+日志的可见失败
分支并返回 False，且不碰文件框、不执行 b2e、不往磁盘写启动器；d) psutil 优先、'dnf' 子串匹配、
CommandLine 缺失时退化。

跑法：.venv\Scripts\python.exe tests\launcher_check.py
'''
import sys, os, io, json, subprocess, locale
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from dnfpkgtool import ps as PS
import dnfpkgtool.appCommon as AC
import tkinter.messagebox as MB

_realGetDNF = PS.getDNF   # c/d 段会把 PS.getDNF / psutil.process_iter / subprocess.run 换成假的，这里留真货给 e 段用
_realProcessIter = PS.psutil.process_iter
_realSubprocessRun = PS.subprocess.run

failed = []
def check(name, cond, extra=''):
    print(('PASS  ' if cond else 'FAIL  ') + name + (('  ' + str(extra)) if extra else ''))
    if not cond:
        failed.append(name)

# ---------- a) 真实环境：能不能找到正在运行的 DNF ----------
procs = _realGetDNF()
real = next((p for p in procs if p['exe']), None)
if procs:
    check('a1 真实环境找到 DNF 进程', real is not None,
          [(p['pid'], p['name'], p['exe']) for p in procs])
    if real:
        print('      真实 pid=%s name=%s exe=%s args=%r%s' % (real['pid'], real['name'], real['exe'],
              [a[:40] for a in real['args']], ' …(%d 字节)' % len(real['args'][0]) if real['args'] else ''))
else:
    _grp = subprocess.run(['whoami','/groups'],capture_output=True).stdout.decode('gbk','replace')
    print('SKIP  a 未发现正在运行的 DNF 进程（psutil+WMI 都空）；本进程状态=%s；psutil 可见进程数=%d'
          % ('Low 完整性/受限令牌（读不到高完整性进程）' if 'S-1-16-4096' in _grp else '正常', len(list(PS.psutil.process_iter()))))

# ---------- b) 启动命令拼装（纯函数，不碰磁盘） ----------
FAKE_ARGS = ['X0wOvw+abc/def==','tok2']
bat, b2e = PS._build_launcher_cmds(r'D:\game\DNF1031客户端\DNF.exe', FAKE_ARGS,
                                    r'D:\game\out.exe', r'D:\game\out.bat', r'C:\repo\config\b2e.exe')
check('b1 bat 形如 start "" "<exe>" <args>',
      bat == 'start "" "D:\\game\\DNF1031客户端\\DNF.exe" X0wOvw+abc/def== tok2', bat)
check('b2 b2e 命令带 /bat /exe /icon /invisible',
      b2e == '"C:\\repo\\config\\b2e.exe" /bat "D:\\game\\out.bat" /exe "D:\\game\\out.exe" /icon "' + PS.ICON_PATH + '" /invisible', b2e)
bat0, _ = PS._build_launcher_cmds(r'D:\game\DNF.exe', [], r'a.exe', r'a.bat', r'b2e.exe')
check('b3 读不到 CommandLine（args 为空）时退化成只启动 exe', bat0 == 'start "" "D:\\game\\DNF.exe"', bat0)
if real:
    batReal, _ = PS._build_launcher_cmds(real['exe'], real['args'], r'D:\game\out.exe', r'D:\game\out.bat', 'b2e.exe')
    check('b4 真实进程的 exe/args 也能拼出 start "" "<exe>" <args>',
          batReal == ('start "" "%s"%s' % (real['exe'], ''.join(' '+a for a in real['args']))), batReal[:100])

# ---------- c) 零进程 / 读不到路径 / 异常：可见失败分支 ----------
seen = {}
MB.showwarning = lambda *a, **k: seen.setdefault('warn',[]).append(a)
AC.log = lambda t: seen.setdefault('log',[]).append(t)
def boom(*a, **k):
    raise AssertionError('失败分支不该碰这里：%r' % (a,))
PS.asksaveasfilename = boom      # 不许弹真实文件框
PS.subprocess.Popen = boom       # 不许执行 b2e、不许 explorer
class SyncThread:                # 让后台线程同步跑，好断言 inner 的返回值
    def __init__(self, target=None, daemon=None):
        self.target = target
    def start(self):
        try:
            seen['ret'] = self.target()
        except BaseException as e:
            seen['exc'] = e
PS.threading.Thread = SyncThread

PS.getDNF = lambda: []
PS.saveStart()
check('c1 零进程：inner 返回 False（不是静默 return）', seen.get('ret') is False, seen.get('ret'))
check('c2 零进程：弹了 showwarning 且提示语含「未找到 DNF 游戏进程…管理员」',
      bool(seen.get('warn')) and '未找到 DNF 游戏进程' in str(seen['warn'][0]) and '管理员' in str(seen['warn'][0]),
      seen.get('warn'))
check('c3 零进程：写了日志', any('未找到 DNF 游戏进程' in t for t in seen.get('log',[])), seen.get('log'))
check('c4 零进程：没开文件框、没执行 b2e', 'exc' not in seen, seen.get('exc'))

seen.clear()
PS.getDNF = lambda: [{'pid':26376,'name':'DNF.exe','exe':'','args':[]}]
PS.saveStart()
check('c5 找到进程但读不到 exe 路径：返回 False + 提示管理员',
      seen.get('ret') is False and '读不到' in str(seen.get('warn')) and '管理员' in str(seen.get('warn')), seen.get('warn'))

seen.clear()
PS.getDNF = lambda: (_ for _ in ()).throw(RuntimeError('boom'))
PS.saveStart()
check('c6 getDNF 抛异常：弹窗+日志+返回 False，线程不静默死',
      seen.get('ret') is False and bool(seen.get('warn')) and any('生成一键启动器失败' in t for t in seen.get('log',[])),
      (seen.get('ret'), seen.get('warn')))

seen.clear()
PS.getDNF = lambda: []
PS.workingFlg = True
guard = PS.saveStart()
PS.workingFlg = False
check('c7 workingFlg 已置位时直接返回 False 且不起线程（防重入）', guard is False and 'ret' not in seen, guard)

# ---------- d) 检测逻辑：psutil 优先 / 'dnf' 子串 / WMI 兜底解析 ----------
class FakeProc:
    def __init__(self, pid, name, exe, cmd):
        self.pid, self._n, self._e, self._c = pid, name, exe, cmd
    def name(self): return self._n
    def exe(self):  return self._e
    def cmdline(self): return self._c

calls = []
PS.subprocess.run = lambda *a, **k: calls.append(a) or (_ for _ in ()).throw(AssertionError('psutil 命中时不该跑 WMI'))
PS.psutil.process_iter = lambda: [FakeProc(1,'explorer.exe','C:/x',['x']),
                                  FakeProc(26376,'DNF.exe',r'D:\game\DNF.exe',[r'D:\game\DNF.exe','tok'])]
got = _realGetDNF()
check('d1 psutil 能读到时不跑 powershell', calls == [], calls)
check('d2 候选统一成 dict，args 去掉 argv[0]',
      got == [{'pid':26376,'name':'DNF.exe','exe':r'D:\game\DNF.exe','args':['tok']}], got)

class FakeCP:
    def __init__(self, out): self.stdout = out
PS.psutil.process_iter = lambda: []
_cim = json.dumps({'ProcessId':26376,'Name':'DNF.exe','ExecutablePath':r'D:\game\DNF1031客户端\DNF.exe',
                   'CommandLine':'"D:\\game\\DNF1031客户端\\DNF.exe" X0wOvw+abc/def== tok2'}, ensure_ascii=False)
PS.subprocess.run = lambda *a, **k: FakeCP(_cim.encode('utf-8'))
got = _realGetDNF()
check('d3 psutil 空时走 WMI 兜底，解析出 exe/args（单对象 JSON 也算）',
      got == [{'pid':26376,'name':'DNF.exe','exe':r'D:\game\DNF1031客户端\DNF.exe','args':['X0wOvw+abc/def==','tok2']}], got)

_cim2 = json.dumps({'ProcessId':1,'Name':'DNF.exe','ExecutablePath':r'D:\game\DNF.exe','CommandLine':None}, ensure_ascii=False)
PS.subprocess.run = lambda *a, **k: FakeCP(_cim2.encode('utf-8'))
got = _realGetDNF()
check('d4 CommandLine 为 None 时 args=[]',
      got == [{'pid':1,'name':'DNF.exe','exe':r'D:\game\DNF.exe','args':[]}], got)
PS.subprocess.run = lambda *a, **k: FakeCP(b'')
check('d5 WMI 空输出返回 []', _realGetDNF() == [])
_saveErr, sys.stderr = sys.stderr, io.StringIO()   # d6 会故意抛，traceback 不该刷屏
PS.subprocess.run = lambda *a, **k: (_ for _ in ()).throw(OSError('no powershell'))
ok = _realGetDNF() == []
sys.stderr = _saveErr
check('d6 WMI 调用失败只返回 [] 不往外抛', ok)

# ---------- e) 端到端（只有真找到进程才跑）：真 exe/args 走完整流程，但不执行 b2e、不落用户磁盘 ----------
if real:
    import tempfile, shutil, pathlib
    tmp = tempfile.mkdtemp(prefix='dnf_launcher_check_')
    outPath = pathlib.Path(tmp)/'DNF一键登录.exe'
    outPath_bat = pathlib.Path(tmp)/'DNF一键登录.bat'
    cap = {}
    class FakePopen:                     # 挡住真 b2e：只记录命令，读一眼此刻的 bat
        class _S:
            def readline(self): return b''
        def __init__(self, cmd, **kw):
            cap['cmd'] = cmd
            # bat 用 open(...,'w') 默认编码写（Windows 本地代码页，cmd 也是按它读的），这里照同一种读
            cap['bat'] = outPath_bat.read_bytes().decode(locale.getencoding(),errors='replace')
            self.stdout = self._S()
        def kill(self): pass
    PS.getDNF = _realGetDNF
    PS.psutil.process_iter = _realProcessIter
    PS.subprocess.run = _realSubprocessRun
    PS.subprocess.Popen = FakePopen
    PS.asksaveasfilename = lambda **kw: str(outPath)
    seen.clear()
    PS.saveStart()
    check('e1 端到端：真 DNF 的 exe/args 走通并返回 True', seen.get('ret') is True, (seen.get('ret'), seen.get('exc')))
    check('e2 端到端：交给 b2e 的 bat 就是 start "" "<exe>" <args>',
          cap.get('bat') == ('start "" "%s"%s' % (real['exe'], ''.join(' '+a for a in real['args']))), str(cap.get('bat'))[:80])
    check('e3 端到端：b2e 命令 = <cwd>\\config\\b2e.exe /bat <tmp>.bat /exe <tmp>.exe /icon ... /invisible',
          cap.get('cmd') == ('"%s" /bat "%s" /exe "%s" /icon "%s" /invisible'
                             % (os.path.join(os.getcwd(), 'config', 'b2e.exe'), outPath_bat, outPath, PS.ICON_PATH)),
          str(cap.get('cmd'))[:160])
    check('e4 端到端：真 b2e 没被执行，exe 也不存在（没往用户磁盘写启动器）', not outPath.exists())
    shutil.rmtree(tmp, ignore_errors=True)

print('----')
if failed:
    print('FAILED %d: %s' % (len(failed), failed))
    sys.exit(1)
print('ALL PASSED')
