import allure
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
    @allure.description("使用有效的工号和密码进行登录，验证登录成功")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_success(self, page: Page):
        success_data = DataLoader.get_test_data("login/login_data.yaml", "aixmy_login_test")
        login_page = LoginPage(page)
        login_page.open()
        login_page.login(employee_id=success_data["employee_id"], password=success_data["password"])
