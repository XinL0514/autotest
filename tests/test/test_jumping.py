import allure
import re
from playwright.sync_api import Page
from pages.modules.test.test_page import TestPage
from pages.modules.test.jump_page import JumpPage
from utils.assertion import Assertion
from utils.logger import Logger

logger = Logger.get_logger("TestJumping")
assertion = Assertion("TestJumping")


@allure.feature("窗口跳转")
class TestJumping:
    @allure.story("新窗口")
    @allure.title("测试点击按钮打开新窗口")
    @allure.description("点击 Window Open Test 后，验证新窗口可正常操作")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_open_new_window(self, page: Page):
        test_page = TestPage(page)
        test_page.open()
        new_page = test_page.jump_to_new_page()
        jump_page = JumpPage(new_page)
        url = jump_page.page.url
        logger.info(f"跳转页面URL: {url}")
        assertion.assert_has_url(
            jump_page.page,
            re.compile(r".*/framesTest\.htm$"),
            "新窗口URL应跳转到 framesTest 页面"
        )
        top_frame = jump_page.get_top_frame()
        assertion.assert_is_display(top_frame, jump_page.TOP_FRAME_LINK, "新窗口顶部 frame 中 Link Test 链接可见验证")
