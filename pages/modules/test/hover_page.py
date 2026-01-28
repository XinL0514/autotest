from pages.base_page import BasePage
from config.config import BASE_URL
from utils.element import Element
from utils.logger import Logger
logger = Logger.get_logger("HoverPage")



class HoverPage(BasePage):
    HOVERBTN = Element("text", "Hi Kamlesh", desc="悬停按钮", exact=True)
    WELCOME_TEXT = Element(
    "text", "Hi Kamlesh",
    desc="欢迎语",
    exact=True  # 只匹配 "欢迎回来"，不匹配 "欢迎回来，张三"
)
    
        
    def hover_to_btn(self):
        self.hover(self.WELCOME_TEXT)
    
    # def verify_page(self):
    #    self.frame_click(self.VER, self.FRAMELOCATOR)
        

    # def get_test_frame_text(self):
    #     return self.get_text(self.TESTFREAM)
    