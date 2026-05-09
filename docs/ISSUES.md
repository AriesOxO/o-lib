# Olib 问题跟踪

## 构建测试结果

测试日期: 2026-05-10
Python: 3.10.6
PyQt5: 5.15.11
PyQt-Fluent-Widgets: 1.11.2

### 问题列表

| # | 严重程度 | 模块 | 描述 | 状态 |
|---|----------|------|------|------|
| 1 | 高 | app/utils/mod_check.py | CheckUpdate 网络请求无异常处理，服务器不可达时导致应用崩溃 | ✅ 已修复 |
| 2 | 低 | app/views/searchInterface.py | SearchInterface 重复添加布局，Qt 运行时警告 | ✅ 已修复 |
| 3 | 低 | app/common/config.py | 缺少 config 目录和 download 目录的自动创建 | ✅ 已修复 |

---

## 问题详情

### #1 CheckUpdate 网络请求无异常处理（高）

**文件**: `app/utils/mod_check.py`

**现象**: `Window.__init__` → `checkUpdate()` → `CheckUpdate()` → `__get_config()` 中直接调用 `requests.get()` 且无 try/except。当生产服务器不可达时，抛出 `ConnectionError`，导致主窗口无法创建，应用直接崩溃。

**复现**: 在无网络环境或服务器地址无效时启动应用。

**修复方案**: 在 `__get_config()` 中添加异常处理，网络失败时 `self.__config` 保持 None；在 `get_notice()` 和 `handle_version()` 中对 `__config is None` 做安全处理。

**修复内容**:
- `__get_config()`: 添加 try/except，捕获所有异常，失败时设置 `self.__config = None`，添加 timeout=5
- `__get_version_status()`: 增加 `if self.__config is None: return 0` 提前返回
- `get_notice()`: 增加 None 检查，返回安全默认值 `{'show': False, 'title': '', 'content': ''}`
- `get_update_url()`: 增加 None 检查

---

### #2 SearchInterface 重复添加布局（低）

**文件**: `app/views/searchInterface.py`

**现象**: Qt 运行时警告 `QLayout: Attempting to add QLayout "" to SearchInterface "搜索页", which already has a layout`

**原因**: `SearchInterface.__init__` 中先创建了 `self.layout = QVBoxLayout(self)`，然后在 `initUI()` 中又创建了 `hbox = QHBoxLayout(self)` 并传入 `self` 作为 parent，导致尝试给已有布局的 widget 再设置一个布局。

**修复方案**: 将 `hbox = QHBoxLayout(self)` 改为 `hbox = QHBoxLayout()`（不传 parent），因为它后续通过 `self.layout.addLayout(hbox)` 添加为子布局。

**修复内容**: 修改了 `initUI()` 和 `add_command_bar()` 两处 `QHBoxLayout(self)` → `QHBoxLayout()`。

---

### #3 缺少目录自动创建（低）

**文件**: `app/common/config.py`, `app.py`

**现象**: 首次运行时如果 `config/` 目录或 `download/` 目录不存在，可能导致文件操作失败。

**修复方案**: 在应用启动时确保必要目录存在。

**修复内容**: 在 `app.py` 的 `if __name__ == '__main__'` 中，`setup_logger()` 之后添加 `os.makedirs('config', exist_ok=True)` 和 `os.makedirs('download', exist_ok=True)`。
