# Web UI Automation Framework

基于 Python + Playwright + Pytest 的 Web UI 自动化测试框架，采用 Page Object Model (POM) 设计模式。

## 特性

- ✅ **Page Object Model** - 清晰的页面对象分层设计
- ✅ **Mixin 架构** - 8 个功能 Mixin 提供可复用的操作能力
- ✅ **统一断言** - 自定义 Assertion 类，支持丰富的断言方法
- ✅ **Element 定位器** - 类型安全的元素定位配置
- ✅ **登录状态管理** - 自动保存和复用认证状态
- ✅ **YAML 数据驱动** - 测试数据与代码分离
- ✅ **Allure 报告** - 美观的测试报告
- ✅ **异常处理** - 统一的异常捕获和日志记录
- ✅ **HTTP Client** - 内置轻量 HTTP 客户端，支持接口级后置处理（无额外依赖）

## 当前运行约定

- 当前 `config/config.py` 默认 `BASE_URL` 指向业务站点：`http://101.200.193.143/`
- 默认可直接运行的业务测试主要在：`tests/login/`、`tests/mar/`、`tests/blood/`
- `tests/test/` 下是基于 Sahi Demo 的示例/练习用例；如果要跑这一组，需要先把 `BASE_URL` 切换到 `https://sahitest.com/demo/index.htm`

## 快速开始

### 环境要求

- Python 3.9+
- pip

### 安装依赖

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

### 业务测试首次运行

```bash
cp .env.local.example .env.local
# 编辑 .env.local，填入真实业务账号
```

说明：

- `authenticated_page` / `authenticated_state` 依赖业务账号，但账号不再从 `test_data/login/login_data.yaml` 读取
- 框架会优先读取进程环境变量，其次读取仓库根目录的 `.env.local` / `.env.auth.local`
- VS Code 测试资源管理器和调试配置已经指向 `${workspaceFolder}/.env.local`

### 运行测试

```bash
# 运行业务测试（默认推荐）
pytest tests/login tests/mar tests/blood -v

# 运行指定文件
pytest tests/login/test_login.py
pytest tests/mar/test_mar.py -v -s

# 失败时保留 trace
pytest --trace-mode=retain-on-failure

# 生成并查看 Allure 报告
pytest --alluredir=allure-results
allure serve allure-results

# 运行 Sahi Demo 示例用例前，先把 BASE_URL 改为 https://sahitest.com/demo/index.htm
pytest tests/test/test_select.py -v
```

### 录制脚本（Playwright codegen）

项目已内置录制脚本：`tools/record.py`，用于快速录制浏览器操作并生成 Python/pytest 脚本。

```bash
# 使用 config/config.py 的 BASE_URL 录制（默认移动端设备）
python3 tools/record.py

# 桌面模式录制
python3 tools/record.py --platform

# 带业务登录态录制（从 .env.local 的 AUTOTEST_AUTH_USER_JSON 注入）
python3 tools/record.py --platform --business-auth

# 指定输出文件名（生成到 tools/recordings/）
python3 tools/record.py --output aixmy_flow

# 指定格式为 pytest
python3 tools/record.py --format pytest

# 查看设备列表
python3 tools/record.py --list-devices
```

说明：

- 录制产物目录：`tools/recordings/`
- `--platform` 与 `--device` 不能同时使用
- `--business-auth`：从环境变量或 `.env.local` 读取 `AUTOTEST_AUTH_USER_JSON`，自动注入 localStorage 登录态，录制结束后临时文件自动删除；需要先确保 `.env.local` 中已配置该字段
- `--output` 只接受文件名，不支持路径

### VS Code 中一键启动录制

仓库 `.vscode/launch.json` 已新增调试配置：`Record: Playwright Codegen`。

使用方式：

1. 打开“运行和调试”面板
2. 选择 `Record: Playwright Codegen`
3. 点击运行，关闭录制浏览器窗口即可结束

## 项目结构

