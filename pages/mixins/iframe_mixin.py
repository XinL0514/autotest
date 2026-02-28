import allure
from playwright.sync_api import FrameLocator
from pages.mixins.locator_mixin import LocatorInput
from utils.exception_handler import FrameExceptionHandler
from typing import Optional


class IframeMixin:
    """iframe 操作"""

    def _run_frame_locator_method(
        self,
        frame_locator: str,
        element_locator: LocatorInput,
        method_name: str,
        *args,
        timeout: int = None,
        use_timeout: bool = True,
        **kwargs,
    ):
        """在指定 iframe 上下文中，复用统一 Locator 执行管道"""
        frame = self.switch_to_frame(frame_locator)
        return self._run_locator_method(
            element_locator,
            method_name,
            *args,
            timeout=timeout,
            context=frame,
            use_timeout=use_timeout,
            **kwargs,
        )

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
    def frame_click(self, frame_locator: str, element_locator: LocatorInput, timeout: int = None):
        """在指定 iframe 中点击元素"""
        loc_desc = self._get_locator_description(element_locator)
        self.logger.info(f"在 iframe '{frame_locator}' 中点击元素: {loc_desc}")
        self._run_frame_locator_method(frame_locator, element_locator, "click", timeout=timeout)
        self.logger.info(f"成功点击 iframe 中的元素: {loc_desc}")

    @allure.step("在 iframe 中填充元素")
    @FrameExceptionHandler.handle_frame_exception("在 iframe 中填充元素")
    def frame_fill(self, frame_locator: str, element_locator: LocatorInput, text: str, timeout: int = None):
        """在指定 iframe 中填充输入框"""
        loc_desc = self._get_locator_description(element_locator)
        self.logger.info(f"在 iframe '{frame_locator}' 中填充元素: {loc_desc}, 内容: {text}")
        self._run_frame_locator_method(frame_locator, element_locator, "fill", text, timeout=timeout)
        self.logger.info(f"成功填充 iframe 中的元素: {loc_desc}")

    @allure.step("获取 iframe 中元素的文本")
    @FrameExceptionHandler.handle_frame_exception("获取 iframe 中元素的文本")
    def frame_get_text(self, frame_locator: str, element_locator: LocatorInput, timeout: int = None) -> Optional[str]:
        """获取指定 iframe 中元素的文本"""
        loc_desc = self._get_locator_description(element_locator)
        self.logger.info(f"获取 iframe '{frame_locator}' 中元素文本: {loc_desc}")
        text = self._run_frame_locator_method(frame_locator, element_locator, "text_content", timeout=timeout)
        self.logger.info(f"成功获取文本: {text}")
        return text

    @allure.step("检查 iframe 中元素是否可见")
    @FrameExceptionHandler.handle_frame_exception("检查 iframe 中元素是否可见", return_on_error=False)
    def frame_is_visible(self, frame_locator: str, element_locator: LocatorInput) -> bool:
        """检查指定 iframe 中元素是否可见"""
        loc_desc = self._get_locator_description(element_locator)
        visible = self._run_frame_locator_method(
            frame_locator,
            element_locator,
            "is_visible",
            use_timeout=False,
        )
        if visible:
            self.logger.info(f"iframe 中元素可见: {loc_desc}")
        else:
            self.logger.warning(f"iframe 中元素不可见: {loc_desc}")
        return visible

    @allure.step("等待 iframe 中元素出现")
    @FrameExceptionHandler.handle_frame_exception("等待 iframe 中元素出现")
    def frame_wait_for_selector(self, frame_locator: str, element_locator: LocatorInput, timeout: int = None):
        """等待 iframe 中元素出现"""
        loc_desc = self._get_locator_description(element_locator)
        self.logger.info(f"等待 iframe '{frame_locator}' 中元素出现: {loc_desc}")
        self._run_frame_locator_method(frame_locator, element_locator, "wait_for", timeout=timeout, state="visible")
        self.logger.info(f"iframe 中元素已出现: {loc_desc}")
