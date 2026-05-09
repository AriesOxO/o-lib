# Olib 开发指南

## 环境要求

- Python 3.8+
- Windows 操作系统（主要目标平台）
- pip 25.0+

## 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/shiyi-0x7f/o-lib.git
cd o-lib

# 2. 创建虚拟环境（推荐）
python -m venv venv
venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置开发环境
echo APP_ENV=dev > .env

# 5. 运行
python app.py
```

## 依赖说明

| 包名 | 用途 |
|------|------|
| PyQt5 | GUI 框架 |
| PyQt-Fluent-Widgets | Fluent Design UI 组件库 |
| loguru | 日志系统 |
| python-dotenv | 环境变量管理 |
| requests | HTTP 请求 |
| psutil | 系统信息（MAC 地址获取） |

## 环境变量

在项目根目录创建 `.env` 文件：

```env
# 开发环境 - 连接本地服务器 http://127.0.0.1:8000
APP_ENV=dev

# 测试环境
# APP_ENV=test

# 生产环境（默认，不设置即为 prod）
# APP_ENV=prod
```

| 环境 | 服务器 | 日志级别 |
|------|--------|----------|
| dev | http://127.0.0.1:8000 | DEBUG（控制台+文件） |
| test | https://测试服务器 | DEBUG |
| prod | https://生产服务器 | INFO（仅控制台） |

## 构建打包

### 使用 PyInstaller

```bash
# 安装 PyInstaller
pip install pyinstaller

# 基本打包（单文件）
pyinstaller --onefile --windowed --icon=logo.ico --name=Olib app.py

# 带资源文件打包
pyinstaller --onefile --windowed --icon=logo.ico --name=Olib --add-data "config;config" app.py
```

产物位于 `dist/Olib.exe`。

### 验证构建

```bash
# 语法检查
python -c "
import py_compile, os, sys
errors = []
for root, dirs, files in os.walk('app'):
    dirs[:] = [d for d in dirs if d != '__pycache__']
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            try:
                py_compile.compile(path, doraise=True)
            except py_compile.PyCompileError as e:
                errors.append(str(e))
if errors:
    for e in errors:
        print(e)
    sys.exit(1)
else:
    print('All files OK')
"

# 模块导入测试
python -c "from app.views.main_window import Window; print('OK')"
```

## 项目模块

| 目录 | 职责 |
|------|------|
| `app/common/` | 配置定义、Qt 资源文件、样式表 |
| `app/tools/` | 核心业务逻辑（搜索引擎、下载器） |
| `app/utils/` | 工具函数（环境、日志、域名、更新、UUID） |
| `app/views/` | UI 视图层（主窗口、搜索页、下载页、设置页） |

## 开发规范

### 代码风格

- 文件头部包含编码声明、版权、时间、作者
- 使用 `loguru` 记录日志，禁止使用 `print` 调试
- 耗时操作（网络请求、文件IO）必须放在 `QThread` 中
- 通过 `pyqtSignal` 进行线程间通信

### 命名规范

- 文件名：snake_case（如 `mod_check.py`）
- 类名：PascalCase（如 `OlibSearcherV4`）
- 函数/变量：snake_case（如 `get_domain`）
- 常量：UPPER_CASE（如 `PRODHOST`）

### 添加新页面

1. 在 `app/views/` 创建新 Interface 类（继承 `QFrame` 或 `ScrollArea`）
2. 在 `main_window.py` 中实例化并通过 `addSubInterface` 注册
3. 如需样式，在 `style_sheet.py` 中添加枚举值

### 添加新配置项

1. 在 `app/common/config.py` 的 `Config` 类中添加 `ConfigItem`
2. 在设置页面添加对应的设置卡片
3. 通过 `cfg.get(cfg.xxx)` 或 `cfg.xxx.value` 读取

### 添加新工具模块

1. 在 `app/utils/` 下创建 `mod_xxx.py`
2. 在 `app/utils/__init__.py` 中导出

## 配置文件

运行时配置自动存储在 `config/config.json`，由 QFluentWidgets 的 `qconfig` 管理。首次运行时自动创建。

## 常见问题

### pip 安装 qfluentwidgets 失败

该包在 PyPI 上的名称是 `PyQt-Fluent-Widgets`，不是 `qfluentwidgets`：

```bash
pip install PyQt-Fluent-Widgets
```

### 启动时报 config 目录不存在

应用会自动创建 `config/` 和 `download/` 目录。如果仍有问题，手动创建即可。

### 无网络环境下启动崩溃

已修复。应用在无法连接服务器时会优雅降级，不影响基本功能。
