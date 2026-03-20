import allure
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
        mar_page.add_medication_record(
            mar_name,
            mar_data["mar_dosage"],
            mar_data["mar_frequency"],
            mar_data["mar_purpose"],
            mar_data["mar_side_effects"]
        )
        assertion.assert_is_checked(mar_page, mar_page.MAR_STILL_USING_CHECKBOX, "当前仍在使用复选框默认选中验证")
        mar_page.click_save_btn()
        assertion.assert_has_text(mar_page, mar_page.MEDICATION_NAME, mar_name, "新增用药记录名称验证")
        mar_page.delete_last_medication()
        assertion.assert_is_display(mar_page, mar_page.DELETE_SUCCESS_BUTTON, "删除成功提示验证")
        assertion.assert_not_has_text(mar_page, mar_page.MEDICATION_NAME, mar_name, "删除后最新药物名称不应仍为刚创建记录")
