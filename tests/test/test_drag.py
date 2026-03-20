import allure
import re
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
        assertion.assert_has_text(drag_page, drag_page.DROP_TARGET, "dropped", "拖拽目标区域文本更新验证")
        assertion.assert_has_class(
            drag_page, drag_page.DROP_TARGET,
            re.compile(r".*dropped.*"),
            "拖拽目标区域样式更新验证"
        )
