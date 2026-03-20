from pages.base_page import BasePage
from config.config import DEFAULT_UPLOAD_FILE_NAME
from utils.element import Element


class UploadPage(BasePage):
    UPLOAD_FILE_BTN = Element("role", ("link", "File Upload Test"), desc="上传文件按钮")
    UPLOAD_FILE_INPUT = Element("role", ("textbox", "File:"), desc="上传文件输入框")

    def click_switch_to_upload_file_page(self):
        return self.click_and_handle_new_page(self.UPLOAD_FILE_BTN)

    def click_upload_file_input(self, file_name: str = DEFAULT_UPLOAD_FILE_NAME):
        file_path = self.build_upload_file_path(file_name)
        self.file_choose_file(self.UPLOAD_FILE_INPUT, file_path)
