# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Web UI automation framework using Python + Playwright + Pytest with Page Object Model (POM) pattern.

- **Base URL**: configured in `config/config.py` (current value: `http://101.200.193.143/`)
- **Browser**: Chromium by default via `pytest-playwright`
- **Timeout**: 30000ms
- **Reports**: Allure

## Directory Structure

```
autotest/
├── config/config.py              # Global config (BASE_URL, TIMEOUT, HEADLESS)
├── fixtures/
│   ├── page_factory.py           # Shared page/tracing creation logic
│   └── business_auth.py          # Business login state fixtures
├── pages/
│   ├── base_page.py              # BasePage (inherits 8 Mixins) + frame() method
│   ├── frame_context.py          # FrameContext — iframe proxy, same API as BasePage
│   ├── mixins/                   # LocatorMixin, ActionMixin, SelectMixin, FileMixin,
│   │                             # WindowMixin, NavigationMixin, DialogMixin, DragMixin
│   ├── common/                   # Shared page objects (login)
│   │   ├── login/login_page.py
│   └── modules/                  # Feature modules (mar, blood, test)
├── tests/                        # Test cases (mirrors pages/modules structure)
│   └── conftest.py               # Exposes business auth fixtures to tests/
├── utils/
│   ├── assertion.py              # Assertion class (Playwright expect based)
│   ├── element.py                # Element locator config class
│   ├── logger.py                 # Logger utility
│   ├── data_loader.py            # YAML test data loader
│   ├── exception_handler.py      # Exception handler decorator
│   └── time_utils.py             # Time utilities
├── test_data/                    # YAML test data + auth_state.json
├── conftest.py                   # Root fixtures (page, tracing, failure attachments)
└── pytest.ini                    # Pytest discovery options
```

## Core Conventions

### 🔴 Critical Rules (Must Follow)

**1. Always Use `Assertion` Class — Never use native `assert`**

All assertions are based on Playwright `expect` and provide auto-wait, Allure steps, and detailed error output.

```python
from utils.assertion import Assertion
assertion = Assertion()
```

Available assertion methods — all follow `(page_obj, element, message)` signature:

| Method | Playwright equivalent | Use case |
|---|---|---|
| `assert_is_display(page_obj, element, message)` | `to_be_visible()` | 元素可见 |
| `assert_not_display(page_obj, element, message)` | `not_to_be_visible()` | 元素不可见 |
| `assert_is_checked(page_obj, element, message)` | `to_be_checked()` | 复选框选中 |
| `assert_is_unchecked(page_obj, element, message)` | `not_to_be_checked()` | 复选框未选中 |
| `assert_has_text(page_obj, element, text, message)` | `to_have_text()` | 文本完全匹配 |
| `assert_not_has_text(page_obj, element, text, message)` | `not_to_have_text()` | 文本不匹配 |
| `assert_contains_text(page_obj, element, text, message)` | `to_contain_text()` | 文本包含 |
| `assert_has_value(page_obj, element, value, message)` | `to_have_value()` | 输入框/select值（支持正则） |
| `assert_has_css(page_obj, element, prop, value, message)` | `to_have_css()` | CSS属性值 |
| `assert_has_class(page_obj, element, pattern, message)` | `to_have_class()` | CSS class（支持正则） |
| `assert_has_url(page, url_pattern, message)` | `to_have_url()` | 页面URL（支持正则） |
| `assert_is_display_raw(locator, message)` | `to_be_visible()` | 直接传入已解析的Locator（frame等特殊场景） |

`expect_that(locator, description)` 作为低级扩展口保留，遇到没有具名方法的断言时使用。

**2. Choose Correct Page Fixture**
- Tests WITHOUT login: `def test_foo(self, page: Page):`
- Tests WITH login: `def test_foo(self, authenticated_page: Page):`

The `authenticated_page` fixture automatically handles login state management via `authenticated_state` session fixture.
These business auth fixtures are implemented in `fixtures/business_auth.py` and imported into the test tree by `tests/conftest.py`.

**3. Follow Modular Structure** — When adding a new feature module (e.g., "reports"):
- `pages/modules/reports/reports_page.py` — Page object class
- `tests/reports/test_reports.py` — Test cases
- `test_data/reports/reports_data.yaml` — Test data (if needed)

**4. All Pages Inherit from BasePage**
```python
from pages.base_page import BasePage

class ReportsPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
```

BasePage provides `self.page`, `self.timeout`, and `self.logger` automatically.

### 🟡 Important Patterns

**5. Use `Element` Class for All Locators**

`Element` is the **only** way to define locators in page objects. Never use raw strings or tuples.

```python
from utils.element import Element

# Role locator
BTN_LOGIN = Element("role", ("button", "登录"), desc="Login button")

# CSS / XPath
INPUT_NAME = Element("css", "#username", desc="Username input")
XPATH_ELEM = Element("xpath", "//div[@class='content']", desc="Content div")

# Text / placeholder
USERNAME = Element("placeholder", "请输入用户名", desc="Username", exact=True)

# With filter_params
ROW_ITEM = Element("role", ("row",), desc="Table row", filter_params={"has_text": "John"})

# With nth / first / last
FIRST_ROW = Element("role", ("row",), desc="First row", nth=0)
LAST_ROW  = Element("role", ("row",), desc="Last row", last=True)

# With custom timeout
SLOW_ELEM = Element("css", ".loading", desc="Loading", timeout=60000)
```

