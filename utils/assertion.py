import allure
from playwright.sync_api import Locator, Page, expect
from typing import Union

from utils.logger import Logger


def _short_repr(value, max_length: int = 120) -> str:
    """格式化断言参数，避免附件内容过长。"""
    rendered = repr(value)
    if len(rendered) <= max_length:
        return rendered
    return f"{rendered[:max_length - 3]}..."


class AllureExpectation:
    """对 Playwright expect 的轻量封装，保留 Allure 步骤和附件。"""

    def __init__(self, actual, description: str, logger):
        self.actual = actual
        self.description = description or "Playwright expect 断言"
        self.logger = logger

    def _render_invocation(self, method_name: str, args, kwargs) -> str:
        parts = [_short_repr(arg) for arg in args]
        parts.extend(f"{key}={_short_repr(value)}" for key, value in kwargs.items())
        joined = ", ".join(parts)
        return f"expect.{method_name}({joined})"

    def __getattr__(self, method_name: str):
        assertion_method = getattr(expect(self.actual), method_name)

        def wrapped(*args, **kwargs):
            invocation = self._render_invocation(method_name, args, kwargs)
            with allure.step(self.description):
                try:
                    result = assertion_method(*args, **kwargs)
                    self.logger.info(f"✓ expect断言成功: {self.description} [{invocation}]")
                    allure.attach(
                        f"步骤: {self.description}\n断言: {invocation}\n结果: 通过",
                        name="expect断言结果",
                        attachment_type=allure.attachment_type.TEXT
                    )
                    return result
                except AssertionError as error:
                    self.logger.error(f"✗ expect断言失败: {self.description} [{invocation}]")
                    allure.attach(
                        f"步骤: {self.description}\n断言: {invocation}\n结果: 失败\n错误: {error}",
                        name="expect断言失败详情",
                        attachment_type=allure.attachment_type.TEXT
                    )
                    raise
                except Exception as error:
                    self.logger.error(f"✗ expect断言异常: {self.description} [{invocation}] - {error}")
                    allure.attach(
                        f"步骤: {self.description}\n断言: {invocation}\n异常: {error}",
                        name="expect断言异常详情",
                        attachment_type=allure.attachment_type.TEXT
                    )
                    raise

        return wrapped


class Assertion:
    """断言封装类，基于 Playwright expect 提供带 Allure 步骤的断言方法。"""

    def __init__(self, name: str = "Assertion"):
        self.logger = Logger.get_logger(name)

    def expect_that(self, actual: Union[Locator, Page], description: str = "") -> AllureExpectation:
        """创建带 Allure 步骤/附件的 Playwright expect 包装器（低级扩展口）。"""
        return AllureExpectation(actual, description, self.logger)

    # ── 元素可见性 ──────────────────────────────────────────────────────────────

    @allure.step("断言元素可见: {element}")
    def assert_is_display(self, page_obj, element, message: str = ""):
        """断言页面元素可见。"""
        self.expect_that(
            page_obj.locator(element),
            message or f"断言元素可见: {element}"
        ).to_be_visible()

    @allure.step("断言元素不可见: {element}")
    def assert_not_display(self, page_obj, element, message: str = ""):
        """断言页面元素不可见。"""
        self.expect_that(
            page_obj.locator(element),
            message or f"断言元素不可见: {element}"
        ).not_to_be_visible()

    def assert_is_display_raw(self, locator, message: str = ""):
        """断言已解析的 Locator 可见（适用于 FrameLocator 等特殊场景）。"""
        self.expect_that(locator, message or "断言元素可见").to_be_visible()

    # ── 复选框状态 ──────────────────────────────────────────────────────────────

    @allure.step("断言元素选中: {element}")
    def assert_is_checked(self, page_obj, element, message: str = ""):
        """断言页面元素选中。"""
        self.expect_that(
            page_obj.locator(element),
            message or f"断言元素选中: {element}"
        ).to_be_checked()

    @allure.step("断言元素未选中: {element}")
    def assert_is_unchecked(self, page_obj, element, message: str = ""):
        """断言页面元素未选中。"""
        self.expect_that(
            page_obj.locator(element),
            message or f"断言元素未选中: {element}"
        ).not_to_be_checked()

    # ── 文本断言 ────────────────────────────────────────────────────────────────

    @allure.step("断言元素文本: '{expected_text}'")
    def assert_has_text(self, page_obj, element, expected_text, message: str = ""):
        """断言元素文本等于期望值。"""
        self.expect_that(
            page_obj.locator(element),
            message or f"断言元素文本等于: {expected_text}"
        ).to_have_text(expected_text)

    @allure.step("断言元素文本不等于: '{unexpected_text}'")
    def assert_not_has_text(self, page_obj, element, unexpected_text, message: str = ""):
        """断言元素文本不等于指定值。"""
        self.expect_that(
            page_obj.locator(element),
            message or f"断言元素文本不等于: {unexpected_text}"
        ).not_to_have_text(unexpected_text)

    @allure.step("断言元素包含文本: '{expected_text}'")
    def assert_contains_text(self, page_obj, element, expected_text, message: str = ""):
        """断言元素文本包含期望值。"""
        self.expect_that(
            page_obj.locator(element),
            message or f"断言元素文本包含: {expected_text}"
        ).to_contain_text(expected_text)

    # ── 值/样式断言 ─────────────────────────────────────────────────────────────

    @allure.step("断言元素值: '{expected_value}'")
    def assert_has_value(self, page_obj, element, expected_value, message: str = ""):
        """断言输入元素的值等于期望值（支持正则）。"""
        self.expect_that(
            page_obj.locator(element),
            message or f"断言元素值等于: {expected_value}"
        ).to_have_value(expected_value)

    @allure.step("断言元素CSS属性: '{css_property}' = '{value}'")
    def assert_has_css(self, page_obj, element, css_property: str, value, message: str = ""):
        """断言元素的 CSS 属性值。"""
        self.expect_that(
            page_obj.locator(element),
            message or f"断言CSS {css_property}: {value}"
        ).to_have_css(css_property, value)

    @allure.step("断言元素包含CSS类: '{class_pattern}'")
    def assert_has_class(self, page_obj, element, class_pattern, message: str = ""):
        """断言元素包含指定 CSS class（支持正则）。"""
        self.expect_that(
            page_obj.locator(element),
            message or f"断言元素包含class: {class_pattern}"
        ).to_have_class(class_pattern)

    # ── 页面级断言 ──────────────────────────────────────────────────────────────

    @allure.step("断言页面URL: '{url_pattern}'")
    def assert_has_url(self, page, url_pattern, message: str = ""):
        """断言页面 URL 匹配期望值（支持正则）。"""
        self.expect_that(
            page,
            message or f"断言页面URL: {url_pattern}"
        ).to_have_url(url_pattern)
