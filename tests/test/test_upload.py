import allure
import pytest
from playwright.sync_api import Page
from pages.common.uploadfile import upload_page
from pages.modules.test.test_page import TestPage
from pages.common.uploadfile.upload_page import UploadPage
from utils.data_loader import DataLoader
from utils.logger import Logger
from utils.assertion import Assertion
from utils.time_utils import timeStamp
logger = Logger.get_logger("TestUpload")
assertion = Assertion("TestUpload")


@allure.feature("上传文件")
class TestUpload:
    @allure.story("上传文件")
    @allure.title("测试上传文件")
    @allure.description("点击上传文件按钮，验证上传文件页面是否显示")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_upload_file(self, page: Page):
        test_page = TestPage(page)
        test_page.open()
        test_page.click_switch_to_upload_file_page2()
        test_page.page.wait_for_timeout(500)
        url = test_page.page.url
        logger.info(f"上传文件页面URL: {url}")
        test_page.click_upload_file_input()
        
        test_page.page.wait_for_timeout(5000)
        