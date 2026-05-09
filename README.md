# Olib 开源图书客户端

一款永久免费的电子书搜索与下载桌面应用，基于 PyQt5 + QFluentWidgets 构建。

![image](https://github.com/user-attachments/assets/30555bbe-e6a4-40e5-9f81-1bf304464ba5)

## 功能特性

- 📚 电子书搜索（支持 100+ 种语言）
- 📥 一键下载（支持 txt/pdf/epub/mobi/azw/azw3）
- 🔍 多种搜索模式（热度/匹配度/名称/日期）
- 📖 在线预览
- 🎨 Fluent Design 风格界面
- 🌙 明暗主题切换
- 🔄 自动更新检查

## 快速开始

### 环境要求

- Python 3.8+
- Windows 操作系统

### 安装

```bash
# 克隆仓库
git clone https://github.com/shiyi-0x7f/o-lib.git
cd o-lib

# 安装依赖
pip install -r requirements.txt

# 运行
python app.py
```

### 从发布版安装

前往 [Releases](https://github.com/shiyi-0x7f/o-lib/releases) 下载最新版本的可执行文件。

## 构建打包

```bash
# 安装打包工具
pip install pyinstaller

# 打包为单文件可执行程序
pyinstaller --onefile --windowed --icon=logo.ico --name=Olib app.py
```

打包产物在 `dist/` 目录下。

## 开发

```bash
# 创建虚拟环境
python -m venv venv
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 设置开发环境
echo APP_ENV=dev > .env

# 运行
python app.py
```

详细开发文档见 [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)。

## 项目结构

```
o-lib/
├── app.py              # 应用入口
├── requirements.txt    # Python 依赖
├── app/
│   ├── common/         # 配置、资源、样式
│   ├── tools/          # 搜索和下载引擎
│   ├── utils/          # 工具模块
│   └── views/          # UI 界面
└── docs/               # 项目文档
```

## 贡献

欢迎贡献代码！请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

## 联系作者

- BiliBili: [拾壹0x7f](https://space.bilibili.com/19276680)
- 公众号: 拾壹0x7f
- 主页: [11xy.cn](https://www.11xy.cn)

## 许可证

[GPL-3.0](LICENSE) © shiyi0x7f
