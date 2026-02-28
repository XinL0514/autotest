import allure
from pages.mixins.locator_mixin import LocatorInput
from utils.exception_handler import ExceptionHandler
from typing import Optional


class ActionMixin:
    """基础交互操作：点击、填充、获取文本、可见性检查、悬停等"""

    @allure.step("导航到页面")
    @ExceptionHandler.handle_playwright_exception("导航到页面")
    def navigate(self, url: str, wait_until: str = "domcontentloaded"):
        """导航到指定URL

        Args:
            url: 目标 URL
            wait_until: 页面加载等待策略（domcontentloaded/load/networkidle）
        """
        self.logger.info(f"导航到页面: {url}, 等待策略: {wait_until}")
        self.page.goto(url, wait_until=wait_until)
        self.logger.info(f"成功加载页面: {url}")

    @allure.step("点击元素")
    @ExceptionHandler.handle_playwright_exception("点击元素")
    def click(self, locator: LocatorInput, timeout: int = None):
        """智能点击元素 - 支持 CSS/XPath 字符串、Role 元组或 Element 对象"""
        loc_desc = self._get_locator_description(locator)
        self.logger.info(f"尝试点击元素: {loc_desc}")
        self._run_locator_method(locator, "click", timeout=timeout)
        self.logger.info(f"成功点击元素: {loc_desc}")

    @allure.step("填充元素")
    @ExceptionHandler.handle_playwright_exception("填充元素")
    def fill(self, locator: LocatorInput, text: str, timeout: int = None):
        """智能填充输入框 - 支持 CSS/XPath 字符串、Role 元组或 Element 对象"""
        loc_desc = self._get_locator_description(locator)
        self.logger.info(f"尝试填充元素: {loc_desc}, 内容: {text}")
        self._run_locator_method(locator, "fill", text, timeout=timeout)
        self.logger.info(f"成功填充元素: {loc_desc}")

    @allure.step("获取元素文本")
    @ExceptionHandler.handle_playwright_exception("获取元素文本")
    def get_text(self, locator: LocatorInput, timeout: int = None) -> Optional[str]:
        """智能获取元素文本 - 支持 CSS/XPath 字符串、Role 元组或 Element 对象"""
        loc_desc = self._get_locator_description(locator)
        self.logger.info(f"尝试获取元素文本: {loc_desc}")
        text = self._run_locator_method(locator, "text_content", timeout=timeout)
        self.logger.info(f"成功获取文本: {loc_desc}, 内容: {text}")
        return text

    @allure.step("检查元素可见性")
    @ExceptionHandler.handle_playwright_exception("检查元素可见性", return_on_error=False, raise_assertion=False)
    def is_visible(self, locator: LocatorInput) -> bool:
        """智能检查元素是否可见"""
        loc_desc = self._get_locator_description(locator)
        visible = self._run_locator_method(locator, "is_visible", use_timeout=False)
        if visible:
            self.logger.info(f"元素可见: {loc_desc}")
        else:
            self.logger.warning(f"元素不可见: {loc_desc}")
        return visible

    @allure.step("等待元素出现")
    @ExceptionHandler.handle_playwright_exception("等待元素出现")
    def wait_for_selector(self, locator: LocatorInput, timeout: int = None):
        """智能等待元素出现"""
        loc_desc = self._get_locator_description(locator)
        self.logger.info(f"等待元素出现: {loc_desc}")
        self._run_locator_method(locator, "wait_for", timeout=timeout, state="visible")
        self.logger.info(f"元素已出现: {loc_desc}")

    @allure.step("双击元素")
    @ExceptionHandler.handle_playwright_exception("双击元素")
    def double_click(self, locator: LocatorInput, timeout: int = None):
        """智能双击元素"""
        loc_desc = self._get_locator_description(locator)
        self.logger.info(f"尝试双击元素: {loc_desc}")
        self._run_locator_method(locator, "dblclick", timeout=timeout)
        self.logger.info(f"成功双击元素: {loc_desc}")

    @allure.step("右键点击元素")
    @ExceptionHandler.handle_playwright_exception("右键点击元素")
    def right_click(self, locator: LocatorInput, timeout: int = None):
        """智能右键点击元素"""
        loc_desc = self._get_locator_description(locator)
        self.logger.info(f"尝试右键点击元素: {loc_desc}")
        self._run_locator_method(locator, "click", timeout=timeout, button="right")
        self.logger.info(f"成功右键点击元素: {loc_desc}")

    @allure.step("获取元素属性")
    @ExceptionHandler.handle_playwright_exception("获取元素属性")
    def get_attribute(self, locator: LocatorInput, attribute: str, timeout: int = None) -> Optional[str]:
        """智能获取元素属性值"""
        loc_desc = self._get_locator_description(locator)
        self.logger.info(f"尝试获取元素属性: {loc_desc}, 属性名: {attribute}")
        value = self._run_locator_method(locator, "get_attribute", attribute, timeout=timeout)
        self.logger.info(f"成功获取属性: {loc_desc}, {attribute}={value}")
        return value

    @allure.step("获取输入框的值")
    @ExceptionHandler.handle_playwright_exception("获取输入框的值")
    def get_input_value(self, locator: LocatorInput, timeout: int = None) -> str:
        """智能获取输入框当前值"""
        loc_desc = self._get_locator_description(locator)
        self.logger.info(f"尝试获取输入框的值: {loc_desc}")
        value = self._run_locator_method(locator, "input_value", timeout=timeout)
        self.logger.info(f"成功获取输入框的值: {loc_desc}, 值: {value}")
        return value

    @allure.step("检查元素是否选中")
    @ExceptionHandler.handle_playwright_exception("检查元素是否选中", return_on_error=False, raise_assertion=False)
    def is_checked(self, locator: LocatorInput) -> bool:
        """智能检查元素是否选中"""
        loc_desc = self._get_locator_description(locator)
        checked = self._run_locator_method(locator, "is_checked", use_timeout=False)
        if checked:
            self.logger.info(f"元素已选中: {loc_desc}")
        else:
            self.logger.warning(f"元素未选中: {loc_desc}")
        return checked

    @allure.step("选中元素")
    @ExceptionHandler.handle_playwright_exception("选中元素")
    def check(self, locator: LocatorInput, timeout: int = None):
        """智能选中元素"""
        loc_desc = self._get_locator_description(locator)
        self.logger.info(f"尝试选中元素: {loc_desc}")
        self._run_locator_method(locator, "check", timeout=timeout)
        self.logger.info(f"成功选中元素: {loc_desc}")

    @allure.step("取消选中元素")
    @ExceptionHandler.handle_playwright_exception("取消选中元素")
    def uncheck(self, locator: LocatorInput, timeout: int = None):
        """智能取消选中元素"""
        loc_desc = self._get_locator_description(locator)
        self.logger.info(f"尝试取消选中元素: {loc_desc}")
        self._run_locator_method(locator, "uncheck", timeout=timeout)
        self.logger.info(f"成功取消选中元素: {loc_desc}")

    @allure.step("悬停到元素")
    @ExceptionHandler.handle_playwright_exception("悬停到元素")
    def hover(self, locator: LocatorInput, position: dict = None, force: bool = False, timeout: int = None):
        """悬停到元素上"""
        loc_desc = self._get_locator_description(locator)
        self.logger.info(f"尝试悬停到元素: {loc_desc}")
        hover_options = {}
        if position:
            hover_options["position"] = position
        if force:
            hover_options["force"] = force
        self._run_locator_method(locator, "hover", timeout=timeout, **hover_options)
        self.logger.info(f"成功悬停到元素: {loc_desc}")

    @allure.step("悬停并等待元素出现")
    @ExceptionHandler.handle_playwright_exception("悬停并等待元素出现")
    def hover_and_wait(self, hover_locator: LocatorInput,
                       wait_locator: LocatorInput,
                       wait_timeout: int = None):
        """悬停到元素并等待另一个元素出现"""
        hover_desc = self._get_locator_description(hover_locator)
        wait_desc = self._get_locator_description(wait_locator)

        self.logger.info(f"悬停到元素: {hover_desc}")
        self._run_locator_method(hover_locator, "hover")

        self.logger.info(f"等待元素出现: {wait_desc}")
        self._run_locator_method(wait_locator, "wait_for", timeout=wait_timeout, state="visible")

        self.logger.info(f"悬停并等待成功: {hover_desc} -> {wait_desc}")
