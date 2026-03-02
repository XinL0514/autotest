# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Web UI automation framework using Python + Playwright + Pytest with Page Object Model (POM) pattern.

- **Base URL**: `https://sahitest.com/demo/index.htm`
- **Browser**: Chromium (headed mode by default)
- **Timeout**: 30000ms
- **Reports**: Allure

## Directory Structure

```
autotest/
├── config/config.py              # Global config (BASE_URL, TIMEOUT, HEADLESS)
├── pages/
│   ├── base_page.py              # BasePage (inherits 9 Mixins)
│   ├── mixins/                   # LocatorMixin, ActionMixin, SelectMixin, FileMixin,
│   │                             # WindowMixin, NavigationMixin, IframeMixin, DialogMixin, DragMixin
│   ├── common/                   # Shared page objects (login, upload)
│   │   ├── login/login_page.py
│   │   └── uploadfile/upload_page.py
│   └── modules/                  # Feature modules (mar, blood, test)
├── tests/                        # Test cases (mirrors pages/modules structure)
├── utils/
│   ├── assertion.py              # Assertion class
│   ├── element.py                # Element locator config class
│   ├── logger.py                 # Logger utility
│   ├── data_loader.py            # YAML test data loader
│   ├── exception_handler.py      # Exception handler decorator
│   └── time_utils.py             # Time utilities
├── test_data/                    # YAML test data + auth_state.json
├── conftest.py                   # Fixtures (page, authenticated_page, authenticated_state)
└── pytest.ini                    # Pytest options
```

## Core Conventions

### 🔴 Critical Rules (Must Follow)

**1. Always Use `Assertion` Class — Never use native `assert`**
```python
from utils.assertion import Assertion
assertion = Assertion()
assertion.assert_equal(actual, expected, "Verify login success")
```

Available assertion methods:
- `assert_equal(actual, expected, message)` / `assert_not_equal`
- `assert_contains(actual, expected, message)` / `assert_not_contains`
- `assert_true(condition, message)` / `assert_false`
- `assert_greater(actual, expected, message)` / `assert_less`
- `assert_in(item, items, message)`
- `assert_is_display(page, selector, message)` / `assert_not_display`
- `assert_is_checked(page, selector, message)` / `assert_is_unchecked`

**2. Choose Correct Page Fixture**
- Tests WITHOUT login: `def test_foo(self, page: Page):`
- Tests WITH login: `def test_foo(self, authenticated_page: Page):`

The `authenticated_page` fixture automatically handles login state management via `authenticated_state` session fixture.

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

**5. Use `Element` Class for Locators**

`Element` is the preferred way to define locators in page objects:
```python
from utils.element import Element

# Basic usage - supports both positional and keyword arguments
BTN_SUBMIT = Element("role", ("button",), desc="Submit button")
BTN_LOGIN = Element("role", ("button", "登录"), desc="Login button")

# Or use keyword arguments (more explicit)
BTN_SUBMIT = Element(by="role", value=("button",), desc="Submit button")

# CSS/XPath - string format
INPUT_NAME = Element("css", "#username", desc="Username input")
XPATH_ELEM = Element("xpath", "//div[@class='content']", desc="Content div")

# Text/placeholder - string format
USERNAME = Element("placeholder", "请输入用户名", desc="Username", exact=True)

# With filter_params
ROW_ITEM = Element("role", ("row",), desc="Table row",
                   filter_params={"has_text": "John"})

# With nth/first/last
FIRST_ROW = Element("role", ("row",), desc="First row", nth=0)
LAST_ROW  = Element("role", ("row",), desc="Last row", last=True)

# With custom timeout
SLOW_ELEM = Element("css", ".loading", desc="Loading", timeout=60000)
```

Supported `by` values: `role`, `text`, `placeholder`, `label`, `testid`, `css`, `xpath`, `title`, `alt_text`

Locator timeout priority: method arg > `Element.timeout` > `BasePage.timeout`

**6. BasePage Mixin Methods Reference**

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

Other Mixins: `FileMixin` (upload), `WindowMixin` (multi-window), `NavigationMixin`, `IframeMixin`, `DialogMixin`, `DragMixin`

**7. Load Test Data via DataLoader**
```python
from utils.data_loader import DataLoader
# Path is relative to test_data/ directory
data = DataLoader.get_test_data("login/login_data.yaml", "valid_user")
username = data["username"]
```

**8. Initialize Logger per Class**
```python
from utils.logger import Logger
self.logger = Logger.get_logger(self.__class__.__name__)
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
pytest --headed                           # Override config.HEADLESS
pytest                                    # Use config.HEADLESS setting

# Trace mode (for debugging)
pytest --trace-mode=on                    # Save trace for all tests
pytest --trace-mode=retain-on-failure     # Save trace only on failure
pytest --trace-mode=off                   # No trace (default)

# Generate and view Allure report
pytest --alluredir=allure-results
allure serve allure-results
```

**Authentication State Management**
- Login state saved to: `test_data/auth_state.json`
- Reset login: Delete `auth_state.json`
- First run: Login executes once and saves state; subsequent runs reuse it
- Auto-refresh: State expires after 1 hour (configurable via `AUTH_STATE_EXPIRY` in conftest.py)
- Online validation: Disabled by default (set `ENABLE_AUTH_VALIDATION=True` to enable)
- Parallel testing: xdist workers get isolated auth state files (`auth_state_worker_*.json`)

**conftest.py Configuration**
Key settings in conftest.py:
- `AUTH_STATE_EXPIRY = 60 * 60` — Auth state validity (1 hour)
- `ENABLE_AUTH_VALIDATION = False` — Online validation toggle
- `LOGIN_SUCCESS_SELECTOR = "button:has-text('用药记录')"` — Element to verify login
- `TRACE_DIR = Path(__file__).parent / "test-results"` — Trace file location

**Fixtures Available**
- `page` — Clean browser page without login
- `authenticated_page` — Browser page with login state loaded
- `authenticated_state` — Session-level fixture that manages login state
- `browser_context_args` — Viewport config (1920x1080)
- `browser_type_launch_args` — Browser launch args (headless mode)