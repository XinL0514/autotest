import sys
from pathlib import Path

# ========== 重要：将项目根目录添加到 Python 路径 ==========
# 这样可以在 debug 模式下直接运行测试文件，也能正确导入模块
PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import allure
import pytest
from playwright.sync_api import Browser, BrowserContext, expect
from config.config import HEADLESS, BASE_URL, TIMEOUT
import time
import os
import hashlib
from datetime import datetime

expect.set_options(timeout=TIMEOUT)


# ========== 认证状态管理配置 ==========
# Storage state 存储目录
STORAGE_STATE_DIR = Path(__file__).parent / "test_data"

# 认证状态有效期（秒），超过此时间将重新登录
# 可根据实际 token 过期时间调整，默认 1 小时
AUTH_STATE_EXPIRY = 60 * 60  # 1 hour

# 是否启用认证状态在线验证（会打开一个临时页面验证 cookies）
# True: 每次都验证（更安全，但会多打开一次页面）
# False: 只检查文件存在性和过期时间（更快，推荐）
ENABLE_AUTH_VALIDATION = False

# Trace 文件保存路径
TRACE_DIR = Path(__file__).parent / "test-results"

# 登录成功后的特征元素选择器（用于验证登录状态）
LOGIN_SUCCESS_SELECTOR = "button:has-text('用药记录')"


def _get_storage_state_path() -> Path:
    """
    获取认证状态文件路径。
    在 xdist 并行运行时按 worker 隔离，避免并发读写同一文件。
    """
    worker_id = os.environ.get("PYTEST_XDIST_WORKER")
    filename = f"auth_state_{worker_id}.json" if worker_id else "auth_state.json"
    return STORAGE_STATE_DIR / filename


def _collect_auth_state(context: BrowserContext, timeout_seconds: float = 3.0, poll_interval: float = 0.2) -> dict:
    """
    在短时间内轮询 storage_state，兼容 cookies/localStorage 异步写入场景。
    返回最后一次读取到的 storage_state。
    """
    deadline = time.time() + timeout_seconds
    state = context.storage_state()
    while time.time() < deadline:
        if state.get("cookies") or state.get("origins"):
            return state
        time.sleep(poll_interval)
        state = context.storage_state()
    return state


def pytest_addoption(parser):
    """添加自定义命令行选项"""
    parser.addoption(
        "--trace-mode",
        action="store",
        choices=["off", "on", "retain-on-failure"],
        default="off",
        help="启用 Playwright tracing: 'on' 所有测试, 'retain-on-failure' 仅失败测试保留, 'off' 禁用 (默认)"
    )


@pytest.fixture(scope="session")
def browser_type_launch_args(pytestconfig):
    """
    浏览器启动参数。
    优先遵循命令行 --headed；未指定时再回退到 config.HEADLESS。
    """
    if pytestconfig.getoption("--headed"):
        return {}
    return {"headless": HEADLESS}


@pytest.fixture(scope="session")
def browser_context_args():
    """配置浏览器上下文参数"""
    return {"viewport": {"width": 1920, "height": 1080}}


def _is_auth_state_valid(browser: Browser) -> bool:
    """
    验证保存的认证状态是否仍然有效
    通过尝试访问需要认证的页面并检查关键元素来判断
    """
    storage_state_path = _get_storage_state_path()
    if not storage_state_path.exists():
        print("ℹ 认证状态文件不存在")
        return False

    context = None
    try:
        print("ℹ 开始验证认证状态...")
        # 创建使用保存状态的临时上下文
        context = browser.new_context(storage_state=str(storage_state_path))
        page = context.new_page()

        # 访问主页
        print(f"ℹ 访问主页: {BASE_URL}")
        page.goto(BASE_URL, timeout=15000)  # 增加超时时间到 15 秒

        # 检查是否存在登录后才有的元素（如"用药记录"按钮）
        # 如果找到该元素，说明认证有效；否则可能跳转到了登录页
        try:
            print("ℹ 检查登录状态（查找'用药记录'按钮）...")
            page.wait_for_selector(LOGIN_SUCCESS_SELECTOR, timeout=10000)  # 增加超时到 10 秒
            print("✓ 认证状态有效，找到'用药记录'按钮")
            return True
        except Exception as e:
            print(f"✗ 未找到'用药记录'按钮: {e}")
            print(f"  当前 URL: {page.url}")
            return False

    except Exception as e:
        print(f"⚠ 验证认证状态失败: {e}")
        return False
    finally:
        if context:
            context.close()


