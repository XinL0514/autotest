from pages.base_page import BasePage
from config.config import BASE_URL
from utils.element import Element
from utils.logger import Logger
logger = Logger.get_logger("HoverPage")



class HoverPage(BasePage):
    # 合并重复的定位器定义
    HOVERBTN = Element("text", "Hi Kamlesh", desc="悬停按钮", exact=True)
    # WELCOME_TEXT 与 HOVERBTN 完全相同，使用别名
    WELCOME_TEXT = HOVERBTN


    def hover_to_btn(self):
        self.hover(self.WELCOME_TEXT)

    # def verify_page(self):
    #    self.frame_click(self.VER, self.FRAMELOCATOR)


    # def get_test_frame_text(self):
    #     return self.get_text(self.TESTFREAM)