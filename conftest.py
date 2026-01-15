import sys
from pathlib import Path

# ========== 重要：将项目根目录添加到 Python 路径 ==========
# 这样可以在 debug 模式下直接运行测试文件，也能正确导入模块
PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import allure
import pytest
from playwright.sync_api import Browser
from config.config import HEADLESS, BASE_URL
import time
import os
from datetime import datetime


# ========== 认证状态管理配置 ==========
# Storage state 文件路径
STORAGE_STATE_PATH = Path(__file__).parent / "test_data" / "auth_state.json"

# 认证状态有效期（秒），超过此时间将重新登录
# 可根据实际 token 过期时间调整，默认 1 小时
AUTH_STATE_EXPIRY = 60 * 60  # 1 hour

# 是否启用认证状态在线验证（会打开一个临时页面验证 cookies）
# True: 每次都验证（更安全，但会多打开一次页面）
# False: 只检查文件存在性和过期时间（更快，推荐）
ENABLE_AUTH_VALIDATION = False

# Trace 文件保存路径
TRACE_DIR = Path(__file__).parent / "test-results"


def pytest_addoption(parser):
    """添加自定义命令行选项"""
    parser.addoption(
        "--trace-mode",
        action="store",
        default="off",
        help="启用 Playwright tracing: 'on' 所有测试, 'retain-on-failure' 仅失败测试保留, 'off' 禁用 (默认)"
    )


@pytest.fixture(scope="session")
def browser_type_launch_args():
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
    if not STORAGE_STATE_PATH.exists():
        print("ℹ 认证状态文件不存在")
        return False

    try:
        print("ℹ 开始验证认证状态...")
        # 创建使用保存状态的临时上下文
        context = browser.new_context(storage_state=str(STORAGE_STATE_PATH))
        page = context.new_page()

        # 访问主页
        print(f"ℹ 访问主页: {BASE_URL}")
        page.goto(BASE_URL, timeout=15000)  # 增加超时时间到 15 秒
        page.wait_for_timeout(2000)  # 增加等待时间到 2 秒

        # 检查是否存在登录后才有的元素（如"用药记录"按钮）
        # 如果找到该元素，说明认证有效；否则可能跳转到了登录页
        try:
            print("ℹ 检查登录状态（查找'用药记录'按钮）...")
            page.wait_for_selector("button:has-text('用药记录')", timeout=10000)  # 增加超时到 10 秒
            print("✓ 认证状态有效，找到'用药记录'按钮")
            context.close()
            return True
        except Exception as e:
            print(f"✗ 未找到'用药记录'按钮: {e}")
            print(f"  当前 URL: {page.url}")
            context.close()
            return False

    except Exception as e:
        print(f"⚠ 验证认证状态失败: {e}")
        return False


def _perform_login(browser: Browser) -> Path:
    """
    执行登录并保存认证状态
    """
    print("\n🔐 执行登录流程...")

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

        # 等待登录成功 - 等待特定元素出现确保登录完成
        try:
            print("ℹ️  等待登录完成（查找'用药记录'按钮）...")
            page.wait_for_selector("button:has-text('用药记录')", timeout=10000)
            print("✅ 登录成功，已检测到主页元素")
        except Exception as e:
            print(f"⚠️  警告：未检测到登录后的主页元素: {e}")
            print(f"   当前 URL: {page.url}")
            print("   继续等待 2 秒...")
            page.wait_for_timeout(2000)

        # 额外等待，确保所有 cookies 都设置完成
        print("ℹ️  等待 cookies 设置...")
        page.wait_for_timeout(1000)

        # 保存认证状态前，检查 cookies
        cookies = context.cookies()
        print(f"ℹ️  当前 Cookies 数量: {len(cookies)}")

        if len(cookies) == 0:
            print("⚠️  警告: 登录后没有 cookies，可能登录失败！")
            print(f"   当前 URL: {page.url}")
            # 截图调试
            screenshot_path = STORAGE_STATE_PATH.parent / "login_debug.png"
            page.screenshot(path=str(screenshot_path))
            print(f"   已保存调试截图: {screenshot_path}")
        else:
            # 显示部分 cookies 信息
            print(f"ℹ️  Cookies 示例:")
            for cookie in cookies[:3]:  # 只显示前3个
                print(f"      - {cookie.get('name')}: {cookie.get('domain')}")
            if len(cookies) > 3:
                print(f"      ... 还有 {len(cookies) - 3} 个")

        # 保存认证状态
        STORAGE_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        context.storage_state(path=str(STORAGE_STATE_PATH))

        print(f"✅ 登录状态已保存到: {STORAGE_STATE_PATH}")

    except Exception as e:
        print(f"❌ 登录失败: {e}")
        # 截图调试
        screenshot_path = STORAGE_STATE_PATH.parent / "login_error.png"
        page.screenshot(path=str(screenshot_path))
        print(f"   已保存错误截图: {screenshot_path}")
        raise
    finally:
        context.close()

    return STORAGE_STATE_PATH


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

    need_refresh = False

    # 检查1：文件是否存在
    if not STORAGE_STATE_PATH.exists():
        print("❌ 认证状态文件不存在，需要登录")
        need_refresh = True

    # 检查2：文件是否过期（基于修改时间）
    elif time.time() - os.path.getmtime(STORAGE_STATE_PATH) > AUTH_STATE_EXPIRY:
        elapsed_hours = (time.time() - os.path.getmtime(STORAGE_STATE_PATH)) / 3600
        print(f"⏰ 认证状态文件已过期（已存在 {elapsed_hours:.1f} 小时，有效期 {AUTH_STATE_EXPIRY/3600} 小时）")
        need_refresh = True

    # 检查3：[可选] 验证认证状态是否有效
    elif ENABLE_AUTH_VALIDATION:
        print("ℹ️  启用在线验证（会打开临时页面验证 cookies）")
        if not _is_auth_state_valid(browser):
            print("❌ 认证状态已失效，需要重新登录")
            need_refresh = True
        else:
            file_age_minutes = (time.time() - os.path.getmtime(STORAGE_STATE_PATH)) / 60
            print(f"✅ 使用现有有效的认证状态（文件创建于 {file_age_minutes:.1f} 分钟前）")
    else:
        # 跳过在线验证，直接使用文件
        file_age_minutes = (time.time() - os.path.getmtime(STORAGE_STATE_PATH)) / 60
        print(f"✅ 使用现有认证状态（文件创建于 {file_age_minutes:.1f} 分钟前）")
        print("ℹ️  跳过在线验证（ENABLE_AUTH_VALIDATION=False）")

    # 如果需要刷新，删除旧文件并重新登录
    if need_refresh:
        print("\n🔄 开始重新登录...")
        if STORAGE_STATE_PATH.exists():
            STORAGE_STATE_PATH.unlink()
        result = _perform_login(browser)
        print("="*60)
        return result

    print("="*60 + "\n")
    return STORAGE_STATE_PATH