def _perform_login(browser: Browser) -> Path:
    """
    执行登录并保存认证状态
    """
    print("\n🔐 执行登录流程...")

    storage_state_path = _get_storage_state_path()

    # 创建临时上下文进行登录
    context = browser.new_context()
    page = context.new_page()

    try:
        # 执行登录流程
        from pages.common.login.login_page import LoginPage
        from utils.data_loader import DataLoader

        login_data = DataLoader.get_test_data("login/login_data.yaml", "valid_user")
        login_page = LoginPage(page)

        print(f"ℹ️  访问登录页面...")
        login_page.open()

        print(f"ℹ️  输入用户名: {login_data['username']}")
        print(f"ℹ️  输入密码: {'*' * len(login_data['password'])}")
        login_page.login(login_data["username"], login_data["password"])

        login_selector_found = False
        # 等待登录成功 - 等待特定元素出现确保登录完成
        try:
            print("ℹ️  等待登录完成（查找'用药记录'按钮）...")
            page.wait_for_selector(LOGIN_SUCCESS_SELECTOR, timeout=10000)
            print("✅ 登录成功，已检测到主页元素")
            login_selector_found = True
        except Exception as e:
            print(f"⚠️  警告：未检测到登录后的主页元素: {e}")
            print(f"   当前 URL: {page.url}")
            print("   继续检查 storage_state...")

        # 保存认证状态前，收集并检查认证状态数据（cookies / origins）
        print("ℹ️  收集认证状态...")
        state = _collect_auth_state(context)
        cookies = state.get("cookies", [])
        origins = state.get("origins", [])
        print(f"ℹ️  当前 Cookies 数量: {len(cookies)}")
        print(f"ℹ️  当前 Origins 数量: {len(origins)}")

        if len(cookies) == 0 and len(origins) == 0:
            screenshot_path = STORAGE_STATE_DIR / "login_debug.png"
            page.screenshot(path=str(screenshot_path))
            raise RuntimeError(
                f"登录后未检测到可用认证状态（cookies/origins均为空）！当前 URL: {page.url}，调试截图: {screenshot_path}"
            )
        elif len(cookies) == 0 and len(origins) > 0:
            # 仅 origins 非空时，仍要求检测到登录态特征元素，避免未登录场景误通过
            if not login_selector_found:
                screenshot_path = STORAGE_STATE_DIR / "login_debug.png"
                page.screenshot(path=str(screenshot_path))
                raise RuntimeError(
                    "仅检测到 origins 但未检测到登录态特征元素，拒绝保存认证状态。"
                    f"当前 URL: {page.url}，调试截图: {screenshot_path}"
                )
            print("⚠️  未检测到 cookies，但存在 origins 且登录态特征元素可见，继续执行")
        else:
            # 显示部分 cookies 信息
            print(f"ℹ️  Cookies 示例:")
            for cookie in cookies[:3]:  # 只显示前3个
                print(f"      - {cookie.get('name')}: {cookie.get('domain')}")
            if len(cookies) > 3:
                print(f"      ... 还有 {len(cookies) - 3} 个")

        # 保存认证状态
        STORAGE_STATE_DIR.mkdir(parents=True, exist_ok=True)
        context.storage_state(path=str(storage_state_path))

        print(f"✅ 登录状态已保存到: {storage_state_path}")

    except Exception as e:
        print(f"❌ 登录失败: {e}")
        # 截图调试
        screenshot_path = STORAGE_STATE_DIR / "login_error.png"
        page.screenshot(path=str(screenshot_path))
        print(f"   已保存错误截图: {screenshot_path}")
        raise
    finally:
        context.close()

    return storage_state_path


