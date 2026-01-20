import allure
import pytest
from playwright.sync_api import Page
from pages.common.login.login_page import LoginPage
from utils.data_loader import DataLoader
from utils.logger import Logger
from utils.assertion import Assertion

logger = Logger.get_logger("TestLogin")
assertion = Assertion("TestLogin")


@allure.feature("用户登录")
class TestLogin:
    @allure.story("成功登录")
    @allure.title("测试用户成功登录")
    @allure.description("使用有效的用户名和密码进行登录，验证登录成功")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_success(self, page: Page):
        success_data = DataLoader.get_test_data("login/login_data.yaml", "valid_user")
        login_page = LoginPage(page)
        login_page.open()
        login_page.login(success_data["username"], success_data["password"])
        # page.wait_for_timeout(5000)
        success = login_page.get_success_message()
        assertion.assert_equal(success, success_data["expected_success"], "登录成功消息验证")

    @allure.story("登录失败")
    @allure.title("测试用户使用无效凭证登录")
    @allure.description("使用无效的用户名和密码进行登录，验证错误提示")
    @allure.severity(allure.severity_level.NORMAL)
    def test_login_invalid_credentials(self, page: Page):
        invalid_data = DataLoader.get_test_data("login/login_data.yaml", "invalid_user")
        logger.debug(f"测试数据: {invalid_data}")
        login_page = LoginPage(page)
        login_page.open()
        login_page.login(invalid_data["username"], invalid_data["password"])
        # page.wait_for_timeout(5000)
        error = login_page.get_error_message()
        assertion.assert_contains(error, invalid_data["expected_error"], "登录失败错误消息验证")        
