from pages.base_page import BasePage
from config.config import BASE_URL
from utils.element import Element
from utils.logger import Logger
logger = Logger.get_logger("UploadPage")



class UploadPage(BasePage):
    UPLOADFILEBTN = Element("role",("link", "File Upload Test"), desc="上传文件按钮")
    UPLOADFILEINPUT = Element("role",("textbox", "File:"), desc="上传文件输入框")

        
    def click_switch_to_upload_file_page(self):
        new_page = self.click_and_handle_new_page(self.UPLOADFILEBTN)
        return new_page
    
    def click_upload_file_input(self):
        # self.click(self.UPLOADFILEINPUT)
        self.file_choose_file(self.UPLOADFILEINPUT, "/Users/hantongxue/Downloads/generat_sql.py")
        

    # def get_test_frame_text(self):
    #     return self.get_text(self.TESTFREAM)
    