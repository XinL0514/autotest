from pages.base_page import BasePage


class FrameContext(BasePage):
    """Frame 上下文代理，让 iframe 内的操作与普通页面完全一致。

    通过 page_obj.frame(frame_css) 获取，不要直接实例化。

    Usage:
        frame = page_obj.frame('[src="index.htm"]')
        frame.click(SOME_ELEMENT)
        frame.fill(INPUT_ELEMENT, "text")
        frame.get_text(TEXT_ELEMENT)

        # 断言也完全相同
        assertion.assert_has_text(frame, ELEMENT, "expected", "描述")
        assertion.assert_is_display(frame, ELEMENT, "描述")

        # frame 用完后直接回到主页面，无需任何"切回"操作
        page_obj.click(MAIN_PAGE_ELEMENT)
    """

    def __init__(self, page_obj, frame_css: str):
        # 复用父页面实例的状态，不走 BasePage.__init__
        self.page = page_obj.page
        self.timeout = page_obj.timeout
        self.logger = page_obj.logger
        self._frame = self.page.frame_locator(frame_css)

    def _get_locator(self, locator, context=None):
        """始终以 frame 为定位上下文（除非显式传入其他 context）。"""
        return super()._get_locator(locator, context=context or self._frame)
