from pages.base_page import BasePage
from config.config import BASE_URL
from utils.element import Element


class SelectPage(BasePage):
    SELECT_PAGE_LINK = Element("role", ("link", "Select Test"), desc="选择页面")
    SELECT_BUTTON = Element("xpath", "//select[@id='s3Id']", desc="选择入口")
    SELECTED_OPTION = Element("css", "#s3Id option:checked", desc="当前选中的选项")
    DEFAULT_OPTION_INDEX = 3
    DEFAULT_OPTION_VALUE = "o3"

    def open(self):
        """打开页面（已登录状态下直接访问）"""
        self.navigate(f"{BASE_URL}")

    def click_select_page(self):
        self.click(self.SELECT_PAGE_LINK)

    def click_select_button(self, index: int = None):
        target_index = self.DEFAULT_OPTION_INDEX if index is None else index
        self.select_option(self.SELECT_BUTTON, index=target_index)
