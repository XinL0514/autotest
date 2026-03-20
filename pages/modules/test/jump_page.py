from pages.base_page import BasePage
from utils.element import Element


class JumpPage(BasePage):
    JUMP_BTN = Element("text", "Window Open Test", desc="跳转按钮", exact=True)
    TOP_FRAME = "[name='top']"   # iframe CSS选择器
    TOP_FRAME_LINK = Element("role", ("link", "Link Test"), desc="顶部frame中的Link Test链接", exact=True)

    def jump_to_new_page(self):
        return self.click_and_handle_new_page(self.JUMP_BTN)

    def get_top_frame(self):
        """返回顶部 frame 上下文，供测试中操作或断言 frame 内元素。"""
        return self.frame(self.TOP_FRAME)

    def verify_page(self):
        self.frame(self.TOP_FRAME).click(self.TOP_FRAME_LINK)
