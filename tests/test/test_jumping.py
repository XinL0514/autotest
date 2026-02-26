import allure
from playwright.sync_api import Page
from pages.modules.test.test_page import TestPage
from pages.modules.test.jump_page import JumpPage
from utils.logger import Logger
logger = Logger.get_logger("TestJumping")


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
        jump_page.verify_page()
        jump_page.page.wait_for_load_state("domcontentloaded")
