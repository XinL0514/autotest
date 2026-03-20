import allure
from playwright.sync_api import Page
from pages.modules.test.test_page import TestPage
from pages.modules.test.hover_page import HoverPage
from utils.logger import Logger
from utils.assertion import Assertion

logger = Logger.get_logger("TestHover")
assertion = Assertion("TestHover")


@allure.feature("悬停")
class TestHover:
    @allure.story("悬停")
    @allure.title("测试悬停按钮")
    @allure.description("测试悬停按钮，验证悬停按钮是否显示")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_hover_btn(self, page: Page):
        test_page = TestPage(page)
        test_page.open()
        test_page.click_hover_page()
        hover_page = HoverPage(page)
        assertion.assert_is_display(hover_page, hover_page.HOVER_BTN, "悬停目标元素可见验证")
        hover_page.hover_to_btn()
        assertion.assert_has_css(
            hover_page, hover_page.HOVER_BTN,
            "background-color", "rgb(0, 128, 0)",
            "悬停后目标元素背景变绿验证"
        )
