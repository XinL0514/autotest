import allure
from playwright.sync_api import FrameLocator
from utils.element import Element
from utils.exception_handler import FrameExceptionHandler
from typing import Union, Tuple


class IframeMixin:
    """iframe 操作"""

    def _build_frame_locator(self, frame: FrameLocator, element_locator: Union[str, Tuple[str, str], Element]):
        """在 iframe 中构建 Locator，委托给 _get_locator 并传入 frame 作为 context"""
        return self._get_locator(element_locator, context=frame)

    @allure.step("切换到 iframe")
    def switch_to_frame(self, frame_locator: str) -> FrameLocator:
        """切换到指定的 iframe，返回 FrameLocator 对象

        Args:
            frame_locator: iframe 的 CSS 选择器

        Returns:
            FrameLocator 对象
        """
        self.logger.info(f"切换到 iframe: {frame_locator}")
        frame = self.page.frame_locator(frame_locator)
        self.logger.info(f"成功切换到 iframe: {frame_locator}")
        return frame

    @allure.step("在 iframe 中点击元素")
    @FrameExceptionHandler.handle_frame_exception("在 iframe 中点击元素")
    def frame_click(self, frame_locator: str, element_locator: Union[str, Tuple[str, str], Element], timeout: int = None):
        """在指定 iframe 中点击元素"""
        loc_desc = self._get_locator_description(element_locator)
        self.logger.info(f"在 iframe '{frame_locator}' 中点击元素: {loc_desc}")

        element = element_locator if isinstance(element_locator, Element) else None
        final_timeout = self._resolve_timeout(timeout, element)

        frame = self.page.frame_locator(frame_locator)
        locator = self._build_frame_locator(frame, element_locator)
        locator.click(timeout=final_timeout)
        self.logger.info(f"成功点击 iframe 中的元素: {loc_desc}")

    @allure.step("在 iframe 中填充元素")
    @FrameExceptionHandler.handle_frame_exception("在 iframe 中填充元素")
    def frame_fill(self, frame_locator: str, element_locator: Union[str, Tuple[str, str], Element], text: str, timeout: int = None):
        """在指定 iframe 中填充输入框"""
        loc_desc = self._get_locator_description(element_locator)
        self.logger.info(f"在 iframe '{frame_locator}' 中填充元素: {loc_desc}, 内容: {text}")

        element = element_locator if isinstance(element_locator, Element) else None
        final_timeout = self._resolve_timeout(timeout, element)

        frame = self.page.frame_locator(frame_locator)
        locator = self._build_frame_locator(frame, element_locator)
        locator.fill(text, timeout=final_timeout)
        self.logger.info(f"成功填充 iframe 中的元素: {loc_desc}")

    @allure.step("获取 iframe 中元素的文本")
    @FrameExceptionHandler.handle_frame_exception("获取 iframe 中元素的文本")
    def frame_get_text(self, frame_locator: str, element_locator: Union[str, Tuple[str, str], Element], timeout: int = None) -> str:
        """获取指定 iframe 中元素的文本"""
        loc_desc = self._get_locator_description(element_locator)
        self.logger.info(f"获取 iframe '{frame_locator}' 中元素文本: {loc_desc}")

        element = element_locator if isinstance(element_locator, Element) else None
        final_timeout = self._resolve_timeout(timeout, element)

        frame = self.page.frame_locator(frame_locator)
        locator = self._build_frame_locator(frame, element_locator)
        text = locator.text_content(timeout=final_timeout)
        self.logger.info(f"成功获取文本: {text}")
        return text

    @allure.step("检查 iframe 中元素是否可见")
    @FrameExceptionHandler.handle_frame_exception("检查 iframe 中元素是否可见", return_on_error=False)
    def frame_is_visible(self, frame_locator: str, element_locator: Union[str, Tuple[str, str], Element]) -> bool:
        """检查指定 iframe 中元素是否可见"""
        loc_desc = self._get_locator_description(element_locator)

        frame = self.page.frame_locator(frame_locator)
        locator = self._build_frame_locator(frame, element_locator)
        visible = locator.is_visible()
        if visible:
            self.logger.info(f"iframe 中元素可见: {loc_desc}")
        else:
            self.logger.warning(f"iframe 中元素不可见: {loc_desc}")
        return visible

    @allure.step("等待 iframe 中元素出现")
    @FrameExceptionHandler.handle_frame_exception("等待 iframe 中元素出现")
    def frame_wait_for_selector(self, frame_locator: str, element_locator: Union[str, Tuple[str, str], Element], timeout: int = None):
        """等待 iframe 中元素出现"""
        loc_desc = self._get_locator_description(element_locator)
        self.logger.info(f"等待 iframe '{frame_locator}' 中元素出现: {loc_desc}")

        element = element_locator if isinstance(element_locator, Element) else None
        final_timeout = self._resolve_timeout(timeout, element)

        frame = self.page.frame_locator(frame_locator)
        locator = self._build_frame_locator(frame, element_locator)
        locator.wait_for(state="visible", timeout=final_timeout)
        self.logger.info(f"iframe 中元素已出现: {loc_desc}")