@pytest.fixture(scope="session")
def authenticated_state(browser: Browser) -> Path:
    """
    Session级别的fixture，执行一次登录并保存认证状态
    其他测试可以复用这个状态，避免重复登录

    自动检测功能：
    1. 检查文件是否存在
    2. 检查文件是否过期（基于修改时间）
    3. [可选] 验证认证状态是否有效（尝试访问需要认证的页面）
    4. 如果无效或过期，自动重新登录
    """
    print("\n" + "="*60)
    print("📋 认证状态检查开始")
    print("="*60)

    storage_state_path = _get_storage_state_path()
    need_refresh = False

    # 检查1：文件是否存在
    if not storage_state_path.exists():
        print("❌ 认证状态文件不存在，需要登录")
        need_refresh = True

    # 检查2：文件是否过期（基于修改时间）
    elif time.time() - os.path.getmtime(storage_state_path) > AUTH_STATE_EXPIRY:
        elapsed_hours = (time.time() - os.path.getmtime(storage_state_path)) / 3600
        print(f"⏰ 认证状态文件已过期（已存在 {elapsed_hours:.1f} 小时，有效期 {AUTH_STATE_EXPIRY/3600} 小时）")
        need_refresh = True

    # 检查3：[可选] 验证认证状态是否有效
    elif ENABLE_AUTH_VALIDATION:
        print("ℹ️  启用在线验证（会打开临时页面验证 cookies）")
        if not _is_auth_state_valid(browser):
            print("❌ 认证状态已失效，需要重新登录")
            need_refresh = True
        else:
            file_age_minutes = (time.time() - os.path.getmtime(storage_state_path)) / 60
            print(f"✅ 使用现有有效的认证状态（文件创建于 {file_age_minutes:.1f} 分钟前）")
    else:
        # 跳过在线验证，直接使用文件
        file_age_minutes = (time.time() - os.path.getmtime(storage_state_path)) / 60
        print(f"✅ 使用现有认证状态（文件创建于 {file_age_minutes:.1f} 分钟前）")
        print("ℹ️  跳过在线验证（ENABLE_AUTH_VALIDATION=False）")

    # 如果需要刷新，删除旧文件并重新登录
    if need_refresh:
        print("\n🔄 开始重新登录...")
        if storage_state_path.exists():
            storage_state_path.unlink()
        result = _perform_login(browser)
        print("="*60)
        return result

    print("="*60 + "\n")
    return storage_state_path


def _stop_tracing(context, request, tracing_option):
    """停止并按策略保存 tracing，避免 page/authenticated_page 重复逻辑"""
    TRACE_DIR.mkdir(parents=True, exist_ok=True)
    test_name = request.node.name.split('[')[0]
    node_hash = hashlib.md5(request.node.nodeid.encode("utf-8")).hexdigest()[:8]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    trace_path = TRACE_DIR / f"{test_name}_{node_hash}_{timestamp}.zip"
    context.tracing.stop(path=str(trace_path))
    request.node._trace_path = trace_path
    request.node._trace_mode = tracing_option


def _create_page_with_tracing(browser, request, browser_context_args, storage_state=None):
    """创建带 tracing 的 page，提取 page 和 authenticated_page 的通用逻辑

    Args:
        browser: Browser 实例
        request: pytest request 对象
        browser_context_args: context 参数
        storage_state: 可选的登录状态文件路径

    Yields:
        Page: 创建的 page 对象
    """
    tracing_option = request.config.getoption("--trace-mode")

    # 创建 context（带或不带登录状态）
    context_kwargs = {**browser_context_args}
    if storage_state:
        context_kwargs["storage_state"] = str(storage_state)

    context = browser.new_context(**context_kwargs)
    page = context.new_page()

    # 启动 tracing
    if tracing_option in ["on", "retain-on-failure"]:
        context.tracing.start(screenshots=True, snapshots=True, sources=True)

    yield page

    # 停止 tracing
    if tracing_option in ["on", "retain-on-failure"]:
        _stop_tracing(context, request, tracing_option)

    context.close()


def _get_failure_details(report) -> str:
    """提取失败详情文本，优先使用 longreprtext。"""
    details = getattr(report, "longreprtext", "")
    if details:
        return details
    longrepr = getattr(report, "longrepr", "")
    return str(longrepr) if longrepr else ""


