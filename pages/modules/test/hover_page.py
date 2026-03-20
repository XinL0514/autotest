from pages.base_page import BasePage
from utils.element import Element


class HoverPage(BasePage):
    HOVER_BTN = Element("text", "Hi Kamlesh", desc="悬停按钮", exact=True)

    def hover_to_btn(self):
        self.hover(self.HOVER_BTN)
