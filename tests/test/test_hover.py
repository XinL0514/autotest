import allure
import pytest
from playwright.sync_api import Page
from pages.modules.test.test_page import TestPage
from pages.modules.test.hover_page import HoverPage
from utils.data_loader import DataLoader
from utils.logger import Logger
from utils.assertion import Assertion
from utils.time_utils import timeStamp
logger = Logger.get_logger("TestMar")
assertion = Assertion("TestMar")


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
        hover_page.hover_to_btn()
        hover_page.page.wait_for_timeout(5000)