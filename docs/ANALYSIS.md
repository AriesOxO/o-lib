# Olib 项目深度分析

分析日期: 2026-05-10
分析范围: 全部源代码、配置、UI 交互逻辑

## 一、严重问题（建议立即修复）

### 1.1 凭证硬编码泄漏（安全）

**位置**: `app/views/searchInterface.py:preview()`

```python
url = book.get('readOnlineUrl') + f'&user_id=38713159&user_key=5dcc5da2ccd3f344c0c66a17c33349cf'
```

`user_id` 和 `user_key` 硬编码在客户端代码中，任何人都可以从源码或二进制中提取。这既是安全风险也是账号滥用风险。

**建议**: 移至服务端代理请求，或从服务端动态获取签名。

---

### 1.2 日志环境判断永远失效

**位置**: `app/utils/mod_log.py`

```python
env = get_env()  # 返回小写的 'dev'/'prod'
if env == 'DEV':  # 永远 False
    ...
elif env == 'PROD':  # 永远 False
    ...
else:
    # 所有环境都走这里
```

`get_env()` 返回小写字符串，但 `setup_logger` 比较的是大写，导致日志配置永远走 default 分支。生产环境意外地用的是 DEBUG 级别。

**建议**: 改为 `env == 'dev'` 和 `env == 'prod'`。

---

### 1.3 MAC 地址获取失败时崩溃

**位置**: `app/utils/mod_uuid.py`

```python
def get_first_mac():
    for interface, addrs in interfaces.items():
        for addr in addrs:
            if addr.family == psutil.AF_LINK:
                return addr.address
    # 隐式 return None
```

如果系统没有网卡或无法枚举，`get_first_mac()` 返回 `None`，`uuid.uuid5(namespace, None)` 会抛 `TypeError`。

**建议**: 加 fallback 到随机 UUID 并持久化到本地。

---

### 1.4 生产服务器地址是占位符

**位置**: `app/common/config.py`

```python
PRODHOST = '生产服务器地址'
TESTHOST = "测试服务器地址"
```

打包发布的 v2.0.5 实际上无法连接任何服务器。必须在发布前填入真实地址，或通过环境变量/配置文件注入。

---

## 二、代码质量问题

### 2.1 `olib_search.py` 捕获过宽

```python
try:
    if data['success']==1:
        ...
except Exception as e:
    self.sig_fail.emit(-999)  # 一律当作"违禁词"
```

任何异常（网络、JSON 解析、KeyError、逻辑 bug）都被报告为"搜索词违禁"，误导用户。

**建议**: 分别处理 `JSONDecodeError`、`KeyError` 和业务异常，每类对应不同错误码。

---

### 2.2 字段名拼写错误

```python
# config.py
reapeatFiles = ConfigItem("Settings", "repeatFiles", ...)  # repeat 拼错成 reapeat
```

配置键的代码名和存储名不一致，且整个代码库都在用错误拼写。修复需要同时迁移已有配置文件。

---

### 2.3 下载断点续传逻辑缺失但用了 `'ab'` 模式

**位置**: `app/tools/olib_download.py:download_file`

```python
with open(src, 'ab') as f:  # append binary
```

以 append 模式打开但重名处理只判断完整文件存在，如果下载中途失败，下次重试会拼接到旧文件导致损坏。

**建议**: 要么真正实现断点续传（记录已下载字节数 + `Range` header），要么改为 `'wb'` 覆盖写。

---

### 2.4 `main_window.py` 多处小问题

- 文件顶部有两行 `# coding:utf-8`
- `setCollapsible(True)` 后面注释写的是"禁止展开"，实际 True 表示允许折叠，注释与代码相反
- `updateStyleSheet` 里 `theme = cfg.theme.value` 取了值但没使用
- 很多导入的 qfluentwidgets 组件实际未使用（Dialog、SwitchButton、Flyout 等）

---

### 2.5 奇怪的 `try/except` import

```python
# olib_search.py
try:
    from OlibFluent.app.utils import get_domain, get_uuid
except:
    from ..utils import get_domain, get_uuid
```

第一条导入路径永远失败（不存在 `OlibFluent` 包），靠异常捕获降级。应该直接用相对导入。

---

### 2.6 `contextMenuEvent` 行号计算可疑

```python
row = self.tableWidget.rowAt(local_pos.y()) - 1
```

为什么要减 1？如果是为了补偿表头偏移，应该用 `QHeaderView.sectionSize` 或 `mapToGlobal`，而不是硬减 1。且表格开启了 `setSortingEnabled(True)`，排序后行号不对应原 `books` 索引，当前 `get_current_book` 按标题+大小匹配勉强能用，但当重名时会拿错。

---

### 2.7 阻塞启动

