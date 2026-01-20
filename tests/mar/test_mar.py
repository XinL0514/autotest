import allure
import pytest
from playwright.sync_api import Page
from pages.modules.mar.mar_page import MarPage
from utils.data_loader import DataLoader
from utils.logger import Logger
from utils.assertion import Assertion

logger = Logger.get_logger("TestMar")
assertion = Assertion("TestMar")


@allure.feature("用药记录")
class TestMar:
    @allure.story("用药记录")
    @allure.title("测试点击用药记录tab按钮")
    @allure.description("点击用药记录tab按钮，验证用药记录页面是否显示")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_click_mar_tab(self, authenticated_page: Page):
        mar_page = MarPage(authenticated_page)
        mar_page.open()
        nowpage =  authenticated_page.url
        logger.info(f"nowpage: {nowpage}")
        mar_page.test_fun1()
        mar_page.click_mar_tab()
        mar_page.add_medication_record("test", "10mg", "10mg", "10mg", "10mg", True)
        # checked = mar_page.assert_still_using_checkbox()
        assertion.assert_is_checked(mar_page, mar_page.MAR_STILL_USING_CHECKBOX, "当前还在使用是否是选中")
        # mar_page.click(mar_page.SAVE_MAR_BUTTON)
        # mar_page.click(mar_page.CANCEL_BUTTON)
        # mar_page.click(mar_page.DELETE_MAR_BUTTON)
        # mar_page.click(mar_page.DELETE_MAR_BUTTON)

    # @allure.story("登录失败")
    # @allure.title("测试用户使用无效凭证登录")
    # @allure.description("使用无效的用户名和密码进行登录，验证错误提示")
    # @allure.severity(allure.severity_level.NORMAL)
    # def test_login_invalid_credentials(self, page: Page):
    #     invalid_data = DataLoader.get_test_data("login_data.yaml", "invalid_user")
    #     logger.debug(f"测试数据: {invalid_data}")
    #     login_page = LoginPage(page)
    #     login_page.open()
    #     login_page.login(invalid_data["username"], invalid_data["password"])
    #     # page.wait_for_timeout(5000)
    #     error = login_page.get_error_message()
    #     assertion.assert_contains(error, invalid_data["expected_error"], "登录失败错误消息验证")
        