def _is_dataloader_related_error(call, failure_details: str) -> bool:
    """判断失败是否与 DataLoader 测试数据读取相关。"""
    keywords = (
        "DataLoader",
        "utils/data_loader.py",
        "测试数据文件",
        "测试数据 key",
        "test_data/"
    )
    if any(keyword in failure_details for keyword in keywords):
        return True

    excinfo = getattr(call, "excinfo", None)
    if excinfo and excinfo.value:
        exc_summary = f"{type(excinfo.value).__name__}: {excinfo.value}"
        if "测试数据" in exc_summary:
            return True

    return False


def _attach_failure_details(item, report, call):
    """失败时附加堆栈与 DataLoader 诊断信息到 Allure。"""
    details = _get_failure_details(report)
    if not details:
        return

    allure.attach(
        details,
        name=f"失败堆栈_{report.when}_{item.name}",
        attachment_type=allure.attachment_type.TEXT
    )

    if _is_dataloader_related_error(call, details):
        excinfo = getattr(call, "excinfo", None)
        if excinfo and excinfo.value:
            summary = f"{type(excinfo.value).__name__}: {excinfo.value}"
        else:
            summary = "DataLoader 相关异常（无可用异常对象）"

        allure.attach(
            (
                f"测试节点: {item.nodeid}\n"
                f"失败阶段: {report.when}\n"
                f"异常摘要: {summary}\n"
                "建议检查: 测试数据文件路径、YAML 结构、key 名称。"
            ),
            name=f"DataLoader异常摘要_{item.name}",
            attachment_type=allure.attachment_type.TEXT
        )


@pytest.fixture(scope="function")
def page(browser: Browser, request, browser_context_args):
    """默认的page fixture，不带登录状态"""
    yield from _create_page_with_tracing(browser, request, browser_context_args)


@pytest.fixture(scope="function")
def authenticated_page(browser: Browser, authenticated_state: Path, request, browser_context_args):
    """
    带登录状态的page fixture
    使用方法：在测试函数参数中使用 authenticated_page 替代 page
    """
    yield from _create_page_with_tracing(browser, request, browser_context_args, storage_state=authenticated_state)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """在测试失败时自动截图并附加到 Allure 报告，同时保存测试结果用于 tracing 判断"""
    outcome = yield
    report = outcome.get_result()

    # 保存测试结果到 item，供 fixture 使用
    setattr(item, f"rep_{report.when}", report)

    if report.when in ("setup", "call", "teardown") and report.failed:
        try:
            _attach_failure_details(item, report, call)
        except Exception as e:
            print(f"附加失败详情到 Allure 失败: {e}")

        # 获取页面对象（支持 page 和 authenticated_page）
        page = item.funcargs.get("page") or item.funcargs.get("authenticated_page")
        if page:
            try:
                # 截图
                screenshot_bytes = page.screenshot(full_page=True)
                allure.attach(
                    screenshot_bytes,
                    name=f"失败截图_{item.name}",
                    attachment_type=allure.attachment_type.PNG
                )

                # 附加页面 URL
                allure.attach(
                    page.url,
                    name="页面URL",
                    attachment_type=allure.attachment_type.TEXT
                )
            except Exception as e:
                print(f"截图失败: {e}")

    # 在 teardown 完成后按策略处理 trace（附加或删除）
    if report.when == "teardown" and hasattr(item, '_trace_path'):
        trace_path = item._trace_path
        trace_mode = getattr(item, "_trace_mode", "on")
        rep_setup = getattr(item, "rep_setup", None)
        rep_call = getattr(item, "rep_call", None)
        test_failed = (
            (rep_setup is not None and rep_setup.failed) or
            (rep_call is not None and rep_call.failed) or
            report.failed
        )

        if trace_mode == "retain-on-failure" and not test_failed:
            if trace_path.exists():
                try:
                    trace_path.unlink()
                except Exception as e:
                    print(f"删除无失败 trace 失败: {e}")
            return

        if trace_path.exists():
            try:
                # 使用文件名（去除 .zip 扩展名）作为附件名称
                trace_name = trace_path.stem  # 例如：test_click_mar_tab_20251230_194328
                with open(trace_path, 'rb') as f:
                    allure.attach(
                        f.read(),
                        name=f"Trace_{trace_name}",
                        attachment_type="application/zip",
                        extension="zip"
                    )
            except Exception as e:
                print(f"附加 trace 失败: {e}")
                
