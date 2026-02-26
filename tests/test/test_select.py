import allure
import pytest
from playwright.sync_api import Page
from pages.modules.test.test_page import TestPage
from pages.common.uploadfile.upload_page import UploadPage
from pages.modules.test.jump_page import JumpPage
from utils.data_loader import DataLoader
from pages.modules.test.select_page import SelectPage
from utils.logger import Logger
from utils.assertion import Assertion
from utils.time_utils import timeStamp
logger = Logger.get_logger("TestSelect")
assertion = Assertion("TestSelect")


@allure.feature("选择")
class TestSelect:
    @allure.story("选择")
    @allure.title("测试选择按钮")
    @allure.description("测试选择按钮，验证选择按钮是否显示")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_click_select_button(self, page: Page):
        test_page = SelectPage(page)
        test_page.open()
        test_page.click_select_page()
        test_page.click_select_button()
        test_page.page.wait_for_load_state("domcontentloaded")
