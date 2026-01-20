import allure
from utils.logger import Logger


class Assertion:
    """断言封装类，集成 Allure 报告"""

    def __init__(self, name: str = "Assertion"):
        self.logger = Logger.get_logger(name)

    @allure.step("断言相等: 期望 '{expected}' 等于 '{actual}'")
    def assert_equal(self, actual, expected, message: str = ""):
        """断言两个值相等"""
        try:
            assert actual == expected, message or f"期望值: {expected}, 实际值: {actual}"
            self.logger.info(f"✓ 断言成功: {actual} == {expected}")
            allure.attach(
                f"期望值: {expected}\n实际值: {actual}\n结果: 通过",
                name="断言结果",
                attachment_type=allure.attachment_type.TEXT
            )
        except AssertionError as e:
            self.logger.error(f"✗ 断言失败: {actual} != {expected}")
            allure.attach(
                f"期望值: {expected}\n实际值: {actual}\n结果: 失败\n{message}",
                name="断言失败详情",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(str(e))

    @allure.step("断言不相等: '{actual}' 不等于 '{not_expected}'")
    def assert_not_equal(self, actual, not_expected, message: str = ""):
        """断言两个值不相等"""
        try:
            assert actual != not_expected, message or f"期望值不等于: {not_expected}, 实际值: {actual}"
            self.logger.info(f"✓ 断言成功: {actual} != {not_expected}")
            allure.attach(
                f"不期望值: {not_expected}\n实际值: {actual}\n结果: 通过",
                name="断言结果",
                attachment_type=allure.attachment_type.TEXT
            )
        except AssertionError as e:
            self.logger.error(f"✗ 断言失败: {actual} == {not_expected}")
            allure.attach(
                f"不期望值: {not_expected}\n实际值: {actual}\n结果: 失败\n{message}",
                name="断言失败详情",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(str(e))

    @allure.step("断言包含: '{actual}' 包含 '{expected}'")
    def assert_contains(self, actual: str, expected: str, message: str = ""):
        """断言字符串包含某个子串"""
        try:
            assert expected in actual, message or f"'{actual}' 不包含 '{expected}'"
            self.logger.info(f"✓ 断言成功: '{actual}' 包含 '{expected}'")
            allure.attach(
                f"期望包含: {expected}\n实际值: {actual}\n结果: 通过",
                name="断言结果",
                attachment_type=allure.attachment_type.TEXT
            )
        except AssertionError as e:
            self.logger.error(f"✗ 断言失败: '{actual}' 不包含 '{expected}'")
            allure.attach(
                f"期望包含: {expected}\n实际值: {actual}\n结果: 失败\n{message}",
                name="断言失败详情",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(str(e))

    @allure.step("断言不包含: '{actual}' 不包含 '{not_expected}'")
    def assert_not_contains(self, actual: str, not_expected: str, message: str = ""):
        """断言字符串不包含某个子串"""
        try:
            assert not_expected not in actual, message or f"'{actual}' 包含 '{not_expected}'"
            self.logger.info(f"✓ 断言成功: '{actual}' 不包含 '{not_expected}'")
            allure.attach(
                f"不期望包含: {not_expected}\n实际值: {actual}\n结果: 通过",
                name="断言结果",
                attachment_type=allure.attachment_type.TEXT
            )
        except AssertionError as e:
            self.logger.error(f"✗ 断言失败: '{actual}' 包含 '{not_expected}'")
            allure.attach(
                f"不期望包含: {not_expected}\n实际值: {actual}\n结果: 失败\n{message}",
                name="断言失败详情",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(str(e))

    @allure.step("断言为真: {condition}")
    def assert_true(self, condition, message: str = ""):
        """断言条件为真"""
        try:
            assert condition is True or condition, message or f"期望为 True, 实际为 {condition}"
            self.logger.info(f"✓ 断言成功: 条件为 True")
            allure.attach(
                f"条件: {condition}\n结果: 通过",
                name="断言结果",
                attachment_type=allure.attachment_type.TEXT
            )
        except AssertionError as e:
            self.logger.error(f"✗ 断言失败: 条件为 False")
            allure.attach(
                f"条件: {condition}\n结果: 失败\n{message}",
                name="断言失败详情",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(str(e))

    @allure.step("断言为假: {condition}")
    def assert_false(self, condition, message: str = ""):
        """断言条件为假"""
        try:
            assert condition is False or not condition, message or f"期望为 False, 实际为 {condition}"
            self.logger.info(f"✓ 断言成功: 条件为 False")
            allure.attach(
                f"条件: {condition}\n结果: 通过",
                name="断言结果",
                attachment_type=allure.attachment_type.TEXT
            )
        except AssertionError as e:
            self.logger.error(f"✗ 断言失败: 条件为 True")
            allure.attach(
                f"条件: {condition}\n结果: 失败\n{message}",
                name="断言失败详情",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(str(e))

    @allure.step("断言大于: {actual} > {expected}")
    def assert_greater(self, actual, expected, message: str = ""):
        """断言实际值大于期望值"""
        try:
            assert actual > expected, message or f"{actual} 不大于 {expected}"
            self.logger.info(f"✓ 断言成功: {actual} > {expected}")
            allure.attach(
                f"实际值: {actual}\n期望大于: {expected}\n结果: 通过",
                name="断言结果",
                attachment_type=allure.attachment_type.TEXT
            )
        except AssertionError as e:
            self.logger.error(f"✗ 断言失败: {actual} <= {expected}")
            allure.attach(
                f"实际值: {actual}\n期望大于: {expected}\n结果: 失败\n{message}",
                name="断言失败详情",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(str(e))

    @allure.step("断言小于: {actual} < {expected}")
    def assert_less(self, actual, expected, message: str = ""):
        """断言实际值小于期望值"""
        try:
            assert actual < expected, message or f"{actual} 不小于 {expected}"
            self.logger.info(f"✓ 断言成功: {actual} < {expected}")
            allure.attach(
                f"实际值: {actual}\n期望小于: {expected}\n结果: 通过",
                name="断言结果",
                attachment_type=allure.attachment_type.TEXT
            )
        except AssertionError as e:
            self.logger.error(f"✗ 断言失败: {actual} >= {expected}")
            allure.attach(
                f"实际值: {actual}\n期望小于: {expected}\n结果: 失败\n{message}",
                name="断言失败详情",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(str(e))

    @allure.step("断言在列表中: '{item}' 在 {items}")
    def assert_in(self, item, items, message: str = ""):
        """断言元素在列表中"""
        try:
            assert item in items, message or f"'{item}' 不在 {items} 中"
            self.logger.info(f"✓ 断言成功: '{item}' 在列表中")
            allure.attach(
                f"元素: {item}\n列表: {items}\n结果: 通过",
                name="断言结果",
                attachment_type=allure.attachment_type.TEXT
            )
        except AssertionError as e:
            self.logger.error(f"✗ 断言失败: '{item}' 不在列表中")
            allure.attach(
                f"元素: {item}\n列表: {items}\n结果: 失败\n{message}",
                name="断言失败详情",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(str(e))

    @allure.step("断言元素可见: {selector}")
    def assert_is_display(self, page, selector: str, message: str = ""):
        """断言页面元素可见"""
        try:
            is_visible = page.is_visible(selector)
            assert is_visible, message or f"元素 '{selector}' 不可见"
            self.logger.info(f"✓ 断言成功: 元素 '{selector}' 可见")
            allure.attach(
                f"选择器: {selector}\n可见性: 是\n结果: 通过",
                name="断言结果",
                attachment_type=allure.attachment_type.TEXT
            )
        except AssertionError as e:
            self.logger.error(f"✗ 断言失败: 元素 '{selector}' 不可见")
            allure.attach(
                f"选择器: {selector}\n可见性: 否\n结果: 失败\n{message}",
                name="断言失败详情",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(str(e))
        except Exception as e:
            self.logger.error(f"✗ 断言失败: 检查元素 '{selector}' 时出错 - {str(e)}")
            allure.attach(
                f"选择器: {selector}\n错误: {str(e)}\n结果: 失败",
                name="断言失败详情",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(f"检查元素可见性时出错: {str(e)}")

    @allure.step("断言元素不可见: {selector}")
    def assert_not_display(self, page, selector: str, message: str = ""):
        """断言页面元素不可见"""
        try:
            is_visible = page.is_visible(selector)
            assert not is_visible, message or f"元素 '{selector}' 可见"
            self.logger.info(f"✓ 断言成功: 元素 '{selector}' 不可见")
            allure.attach(
                f"选择器: {selector}\n可见性: 否\n结果: 通过",
                name="断言结果",
                attachment_type=allure.attachment_type.TEXT
            )
        except AssertionError as e:
            self.logger.error(f"✗ 断言失败: 元素 '{selector}' 可见")
            allure.attach(
                f"选择器: {selector}\n可见性: 是\n结果: 失败\n{message}",
                name="断言失败详情",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(str(e))
        except Exception as e:
            self.logger.error(f"✗ 断言失败: 检查元素 '{selector}' 时出错 - {str(e)}")
            allure.attach(
                f"选择器: {selector}\n错误: {str(e)}\n结果: 失败",
                name="断言失败详情",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(f"检查元素可见性时出错: {str(e)}")
    
    @allure.step("断言元素选中: {selector}")
    def assert_is_checked(self, page, selector: str, message: str = ""):
        """断言页面元素选中"""
        try:
            is_checked = page.is_checked(selector)
            assert  is_checked, message or f"元素 '{selector}' 未选中"
            self.logger.info(f"✓ 断言成功: 元素 '{selector}' 选中")
            allure.attach(
                f"选择器: {selector}\n选中: 是\n结果: 通过",
                name="断言结果",
                attachment_type=allure.attachment_type.TEXT
            )
        except AssertionError as e:
            self.logger.error(f"✗ 断言失败: 元素 '{selector}' 未选中")
            allure.attach(
                f"选择器: {selector}\n选中: 否\n结果: 失败\n{message}",
                name="断言失败详情",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(str(e))
        except Exception as e:
            self.logger.error(f"✗ 断言失败: 检查元素 '{selector}' 时出错 - {str(e)}")
            allure.attach(
                f"选择器: {selector}\n错误: {str(e)}\n结果: 失败",
                name="断言失败详情",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(f"检查元素选中时出错: {str(e)}")
        
    @allure.step("断言元素未选中: {selector}")
    def assert_is_unchecked(self, page, selector: str, message: str = ""):
        """断言页面元素未选中"""
        try:
            is_checked = page.is_checked(selector)
            assert not is_checked, message or f"元素 '{selector}' 选中"
            self.logger.info(f"✓ 断言成功: 元素 '{selector}' 未选中")
            allure.attach(
                f"选择器: {selector}\n选中: 否\n结果: 通过",
                name="断言结果",
                attachment_type=allure.attachment_type.TEXT
            )
        except AssertionError as e:
            self.logger.error(f"✗ 断言失败: 元素 '{selector}' 选中")
            allure.attach(
                f"选择器: {selector}\n选中: 是\n结果: 失败\n{message}",
                name="断言失败详情",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(str(e))
        except Exception as e:
            self.logger.error(f"✗ 断言失败: 检查元素 '{selector}' 时出错 - {str(e)}")
            allure.attach(
                f"选择器: {selector}\n错误: {str(e)}\n结果: 失败",
                name="断言失败详情",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(f"检查元素未选中时出错: {str(e)}")
