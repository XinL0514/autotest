from pages.base_page import BasePage
from config.config import BASE_URL
from utils.element import Element
from utils.logger import Logger
logger = Logger.get_logger("JumpPage")



class JumpPage(BasePage):
    JUMPBTN = Element("text",("Window Open Test"), desc="跳转按钮", exact=True)
    VER = "[name='top']"
    FRAMELOCATOR = Element("role", ("link", "Link Test"), desc="跳转按钮", exact=True)
    
        
    def jump_to_new_page(self):
        new_page = self.click_and_handle_new_page(self.JUMPBTN)
        return new_page
    
    def verify_page(self):
       self.frame_click(self.VER, self.FRAMELOCATOR)
        

    # def get_test_frame_text(self):
    #     return self.get_text(self.TESTFREAM)
    