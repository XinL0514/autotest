import allure
import pytest
from playwright.sync_api import Page
from pages.modules.test.test_page import TestPage
from pages.common.uploadfile.upload_page import UploadPage
from pages.modules.test.jump_page import JumpPage
from utils.data_loader import DataLoader
from utils.logger import Logger
from utils.assertion import Assertion
from utils.time_utils import timeStamp
logger = Logger.get_logger("TestMar")
assertion = Assertion("TestMar")


@allure.feature("用药记录")
class TestMar:
    @allure.story("用药记录")
    @allure.title("测试点击用药记录tab按钮")
    @allure.description("点击用药记录tab按钮，验证用药记录页面是否显示")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_click_mar_tab(self, page: Page):
        test_page = TestPage(page)
        test_page.open()
        new_page = test_page.jump_to_new_page()
        jump_page = JumpPage(new_page)
        url = jump_page.page.url
        logger.info(f"跳转页面URL: {url}")
        jump_page.verify_page()
        jump_page.page.wait_for_load_state("domcontentloaded")
