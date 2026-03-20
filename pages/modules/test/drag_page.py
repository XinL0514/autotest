from pages.base_page import BasePage
from utils.element import Element


class DragPage(BasePage):
    DRAG_BTN = Element("text", "Drag me", desc="拖拽按钮", exact=True)
    DROP_BTN = Element("text", "Item 1", desc="放置按钮", exact=True)
    DROP_TARGET = Element("css", ".item", desc="第一个放置区域", first=True)

    def drag_to_btn(self):
        self.drag_to(self.DRAG_BTN, self.DROP_BTN)