@pytest.fixture(scope="function")
def page(browser: Browser, request):
    """默认的page fixture，不带登录状态"""
    tracing_option = request.config.getoption("--trace-mode")

    context = browser.new_context(viewport={"width": 1920, "height": 1080})
    page = context.new_page()

    # 启动 tracing
    if tracing_option in ["on", "retain-on-failure"]:
        context.tracing.start(screenshots=True, snapshots=True, sources=True)

    yield page

    # 停止并保存 tracing
    if tracing_option in ["on", "retain-on-failure"]:
        # 获取测试结果
        test_failed = hasattr(request.node, 'rep_call') and request.node.rep_call.failed

        # 根据策略决定是否保存 trace
        should_save = (tracing_option == "on") or (tracing_option == "retain-on-failure" and test_failed)

        if should_save:
            TRACE_DIR.mkdir(parents=True, exist_ok=True)
            # 生成文件名：测试方法名（去除参数）+ 时间戳
            test_name = request.node.name.split('[')[0]  # 去除 [chromium] 等参数
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            trace_path = TRACE_DIR / f"{test_name}_{timestamp}.zip"
            context.tracing.stop(path=str(trace_path))

            # 将 trace 路径保存到 request.node，供 hook 使用
            request.node._trace_path = trace_path
        else:
            context.tracing.stop()

    context.close()


@pytest.fixture(scope="function")
def authenticated_page(browser: Browser, authenticated_state: Path, request):
    """
    带登录状态的page fixture
    使用方法：在测试函数参数中使用 authenticated_page 替代 page
    """
    tracing_option = request.config.getoption("--trace-mode")

    context = browser.new_context(
        storage_state=str(authenticated_state),
        viewport={"width": 1920, "height": 1080}
    )
    page = context.new_page()

    # 启动 tracing
    if tracing_option in ["on", "retain-on-failure"]:
        context.tracing.start(screenshots=True, snapshots=True, sources=True)

    yield page

    # 停止并保存 tracing
    if tracing_option in ["on", "retain-on-failure"]:
        # 获取测试结果
        test_failed = hasattr(request.node, 'rep_call') and request.node.rep_call.failed

        # 根据策略决定是否保存 trace
        should_save = (tracing_option == "on") or (tracing_option == "retain-on-failure" and test_failed)

        if should_save:
            TRACE_DIR.mkdir(parents=True, exist_ok=True)
            # 生成文件名：测试方法名（去除参数）+ 时间戳
            test_name = request.node.name.split('[')[0]  # 去除 [chromium] 等参数
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            trace_path = TRACE_DIR / f"{test_name}_{timestamp}.zip"
            context.tracing.stop(path=str(trace_path))

            # 将 trace 路径保存到 request.node，供 hook 使用
            request.node._trace_path = trace_path
        else:
            context.tracing.stop()

    context.close()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):  # noqa: ARG001
    """在测试失败时自动截图并附加到 Allure 报告，同时保存测试结果用于 tracing 判断"""
    outcome = yield
    report = outcome.get_result()

    # 保存测试结果到 item，供 fixture 使用
    setattr(item, f"rep_{report.when}", report)

    if report.when == "call" and report.failed:
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

    # 在 teardown 完成后附加 trace（如果存在）
    if report.when == "teardown" and hasattr(item, '_trace_path'):
        trace_path = item._trace_path
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
