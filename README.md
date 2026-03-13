# Web UI Automation Framework

基于 Python + Playwright + Pytest 的 Web UI 自动化测试框架，采用 Page Object Model (POM) 设计模式。

## 特性

- ✅ **Page Object Model** - 清晰的页面对象分层设计
- ✅ **Mixin 架构** - 9 个功能 Mixin 提供可复用的操作能力
- ✅ **统一断言** - 自定义 Assertion 类，支持丰富的断言方法
- ✅ **Element 定位器** - 类型安全的元素定位配置
- ✅ **登录状态管理** - 自动保存和复用认证状态
- ✅ **YAML 数据驱动** - 测试数据与代码分离
- ✅ **Allure 报告** - 美观的测试报告
- ✅ **异常处理** - 统一的异常捕获和日志记录

## 快速开始

### 环境要求

- Python 3.8+
- pip

### 安装依赖

```bash
pip install -r requirements.txt
playwright install chromium
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行指定模块
pytest tests/login/test_login.py

# 使用不同浏览器
pytest --browser firefox

# 失败时保留追踪
pytest --trace-mode=retain-on-failure

# 生成并查看 Allure 报告
pytest --alluredir=allure-results
allure serve allure-results
```

## 项目结构

```
autotest/
├── config/
│   └── config.py              # 全局配置（BASE_URL, TIMEOUT, HEADLESS）
├── pages/
│   ├── base_page.py           # BasePage（继承 9 个 Mixin）
│   ├── mixins/                # 功能 Mixin 模块
│   │   ├── locator_mixin.py   # 元素定位
│   │   ├── action_mixin.py    # 基础操作（点击、填充、获取文本等）
│   │   ├── select_mixin.py    # 下拉选择
│   │   ├── file_mixin.py      # 文件上传
│   │   ├── window_mixin.py    # 多窗口管理
│   │   ├── navigation_mixin.py # 页面导航
│   │   ├── iframe_mixin.py    # iframe 操作
│   │   ├── dialog_mixin.py    # 弹窗处理
│   │   └── drag_mixin.py      # 拖拽操作
│   ├── common/                # 通用页面对象
│   │   ├── login/
│   │   └── uploadfile/
│   └── modules/               # 业务模块页面对象
├── tests/                     # 测试用例（镜像 pages/modules 结构）
├── utils/
│   ├── assertion.py           # 断言工具类
│   ├── element.py             # 元素定位配置类
│   ├── logger.py              # 日志工具
│   ├── data_loader.py         # YAML 数据加载器
│   ├── exception_handler.py   # 异常处理装饰器
│   └── time_utils.py          # 时间工具
├── test_data/                 # YAML 测试数据 + auth_state.json
├── conftest.py                # Pytest fixtures
├── pytest.ini                 # Pytest 配置
└── README.md
```

## 核心概念

### 1. BasePage 与 Mixin111

所有页面对象继承自 `BasePage`，自动获得 9 个 Mixin 的能力：

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
    BTN_LOGIN = Element(by="role", value="button", desc="登录按钮", filter_params={"name": "Login"})
```

支持的定位方式：`role`, `text`, `placeholder`, `label`, `testid`, `css`, `xpath`, `title`, `alt_text`

### 3. 统一断言

**必须使用** `Assertion` 类，禁止使用原生 `assert`：

```python
from utils.assertion import Assertion

assertion = Assertion()
assertion.assert_equal(actual, expected, "验证登录成功")
assertion.assert_is_display(page, selector, "验证元素可见")
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
- **需要登录**：`def test_foo(self, authenticated_page: Page):`

登录状态自动保存到 `test_data/auth_state.json`，后续测试自动复用。

### 6. Allure 装饰器

```python
import allure

@allure.feature("登录模块")
class TestLogin:
    @allure.story("成功登录")
    @allure.title("使用有效凭证登录")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_success(self, authenticated_page: Page):
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
BASE_URL = "https://sahitest.com/demo/index.htm"
TIMEOUT = 30000  # 毫秒
HEADLESS = False  # True 为无头模式
```

## 常见问题

**Q: 如何重置登录状态？**
A: 删除 `test_data/auth_state.json` 文件

**Q: 如何查看测试追踪？**
A: 使用 `pytest --trace-mode=retain-on-failure`，失败时会保存追踪文件

**Q: 如何并行运行测试？**
A: 安装 `pytest-xdist`，使用 `pytest -n auto`

## 技术栈

- **Python 3.8+**
- **Playwright** - 浏览器自动化
- **Pytest** - 测试框架
- **Allure** - 测试报告
- **PyYAML** - 数据驱动

## License

MIT
