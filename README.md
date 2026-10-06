# DNF 私服工具箱（背包 / PVF / GM）

## 介绍

- DNF 私服工具箱：PVF 解析/编辑，以及数据库侧的 角色 / 背包 / 邮件 / 宠物 / 时装 / 任务 / GM / 封停 / 角色表 / 数据库 等页签。
- 本仓库是 [Zageku/DNF_pvf_python](https://github.com/Zageku/DNF_pvf_python) 的 fork，本项目地址：[a87150/DNF_pvf_python](https://github.com/a87150/DNF_pvf_python)。
- 源码运行需要 Windows + Python 3.14。

## 使用

1. 装依赖：`pip install -r requirements.txt`（PyMySQL 必须锁 1.0.2，1.1+ 写汉字会乱码）。
2. 配置：把 `config/config.example.json` 复制成 `config/config.json`，填好数据库信息（该文件不入库）。
3. 源码运行：`python main.py`。
4. 或直接用 `dist\DNF背包编辑工具.exe`，双击即用。
5. 自己打包（PyInstaller onefile + windowed）：

```powershell
python -m PyInstaller --noconfirm --clean --onefile --windowed --runtime-tmpdir . ^
  --name DNF背包编辑工具 --add-data "config;config" ^
  --exclude-module matplotlib --exclude-module numpy --exclude-module scipy --exclude-module pandas ^
  --exclude-module PyQt5 --exclude-module PyQt6 --exclude-module PySide2 --exclude-module PySide6 ^
  --exclude-module IPython --exclude-module pytest --exclude-module setuptools --exclude-module pip ^
  --exclude-module wheel --exclude-module distutils --exclude-module lib2to3 --exclude-module pygments ^
  --exclude-module docutils main.py
```

> **不要排除 PIL/Pillow**：ttkbootstrap 渲染主题素材硬依赖它。

6. 连库：数据库页填 IP / 端口 / 账户 / 密码 → 点「连接数据库」。

## 修改了什么

- 升级到 Python 3.14 并调整依赖。
- 精简：删死文件 / 无用资源 / 无用依赖，exe 31.27 MiB。
- 汉字写库编码修复：PyMySQL 锁 1.0.2 + latin1/bytes 路径。
- py3.14 线程模型整改：控件操作一律回主线程，主线程泵不会因异常停止、不会永久挂起。
- PVF 编辑器左侧合并成「1 个搜索栏 + 1 个结果列表 + 4 个按钮（提交编辑 / 提交邮件 / 修改物品数据 / 以该物品为模板）」。
- 新增「角色表」页（状态 / 角色ID / 角色名 / 等级 / 职业 / UID；删除、恢复、拷贝、备份选中角色，读取恢复数据；右栏账号 ID 查找 + 转移角色到右侧账号）；备份文件 `.cbak` 与原版格式一致：zlib + pickle(PROTO3)、16 个裸表名行元组。
- 关于页去掉 QQ 群二维码与「项目地址 / 交流群」按钮，改为「原项目地址 / 本项目地址」两条可点击链接。
- 修复打包版连接流程三个根因：print2title 归属、eventList.json 编码导致连接线程死、PyMySQL 在 frozen 进程 getpass 失败导致启动即退。
- 移除 pyqrcode / pypng 依赖与若干无用配置键。
