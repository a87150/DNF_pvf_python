# DNF 私服工具箱（背包 / PVF / GM）

本项目是 [Zageku/DNF_pvf_python](https://github.com/Zageku/DNF_pvf_python) 的 **fork**（本仓库：[a87150/DNF_pvf_python](https://github.com/a87150/DNF_pvf_python)）。原版功能全部保留，并在此之上完成一轮结构精简与兼容性升级：裁剪死代码约 4700 行，修复打包（PyInstaller）与汉字编码问题，调整界面布局。

> 仅用于自建 DNF 私服的日常维护。本工具会直接读写线上数据库与 `Script.pvf`，操作前务必备份。

## 一、项目简介

面向 DNF 台服/私服的桌面工具箱，使用 Python + tkinter/ttkbootstrap 实现，直接操作服务端 MySQL：

- 把角色背包、仓库等字段当作 **blob** 解析与重写（每件物品为 61 字节的 `DnfItemSlot` 结构）
- 解析并编辑客户端资源 **`Script.pvf`**（背包编辑器与 PVF 编辑器共用同一份已加载的 PVF）
- 提供邮件发送、角色属性修改、时装/宠物清理等 GM 能力
- 附带一套自建登录网关（`pkgLogin/`）

## 二、功能列表

| 模块 | 能力 |
|---|---|
| 角色背包编辑 | 解析 `charac_inven_expand` 等 blob 字段，可视化增删改物品、数量、强化/锻造/增幅数值 |
| PVF 物品搜索与编辑 | 从 `Script.pvf` 读取物品库做关键字搜索，选中后直接提交到背包或邮件 |
| 强制穿戴 | 忽略职业/等级/部位限制，把装备穿到目标角色 |
| 时装 / 宠物删除 | 清理时装栏与宠物栏数据 |
| 强化 / 锻造 / 增幅 | 批量设置装备的强化等级、锻造等级与增幅属性 |
| 魔法封印 | 设置或清除魔法封印属性 |
| 改名 / 转职 / 升级 | 修改角色名、职业、等级等基础属性 |
| 炸背包物品清理 | 删除背包中异常、重复或溢出的物品槽位 |
| PVF 编辑器 | 解析 `Script.pvf`，支持搜索、编辑与导出（共用背包编辑器已加载的 PVF，不重复导入） |
| 邮件发送 | 文本邮件、带道具邮件，以及群发 / 在线 / 全体发送 |

## 三、环境要求

- **操作系统**：Windows（界面依赖 tkinter，DPI 缩放走 Windows API）
- **Python**：3.14（已在 CPython 3.14.7 验证）
- **依赖**：见 [requirements.txt](requirements.txt)
- **数据库**：可访问的服务端 MySQL，地址、账号、端口保存在 [config/config.json](config/config.json)

### PyMySQL 必须锁定 1.0.2

```bash
pip install "PyMySQL==1.0.2"
```

PyMySQL **1.1 及以上**会把 `bytes` 型参数转义为 `_binary X'...'`，而 1.0.2 转义为 `'...'`（按连接字符集解释）。邮件正文等汉字内容是以 `bytes` 传入的，两者落到数据库里的字节完全不同 —— 使用高版本会导致游戏内显示乱码，且**与界面上的编码选项无关**。因此 [requirements.txt](requirements.txt) 中已固定：

```text
PyMySQL==1.0.2
```

## 四、运行与打包

### 4.1 源码运行

```bash
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe main.py
```

[main.py](main.py) 作为入口承担三件事：把工作目录切到脚本所在目录、首次运行时把内置 `config/` 复制到程序旁边（打包后便于持久化配置）、调用 `multiprocessing.freeze_support()`。另提供 PVF 加载自检开关：

```bash
.venv\Scripts\python.exe main.py --loadpvf D:\Script.pvf
```

结果写入工作目录下的 `log/`。

### 4.2 打包为单文件 exe

```powershell
.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --onefile --windowed `
  --runtime-tmpdir . `
  --name DNF背包编辑工具 `
  --add-data "config;config" `
  --collect-all ttkbootstrap --collect-all jsoneditor --collect-all zhconv `
  --exclude-module matplotlib --exclude-module numpy `
  main.py
```

产物为 `dist/DNF背包编辑工具.exe`（约 33.8 MB），运行后在同级目录生成 `config/` 与 `log/`。

### 4.3 打包参数逐条说明

| 参数 / 代码 | 为什么必需 |
|---|---|
| `--onefile --windowed` | 打成单个 exe，且不弹出控制台窗口 |
| `--runtime-tmpdir .` | 单文件引导器默认解压到 `%TEMP%`；当 `%TEMP%` 不可写时会退回 `C:\Windows\Temp`，**非管理员账号写不进去**，启动即报 `Could not create temporary directory!`。指定在 exe 同级目录解压即可绕开 |
| `main.py` 中的 `multiprocessing.freeze_support()` | PVF 解析使用 `multiprocessing.Pool` 多进程；冻结成 exe 后若不调用它，子进程无法创建，表现为**加载 PVF 一直无响应** |
| `--collect-all zhconv` | `zhconv` 的 `zhcdict.json` 是运行时按路径读取的数据文件，静态分析收不到；缺失时加载 PVF（以及所有简繁转换）会抛 `FileNotFoundError: ...zhconv\zhcdict.json` |
| `--add-data "config;config"` | 运行时需要 `config/` 下的配置、道具表、`b2e.exe` 等资源 |
| `--collect-all ttkbootstrap` | 界面主题的资源文件 |
| `--collect-all jsoneditor` | 物品属性 JSON 编辑器所需的前端资源 |
| `--exclude-module matplotlib numpy` | 项目未使用这两个库，排除以缩小体积、加快启动 |

## 五、本轮升级改动清单

### 5.1 结构精简

- 删除无引用代码约 **4700 行**：多余的界面变体、重复的搜索窗口、旧驱动副本、无人调用的辅助模块与图片资源。

### 5.2 汉字编码三连修

| 改动 | 动机 |
|---|---|
| `PyMySQL` 锁定 1.0.2 | 1.1 及以上版本的 `_binary X'..'` 转义改变了落库字节，导致游戏内邮件汉字乱码 |
| `decode()` 无损化（[sqlManager2.py](dnfpkgtool/sqlManager2.py)） | 原实现用 `encode('latin1','replace')` 处理数据库取回的字符；当记录是由 `utf-8` 连接取回的**正常 Unicode** 名字时，汉字会被整体替换成 `?`，界面显示问号，一旦保存就把 `?` 真正写进数据库 |
| `getCharactorNo()` 参数化 | 原实现把 `SQL_ENCODE_LIST` 的默认项 `'混合'`（并非编码名）当作编码传给 `.decode()`，命中即 `LookupError`；且用字符串拼接构造 SQL。改为按参数传 `bytes`，并分别在 `latin1` 与 `utf-8` 两种连接字符集下查询，与同文件的 `getCharacterInfo()` 保持一致 |

### 5.3 界面调整

- **主窗口默认放大**：读取 `RESOLUTION` 配置后抬到不低于 1200×800，且不超过屏幕可用区域。
- **全局事件日志下移**：事件日志区移动到主界面底部，固定 12 行并放大字号，统一记录全局信息（PVF 加载、数据库连接、邮件发送等）。
- **PVF 编辑器瘦身**：移除独立的 PVF 加载框、编码选择框与内置日志面板，界面只保留修改与导出相关操作。
- **搜索功能合并**：原先重复的"专用搜索"入口合并进统一的物品搜索面板。

### 5.4 交互与入口

- 启动时的广告弹窗改为**提示 PVF 文件位置**：`/home/neople/game/Script.pvf` —— 需先从服务器把 `Script.pvf` 下载到本机再打开。
- 删除**失效的旧 GM 工具入口**：其引用的对象从未被赋值，点击必然抛错，属于无功能入口。

## 六、常见问题（Q&A）

**Q1：游戏里收到的邮件，汉字全变成乱码？**
A：MySQL 驱动版本问题。PyMySQL ≥ 1.1 会把 `bytes` 参数转义为 `_binary X'..'`，与 1.0.2 的 `'...'` 在数据库端的解释方式不同，落库字节因此改变。执行 `pip install "PyMySQL==1.0.2"`（本项目已锁定）后重新打包即可。

**Q2：加载 PVF 报 `FileNotFoundError: ...\zhconv\zhcdict.json`？**
A：打包时漏掉了 `zhconv` 的数据文件。打包命令加上 `--collect-all zhconv`。

**Q3：非管理员身份运行 exe 报 `Could not create temporary directory!`？**
A：单文件引导器需要一个可写的解压目录，而「混合」自动探测无法解决权限问题。打包时加 `--runtime-tmpdir .`，并确保 exe 位于**当前用户可写**的目录（不要放在 `Program Files` 等受保护路径）。

**Q4：打包后双击 exe，加载 PVF 一直无响应（既不报错也不结束）？**
A：缺少 `multiprocessing.freeze_support()`。PVF 解析使用多进程，冻结后必须先调用它再进入主逻辑（[main.py](main.py) 已内置）。

**Q5：界面和日志区域太小？**
A：窗口尺寸取自配置 `RESOLUTION`，会被抬到不低于 1200×800；事件日志区固定 12 行并放大字号。屏幕分辨率较低时会自动限制在屏幕可用区域内。

**Q6：修改界面上的"角色显示及编码"后，邮件文字仍然乱码？**
A：该选项只影响读取角色名时的解码显示；邮件正文写入固定使用 `utf-8` 与 `latin1` 连接字符集，不经过该选项。

**Q7：打包时报错或产物没更新？**
A：先关闭正在运行的 exe。文件被占用时 PyInstaller 写不进目标文件，构建会失败或留下旧产物，请核对 exe 的时间戳与体积。

## 七、目录结构

```text
dnf/
├─ main.py                     入口：切工作目录、首次复制 config、freeze_support、PVF 自检开关
├─ requirements.txt            依赖清单（PyMySQL 固定 1.0.2）
├─ dnfpkgtool/                 主程序包
│  ├─ __main__.py              主窗口与各功能页（背包、邮件、搜索……）
│  ├─ sqlManager2.py           MySQL 读写层：物品 blob、编码转换、邮件写入
│  ├─ cacheManager.py          PVF 缓存与配置读写
│  ├─ pvfReader.py             PVF 解析（多进程）
│  ├─ pvfEditor.py             PVF 数据模型与编辑
│  ├─ pvfEditorGUI.py          PVF 编辑器界面
│  ├─ itemSlotFrame.py         物品槽位界面
│  ├─ characFrame.py           角色信息界面
│  └─ ...                      其他功能帧与工具
├─ pkgLogin/                   自建登录网关（客户端 / 服务端）
├─ config/                     配置、道具 CSV、PVF 缓存、图标
│  ├─ config.json              运行配置（数据库、界面等）
│  └─ pvfCache/                PVF 解析缓存
├─ tests/                      自检脚本（离线运行）
├─ log/                        运行日志
└─ dist/                       打包产物（exe + config/ + log/）
```

## 八、注意事项

- **不要引用 `images/ico.png`**：图片资源已在本轮清理中删除。程序图标请使用 `config/DNF.ico` 或 `config/ico.ico`。
- **仓库源文件是 CRLF 换行**：用脚本批量修改时，先以 `read_bytes()` 读出，把 `\r\n` 归一化为 `\n` 再做匹配替换，写回时把 `\n` 还原为 `\r\n`。直接对假定为 LF 的文本调用 `count()` 会匹配失败。
- **配置会被程序覆盖保存**：`config/config.json` 在修改数据库或界面设置时由程序写回，调试前请先备份。
- **直接操作线上数据**：本工具会真实写入数据库与 PVF 文件，请先备份 `taiwan_cain`、`taiwan_cain_2nd` 等相关库以及 `Script.pvf`。
- **打包产物是便携的**：首次运行会把内置 `config/` 复制到 exe 同级目录，此后设置保存在该目录；删除整个文件夹即可完全卸载。

## 更新记录

- **搜索与修改物品合并**：PVF 编辑器的搜索面板新增「修改物品数据」按钮，选中搜索结果点一下就把该物品的完整数据填进背包页签的“修改物品”控件，不必再手输物品名（搜索后端本来就是同一套 search_Items，这次把入口也并到一个面板上）。

## 来源

- 上游原版：[Zageku/DNF_pvf_python](https://github.com/Zageku/DNF_pvf_python)
- 本仓库（fork）：[a87150/DNF_pvf_python](https://github.com/a87150/DNF_pvf_python)
- 尊重原作者版权与致谢；本 fork 的改动集中在结构精简、打包与编码修复、界面调整，详见「升级改动清单」。
