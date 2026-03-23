import os
import time
from pathlib import Path

import pytest
from playwright.sync_api import Browser, BrowserContext

from fixtures.page_factory import create_page_with_tracing
from pages.common.login.login_page import LoginPage
from utils.data_loader import DataLoader


STORAGE_STATE_DIR = Path(__file__).resolve().parent.parent / "test_data"
AUTH_STATE_EXPIRY = 60 * 60  # 1 hour
ENABLE_AUTH_VALIDATION = False


def _get_storage_state_path() -> Path:
    """Return the auth state path, isolating by xdist worker when needed."""
    worker_id = os.environ.get("PYTEST_XDIST_WORKER")
    filename = f"auth_state_{worker_id}.json" if worker_id else "auth_state.json"
    return STORAGE_STATE_DIR / filename


def _collect_auth_state(
    context: BrowserContext,
    timeout_seconds: float = 3.0,
    poll_interval: float = 0.2,
) -> dict:
    """Poll storage_state briefly to tolerate async cookie/localStorage writes."""
    deadline = time.time() + timeout_seconds
    state = context.storage_state()
    while time.time() < deadline:
        if state.get("cookies") or state.get("origins"):
            return state
        time.sleep(poll_interval)
        state = context.storage_state()
    return state


def _is_auth_state_valid(browser: Browser) -> bool:
    """Validate saved auth state by using the business login page object."""
    storage_state_path = _get_storage_state_path()
    if not storage_state_path.exists():
        print("INFO auth state file missing")
        return False

    context = None
    try:
        print("INFO validating business auth state...")
        context = browser.new_context(storage_state=str(storage_state_path))
        page = context.new_page()
        login_page = LoginPage(page)
        login_page.open()
        login_page.wait_until_logged_in(timeout=10000)
        print("OK business auth state is valid")
        return True
    except Exception as error:
        print(f"WARN auth state validation failed: {error}")
        return False
    finally:
        if context:
            context.close()


def _perform_login(browser: Browser) -> Path:
    """Perform business login and persist storage state for reuse."""
    print("\nStarting business login flow...")

    storage_state_path = _get_storage_state_path()
    context = browser.new_context()
    page = context.new_page()

    try:
        login_data = DataLoader.get_test_data("login/login_data.yaml", "valid_user")
        login_page = LoginPage(page)

        print("INFO opening login page...")
        login_page.open()

        print(f"INFO input username: {login_data['username']}")
        print(f"INFO input password: {'*' * len(login_data['password'])}")
        login_page.login(login_data["username"], login_data["password"])
        login_page.wait_until_logged_in(timeout=10000)
        print("OK login completed")

        print("INFO collecting auth state...")
        state = _collect_auth_state(context)
        cookies = state.get("cookies", [])
        origins = state.get("origins", [])
        print(f"INFO cookies count: {len(cookies)}")
        print(f"INFO origins count: {len(origins)}")

        if len(cookies) == 0 and len(origins) == 0:
            screenshot_path = STORAGE_STATE_DIR / "login_debug.png"
            page.screenshot(path=str(screenshot_path))
            raise RuntimeError(
                "No auth state detected after login "
                f"(cookies/origins both empty). Current URL: {page.url}, "
                f"debug screenshot: {screenshot_path}"
            )

        STORAGE_STATE_DIR.mkdir(parents=True, exist_ok=True)
        context.storage_state(path=str(storage_state_path))
        print(f"OK auth state saved to: {storage_state_path}")
    except Exception as error:
        print(f"ERROR business login failed: {error}")
        screenshot_path = STORAGE_STATE_DIR / "login_error.png"
        page.screenshot(path=str(screenshot_path))
        print(f"Saved error screenshot: {screenshot_path}")
        raise
    finally:
        context.close()

    return storage_state_path


@pytest.fixture(scope="session")
def authenticated_state(browser: Browser) -> Path:
    """Business-only authenticated storage state."""
    print("\n" + "=" * 60)
    print("Business auth state check start")
    print("=" * 60)

    storage_state_path = _get_storage_state_path()
    need_refresh = False

    if not storage_state_path.exists():
        print("INFO auth state file missing, login required")
        need_refresh = True
    elif time.time() - os.path.getmtime(storage_state_path) > AUTH_STATE_EXPIRY:
        elapsed_hours = (time.time() - os.path.getmtime(storage_state_path)) / 3600
        print(
            "INFO auth state expired "
            f"({elapsed_hours:.1f}h old, ttl {AUTH_STATE_EXPIRY / 3600:.1f}h)"
        )
        need_refresh = True
    elif ENABLE_AUTH_VALIDATION:
        print("INFO online auth validation enabled")
        if not _is_auth_state_valid(browser):
            print("INFO auth state invalid, relogin required")
            need_refresh = True
        else:
            file_age_minutes = (time.time() - os.path.getmtime(storage_state_path)) / 60
            print(f"OK using valid auth state ({file_age_minutes:.1f} min old)")
    else:
        file_age_minutes = (time.time() - os.path.getmtime(storage_state_path)) / 60
        print(f"OK using cached auth state ({file_age_minutes:.1f} min old)")
        print("INFO skipped online auth validation")

    if need_refresh:
        print("\nRefreshing business auth state...")
        if storage_state_path.exists():
            storage_state_path.unlink()
        result = _perform_login(browser)
        print("=" * 60)
        return result

    print("=" * 60 + "\n")
    return storage_state_path


@pytest.fixture(scope="function")
def authenticated_page(browser: Browser, authenticated_state: Path, request, browser_context_args):
    """Business-only page fixture with storage state loaded."""
    yield from create_page_with_tracing(
        browser,
        request,
        browser_context_args,
        storage_state=authenticated_state,
    )
