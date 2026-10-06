# DNF 私服工具箱（背包 / PVF / GM）

面向 DNF 台服 / 私服服务端维护的桌面工具箱：Python 3.14 + tkinter / ttkbootstrap，直接读写服务端 MySQL 与 `Script.pvf`。

> 只用于自建私服的日常维护。本工具会**真实写入线上数据库与 PVF 文件**，操作前务必备份。

## 来源

- 上游原版（原作者）：[Zageku/DNF_pvf_python](https://github.com/Zageku/DNF_pvf_python)
- 本仓库（fork）：[a87150/DNF_pvf_python](https://github.com/a87150/DNF_pvf_python)

本仓库是上游的 fork，在原版全部功能之上做了一轮结构精简、Python 3.14 / PyInstaller 兼容修复与界面调整。
改动集中在自己新增的文件与打补丁的函数上，数据库里的 blob 结构、邮件写库的 `bytes + latin1` 约定、以及 `PyMySQL` 的版本锁定都保持原样。尊重原作者版权，问题与建议请优先参考上游文档。

## 功能列表

| 页签 / 模块 | 能力 |
|---|---|
| 查询 | 账号查询（UID / 账号名）与角色查询（角色名，留空即加载**在线角色**）；结果树就是“角色表”，列出角色ID / 角色名 / 等级 / 职业 / UID，选中即加载该角色全部数据 |
| 背包 | 解析 `charac_inven_expand` 等 blob 字段，可视化增删改物品：数量、耐久、强化 / 锻造 / 增幅、魔法封印、封装状态；支持复制/粘贴代码、导出导入 blob（61 字节 `DnfItemSlot`） |
| 邮件 | 文本邮件与带道具邮件，支持发送到当前角色 / 全服 / 在线角色 / VIP；可清空全服邮件 |
| 宠物 | 宠物栏与宠物装备的查看、清理与编辑 |
| 时装 | 时装栏（`user_items`）查看与清理 |
| 任务 | 当前任务列表、放弃任务、标记任务完成状态 |
| GM | 充值（点券 / 代币 / SP / TP / QP）、清洗数据、封禁、活动列表、泡点（自动发放点券） |
| 封停 | 按账号或角色封禁 / 解封，封停列表（`punish_type` 禁止登陆 / 限制交易） |
| 角色表 | 左栏「角色操作」：状态 / 角色ID / 角色名 / 等级 / 职业 / UID，加 删除 / 恢复 / 拷贝 / 备份选中角色（`.cbak`）/ 读取恢复数据；右栏「角色转移」：查目标账号后把选中角色转移到右侧账号 |
| 其它 | 角色基础属性修改（改名 / 转职 / 升级 / 觉醒）、账号金库等 |
| 数据库 | 连接配置与连接器选择、在线人数、数据库备份 / 还原 / 重置、**用户管理**（`mysql.user` 用户列表与增删改） |
| 关于 / 设置 | 版本信息、主题切换、分辨率保存、项目链接 |

### PVF 编辑器

与背包编辑器**共用同一份已加载的 PVF**（不重复导入，也不弹文件选择框）。左侧合并为“一个搜索栏 + 一个结果列表 + 四个按钮”：

1. **提交编辑** —— 把选中物品提交到背包页签的物品编辑框
2. **提交邮件** —— 把选中物品提交到邮件附件
3. **修改物品数据** —— 把该物品的完整数据载入右侧“道具数据修改”面板（支持 JSON 编辑）
4. **以该物品为模板** —— 以该物品为模板新建一份数据

搜索与“修改物品”的入口已合并到同一面板，不必再手输物品名。

> **「角色表」页是按原版编译版复刻的**：上游 [本仓库](https://github.com/a87150/DNF_pvf_python) 的源码里没有这一页（原版的界面只存在于编译分发的 `dnf_pkgtool_win64_V.23.09.15` 里），本仓库照原版的页签顺序（封停 → **角色表** → 其它）、列头与数据库语义把它补了回来，见 [characTableFrame.py](dnfpkgtool/characTableFrame.py)。
> 原版还有一页「留言」（`msgFrame`：留言列表 / 留言IP / 发布留言），本仓库**尚未复刻**，页签里没有它。
> 状态三档照原版：`charac_info.delete_flag=1` → `已删除`；否则该角色不在它账号的 `charac_view` 缓存里 → `隐藏`；其余留空。

## 环境与依赖

- **操作系统**：Windows（DPI 缩放走 `ctypes.windll.shcore`，界面为 tkinter）
- **Python**：3.14（已在 CPython 3.14.7 验证）
- **数据库**：可访问的服务端 MySQL（默认连 `192.168.200.131:3306`，账号见配置）
- **依赖**：见 [requirements.txt](requirements.txt)

| 依赖 | 用途 / 注意 |
|---|---|
| **PyMySQL==1.0.2** | **必须锁 1.0.2**，原因见下 |
| ttkbootstrap | 界面主题 |
| Pillow / pyqrcode / pypng | 二维码与图片 |
| pyperclip | 剪贴板（物品代码复制粘贴） |
| jsoneditor | PVF 高级编辑用的浏览器版 JSON 编辑器 |
| zhconv | 简繁转换（活动名、物品名） |
| paramiko | SSH 连接服务器（启停服务端、上传文件） |
| psutil | 进程信息 |
| pycryptodome / cryptography | 登录网关与加密 |

### 为什么 PyMySQL 必须锁 1.0.2

邮件正文与发件人名是以 **`bytes`（UTF-8 编码）+ `latin1` 连接字符集** 写进 `taiwan_cain_2nd.letter` / `postal` 的：靠连接字符集让服务端按原始字节存下来，游戏里才不会乱码（详见 [sqlManager2.py](dnfpkgtool/sqlManager2.py) 的 `send_message` / `send_postal`）。

PyMySQL **1.1 及以上**会把 `bytes` 型参数转义成 `_binary X'...'`，1.0.2 则转义成 `'...'`（按连接字符集解释），两者落到数据库里的字节不同 —— 用高版本会导致**游戏内邮件汉字乱码**，而且与界面上的“角色显示及编码”选项无关。因此 [requirements.txt](requirements.txt) 固定为：

```text
PyMySQL==1.0.2
```

这一条与数据库取回数据的解码（`utf-8` / `cp1252` / `latin1` 回退，见 `decode_charac_list`、`getCharactorNo`）是两件独立的事，改动时不要混在一起。

## 配置说明

运行配置是 **`config/config.json`**，它**不入库**（已在 `.gitignore` 忽略）。新环境请复制一份模板再改：

```powershell
Copy-Item config\config.example.json config\config.json
```

| 配置项 | 含义 |
|---|---|
| `DB_IP` / `DB_PORT` / `DB_USER` / `DB_PWD` | 服务端 MySQL 地址与账号（连不上时先查这里） |
| `DB_CONFIGS` | 按 IP 记住的多套数据库连接（界面下拉切换） |
| `SERVER_IP` / `SERVER_PORT` / `SERVER_USER` / `SERVER_PWD` | SSH（启停服务端、上传文件） |
| `PVF_PATH` | 上次加载的 `Script.pvf` 路径；为空时启动不自动加载 |
| `RESOLUTION` / `THEME` / `FONT` | 界面尺寸、主题、字号 |
| `SENDERS` / `MESSAGES` / `DIY_2` | 邮件发件人 / 正文 / 常用命令的历史记录 |

**`config/config.json` 缺失时的行为**：程序不会崩溃，`cacheM.load_config()` 直接使用内置默认值（`DB_IP=192.168.200.131`、`DB_PORT=3306`、`DB_USER=game`、`DB_PWD=123456`），并在启动时把这份默认配置**写回** `config/config.json`。此时“连接数据库”会失败并给出日志；请把 IP / 账号改成自己的。

**其它 config 文件不要删**：`eventList.json`（活动名，程序会自动与数据库对比后重写为简体）、`jobDict.json`、`equTypeDict.json`、`stkTypeDict.json`、`magicSealDict.json`、`avatarHidden.json`、`expTable.json`、`pvfKeywords*.json`、全物品 CSV、`pvf.tinycache` 与 `pvfCache/`（PVF 解析缓存）。

## 运行方式

### 源码运行

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe main.py
```

[main.py](main.py) 是入口，负责三件事：把工作目录切到脚本/exe 所在目录、首次运行时（打包后）把内置 `config/` 复制到 exe 同级、调用 `multiprocessing.freeze_support()`。它还带一个 PVF 加载自检开关（结果写进 `log/`）：

```powershell
.venv\Scripts\python.exe main.py --loadpvf D:\Script.pvf
```

### 直接运行 exe

双击 `dist\DNF背包编辑工具.exe`。首次运行会在 exe 同级生成 `config/`（内含 `config.json`，用的是默认库地址，记得改）与 `log/`。

## 打包

```powershell
.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --onefile --windowed `
  --runtime-tmpdir . `
  --name DNF背包编辑工具 `
  --add-data "config;config" `
  --collect-all ttkbootstrap --collect-all jsoneditor --collect-all zhconv `
  --exclude-module matplotlib --exclude-module numpy `
  main.py
```

产物为 `dist\DNF背包编辑工具.exe`，**约 31.4 MiB / 32.9 MB**（`--onefile`，本轮实测 32,876,474 字节）。调试时改成 `--console --onedir`，可直接看 stdout/stderr：

```powershell
.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --console --onedir --runtime-tmpdir . `
  --name DNF_dbg --specpath build_dbg\spec --workpath build_dbg\work --distpath build_dbg\dist `
  --add-data "<仓库绝对路径>\config;config" `
  --collect-all ttkbootstrap --collect-all jsoneditor --collect-all zhconv `
  --exclude-module matplotlib --exclude-module numpy main.py
```

### 打包参数逐条说明

| 参数 / 代码 | 为什么必需 |
|---|---|
| `--onefile --windowed` | 单个 exe，且不弹出控制台窗口 |
| `--runtime-tmpdir .` | 单文件引导器默认解压到 `%TEMP%`；不可写时会退回 `C:\Windows\Temp`，非管理员账号写不进去，启动即报 `Could not create temporary directory!`。指定在 exe 同级解压即可绕开 |
| `main.py` 的 `multiprocessing.freeze_support()` | PVF 解析使用多进程；冻结后不调用它，子进程起不来，表现为**加载 PVF 一直无响应** |
| `--collect-all zhconv` | `zhcdict.json` 是运行时按路径读的数据文件，静态分析收不到；缺失时抛 `FileNotFoundError: ...zhconv\zhcdict.json` |
| `--collect-all ttkbootstrap` / `--collect-all jsoneditor` | 主题资源与 JSON 编辑器前端资源 |
| `--add-data "config;config"` | 运行时需要 `config/` 下的配置、道具表、`b2e.exe` 等资源 |
| `--exclude-module matplotlib numpy` | 项目未用到，排除以缩小体积、加快启动（本仓库**不引入**这两个库） |

### 体积对比

| 形态 | 体积 |
|---|---|
| `--onefile --windowed`（正式发布） | 约 31.4 MiB（32.9 MB，32,876,474 字节） |
| `--onedir --console`（调试） | exe 本体约 8.7 MB + `_internal/` 目录 |
| 修剪前的老版本（未排除 matplotlib/numpy、未删死代码） | 明显更大 |

> 打包前先关掉正在运行的 exe：文件被占用时 PyInstaller 写不进去，会构建失败或留下旧产物。核对时间戳与体积确认真的是新包。

### 打包后“双击没反应”怎么排查

用 `--console --onefile` 打一个同样的包，在**干净的空目录**里运行，把 stdout+stderr 重定向到文件：Python 的 traceback 会直接告诉你挂在哪个 import 上（本轮就是这样抓到 `getpass.getuser` 那条：`OSError: No username set in the environment`）。窗口态 exe 看不到输出，但同样会在 exe 同级目录写 `log/`；**连 `log/` 都没有，说明崩在 `appCommon` 导入之前**。

## 关键技术点

### 1. 源文件是 CRLF

仓库里的 `.py` / `.md` 都是 **CRLF** 换行。用脚本批量改文件时：`read_bytes()` → `decode()` → `replace('\r\n', '\n')` 做匹配替换 → 写回时 `replace('\n', '\r\n')` → `write_bytes()`。直接按 LF 文本去 `count()` / `replace()` 会匹配失败或把整个文件改成 LF。

### 2. 编码：数据库与配置文件

- **写邮件**：`bytes`（UTF-8）+ `latin1` 连接字符集，见上文“为什么 PyMySQL 必须锁 1.0.2”。
- **读角色名**：数据库里可能是 `latin1` / `cp1252` 形态的字节，也可能已经是正常 Unicode，`decode_charac_list` 会依次尝试解码并回退，**不能**用 `encode('latin1','replace')` 把正常 Unicode 变成 `?`（会把问号真写进库）。
- **读 config 下的 JSON**：统一走 [pvfJson.py](dnfpkgtool/pvfJson.py) 的 `loadJsonFile()`，按 `utf-8-sig` → `utf-8` → `gbk` 依次尝试。老配置文件是中文 Windows 上用 locale（GBK）写出来的，新写的必须是 UTF-8，写死任何一种都会有人读不出来。**这是本次“数据库页用户列表空”的直接原因**：`config/eventList.json` 是 UTF-8，裸 `open(path,'r')` 落到 GBK 解码，在连接流程里抛 `UnicodeDecodeError` 把后台线程打死。

### 3. py3.14 线程模型：控件操作必须回主线程

Python 3.14 下**非主线程操作任何 Tk 控件 / Tk 变量都会抛** `RuntimeError: main thread is not in main loop`（旧 py3.6 能容忍，所以升级后才集中暴露）。因此：

- 后台线程只跑 DB / 网络 / 耗时活；任何控件读写都通过 [appCommon.py](dnfpkgtool/appCommon.py) 的 `runOnUi(func, *args)` 交回主线程执行并取回结果。
- `startUiPump(root)` 在主线程每 30 ms 清一次队列，必须在**起任何后台线程之前**调用。
- **泵绝不允许停**：泵回调里的异常只记录（写日志文件，`--windowed` 下 `sys.stderr` 是 `None`，`traceback.print_exc()` 自己会抛），`root.after(30, pump)` 放在 `finally` 里保证 re-arm。泵一旦漏掉 re-arm，所有后台线程的 `runOnUi` 会永久 `wait()` —— 表现就是“点了连接数据库，日志里连一句正在连接都没有”。
- **`runOnUi` 绝不允许永久挂起**：`done.wait(UI_CALL_TIMEOUT)`（60 s）超时后记录明确错误并抛 `RuntimeError`，让调用方能看到。

### 4. 主窗口构造与布局

`GuiApp` 由 [__main__.py](dnfpkgtool/__main__.py) 组合多个 mixin（`guiInit` / `guiTabMain` / `guiTabCharac` / `guiTabGM` / `guiTabSsh` / `guiActions`），各页签的构建与回调都在各自 mixin 里。窗口尺寸读取 `RESOLUTION` 后抬到不低于 1200×800，且不超过屏幕可用区域。

## 测试

全部为**离线自检脚本**（不连真实数据库的也用假数据），逐个跑：

```powershell
.venv\Scripts\python.exe -W error::SyntaxWarning -m compileall -q dnfpkgtool tests
.venv\Scripts\python.exe tests\ui_thread_check.py
.venv\Scripts\python.exe tests\search_merge_check.py
.venv\Scripts\python.exe tests\editor_editbutton_check.py
.venv\Scripts\python.exe tests\uitree_check.py
.venv\Scripts\python.exe tests\editor_search_check.py
.venv\Scripts\python.exe tests\selfcheck.py
.venv\Scripts\python.exe tests\name_codec_check.py
.venv\Scripts\python.exe tests\charac_table_check.py
.venv\Scripts\python.exe tests\conn_flow_check.py
```

| 脚本 | 查什么 |
|---|---|
| `ui_thread_check.py` | 跨线程回主线程：后台取用户列表能填充 6 行；**泵被回调异常撞过之后仍能 re-arm**；泵错误出口写日志文件；**主线程不响应时 `runOnUi` 超时抛错而不是永久挂起** |
| `search_merge_check.py` | PVF 编辑器左侧是“一个搜索栏 + 一个结果列表 + 四个按钮”，按钮顺序与回调（提交编辑 / 提交邮件 / 修改物品数据 / 以该物品为模板）正确 |
| `editor_editbutton_check.py` | “修改物品数据”“以该物品为模板”按钮在道具 / 装备两个 tab 上都能正确载入左右两侧内容 |
| `uitree_check.py` | 界面结构无断口：广告位 / 图片 / 旧 GM 工具入口已删除，全局日志区存在且能收到消息，页签齐全 |
| `editor_search_check.py` | 搜索整条链：筛选 → 结果树 → 选中 → 提交回调；装备 / 时装分支；共用背包编辑器的 PVF（不弹文件框、编码跟随） |
| `selfcheck.py` | 纯数据逻辑：物品 blob 打包 / 解包、等级与稀有度、`rarityMap` 单一来源、`search_Items` 的关键字 / 等级 / 稀有度 / 唯一 / 时装 / 基础属性分支 |
| `name_codec_check.py` | 角色名相关 SQL 的编码：`getCharactorNo` 不再把“混合”当编码名抛 `LookupError`，改用参数化查询 |
| `charac_table_check.py` | 角色表页：列头 / 八颗按钮的顺序与回调、左栏数据源与“查询”页共用 `sqlM.getCharacterInfo`、状态三档（已删除 / 隐藏 / 空）、删除 / 恢复 / 转移 / 拷贝 / 备份 / 恢复数据的 SQL 与线程纪律（真库那一段只 `SELECT` 与 `.cbak` 往返比对） |
| `conn_flow_check.py` | **需要真实数据库**（连不上会打印 SKIP 直接退出 0，不算失败）：按 `__main__.run()` 的真实启动路径建窗口，断言 12 个页签且含「角色表」（顺序 封停 → 角色表 → 其它）、`print2title` 已装进 `appCommon`、数据库用户树 6 行、连接器已填充、后台线程零异常、`CONNECTING_FLG` 复位，且日志里真的写下“正在连接数据库 / 数据库连接成功”。在线角色只有用户此刻人在游戏里才有：日志是 `当前在线角色已加载(0)` 时打印 `SKIP  在线角色（当前无人在线）`，不算失败 |

`charac_table_check.py` 与 `conn_flow_check.py` 需要真实数据库（都只连 `config/config.json` 里的库做只读查询），连不上时打印 `SKIP` 并以 0 退出。

## 常见问题

**Q1：游戏里收到的邮件汉字乱码？**
A：PyMySQL 版本问题。`pip install "PyMySQL==1.0.2"` 后重新打包；与界面上的编码选项无关。

**Q2：点“连接数据库”后没有反应，日志里连“正在连接数据库…”都没有？**
A：UI 泵停了（历史上是泵回调里 `traceback.print_exc()` 在 `--windowed` 下自己抛，导致 `root.after` 不再 re-arm）。当前版本已修：泵异常只记录不逃逸、re-arm 放在 `finally`、`runOnUi` 60 s 超时抛错。日志文件里会留下 `[UI泵] ...` 记录。

**Q3：数据库页“用户管理”列表空 / 角色表空？**
A：连接流程中途抛异常导致后台线程提前结束。历史原因是 `config/eventList.json`（UTF-8）被以 GBK 解码——现已统一走 `loadJsonFile()`。若仍为空，先看 `log/` 里最新日志的报错行。

**Q4：加载 PVF 报 `FileNotFoundError: ...zhconv\zhcdict.json`？**
A：打包漏了 `zhconv` 数据文件，打包命令加 `--collect-all zhconv`。

**Q5：非管理员运行 exe 报 `Could not create temporary directory!`？**
A：打包时加 `--runtime-tmpdir .`，并把 exe 放在当前用户可写的目录。

**Q6：打包后双击 exe，加载 PVF 一直无响应？**
A：缺少 `multiprocessing.freeze_support()`（[main.py](main.py) 已内置，且必须在主逻辑之前调用）。

**Q7：修改“角色显示及编码”后邮件文字仍乱码？**
A：该选项只影响读取角色名时的解码显示；邮件正文写入固定 `utf-8` + `latin1`，不经过该选项。

**Q8：打包后双击 exe 没有任何反应，连 `log/` 都不生成？**
A：崩在 `appCommon` 导入之前。先按「打包后"双击没反应"怎么排查」用 `--console` 版拿到 traceback。已知的一种是 PyMySQL 1.0.2 在导入时调 `getpass.getuser()`，而打包后的进程环境里没有 `LOGNAME`/`USER`/`USERNAME`、Windows 又没有 `pwd` 模块，直接抛 `OSError: No username set in the environment`；[main.py](main.py) 已补 `pwd` 兜底，确认你用的是新包。

**Q9：打包报错或产物没更新？**
A：先关掉正在运行的 exe，再核对 exe 时间戳与体积。

## 目录结构

```text
dnf/
├─ main.py                     入口：切工作目录、首次复制 config、freeze_support、--loadpvf 自检
├─ requirements.txt            依赖清单（PyMySQL 固定 1.0.2）
├─ dnfpkgtool/                 主程序包
│  ├─ __main__.py              入口与 GuiApp 组合（各页签方法体拆到下面的 mixin）
│  ├─ appCommon.py             runOnUi / UI 泵 / 日志 / 公共控件与循环导入边界
│  ├─ pvfJson.py               config/*.json 的兼容读取（UTF-8 / GBK）
│  ├─ guiInit.py               主窗口初始化与整体布局
│  ├─ characTableFrame.py      角色表页（复刻原版：状态三档 / 删除 / 恢复 / 拷贝 / 备份 / 转移）
│  ├─ guiTabMain.py            查询 / 背包页与应用逻辑
│  ├─ guiTabCharac.py          角色信息（其它页）
│  ├─ guiTabGM.py              GM / 泡点 / 活动页
│  ├─ guiTabSsh.py             SSH / 封停 / 数据库连接页
│  ├─ guiActions.py            PVF 编辑器、搜索提交、数据库备份还原
│  ├─ sqlManager2.py           MySQL 读写层：物品 blob、编码转换、邮件写入
│  ├─ cacheManager.py          PVF 缓存与配置读写
│  ├─ pvfReader.py             PVF 解析（多进程）
│  ├─ pvfEditor.py / pvfEditorGUI.py   PVF 数据模型与编辑器界面
│  ├─ itemSlotFrame.py / characFrame.py / mailFrame.py / avatarFrame.py / creatureFeame.py
│  └─ widgets/                 标题栏、气泡提示等小控件
├─ pkgLogin/                   自建登录网关（客户端 / 服务端）
├─ config/                     配置、道具 CSV、PVF 缓存、图标
│  ├─ config.example.json      配置模板（复制成 config.json 使用）
│  └─ pvfCache/                PVF 解析缓存
├─ tests/                      自检脚本（含需要真实库的 conn_flow_check.py）
├─ log/                        运行日志
└─ dist/                       打包产物（exe + config/ + log/）
```

## 注意事项

- **不要引用 `images/ico.png`**：图片资源已在清理中删除。程序图标用 `config/DNF.ico` 或 `config/ico.ico`。
- **源文件是 CRLF 换行**，批量修改请按上面的方式做换行归一化。
- **打包后运行的 exe 不要指望 `%TEMP%`**：单文件包用 `--runtime-tmpdir .` 解压到 exe 同级，注意该目录要当前用户可写。
- **`config/config.json` 会被程序覆盖保存**（修改数据库或界面设置时写回），调试前先备份；它不入库。
- **直接操作线上数据**：请先备份 `taiwan_cain`、`taiwan_cain_2nd`、`taiwan_billing`、`d_taiwan` 等相关库以及 `Script.pvf`。
- **打包产物是便携的**：配置保存在 exe 同级目录，删除整个文件夹即可完全卸载。

## 更新记录

### 本轮（当前）

- **修复打包后 exe “双击没反应、连 log/ 都不生成”**：PyMySQL 1.0.2 在导入时（`pymysql/connections.py`）会算 `getpass.getuser()`，它先查 `LOGNAME` / `USER` / `LNAME` / `USERNAME` 再看 `pwd` 模块；打包后的进程环境里这些变量可能都没有，Windows 又没有 `pwd`，于是抛 `OSError: No username set in the environment`，**主程序在建窗口前就退出**。[main.py](main.py) 现在补一个 `pwd` 模块并兜底 `os.getuid`，让取用户名不再依赖环境变量（py3.13 起 `getpass.getuser` 只接住 `ImportError`/`KeyError`，所以 `os.getuid` 必须一起补）。
- **修复“日志只有一行欢迎语、标题不更新”**：[__main__.py](dnfpkgtool/__main__.py) 的 `run()` 用 `global print2title` 只改了本模块的全局名，而 `print()` 在 [appCommon.py](dnfpkgtool/appCommon.py) 里、取的是 **appCommon 自己的全局名**，所以 `print2title` 一直是模块顶部那个 no-op lambda：日志只剩显式 `log()` 调用，标题也永远不刷新。改为 `_appCommon.print2title = print2title`。这是用户看到的 47 字节日志的直接原因。
- **修复“数据库用户列表空 / 角色表空 / 连不上”**：连接流程里 `config/eventList.json` 被以 GBK 解码抛 `UnicodeDecodeError`，后台线程提前结束，导致用户列表、封停树、事件日志、备份列表全都不再刷新。统一改为 `pvfJson.loadJsonFile()` 兼容读取（`utf-8-sig` / `utf-8` / `gbk`）。
- **加固 UI 泵（`appCommon.py`）**：泵回调异常只记录不逃逸（写日志文件而非 stderr）、`root.after(30, pump)` 放进 `finally` 保证 re-arm、`runOnUi` 增加 60 s 超时并在超时后抛 `RuntimeError`。“点连接没反应、日志里连一句正在连接都没有”这类永久挂起不会再发生。
- **新增「角色表」页**（[characTableFrame.py](dnfpkgtool/characTableFrame.py)，复刻原版）：左栏 状态 / 角色ID / 角色名 / 等级 / 职业 / UID + 删除 / 恢复 / 拷贝 / 备份选中角色 / 读取恢复数据，右栏「角色转移」把选中角色转到右侧账号。状态三档照原版：`charac_info.delete_flag=1` → 已删除；不在账号缓存 `charac_view` 里 → 隐藏；其余留空。后者的取法用原版的 `get_charac_view`：`info` = u32(解压后长度) + zlib，解压出来是 36 个 148 字节槽位、槽首 u32 就是角色号。
- **补两处 py3.14 跨线程漏网点**：`selectCharac` 里的 `fill_charac_tab_fun()`（会写 `isVIP` / `isReturnUser` 等 Tk 变量）与 `update_GM()`（GM 页点券 / SP / TP 变量）改为 `runOnUi`；解封流程的封停树刷新同改。
- **编码细节**：`config/config.json` 读取固定按 UTF-8 解码（原来 `bytes.decode()` 跟随 locale，中文 Windows 上是 GBK；失败会被 `except` 吞掉，表现为配置悄悄退回模板）；角色名长度按 UTF-8 计算（原来按 locale，中文名会算错长度并切错字节）；base64 编解码固定 UTF-8。
- **测试**：新增 `tests/conn_flow_check.py`（需要真实库，端到端验证 12 个页签含「角色表」、数据库用户 6 行、不卡死，无人在线时打印 `SKIP  在线角色（当前无人在线）`）与 `tests/charac_table_check.py`（角色表页的列头 / 按钮 / 线程纪律 / 状态三档，真库只读）；`tests/ui_thread_check.py` 增加三条“泵绝不挂起”的断言。
- **重新打包并冒烟验证**：`--onefile --windowed --runtime-tmpdir .` 重出 `dist\DNF背包编辑工具.exe`（32,876,474 字节 / 31.4 MiB），启动后 exe 同级 `log/` 里确实写下「正在连接数据库...」「当前在线角色已加载(0)」「数据库连接成功」——这条用户可见的修复在**打包路径**上也成立。
- **README** 重写（来源、功能、依赖与 PyMySQL 锁版原因、配置缺失行为、打包与体积、关键技术点、测试矩阵）。

### 更早

- **结构精简**：删除无引用代码约 4700 行（多余的界面变体、重复的搜索窗口、旧驱动副本、无人调用的辅助模块与图片资源）；`__main__.py` 从近 5000 行拆成入口 + 6 个 mixin。
- **汉字编码三连修**：锁定 PyMySQL 1.0.2；`decode` 无损化（不再把正常 Unicode 变成 `?`）；`getCharactorNo` 参数化（不再把“混合”当编码名）。
- **界面调整**：主窗口默认放大到不低于 1200×800；全局事件日志移到主界面底部；PVF 编辑器瘦身并共用背包编辑器的 PVF；搜索与修改物品入口合并。
- **交互**：启动提示改为 PVF 文件在服务器上的位置（`/home/neople/game/Script.pvf`）；删除失效的旧 GM 工具入口。
