import allure
from playwright.sync_api import Locator
from utils.element import Element
from utils.exception_handler import ExceptionHandler
from typing import Union, Tuple, Optional


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
    def click(self, locator: Union[str, Tuple[str, str], Element], timeout: int = None):
        """智能点击元素 - 支持 CSS/XPath 字符串、Role 元组或 Element 对象"""
        loc_desc = self._get_locator_description(locator)
        self.logger.info(f"尝试点击元素: {loc_desc}")
        element = locator if isinstance(locator, Element) else None
        final_timeout = self._resolve_timeout(timeout, element)
        self._get_locator(locator).click(timeout=final_timeout)
        self.logger.info(f"成功点击元素: {loc_desc}")

    @allure.step("填充元素")
    @ExceptionHandler.handle_playwright_exception("填充元素")
    def fill(self, locator: Union[str, Tuple[str, str], Element], text: str, timeout: int = None):
        """智能填充输入框 - 支持 CSS/XPath 字符串、Role 元组或 Element 对象"""
        loc_desc = self._get_locator_description(locator)
        self.logger.info(f"尝试填充元素: {loc_desc}, 内容: {text}")
        element = locator if isinstance(locator, Element) else None
        final_timeout = self._resolve_timeout(timeout, element)
        self._get_locator(locator).fill(text, timeout=final_timeout)
        self.logger.info(f"成功填充元素: {loc_desc}")

    @allure.step("获取元素文本")
    @ExceptionHandler.handle_playwright_exception("获取元素文本")
    def get_text(self, locator: Union[str, Tuple[str, str], Element], timeout: int = None) -> str:
        """智能获取元素文本 - 支持 CSS/XPath 字符串、Role 元组或 Element 对象"""
        loc_desc = self._get_locator_description(locator)
        self.logger.info(f"尝试获取元素文本: {loc_desc}")
        element = locator if isinstance(locator, Element) else None
        final_timeout = self._resolve_timeout(timeout, element)
        text = self._get_locator(locator).text_content(timeout=final_timeout)
        self.logger.info(f"成功获取文本: {loc_desc}, 内容: {text}")
        return text

    @allure.step("检查元素可见性")
    @ExceptionHandler.handle_playwright_exception("检查元素可见性", return_on_error=False, raise_assertion=False)
    def is_visible(self, locator: Union[str, Tuple[str, str], Element]) -> bool:
        """智能检查元素是否可见"""
        loc_desc = self._get_locator_description(locator)
        visible = self._get_locator(locator).is_visible()
        if visible:
            self.logger.info(f"元素可见: {loc_desc}")
        else:
            self.logger.warning(f"元素不可见: {loc_desc}")
        return visible

    @allure.step("等待元素出现")
    @ExceptionHandler.handle_playwright_exception("等待元素出现")
    def wait_for_selector(self, locator: Union[str, Tuple[str, str], Element], timeout: int = None):
        """智能等待元素出现"""
        loc_desc = self._get_locator_description(locator)
        self.logger.info(f"等待元素出现: {loc_desc}")
        element = locator if isinstance(locator, Element) else None
        final_timeout = self._resolve_timeout(timeout, element)
        self._get_locator(locator).wait_for(state="visible", timeout=final_timeout)
        self.logger.info(f"元素已出现: {loc_desc}")

    @allure.step("双击元素")
    @ExceptionHandler.handle_playwright_exception("双击元素")
    def double_click(self, locator: Union[str, Tuple[str, str], Element], timeout: int = None):
        """智能双击元素"""
        loc_desc = self._get_locator_description(locator)
        self.logger.info(f"尝试双击元素: {loc_desc}")
        element = locator if isinstance(locator, Element) else None
        final_timeout = self._resolve_timeout(timeout, element)
        self._get_locator(locator).dblclick(timeout=final_timeout)
        self.logger.info(f"成功双击元素: {loc_desc}")

    @allure.step("右键点击元素")
    @ExceptionHandler.handle_playwright_exception("右键点击元素")
    def right_click(self, locator: Union[str, Tuple[str, str], Element], timeout: int = None):
        """智能右键点击元素"""
        loc_desc = self._get_locator_description(locator)
        self.logger.info(f"尝试右键点击元素: {loc_desc}")
        element = locator if isinstance(locator, Element) else None
        final_timeout = self._resolve_timeout(timeout, element)
        self._get_locator(locator).click(button="right", timeout=final_timeout)
        self.logger.info(f"成功右键点击元素: {loc_desc}")

    @allure.step("获取元素属性")
    @ExceptionHandler.handle_playwright_exception("获取元素属性")
    def get_attribute(self, locator: Union[str, Tuple[str, str], Element], attribute: str, timeout: int = None) -> Optional[str]:
        """智能获取元素属性值"""
        loc_desc = self._get_locator_description(locator)
        self.logger.info(f"尝试获取元素属性: {loc_desc}, 属性名: {attribute}")
        element = locator if isinstance(locator, Element) else None
        final_timeout = self._resolve_timeout(timeout, element)
        value = self._get_locator(locator).get_attribute(attribute, timeout=final_timeout)
        self.logger.info(f"成功获取属性: {loc_desc}, {attribute}={value}")
        return value

    @allure.step("获取输入框的值")
    @ExceptionHandler.handle_playwright_exception("获取输入框的值")
    def get_input_value(self, locator: Union[str, Tuple[str, str], Element], timeout: int = None) -> str:
        """智能获取输入框当前值"""
        loc_desc = self._get_locator_description(locator)
        self.logger.info(f"尝试获取输入框的值: {loc_desc}")
        element = locator if isinstance(locator, Element) else None
        final_timeout = self._resolve_timeout(timeout, element)
        value = self._get_locator(locator).input_value(timeout=final_timeout)
        self.logger.info(f"成功获取输入框的值: {loc_desc}, 值: {value}")
        return value

    @allure.step("检查元素是否选中")
    @ExceptionHandler.handle_playwright_exception("检查元素是否选中", return_on_error=False, raise_assertion=False)
    def is_checked(self, locator: Union[str, Tuple[str, str], Element]) -> bool:
        """智能检查元素是否选中"""
        loc_desc = self._get_locator_description(locator)
        checked = self._get_locator(locator).is_checked()
        if checked:
            self.logger.info(f"元素已选中: {loc_desc}")
        else:
            self.logger.warning(f"元素未选中: {loc_desc}")
        return checked

    @allure.step("选中元素")
    @ExceptionHandler.handle_playwright_exception("选中元素")
    def check(self, locator: Union[str, Tuple[str, str], Element], timeout: int = None):
        """智能选中元素"""
        loc_desc = self._get_locator_description(locator)
        self.logger.info(f"尝试选中元素: {loc_desc}")
        element = locator if isinstance(locator, Element) else None
        final_timeout = self._resolve_timeout(timeout, element)
        self._get_locator(locator).check(timeout=final_timeout)
        self.logger.info(f"成功选中元素: {loc_desc}")

    @allure.step("取消选中元素")
    @ExceptionHandler.handle_playwright_exception("取消选中元素")
    def uncheck(self, locator: Union[str, Tuple[str, str], Element], timeout: int = None):
        """智能取消选中元素"""
        loc_desc = self._get_locator_description(locator)
        self.logger.info(f"尝试取消选中元素: {loc_desc}")
        element = locator if isinstance(locator, Element) else None
        final_timeout = self._resolve_timeout(timeout, element)
        self._get_locator(locator).uncheck(timeout=final_timeout)
        self.logger.info(f"成功取消选中元素: {loc_desc}")

    @allure.step("悬停到元素")
    @ExceptionHandler.handle_playwright_exception("悬停到元素")
    def hover(self, locator: Union[str, Tuple[str, str], Element], position: dict = None, force: bool = False, timeout: int = None):
        """悬停到元素上"""
        loc_desc = self._get_locator_description(locator)
        self.logger.info(f"尝试悬停到元素: {loc_desc}")
        element = locator if isinstance(locator, Element) else None
        final_timeout = self._resolve_timeout(timeout, element)
        hover_options = {"timeout": final_timeout}
        if position:
            hover_options["position"] = position
        if force:
            hover_options["force"] = force
        self._get_locator(locator).hover(**hover_options)
        self.logger.info(f"成功悬停到元素: {loc_desc}")

    @allure.step("悬停并等待元素出现")
    @ExceptionHandler.handle_playwright_exception("悬停并等待元素出现")
    def hover_and_wait(self, hover_locator: Union[str, Tuple[str, str], Element],
                       wait_locator: Union[str, Tuple[str, str], Element],
                       wait_timeout: int = None):
        """悬停到元素并等待另一个元素出现"""
        hover_desc = self._get_locator_description(hover_locator)
        wait_desc = self._get_locator_description(wait_locator)

        hover_element = hover_locator if isinstance(hover_locator, Element) else None
        hover_timeout = self._resolve_timeout(None, hover_element)

        wait_element = wait_locator if isinstance(wait_locator, Element) else None
        final_wait_timeout = self._resolve_timeout(wait_timeout, wait_element)

        self.logger.info(f"悬停到元素: {hover_desc}")
        self._get_locator(hover_locator).hover(timeout=hover_timeout)

        self.logger.info(f"等待元素出现: {wait_desc}")
        self._get_locator(wait_locator).wait_for(state="visible", timeout=final_wait_timeout)

        self.logger.info(f"悬停并等待成功: {hover_desc} -> {wait_desc}")
