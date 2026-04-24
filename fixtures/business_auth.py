import os
import time
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import pytest
from playwright.sync_api import Browser, BrowserContext

from config.config import (
    AUTH_PASSWORD_ENV,
    AUTH_STATE_TTL_SECONDS,
    AUTH_USERNAME_ENV,
    ENABLE_AUTH_VALIDATION,
)
from fixtures.page_factory import create_page_with_tracing
from pages.common.login.login_page import LoginPage
from utils.logger import Logger


logger = Logger.get_logger("BusinessAuth")

STORAGE_STATE_DIR = Path(__file__).resolve().parent.parent / "test_data"
PROJECT_ROOT = STORAGE_STATE_DIR.parent
LOCAL_ENV_FILES = (
    PROJECT_ROOT / ".env.auth.local",
    PROJECT_ROOT / ".env.local",
)


@dataclass(frozen=True)
class AuthConfig:
    """Business auth credentials sourced from environment variables."""

    username: str
    password: str


@lru_cache(maxsize=1)
def _load_local_env_values() -> dict[str, str]:
    """Load auth-related env values from local untracked env files."""
    env_values: dict[str, str] = {}

    for file_path in LOCAL_ENV_FILES:
        if not file_path.exists():
            continue

        for raw_line in file_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[7:].strip()
            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if value and value[0] == value[-1] and value[0] in {'"', "'"}:
                value = value[1:-1]

            env_values[key] = value

    return env_values


def _get_auth_value(env_name: str) -> str | None:
    """Resolve auth config from process env first, then local env files."""
    value = os.getenv(env_name)
    if value:
        return value
    return _load_local_env_values().get(env_name)


def get_auth_config() -> AuthConfig:
    """Load business auth credentials from process env or local env files."""
    username = _get_auth_value(AUTH_USERNAME_ENV)
    password = _get_auth_value(AUTH_PASSWORD_ENV)

    if not username or not password:
        searched_files = ", ".join(str(path.name) for path in LOCAL_ENV_FILES)
        raise RuntimeError(
            "缺少业务认证账号，请设置环境变量或本地 env 文件: "
            f"{AUTH_USERNAME_ENV} / {AUTH_PASSWORD_ENV}；"
            f"已查找文件: {searched_files}"
        )

    return AuthConfig(username=username, password=password)


def _get_storage_state_path() -> Path:
    """Return the auth state path, isolating by xdist worker when needed."""
    worker_id = os.environ.get("PYTEST_XDIST_WORKER")
    filename = f"auth_state_{worker_id}.json" if worker_id else "auth_state.json"
    return STORAGE_STATE_DIR / filename


def _get_temp_storage_state_path(target_path: Path) -> Path:
    """Build a temp auth state path next to the final target file."""
    return target_path.with_suffix(f".tmp{target_path.suffix}")


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


def _is_auth_state_valid(browser: Browser, storage_state_path: Path) -> bool:
    """Validate a saved auth state by using the business login page object."""
    if not storage_state_path.exists():
        logger.info(f"auth state file missing: {storage_state_path}")
        return False

    context = None
    try:
        logger.info(f"validating business auth state: {storage_state_path}")
        context = browser.new_context(storage_state=str(storage_state_path))
        page = context.new_page()
        login_page = LoginPage(page)
        login_page.open()
        login_page.wait_until_logged_in(timeout=10000)
        logger.info("business auth state is valid")
        return True
    except Exception as error:
        logger.warning(f"auth state validation failed: {error}")
        return False
    finally:
        if context:
            context.close()


def _write_storage_state_to_temp(context: BrowserContext, storage_state_path: Path) -> Path:
    """Write a new auth state to a temp file before promotion."""
    STORAGE_STATE_DIR.mkdir(parents=True, exist_ok=True)
    temp_path = _get_temp_storage_state_path(storage_state_path)
    if temp_path.exists():
        temp_path.unlink()

    context.storage_state(path=str(temp_path))
    if not temp_path.exists():
        raise RuntimeError(f"auth state 临时文件写入失败: {temp_path}")

    return temp_path


