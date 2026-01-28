from pages.base_page import BasePage
from config.config import BASE_URL
from utils.element import Element
from utils.logger import Logger
logger = Logger.get_logger("DragPage")



class DragPage(BasePage):
    DRAGBTN = Element("text", "Drag me", desc="拖拽按钮", exact=True)
    DROPBTN = Element("text", "Item 1", desc="放置按钮", exact=True)
    
        
    def drag_to_btn(self):
        self.drag_to(self.DRAGBTN,self.DROPBTN)
    
    # def verify_page(self):
    #    self.frame_click(self.VER, self.FRAMELOCATOR)
        

    # def get_test_frame_text(self):
    #     return self.get_text(self.TESTFREAM)
    