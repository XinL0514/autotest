import allure
from playwright.sync_api import Page
from pages.modules.test.test_page import TestPage
from pages.modules.test.drag_page import DragPage
from utils.logger import Logger
from utils.assertion import Assertion
logger = Logger.get_logger("TestDrag")
assertion = Assertion("TestDrag")


@allure.feature("拖拽")
class TestDrag:
    @allure.story("拖拽")
    @allure.title("测试拖拽按钮")
    @allure.description("测试拖拽按钮，验证拖拽按钮是否显示")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_drag_btn(self, page: Page):
        test_page = TestPage(page)
        test_page.open()
        test_page.click_drag_page()
        drag_page = DragPage(page)
        drag_page.drag_to_btn()
        drag_page.page.wait_for_load_state("domcontentloaded")
