from allure import label
from pages.base_page import BasePage
from config.config import BASE_URL
from utils.element import Element
from utils.logger import Logger
logger = Logger.get_logger("MarPage")



class SelectPage(BasePage):
    SELECTPAGE = Element("role",("link","Select Test"), desc="选择页面")
    SELECTBTN = Element("xpath", "//select[@id='s3Id']", desc="选择入口")
    SELECTBTN_SELECT_ONE = "o3"
    SELECTBTN_SELECT_ONE = 3
    SELECTOPTION = Element("role",("option","Option 1"), desc="选择选项")

    
    
    def open(self):
        """打开页面（已登录状态下直接访问）"""
        self.navigate(f"{BASE_URL}")
    
    def click_select_page(self):
        self.click(self.SELECTPAGE)

    def click_select_button(self):
        self.select_option(self.SELECTBTN, index=self.SELECTBTN_SELECT_ONE)
        
    def click_test_verify_button(self):
        self.click(self.IFRAEMCLICK)
        
    