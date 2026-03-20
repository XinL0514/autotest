from pages.base_page import BasePage
from config.config import BASE_URL, DEFAULT_UPLOAD_FILE_NAME
from utils.element import Element


class TestPage(BasePage):
    __test__ = False

    FRAME_TEST = Element("text", "Frames Test", desc="Frame入口", exact=True)
    IFRAME_TEST = Element("text", "IFrames Test", desc="IFrame入口", exact=True)
    FRAME_LOCATOR = '[src="index.htm"] >> nth=0'   # iframe CSS选择器
    FRAME_LINK = Element("role", ("link", "Link Test"), desc="Frame链接")
    IFRAME_CLICK = Element("role", ("button", "Click me"), desc="IFrame点击按钮")
    IFRAME_CLICK_TEXT = Element("css", "#checkRecord", desc="IFrame点击后验证文本")
    UPLOAD_FILE_BTN = Element("role", ("link", "File Upload Test"), desc="上传文件入口")
    UPLOAD_FILE_INPUT = Element("css", "#file", desc="文件上传输入框")
    JUMP_HEADING = Element("role", ("heading", "Sahi Tests"), desc="Sahi Tests标题")
    JUMP_BTN = Element("text", "Window Open Test", desc="跳转按钮", exact=True)
    HOVER_PAGE = Element("role", ("link", "Mouse over"), desc="悬停入口")
    DRAG_PAGE = Element("role", ("link", "Drag Drop Test"), desc="拖拽入口")

    def open(self):
        self.navigate(f"{BASE_URL}")

    def click_test_frame(self):
        self.click(self.IFRAME_TEST)

    def click_test_verify_button(self):
        self.frame(self.FRAME_LOCATOR).click(self.IFRAME_CLICK)

    def get_test_verify_button_text(self):
        return self.frame(self.FRAME_LOCATOR).get_text(self.IFRAME_CLICK_TEXT)

    def frame_click_link(self):
        self.frame(self.FRAME_LOCATOR).click(self.FRAME_LINK)

    def click_switch_to_upload_file_page(self):
        self.click(self.UPLOAD_FILE_BTN)

    def click_upload_file_input(self, file_name: str = DEFAULT_UPLOAD_FILE_NAME):
        self.file_choose_file(self.UPLOAD_FILE_INPUT, file_name)

    def click_test_jump_button(self):
        self.click(self.JUMP_HEADING)

    def jump_to_new_page(self):
        return self.click_and_handle_new_page(self.JUMP_BTN)

    def click_hover_page(self):
        self.click(self.HOVER_PAGE)

    def click_drag_page(self):
        self.click(self.DRAG_PAGE)
