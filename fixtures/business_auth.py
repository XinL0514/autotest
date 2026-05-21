import json
import os
from functools import lru_cache
from pathlib import Path

import pytest
from playwright.sync_api import BrowserContext

from config.config import AUTH_USER_JSON_ENV
from fixtures.page_factory import create_page_from_existing_context_with_tracing
from utils.logger import Logger


logger = Logger.get_logger("BusinessAuth")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOCAL_ENV_FILES = (
    PROJECT_ROOT / ".env.auth.local",
    PROJECT_ROOT / ".env.local",
)


@lru_cache(maxsize=1)
def _load_local_env_values() -> dict[str, str]:
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
    value = os.getenv(env_name)
    if value:
        return value
    return _load_local_env_values().get(env_name)


def _get_user_json() -> str | None:
    return _get_auth_value(AUTH_USER_JSON_ENV)


def _inject_token(context: BrowserContext, user_json: str) -> None:
    from config.config import BASE_URL
    page = context.new_page()
    try:
        page.goto("https://aixmy.miaobi.cn")
        page.evaluate("(json) => localStorage.setItem('user', json)", user_json)
        page.goto(BASE_URL)
        logger.info("token injected via localStorage")
    finally:
        page.close()


def _is_logged_in(context: BrowserContext) -> bool:
    from config.config import BASE_URL
    from pages.common.login.login_page import LoginPage
    page = context.new_page()
    try:
        page.goto(BASE_URL)
        LoginPage(page).wait_until_logged_in(timeout=8000)
        return True
    except Exception:
        return False
    finally:
        page.close()


def _fetch_user_json_from_page(context: BrowserContext) -> str | None:
    """登录后从 localStorage 读取 user 对象 JSON。"""
    from config.config import BASE_URL
    page = context.new_page()
    try:
        page.goto(BASE_URL)
        user_json = page.evaluate("() => localStorage.getItem('user')")
        return user_json
    except Exception:
        return None
    finally:
        page.close()


def _update_env_local_user_json(user_json: str) -> None:
    """将新 token 写回第一个存在的本地 env 文件的 AUTOTEST_AUTH_USER_JSON 行。"""
    target = next((p for p in LOCAL_ENV_FILES if p.exists()), None)
    if not target:
        logger.warning("no local env file found, skipping AUTOTEST_AUTH_USER_JSON update")
        return

    lines = target.read_text(encoding="utf-8").splitlines()
    new_line = f"AUTOTEST_AUTH_USER_JSON={user_json}"
    updated = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("export "):
            stripped = stripped[7:].strip()
        if stripped.startswith("AUTOTEST_AUTH_USER_JSON"):
            lines[i] = new_line
            updated = True
            break

    if not updated:
        lines.append(new_line)

    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    _load_local_env_values.cache_clear()
    logger.info(f"AUTOTEST_AUTH_USER_JSON updated in {target.name}")


def _login_with_credentials(context: BrowserContext) -> None:
    from pages.common.login.login_page import LoginPage
    from utils.data_loader import DataLoader
    data = DataLoader.get_test_data("login/login_data.yaml", "aixmy_login_test")
    page = context.new_page()
    try:
        login_page = LoginPage(page)
        login_page.open()
        login_page.login(employee_id=data["employee_id"], password=data["password"])
        login_page.wait_until_logged_in(timeout=15000)
        logger.info("fallback login via UI succeeded")
    finally:
        page.close()

    user_json = _fetch_user_json_from_page(context)
    if user_json:
        _update_env_local_user_json(user_json)
    else:
        logger.warning("could not read user JSON from localStorage after login")


@pytest.fixture(scope="session")
def authenticated_state(browser_type, browser_type_launch_args, browser_context_args) -> BrowserContext:
    logger.info("\n" + "=" * 60)
    logger.info("Business auth profile check start")
    logger.info("=" * 60)

    context = browser_type.launch(**browser_type_launch_args).new_context(**browser_context_args)
    try:
        user_json = _get_user_json()
        if user_json:
            try:
                json.loads(user_json)
            except json.JSONDecodeError as e:
                raise RuntimeError(f"AUTOTEST_AUTH_USER_JSON 不是合法 JSON: {e}") from e

            _inject_token(context, user_json)

            if not _is_logged_in(context):
                logger.warning("token injection failed or token expired, falling back to UI login")
                _login_with_credentials(context)
        else:
            logger.info("AUTOTEST_AUTH_USER_JSON not set, using UI login")
            _login_with_credentials(context)

        logger.info("=" * 60 + "\n")
        yield context
    finally:
        context.close()


@pytest.fixture(scope="function")
def authenticated_page(authenticated_state: BrowserContext, request):
    yield from create_page_from_existing_context_with_tracing(authenticated_state, request)