```
autotest/
├── config/
│   └── config.py              # 全局配置（BASE_URL, TIMEOUT, HEADLESS, 认证环境变量名）
├── fixtures/
│   ├── page_factory.py        # 通用 page/tracing 创建逻辑
│   ├── business_auth.py       # 业务专用认证 fixtures
│   └── aixmy_fixtures.py      # Aixmy 专用 fixtures（end_class 后置下课）
├── pages/
│   ├── base_page.py           # BasePage（继承 8 个 Mixin）
│   ├── frame_context.py       # FrameContext iframe 代理
│   ├── mixins/                # 功能 Mixin 模块
│   │   ├── locator_mixin.py   # 元素定位
│   │   ├── action_mixin.py    # 基础操作（点击、填充、获取文本等）
│   │   ├── select_mixin.py    # 下拉选择
│   │   ├── file_mixin.py      # 文件上传
│   │   ├── window_mixin.py    # 多窗口管理
│   │   ├── navigation_mixin.py # 页面导航
│   │   ├── dialog_mixin.py    # 弹窗处理
│   │   └── drag_mixin.py      # 拖拽操作
│   ├── common/                # 通用页面对象
│   │   └── login/
│   └── modules/               # 业务模块页面对象
├── tests/                     # 测试用例（镜像 pages/modules 结构）
├── utils/
│   ├── assertion.py           # 断言工具类
│   ├── element.py             # 元素定位配置类
│   ├── logger.py              # 日志工具
│   ├── data_loader.py         # YAML 数据加载器
│   ├── exception_handler.py   # 异常处理装饰器
│   ├── http_client.py         # HTTP 客户端（标准库 urllib，无额外依赖）
│   └── time_utils.py          # 时间工具
├── test_data/                 # YAML 测试数据 + auth_state*.json
├── .env.local.example         # 本地认证配置模板（不提交真实值）
├── conftest.py                # 根层通用 Pytest fixtures
├── pytest.ini                 # Pytest 配置
└── README.md
```

## 核心概念

### 1. BasePage 与 Mixin

所有页面对象继承自 `BasePage`，自动获得 8 个 Mixin 的能力：

```python
from pages.base_page import BasePage

class LoginPage(BasePage):
    def __init__(self, page):
        super().__init__(page)

    def login(self, username, password):
        self.fill(self.INPUT_USERNAME, username)
        self.fill(self.INPUT_PASSWORD, password)
        self.click(self.BTN_LOGIN)
```

### 2. Element 定位器

使用 `Element` 类定义元素定位器：

```python
from utils.element import Element

class LoginPage(BasePage):
    INPUT_USERNAME = Element(by="css", value="#username", desc="用户名输入框")
    BTN_LOGIN = Element(by="role", value=("button", "登录"), desc="登录按钮")
```

支持的定位方式：`role`, `text`, `placeholder`, `label`, `testid`, `css`, `xpath`, `title`, `alt_text`

### 3. 统一断言

**必须使用** `Assertion` 类，禁止使用原生 `assert`：

```python
from utils.assertion import Assertion

assertion = Assertion()
assertion.assert_has_text(login_page, login_page.LOGIN_SUCCESS, "登录成功", "验证登录成功提示")
assertion.assert_is_display(login_page, login_page.LOGIN_BUTTON, "验证登录按钮可见")
```

### 4. 测试数据加载

使用 `DataLoader` 加载 YAML 测试数据：

```python
from utils.data_loader import DataLoader

data = DataLoader.get_test_data("login/login_data.yaml", "valid_user")
username = data["username"]
```

### 5. Fixture 选择

- **无需登录**：`def test_foo(self, page: Page):`
- **业务模块需要登录**：`def test_foo(self, authenticated_page: Page):`
- **进入课堂需要后置下课**：额外声明 `end_class`，进入课堂后调用 `end_class(aixmy_page)` 注册

说明：