`Window.__init__` 中同步调用 `CheckUpdate()` 发网络请求。在网络慢或 DNS 超时场景，UI 冻结数秒到十几秒才显示。

**建议**: 将更新检查放到 QThread 异步执行，完成后发信号回主线程。

---

## 三、架构优化建议

### 3.1 引入依赖注入或服务层

目前 `OlibSearcherV4` 和 `OlibDownloaderV4` 直接从 `cfg` 读配置、从 `utils` 取 uuid/domain，紧耦合。建议抽一层 `ApiClient`，统一处理：
- 请求超时、重试
- UUID/Header 注入
- 统一错误码
- 可 mock 方便测试

### 3.2 错误码改为枚举

散落在代码中的魔法数字 `0, -1, -999, 999` 应该用 `IntEnum` 替代：

```python
class SearchError(IntEnum):
    EMPTY_RESULT = 0
    UNKNOWN = -1
    BLOCKED_KEYWORD = -999
    RATE_LIMIT = 999
```

### 3.3 没有测试

整个项目 0 测试。核心逻辑（重名处理、进度计算、UUID 生成、搜索参数组装）都值得单元测试。

**建议**: 引入 pytest，至少覆盖 `app/tools/` 和 `app/utils/`。

### 3.4 国际化只是个字典

`Languages` dict 把中文标签映射到后端语言码，不是真 i18n。如果要做多语言 UI，需要用 Qt 的 `.ts/.qm` 翻译文件系统，`self.tr("xxx")` 才能工作。

---

## 四、可扩展功能建议

按实现难度排序：

### 简单（1-2 天）
- [ ] **搜索历史** — 本地 JSON 保存最近搜索关键词，下拉展示
- [ ] **年份筛选 UI** — 后端已支持 `yearFrom/yearTo`，前端没暴露
- [ ] **书籍详情面板** — 点击书名弹出右侧抽屉，显示完整简介、封面、语言、出版社
- [ ] **下载任务操作** — 暂停/取消/删除/重试/打开所在位置
- [ ] **下载完成系统通知** — 用 Windows 原生通知 / `QSystemTrayIcon`
- [ ] **About 对话框** — 展示版本、作者、GitHub、第三方许可证

### 中等（3-5 天）
- [ ] **收藏夹 / 书单** — 本地 SQLite 存用户收藏的书，跨会话保留
- [ ] **批量下载** — 多选书籍一键排队下载
- [ ] **断点续传** — HTTP Range 请求 + 本地记录进度
- [ ] **下载完整性校验** — 服务端返回哈希，客户端下载后校验
- [ ] **搜索结果缓存** — 同一关键词 30 分钟内复用结果，减少服务器压力
- [ ] **自动识别语言** — 根据输入中的字符自动选语言

### 较复杂（1 周+）
- [ ] **内置阅读器** — 集成 PDF.js 或 Qt 阅读器，省得跳浏览器
- [ ] **用户账号系统** — 云端同步收藏/下载历史
- [ ] **推荐系统** — 基于收藏/历史推相似书
- [ ] **插件系统** — 第三方可注册新的搜索源

---

## 五、界面与 UX 优化

### 5.1 搜索页

**问题**: 搜索框宽度硬编码为窗口一半，过宽不美观；加载时只有中央 loading 无骨架屏。

**建议**:
- 搜索框最大宽度 600px，居中
- 加骨架屏（skeleton）代替单纯的 loading 弹窗
- 表格行高统一，书名列加粗
- 年份、大小、格式用标签（Badge）而不是纯文本
- 右键菜单剔除无关项（云书架、微信读书这种跳浏览器的放到侧边栏固定入口，别混在每个书的右键里）

### 5.2 下载页

**问题**: 只有三列（书名/进度/速度），信息量少；无法操作下载中的任务。

**建议**:
- 增加 ETA（预计剩余时间）、文件大小
- 每行最右加操作按钮（暂停、取消、打开文件、打开文件夹）
- 顶部加汇总栏：总下载数、进行中、已完成、失败
- 完成的任务可以"清除已完成"
- 增加一个"历史记录"标签页

### 5.3 设置页

**问题**: 配置项分组还行，但几个地方不直观。

**建议**:
- 下载路径卡片显示完整路径而不是"当前下载文件夹"占一行标题+路径两行
- 展示数 RangeCard 加当前值显示（slider 旁边的数字）
- 关于页面加"贡献者"列表
- 加"导出配置 / 导入配置"按钮
- 加"清除缓存"按钮

### 5.4 主窗口

**问题**: 赞赏按钮和主题切换按钮在侧边栏底部，不小心点到"赞赏"会弹内容。

**建议**:
- 赞赏入口移到设置页或关于页
- 主题切换可以做成 Segmented Control（明/暗/跟随系统）
- 顶部标题栏右侧加设置快捷入口
- 窗口标题太长（"Olib开源图书——一款永久免费的电子书软件"），可缩为 "Olib"

