import sys
from pathlib import Path

# ========== 重要：将项目根目录添加到 Python 路径 ==========
# 这样可以在 debug 模式下直接运行测试文件，也能正确导入模块
PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import allure
import pytest
from playwright.sync_api import Browser, expect

from config.config import HEADLESS, TIMEOUT
from fixtures.page_factory import create_page_with_tracing

expect.set_options(timeout=TIMEOUT)


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
    yield from create_page_with_tracing(browser, request, browser_context_args)


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
                