Supported `by` values: `role`, `text`, `placeholder`, `label`, `testid`, `css`, `xpath`, `title`, `alt_text`

**Exception**: iframe CSS selectors passed to `page_obj.frame(css)` stay as plain strings because
they are used by Playwright's `frame_locator()`, not by the element locator system.

**6. iframe 操作 — 使用 `frame()` 代理**

`BasePage.frame(css)` 返回一个 `FrameContext`，其 API 与普通页面**完全相同**，无需维护两套方法。

```python
# 在 page object 内部
FRAME_LOCATOR = '[src="index.htm"] >> nth=0'  # iframe CSS selector（plain string）

def click_in_frame(self):
    self.frame(self.FRAME_LOCATOR).click(self.SOME_ELEMENT)

def get_text_in_frame(self):
    return self.frame(self.FRAME_LOCATOR).get_text(self.TEXT_ELEMENT)

# 需要对外暴露 frame 供测试断言时
def get_main_frame(self):
    return self.frame(self.FRAME_LOCATOR)
```

```python
# 在测试中
frame = page_obj.get_main_frame()
assertion.assert_is_display(frame, page_obj.ELEMENT, "描述")   # 与普通断言完全相同

# frame 操作完成后直接用 page_obj 回到主页面，无需任何"切换"
page_obj.click(MAIN_ELEMENT)
```

**7. BasePage Mixin Methods Reference**

`ActionMixin`:
- `navigate(url, wait_until)` — navigate to URL
- `click(locator, timeout)` — click element
- `fill(locator, text, timeout)` — fill input
- `get_text(locator, timeout)` — get element text
- `is_visible(locator, timeout)` — check visibility
- `wait_for_selector(locator, timeout)` — wait for element
- `double_click(locator, timeout)`, `right_click(locator, timeout)` — special clicks
- `get_attribute(locator, name, timeout)`, `get_input_value(locator, timeout)` — get values
- `is_checked(locator, timeout)`, `check(locator, timeout)`, `uncheck(locator, timeout)` — checkbox ops
- `hover(locator, timeout)`, `hover_and_wait(locator, wait_time, timeout)` — hover ops

`SelectMixin`:
- `select_option(locator, value/label/index, timeout)` — native `<select>`
- `click_select_option(trigger_locator, option_locator, option_text, timeout)` — custom dropdown

Other Mixins: `FileMixin` (upload), `WindowMixin` (multi-window), `NavigationMixin`, `DialogMixin`, `DragMixin`

**8. Load Test Data via DataLoader**
```python
from utils.data_loader import DataLoader
# Path is relative to test_data/ directory
data = DataLoader.get_test_data("login/login_data.yaml", "valid_user")
username = data["username"]
```

**9. Use ExceptionHandler Decorator on Page Methods**
```python
from utils.exception_handler import ExceptionHandler

@ExceptionHandler.handle_playwright_exception("操作名称", return_on_error=False, raise_assertion=True)
def some_action(self):
    ...
```

**10. Use Allure Decorators**
```python
import allure

@allure.feature("Login Module")
class TestLogin:
    @allure.story("Successful Login")
    @allure.title("Test login with valid credentials")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_success(self, authenticated_page: Page):
        pass
```

### 🟢 Quick Reference

**Common Test Commands**
```bash
# Run all tests
pytest

# Run specific file or directory
pytest tests/login/test_login.py
pytest tests/mar/

# Use different browser
pytest --browser firefox
pytest --browser webkit

# Headed/headless mode
# Default headless behavior comes from config/config.py
pytest --headed                           # headed, overrides config
pytest                                    # uses config/config.py HEADLESS fallback

# Trace mode (for debugging)
pytest --trace-mode=on                    # Save trace for all tests
pytest --trace-mode=retain-on-failure     # Save trace only on failure
pytest --trace-mode=off                   # No trace (default)

# Generate and view Allure report
pytest --alluredir=allure-results
allure serve allure-results
```

**Headed / Headless Control**
- `config/config.py HEADLESS` — default fallback for browser launch
- `pytest --headed` — explicit headed override on the command line

**Authentication State Management**
- Login state saved to: `test_data/auth_state.json`
- Reset login: Delete `auth_state.json`
- First run: Login executes once and saves state; subsequent runs reuse it
- Auto-refresh: State expires after 1 hour (configurable via `AUTH_STATE_EXPIRY` in `fixtures/business_auth.py`)
- Online validation: Disabled by default (set `ENABLE_AUTH_VALIDATION=True` to enable)
- Parallel testing: xdist workers get isolated auth state files (`auth_state_<worker>.json`)

**Fixture Configuration**
Key settings are split by responsibility:
- Root `conftest.py` — generic `page` fixture, trace attachment, screenshot attachment
- `fixtures/page_factory.py` — shared traced page creation and `TRACE_DIR`
- `fixtures/business_auth.py` — `AUTH_STATE_EXPIRY`, `ENABLE_AUTH_VALIDATION`, login-state reuse
- `pages/common/login/login_page.py` — login success marker via `HOME_READY_MARKER`

**Fixtures Available**
- `page` — Clean browser page without login
- `authenticated_page` — Business browser page with login state loaded
- `authenticated_state` — Session-level business auth-state fixture
- `browser_context_args` — Viewport config (1920x1080)
- `browser_type_launch_args` — Browser launch args (headless mode)