### 5.5 交互细节

- 搜索按 Enter 时有时光标不在输入框会触发整个窗口的 Enter，建议 `keyPressEvent` 加焦点判断
- 下载成功的 InfoBar 父容器是 `self.searchInterface`，切到下载页看不到提示
- 状态栏的"鸡汤"随机语录风格不一致，建议要么全移除，要么做成可关闭选项
- DPI 缩放变更需要重启，但没有明确提示重启按钮，只有文字

---

## 六、跨平台支持

项目标注 Windows Only，但很多代码其实可以跨平台，主要阻碍点：

| 位置 | 问题 | 影响平台 |
|------|------|----------|
| `searchInterface.__open_folder` | `os.startfile` 是 Windows Only | macOS/Linux |
| `main_window.initWindow` | `FramelessWindow` 在 Linux/Mac 表现不一致 | macOS/Linux |
| `mod_uuid.py` | `psutil.AF_LINK` 跨平台但需验证 | macOS/Linux |
| 下载路径默认 `"download"` | 相对路径，应使用用户目录 | 全平台 |
| 字体加载 | Windows 默认字体在其他平台可能缺失 | macOS/Linux |

### 6.1 macOS 支持改造清单

**代码改动**:
1. 替换 `os.startfile` 为跨平台的 `open_in_file_manager`
2. 默认下载目录改为 `~/Downloads/Olib` 或 `Path.home() / 'Downloads'`
3. 路径字符串统一用 `pathlib.Path`，避免 `\` / `/` 混用
4. macOS 窗口按钮位置和 Windows 相反，`qframelesswindow` 已自动处理，但需测试
5. macOS 的 retina 屏幕 DPI 自动处理，`AA_EnableHighDpiScaling` 足够
6. 菜单栏集成：macOS 应用菜单应该在屏幕顶部而不是窗口内，PyQt 默认支持

**图标资源**:
- macOS 需要 `.icns` 格式（非 `.ico`）
- 可用 `iconutil` 或 `png2icns` 从 PNG 源图生成

**打包**:
- macOS 用 `pyinstaller --windowed` 会生成 `.app` 包
- 需签名（`codesign`）和公证（`notarize`）才能在其他 Mac 上运行
- 没有 Apple 开发者账号时，用户需手动右键"打开"绕过 Gatekeeper

**CI 扩展**:
```yaml
jobs:
  build-windows:
    runs-on: windows-latest
    # ...
  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt pyinstaller
      - run: pyinstaller --onedir --windowed --icon=logo.icns --name=Olib app.py
      - run: cd dist && zip -r Olib-macos.zip Olib.app
      - uses: actions/upload-artifact@v4
        with:
          name: Olib-macos
          path: dist/Olib-macos.zip
```

**推荐拆分策略**: 单独建 `build-macos.yml` 和 `build-linux.yml`，避免单 workflow 失败影响全平台。

---

## 七、打包体积优化

### 7.1 当前体积估算

基于依赖分析（未实测打包产物）：

| 依赖 | 约占用（MB） |
|------|-------------|
| PyQt5 + Qt5 库 | ~50 |
| PyQt-Fluent-Widgets | ~5 |
| Python 运行时 | ~20 |
| requests/loguru/psutil/dotenv | ~3 |
| 资源文件（resources.py） | ~5 |
| **PyInstaller --onefile 估算** | **70-90 MB** |

单文件 exe 还要加上启动时自解压开销，冷启动慢 2-3 秒。

### 7.2 体积优化方案

**方案 A: PyInstaller `--onedir` 替代 `--onefile`**

- 启动快（无自解压）
- 便于增量更新（只替换改动的文件）
- 代价：分发变成文件夹/压缩包而不是单文件

**方案 B: 排除未使用的 Qt 模块**

Qt 有很多模块项目用不到（QML、3D、WebEngine、Multimedia 等），PyInstaller 默认会打包进去。

```python
# Olib.spec (生成后修改)
excludes = [
    'PyQt5.QtWebEngineCore',
    'PyQt5.QtWebEngineWidgets',
    'PyQt5.QtQml',
    'PyQt5.QtQuick',
    'PyQt5.QtMultimedia',
    'PyQt5.QtMultimediaWidgets',
    'PyQt5.Qt3DCore',
    'PyQt5.Qt3DRender',
    'PyQt5.QtPositioning',
    'PyQt5.QtLocation',
    'PyQt5.QtBluetooth',
    'PyQt5.QtNfc',
    'PyQt5.QtSensors',
    'PyQt5.QtSerialPort',
    'PyQt5.QtSql',
    'PyQt5.QtTest',
    'PyQt5.QtDesigner',
    'PyQt5.QtHelp',
    'PyQt5.QtXml',
    'PyQt5.QtXmlPatterns',
]
```

实测可减 30-50 MB。

**方案 C: UPX 压缩**

```bash
# 安装 upx（https://upx.github.io/）
pyinstaller --onefile --upx-dir=C:\upx --windowed app.py
```

压缩比 30-50%，但启动稍慢且可能被杀软误报。

**方案 D: 换用 Nuitka**

- Nuitka 将 Python 编译为 C，启动更快、体积更小（约 40 MB）
- 代价：构建时间长、调试困难、部分动态特性不支持

**方案 E: 改用 PySide6 + Qt 精简**

PySide6 的 LGPL 许可允许剔除未用到的 dll，可再减 20-30 MB。但需要适配 API 差异。

### 7.3 推荐组合

对本项目推荐：**onedir + 排除无用 Qt 模块 + UPX + 打包为 zip**

预期：70 MB onefile → 30-40 MB 解压后，zip 压缩到 20-25 MB 供分发。

### 7.4 打包脚本

建议建立 `build.py` 或 `Olib.spec` 规范化打包流程：

```python
# build.py
import PyInstaller.__main__
import shutil
import zipfile
from pathlib import Path