def _promote_storage_state(temp_path: Path, target_path: Path) -> Path:
    """Atomically replace the current auth state with the new temp file."""
    STORAGE_STATE_DIR.mkdir(parents=True, exist_ok=True)
    temp_path.replace(target_path)
    return target_path


def _perform_login(browser: Browser, auth_config: AuthConfig) -> Path:
    """Perform business login and persist a new storage state to a temp file."""
    logger.info("Starting business login flow...")

    storage_state_path = _get_storage_state_path()
    context = browser.new_context()
    page = context.new_page()

    try:
        login_page = LoginPage(page)

        logger.info("opening login page...")
        login_page.open()

        logger.info("submitting business login credentials...")
        login_page.login(auth_config.username, auth_config.password)
        login_page.wait_until_logged_in(timeout=10000)
        logger.info("login completed")

        logger.info("collecting auth state...")
        state = _collect_auth_state(context)
        cookies = state.get("cookies", [])
        origins = state.get("origins", [])
        logger.info(f"cookies count: {len(cookies)}")
        logger.info(f"origins count: {len(origins)}")

        if len(cookies) == 0 and len(origins) == 0:
            screenshot_path = STORAGE_STATE_DIR / "login_debug.png"
            page.screenshot(path=str(screenshot_path))
            raise RuntimeError(
                "No auth state detected after login "
                f"(cookies/origins both empty). Current URL: {page.url}, "
                f"debug screenshot: {screenshot_path}"
            )

        temp_path = _write_storage_state_to_temp(context, storage_state_path)
        logger.info(f"new auth state saved to temp file: {temp_path}")
        return temp_path
    except Exception as error:
        logger.error(f"business login failed: {error}")
        screenshot_path = STORAGE_STATE_DIR / "login_error.png"
        page.screenshot(path=str(screenshot_path))
        logger.info(f"Saved error screenshot: {screenshot_path}")
        raise
    finally:
        context.close()


@pytest.fixture(scope="session")
def authenticated_state(browser: Browser) -> Path:
    """Business-only authenticated storage state."""
    logger.info("\n" + "=" * 60)
    logger.info("Business auth state check start")
    logger.info("=" * 60)

    storage_state_path = _get_storage_state_path()
    need_refresh = False

    if not storage_state_path.exists():
        logger.info("auth state file missing, login required")
        need_refresh = True
    elif time.time() - storage_state_path.stat().st_mtime > AUTH_STATE_TTL_SECONDS:
        elapsed_hours = (time.time() - storage_state_path.stat().st_mtime) / 3600
        logger.info(
            "auth state expired "
            f"({elapsed_hours:.1f}h old, ttl {AUTH_STATE_TTL_SECONDS / 3600:.1f}h)"
        )
        need_refresh = True
    elif ENABLE_AUTH_VALIDATION:
        logger.info("online auth validation enabled")
        if not _is_auth_state_valid(browser, storage_state_path):
            logger.info("auth state invalid, relogin required")
            need_refresh = True
        else:
            file_age_minutes = (time.time() - storage_state_path.stat().st_mtime) / 60
            logger.info(f"using valid auth state ({file_age_minutes:.1f} min old)")
    else:
        file_age_minutes = (time.time() - storage_state_path.stat().st_mtime) / 60
        logger.info(f"using cached auth state ({file_age_minutes:.1f} min old)")
        logger.info("skipped online auth validation")

    if need_refresh:
        logger.info("Refreshing business auth state...")
        auth_config = get_auth_config()
        temp_state_path = _perform_login(browser, auth_config)
        try:
            if ENABLE_AUTH_VALIDATION:
                logger.info("validating refreshed auth state before activation...")
                if not _is_auth_state_valid(browser, temp_state_path):
                    raise RuntimeError(f"新生成的 auth state 校验失败: {temp_state_path}")
                logger.info("refreshed auth state validation passed")

            result = _promote_storage_state(temp_state_path, storage_state_path)
            logger.info(f"auth state activated: {result}")
            logger.info("=" * 60)
            return result
        except Exception as error:
            if temp_state_path.exists():
                temp_state_path.unlink()

            if storage_state_path.exists():
                logger.warning(f"existing auth state preserved: {storage_state_path}")

            raise RuntimeError("刷新 business auth state 失败") from error

    logger.info("=" * 60 + "\n")
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
