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
    def test_click_mar_tab(self, page: Page):
        mar_page = MarPage(page)
        mar_page.open()
        # nowpage =  page.url
        # logger.info(f"nowpage: {nowpage}")
        visible1 = mar_page.test_fun1()
        assertion.assert_equal(visible1, True, True)
        # new_page = mar_page.click_mar_tab()
        mar_page.click_mar_tab()
        new_page = mar_page.switch_to_page_by_url("chat.baidu")
        # all_pages = mar_page.get_all_pages()
        # logger.info(f"all_pages: {all_pages}")
        new_mar_page = MarPage(new_page)
        new_mar_page.page.wait_for_timeout(5000)
        visible2, aivisable2 = new_mar_page.test_fun()
        assertion.assert_equal(visible2, True)
        assertion.assert_equal(aivisable2, False)
        mar_page.go_forward()
        # after_pages = new_mar_page.get_all_pages()
        # logger.info(f"after_pages: {after_pages}")
        
        # # pagetest = new_mar_page.switch_to_page_by_url("https://www.baidu.com/")
        # visible3, aivisable3 = new_mar_page.test_fun()        
        # assertion.assert_equal(aivisable3, True)
        # mar_page.close_all_new_windows()
        # after_pages = mar_page.get_all_pages()
        # logger.info(f"after_pages: {after_pages}")
        # assertion.assert_equal(aivisable2, True)
        # testpage = mar_page.get_all_pages()
        # logger.info(f"testpage: {testpage}")
        # afterpage = self.page.url()
        # logger.info(f"afterpage: {afterpage}")
        # testpage = mar_page.get_all_pages()
        # logger.info(f"testpage: {testpage}")
        # authenticated_page.wait_for_timeout(5000)
        # mar_tab_text = mar_page.get_mar_tab_text()
        # assertion.assert_equal(mar_tab_text, "用药记录", "用药记录页面标题验证")
        # assertion.assert_equal(mar_page.get_mar_page_title(), "用药记录", "用药记录页面标题验证")

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
        
