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
│   ├── common/
│   │   ├── login/login_page.py
│   │   └── uploadfile/upload_page.py
│   └── modules/                  # Feature modules (mar, blood, etc.)
├── tests/                        # Test cases (mirrors pages/modules structure)
├── utils/
│   ├── assertion.py              # Assertion class
│   ├── element.py                # Element locator config class
│   ├── logger.py                 # Logger utility
│   ├── data_loader.py            # YAML test data loader
│   ├── exception_handler.py      # Exception handler decorator
│   └── time_utils.py             # Time utilities
├── test_data/                    # YAML test data + auth_state.json
├── conftest.py                   # Fixtures (page, authenticated_page)
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
- `assert_equal` / `assert_not_equal`
- `assert_contains` / `assert_not_contains`
- `assert_true` / `assert_false`
- `assert_greater` / `assert_less`
- `assert_in`
- `assert_is_display(page, selector, message)` / `assert_not_display`
- `assert_is_checked(page, selector, message)` / `assert_is_unchecked`

**2. Choose Correct Page Fixture**
- Tests WITHOUT login: `def test_foo(self, page: Page):`
- Tests WITH login: `def test_foo(self, authenticated_page: Page):`

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

### 🟡 Important Patterns

**5. Use `Element` Class for Locators**

`Element` is the preferred way to define locators in page objects:
```python
from utils.element import Element

# Basic usage
BTN_SUBMIT = Element(by="role", value="button", desc="Submit button")

# With options
ROW_ITEM = Element(by="role", value="row", desc="Table row", nth=0)
LAST_ROW  = Element(by="role", value="row", desc="Last row", last=True)
FILTERED  = Element(by="role", value="row", desc="Row with name",
                    filter_params={"has_text": "John"})
```

Supported `by` values: `role`, `text`, `placeholder`, `label`, `testid`, `css`, `xpath`, `title`, `alt_text`

Locator priority (timeout): method arg > `Element.timeout` > `BasePage.timeout`

**6. BasePage Mixin Methods Reference**

`ActionMixin`:
- `navigate(url, wait_until)` — navigate to URL
- `click(locator, timeout)` — click element
- `fill(locator, text, timeout)` — fill input
- `get_text(locator)` — get element text
- `is_visible(locator)` — check visibility
- `wait_for_selector(locator)` — wait for element
- `double_click()`, `right_click()` — special clicks
- `get_attribute()`, `get_input_value()` — get values
- `is_checked()`, `check()`, `uncheck()` — checkbox ops
- `hover()`, `hover_and_wait()` — hover ops

`SelectMixin`:
- `select_option(locator, value/label/index)` — native `<select>`
- `click_select_option(trigger, option, text)` — custom dropdown

Other Mixins: `FileMixin` (upload), `WindowMixin` (multi-window), `NavigationMixin`, `IframeMixin`, `DialogMixin`, `DragMixin`

**7. Load Test Data via DataLoader**
```python
from utils.data_loader import DataLoader
# Path is relative to test_data/ directory
data = DataLoader.get_test_data("login/login_data.yaml", "valid_user")
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
pytest                                    # Run all tests
pytest tests/login/test_login.py          # Run specific file
pytest --browser firefox                  # Use different browser
pytest --trace-mode=retain-on-failure     # Save trace on failure
allure serve allure-results               # View test report
```

**Authentication State**
- Login state saved to: `test_data/auth_state.json`
- Reset login: Delete `auth_state.json`
- First run: Login executes once and saves state; subsequent runs load it automatically
- conftest handles expiry check and online validation automatically
