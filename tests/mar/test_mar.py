import allure
import pytest
from playwright.sync_api import Page
from pages.modules.mar.mar_page import MarPage
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
    def test_click_mar_tab(self, authenticated_page: Page):
        mar_data = DataLoader.get_test_data("mar/mar_data.yaml", "mar_data")
        mar_name = mar_data["mar_name"] + timeStamp()
        mar_page = MarPage(authenticated_page)
        mar_page.open()
        mar_page.click_mar_tab()
        checked = mar_page.add_medication_record(mar_name, mar_data["mar_dosage"], mar_data["mar_frequency"], mar_data["mar_purpose"], mar_data["mar_side_effects"])
        assertion.assert_true(checked, "当前还在使用是否是选中")
        mar_page.click_save_btn()
        mar_page.page.wait_for_timeout(500)
        medication_name = mar_page.get_medication_name()
        assertion.assert_equal(medication_name, mar_name, "药物名称是否正确")
        deleted_success_dialog = mar_page.delete_last_medication()
        assertion.assert_true(deleted_success_dialog, "删除是否成功")
        deleted_medication_name = mar_page.get_medication_name()
        assertion.assert_not_equal(deleted_medication_name, mar_name, "删除后药物名称是否正确")