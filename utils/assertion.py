import allure
from utils.logger import Logger


class Assertion:
    """断言封装类，集成 Allure 报告"""

    def __init__(self, name: str = "Assertion"):
        self.logger = Logger.get_logger(name)

    def _assert_with_allure(self, condition, success_log: str, error_log: str,
                           success_attach: str, error_attach: str, message: str = ""):
        """通用断言方法，集成日志和 Allure 报告

        Args:
            condition: 断言条件（lambda 或布尔值）
            success_log: 成功时的日志信息
            error_log: 失败时的日志信息
            success_attach: 成功时的 Allure 附件内容
            error_attach: 失败时的 Allure 附件内容
            message: 自定义错误消息
        """
        try:
            # 如果 condition 是 callable，执行它；否则直接使用布尔值
            if callable(condition):
                condition()
            else:
                assert condition, message

            self.logger.info(f"✓ 断言成功: {success_log}")
            allure.attach(
                success_attach,
                name="断言结果",
                attachment_type=allure.attachment_type.TEXT
            )
        except AssertionError as e:
            self.logger.error(f"✗ 断言失败: {error_log}")
            error_content = error_attach
            if message:
                error_content += f"\n{message}"
            allure.attach(
                error_content,
                name="断言失败详情",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(str(e))
        except Exception as e:
            # 处理其他异常（如 page.is_visible 等操作异常）
            self.logger.error(f"✗ 断言失败: {error_log} - {str(e)}")
            allure.attach(
                f"{error_attach}\n错误: {str(e)}",
                name="断言失败详情",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(f"{error_log}: {str(e)}")

    @allure.step("断言相等: 期望 '{expected}' 等于 '{actual}'")
    def assert_equal(self, actual, expected, message: str = ""):
        """断言两个值相等"""
        self._assert_with_allure(
            lambda: assert_helper(actual == expected, message or f"期望值: {expected}, 实际值: {actual}"),
            f"{actual} == {expected}",
            f"{actual} != {expected}",
            f"期望值: {expected}\n实际值: {actual}\n结果: 通过",
            f"期望值: {expected}\n实际值: {actual}\n结果: 失败",
            message
        )

    @allure.step("断言不相等: '{actual}' 不等于 '{not_expected}'")
    def assert_not_equal(self, actual, not_expected, message: str = ""):
        """断言两个值不相等"""
        self._assert_with_allure(
            lambda: assert_helper(actual != not_expected, message or f"期望值不等于: {not_expected}, 实际值: {actual}"),
            f"{actual} != {not_expected}",
            f"{actual} == {not_expected}",
            f"不期望值: {not_expected}\n实际值: {actual}\n结果: 通过",
            f"不期望值: {not_expected}\n实际值: {actual}\n结果: 失败",
            message
        )

    @allure.step("断言包含: '{actual}' 包含 '{expected}'")
    def assert_contains(self, actual: str, expected: str, message: str = ""):
        """断言字符串包含某个子串"""
        self._assert_with_allure(
            lambda: assert_helper(expected in actual, message or f"'{actual}' 不包含 '{expected}'"),
            f"'{actual}' 包含 '{expected}'",
            f"'{actual}' 不包含 '{expected}'",
            f"期望包含: {expected}\n实际值: {actual}\n结果: 通过",
            f"期望包含: {expected}\n实际值: {actual}\n结果: 失败",
            message
        )

    @allure.step("断言不包含: '{actual}' 不包含 '{not_expected}'")
    def assert_not_contains(self, actual: str, not_expected: str, message: str = ""):
        """断言字符串不包含某个子串"""
        self._assert_with_allure(
            lambda: assert_helper(not_expected not in actual, message or f"'{actual}' 包含 '{not_expected}'"),
            f"'{actual}' 不包含 '{not_expected}'",
            f"'{actual}' 包含 '{not_expected}'",
            f"不期望包含: {not_expected}\n实际值: {actual}\n结果: 通过",
            f"不期望包含: {not_expected}\n实际值: {actual}\n结果: 失败",
            message
        )

    @allure.step("断言为真: {condition}")
    def assert_true(self, condition, message: str = ""):
        """断言条件为真"""
        self._assert_with_allure(
            lambda: assert_helper(condition, message or f"期望为 True, 实际为 {condition}"),
            "条件为 True",
            "条件为 False",
            f"条件: {condition}\n结果: 通过",
            f"条件: {condition}\n结果: 失败",
            message
        )

    @allure.step("断言为假: {condition}")
    def assert_false(self, condition, message: str = ""):
        """断言条件为假"""
        self._assert_with_allure(
            lambda: assert_helper(not condition, message or f"期望为 False, 实际为 {condition}"),
            "条件为 False",
            "条件为 True",
            f"条件: {condition}\n结果: 通过",
            f"条件: {condition}\n结果: 失败",
            message
        )

    @allure.step("断言大于: {actual} > {expected}")
    def assert_greater(self, actual, expected, message: str = ""):
        """断言实际值大于期望值"""
        self._assert_with_allure(
            lambda: assert_helper(actual > expected, message or f"{actual} 不大于 {expected}"),
            f"{actual} > {expected}",
            f"{actual} <= {expected}",
            f"实际值: {actual}\n期望大于: {expected}\n结果: 通过",
            f"实际值: {actual}\n期望大于: {expected}\n结果: 失败",
            message
        )

    @allure.step("断言小于: {actual} < {expected}")
    def assert_less(self, actual, expected, message: str = ""):
        """断言实际值小于期望值"""
        self._assert_with_allure(
            lambda: assert_helper(actual < expected, message or f"{actual} 不小于 {expected}"),
            f"{actual} < {expected}",
            f"{actual} >= {expected}",
            f"实际值: {actual}\n期望小于: {expected}\n结果: 通过",
            f"实际值: {actual}\n期望小于: {expected}\n结果: 失败",
            message
        )

    @allure.step("断言在列表中: '{item}' 在 {items}")
    def assert_in(self, item, items, message: str = ""):
        """断言元素在列表中"""
        self._assert_with_allure(
            lambda: assert_helper(item in items, message or f"'{item}' 不在 {items} 中"),
            f"'{item}' 在列表中",
            f"'{item}' 不在列表中",
            f"元素: {item}\n列表: {items}\n结果: 通过",
            f"元素: {item}\n列表: {items}\n结果: 失败",
            message
        )

    @allure.step("断言元素可见: {selector}")
    def assert_is_display(self, page, selector: str, message: str = ""):
        """断言页面元素可见"""
        self._assert_with_allure(
            lambda: assert_helper(page.is_visible(selector), message or f"元素 '{selector}' 不可见"),
            f"元素 '{selector}' 可见",
            f"元素 '{selector}' 不可见",
            f"选择器: {selector}\n可见性: 是\n结果: 通过",
            f"选择器: {selector}\n可见性: 否\n结果: 失败",
            message
        )

    @allure.step("断言元素不可见: {selector}")
    def assert_not_display(self, page, selector: str, message: str = ""):
        """断言页面元素不可见"""
        self._assert_with_allure(
            lambda: assert_helper(not page.is_visible(selector), message or f"元素 '{selector}' 可见"),
            f"元素 '{selector}' 不可见",
            f"元素 '{selector}' 可见",
            f"选择器: {selector}\n可见性: 否\n结果: 通过",
            f"选择器: {selector}\n可见性: 是\n结果: 失败",
            message
        )

    @allure.step("断言元素选中: {selector}")
    def assert_is_checked(self, page, selector: str, message: str = ""):
        """断言页面元素选中"""
        self._assert_with_allure(
            lambda: assert_helper(page.is_checked(selector), message or f"元素 '{selector}' 未选中"),
            f"元素 '{selector}' 选中",
            f"元素 '{selector}' 未选中",
            f"选择器: {selector}\n选中: 是\n结果: 通过",
            f"选择器: {selector}\n选中: 否\n结果: 失败",
            message
        )

    @allure.step("断言元素未选中: {selector}")
    def assert_is_unchecked(self, page, selector: str, message: str = ""):
        """断言页面元素未选中"""
        self._assert_with_allure(
            lambda: assert_helper(not page.is_checked(selector), message or f"元素 '{selector}' 选中"),
            f"元素 '{selector}' 未选中",
            f"元素 '{selector}' 选中",
            f"选择器: {selector}\n选中: 否\n结果: 通过",
            f"选择器: {selector}\n选中: 是\n结果: 失败",
            message
        )


def assert_helper(condition, message):
    """辅助函数，用于在 lambda 中执行 assert"""
    assert condition, message
