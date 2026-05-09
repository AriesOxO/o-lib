# 贡献指南

感谢你对 Olib 项目的关注！我们欢迎任何形式的贡献。

## 如何贡献

### 报告 Bug

1. 在 [Issues](https://github.com/shiyi-0x7f/o-lib/issues) 中搜索是否已有相同问题
2. 如果没有，创建新 Issue，包含以下信息：
   - 操作系统版本
   - Python 版本
   - 复现步骤
   - 期望行为 vs 实际行为
   - 错误截图或日志

### 提交功能建议

在 Issues 中创建 Feature Request，描述：
- 你想解决什么问题
- 你期望的解决方案
- 是否有替代方案

### 提交代码

1. Fork 本仓库
2. 创建功能分支：`git checkout -b feature/你的功能名`
3. 提交更改：`git commit -m "feat: 添加xxx功能"`
4. 推送分支：`git push origin feature/你的功能名`
5. 创建 Pull Request

## 开发环境搭建

```bash
# 克隆仓库
git clone https://github.com/shiyi-0x7f/o-lib.git
cd o-lib

# 创建虚拟环境（推荐）
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 配置开发环境
echo APP_ENV=dev > .env

# 运行
python app.py
```

## 代码规范

- 文件头部包含编码声明、版权信息、时间和作者注释
- 使用 `loguru` 进行日志记录，不使用 `print`
- 耗时操作使用 `QThread`，通过信号槽与 UI 通信
- 变量和函数命名使用 snake_case
- 类命名使用 PascalCase

## Commit 规范

使用语义化提交信息：

- `feat:` 新功能
- `fix:` Bug 修复
- `docs:` 文档更新
- `style:` 代码格式调整（不影响逻辑）
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建/工具链相关

## 项目结构

```
app/
├── common/    # 配置、资源、样式
├── tools/     # 核心业务（搜索、下载）
├── utils/     # 工具函数
└── views/     # UI 视图
```

## 许可证

本项目使用 [GPL-3.0](LICENSE) 许可证。提交代码即表示你同意以相同许可证发布你的贡献。
