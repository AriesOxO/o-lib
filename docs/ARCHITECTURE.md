# Olib 项目架构文档

## 概述

Olib（Open Library）是一款基于 PyQt5 + QFluentWidgets 构建的开源电子书搜索与下载桌面客户端。用户可以通过该应用搜索、预览和下载电子书资源。

## 技术栈

- **语言**: Python
- **GUI 框架**: PyQt5
- **UI 组件库**: QFluentWidgets（Fluent Design 风格）
- **窗口框架**: qframelesswindow（无边框窗口）
- **日志**: loguru
- **环境管理**: python-dotenv
- **网络请求**: requests
- **系统信息**: psutil

## 项目结构

```
OlibFluent/
├── app.py                    # 应用入口
├── config/
│   └── config.json           # 运行时配置文件（自动生成）
├── app/
│   ├── __init__.py
│   ├── common/               # 公共模块
│   │   ├── config.py         # 应用配置定义
│   │   ├── resources.py      # Qt 资源文件（图标、QSS等）
│   │   ├── style_sheet.py    # 样式表管理
│   │   └── __init__.py
│   ├── tools/                # 核心业务逻辑
│   │   ├── olib_search.py    # 搜索引擎（QThread）
│   │   ├── olib_download.py  # 下载器（QThread）
│   │   └── __init__.py
│   ├── utils/                # 工具模块
│   │   ├── mod_env.py        # 环境变量管理
│   │   ├── mod_domain.py     # 服务器域名解析
│   │   ├── mod_log.py        # 日志配置
│   │   ├── mod_check.py      # 版本更新检查
│   │   ├── mod_uuid.py       # 设备UUID生成
│   │   └── __init__.py
│   └── views/                # 视图层
│       ├── main_window.py    # 主窗口
│       ├── searchInterface.py    # 搜索页面
│       ├── downloadInterface.py  # 下载页面
│       ├── setting_interface.py  # 设置页面
│       └── __init__.py
├── 256.ico                   # 应用图标
├── logo.ico                  # Logo图标
├── README.md
└── LICENSE
```

## 模块说明

### app.py（入口）

- 初始化日志系统
- 配置 HiDPI 缩放
- 创建 QApplication 和主窗口

### app/common/config.py（配置）

核心配置类 `Config` 继承自 `QConfig`，管理以下配置项：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| downloadFolder | 下载目录 | "download" |
| downloadSwitch | 下载开关 | True |
| reapeatFiles | 重名文件跳过 | True |
| searchNums | 搜索结果数量 | 50 (50-200) |
| language | 搜索语言 | 0 |
| searchMode | 搜索排序模式 | 0 |
| extensions | 文件格式筛选 | 0 |
| accurate | 精准搜索 | False |
| dpiScale | DPI缩放 | "Auto" |
| checkUpdateAtStartUp | 启动时检查更新 | True |

全局常量：
- `VERSION`: 当前版本号 "2.0.4"
- `AUTHOR`: "shiyi0x7f"
- 支持 100+ 种语言搜索
- 支持 txt/pdf/epub/mobi/azw/azw3 格式筛选

### app/tools/olib_search.py（搜索）

`OlibSearcherV4(QThread)` — 异步搜索线程

- 向服务端 `/getbooks` 接口发送 POST 请求
- 支持参数：书名、语言、格式、页码、排序、数量、精准搜索、年份范围
- 信号：`sig_success(list)` 成功返回书籍列表，`sig_fail(int)` 失败错误码

### app/tools/olib_download.py（下载）

`OlibDownloaderV4(QThread)` — 异步下载线程

- 向服务端 `/getdownurl` 获取下载链接
- 流式下载，实时报告进度和速度
- 支持重名文件处理（跳过/重命名）
- 信号：进度、速度、完成状态、速率限制

### app/views/（视图层）

- **main_window.py**: 主窗口，包含导航栏、页面栈、主题切换、更新检查、通知展示
- **searchInterface.py**: 搜索界面，包含搜索框、筛选条件、结果表格、分页、右键菜单（下载/预览/书架）
- **downloadInterface.py**: 下载管理界面，表格展示下载任务的书名、进度条、速度
- **setting_interface.py**: 设置界面，包含个性化、搜索下载设置、更新设置、关于信息

### app/utils/（工具层）

- **mod_env.py**: 通过 `.env` 文件读取 `APP_ENV` 环境变量（dev/test/prod）
- **mod_domain.py**: 根据环境返回对应服务器地址
- **mod_log.py**: 根据环境配置 loguru 日志级别和输出
- **mod_check.py**: `CheckUpdate` 类，从服务端获取版本信息，处理强制/可选更新
- **mod_uuid.py**: 基于 MAC 地址生成设备唯一标识 UUID

## 数据流

```
用户输入搜索 → SearchInterface → OlibSearcherV4(QThread)
    → POST /getbooks → 返回书籍列表 → 展示在表格中

用户点击下载 → SearchInterface 发出信号 → MainWindow 转发
    → DownloadInterface → OlibDownloaderV4(QThread)
    → POST /getdownurl → GET 下载链接 → 流式写入文件
```

## 环境配置

通过 `.env` 文件中的 `APP_ENV` 变量控制：

| 环境 | 值 | 服务器 |
|------|-----|--------|
| 开发 | dev | http://127.0.0.1:8000 |
| 测试 | test | https://测试服务器地址 |
| 生产 | prod（默认） | https://生产服务器地址 |

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| /getbooks | POST | 搜索书籍 |
| /getdownurl | POST | 获取下载链接 |
| /OlibServer | GET | 获取服务端配置（版本、公告、更新地址） |

所有请求携带 `UUID` Header 用于设备标识。
