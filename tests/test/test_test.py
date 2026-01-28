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
        upload_test_page = test_page.click_switch_to_upload_file_page()
        UploadPage(upload_test_page).click_upload_file_input()
        # test_page.click_test_verify_button()
        # test_page.frame_click_link()
        # text = test_page.get_test_verify_button_text()
        # logger.info(f"按钮文本: {text}")
        test_page.page.wait_for_timeout(5000)
        # pages = test_page.get_page_by_url()
        # logger.info(f"页面数量: {len(pages)}")
        # test_page.click_test_frame_button()
        # test_page.click_test_frame_button()