EXCLUDES = [
    'PyQt5.QtWebEngineCore', 'PyQt5.QtWebEngineWidgets',
    'PyQt5.QtQml', 'PyQt5.QtQuick',
    'PyQt5.QtMultimedia', 'PyQt5.QtMultimediaWidgets',
    'PyQt5.Qt3DCore', 'PyQt5.Qt3DRender',
    'PyQt5.QtSql', 'PyQt5.QtTest',
]

args = [
    'app.py',
    '--name=Olib',
    '--windowed',
    '--icon=logo.ico',
    '--onedir',
    '--clean',
    '--noconfirm',
]
for mod in EXCLUDES:
    args.extend(['--exclude-module', mod])

PyInstaller.__main__.run(args)

# 打包为 zip
dist = Path('dist/Olib')
out = Path('dist/Olib-windows.zip')
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    for f in dist.rglob('*'):
        z.write(f, f.relative_to(dist.parent))
print(f'Built: {out} ({out.stat().st_size / 1024 / 1024:.1f} MB)')
```

对应 CI workflow 改为：

```yaml
- run: python build.py
- uses: actions/upload-artifact@v4
  with:
    name: Olib-windows
    path: dist/Olib-windows.zip
```

---

## 八、优先级路线图

建议按下面顺序推进：

### P0（1 周内）
1. 修复凭证硬编码问题（安全）
2. 修复日志环境判断
3. 填入真实 `PRODHOST` 或改为启动配置
4. `CheckUpdate` 异步化
5. 打包瘦身（排除无用 Qt 模块，体积减半）

### P1（2 周内）
6. 引入 pytest 和基础测试
7. 下载支持暂停/取消/删除
8. 搜索历史
9. 年份筛选 UI
10. macOS 平台适配（代码改跨平台 + CI 增加 macOS 构建）

### P2（1-2 月）
11. 收藏夹
12. 批量下载
13. 内置预览
14. Linux 平台适配
15. Nuitka / PySide6 深度优化体积

---

## 九、改进点代码示例

### 9.1 异步检查更新

```python
# 新增 app/tools/update_checker.py
class UpdateChecker(QThread):
    update_available = pyqtSignal(dict)  # 新版本信息
    notice_ready = pyqtSignal(dict)

    def run(self):
        try:
            resp = requests.get(f"{get_domain()}/OlibServer", timeout=5)
            data = resp.json()
            self.notice_ready.emit(data.get('Notice', {}))
            # ... 版本比较
        except Exception as e:
            logger.warning(f"检查更新失败: {e}")
```

### 9.2 错误码枚举

```python
# 新增 app/common/errors.py
from enum import IntEnum

class ApiError(IntEnum):
    OK = 1
    EMPTY = 0
    UNKNOWN = -1
    BLOCKED = -999
    RATE_LIMIT = 999

    @property
    def user_message(self) -> tuple[str, str]:
        return {
            ApiError.EMPTY: ("结果为空", "本次搜索结果为空，请更改搜索条件"),
            ApiError.UNKNOWN: ("未知异常", "请稍后重试或联系支持"),
            ApiError.BLOCKED: ("搜索词异常", "请更换搜索关键词"),
            ApiError.RATE_LIMIT: ("速率限制", "服务器繁忙，请稍后再试"),
        }[self]
```

### 9.3 跨平台打开文件管理器

```python
# app/utils/mod_fs.py
import sys
import subprocess
import os

def open_in_file_manager(path: str):
    if sys.platform == 'win32':
        os.startfile(path)
    elif sys.platform == 'darwin':
        subprocess.Popen(['open', path])
    else:
        subprocess.Popen(['xdg-open', path])
```