- 根层 `[conftest.py](./conftest.py)` 只提供与业务无关的通用 fixture。
- `authenticated_page` / `authenticated_state` 是业务专用 fixture，定义在 `[fixtures/business_auth.py](./fixtures/business_auth.py)`。
- `end_class` 定义在 `fixtures/aixmy_fixtures.py`，测试结束后（无论成功/失败）自动调用下课接口，确保课堂关闭。
- 目前由 `[tests/conftest.py](./tests/conftest.py)` 统一导入，因此 `tests/` 下的测试都可以按需使用上述 fixture。
- 登录状态会保存到 `test_data/auth_state.json`（或 xdist worker 隔离文件）并复用。
- 当缓存 state 不存在、已过期，或启用了在线校验且校验失败时，框架会读取环境变量或本地 `.env.local` / `.env.auth.local` 中的 `AUTOTEST_AUTH_USERNAME` / `AUTOTEST_AUTH_PASSWORD` 重新登录。
- 如果你在 VS Code 测试资源管理器中执行用例，推荐在仓库根目录创建未提交的 `.env.local`，框架和 VS Code 都会优先读取它。
- 可选环境变量：
  - `AUTOTEST_AUTH_TTL_SECONDS`：登录态缓存有效期，默认 `3600`
  - `AUTOTEST_AUTH_VALIDATE`：设置为 `1/true/yes/on` 时启用在线校验

示例：

```bash
cp .env.local.example .env.local
# 编辑 .env.local，填入真实账号
pytest tests/mar/test_mar.py -v
```

### 6. API 后置处理（end_class）

对于需要进入课堂的用例，使用 `end_class` fixture 确保测试结束后自动调用下课接口：

```python
def test_foo(self, authenticated_page: Page, end_class):
    aixmy_page = AixmyPage(authenticated_page)
    aixmy_page.open()
    aixmy_page.launch_courseware()
    end_class(aixmy_page)  # 注册，测试结束后自动下课
    # ... 测试逻辑 ...
```

- `roomKey` 在 `launch_courseware` 期间从网络响应自动捕获
- token 优先级：`AUTOTEST_AUTH_USER_JSON` env → 请求头拦截 → localStorage
- 测试失败时同样会执行下课，不会遗留未关闭的课堂

### 7. Allure 装饰器

```python
import allure

@allure.feature("登录模块")
class TestLogin:
    @allure.story("成功登录")
    @allure.title("使用有效凭证登录")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_success(self, page: Page):
        pass
```

## 添加新功能模块

假设要添加 "reports" 模块：

1. 创建页面对象：`pages/modules/reports/reports_page.py`
2. 创建测试用例：`tests/reports/test_reports.py`
3. 创建测试数据（可选）：`test_data/reports/reports_data.yaml`

## 配置

编辑 `config/config.py` 修改全局配置：

```python
BASE_URL = "http://101.200.193.143/"
TIMEOUT = 30000
HEADLESS = True

AUTH_USERNAME_ENV = "AUTOTEST_AUTH_USERNAME"
AUTH_PASSWORD_ENV = "AUTOTEST_AUTH_PASSWORD"
AUTH_STATE_TTL_SECONDS = 3600
```

## 常见问题

**Q: 如何重置登录状态？**
A: 删除 `test_data/auth_state.json` 文件

**Q: 在 VS Code 测试资源管理器里怎么跑业务用例？**
A: 复制 `.env.local.example` 为 `.env.local` 并填写真实账号；仓库中的 `.vscode/settings.json` 已配置 `python.envFile=${workspaceFolder}/.env.local`

**Q: 为什么 `tests/test/` 里的用例跑不通？**
A: 这组用例依赖 Sahi Demo 站点，当前默认 `BASE_URL` 是业务站点；运行前先切换 `config/config.py` 中的 `BASE_URL`

**Q: 如何查看测试追踪？**
A: 使用 `pytest --trace-mode=retain-on-failure`，失败时会保存追踪文件

**Q: 如何并行运行测试？**
A: 安装 `pytest-xdist` 后可使用 `pytest -n auto`；业务登录态会自动按 worker 生成 `auth_state_<worker>.json`

## 技术栈

- **Python 3.9+**
- **Playwright** - 浏览器自动化
- **Pytest** - 测试框架
- **Allure** - 测试报告
- **PyYAML** - 数据驱动

## License

MIT