import allure
from playwright.sync_api import Page
from pages.modules.blood.blood_entry_page import BloodEntryPage
from utils.data_loader import DataLoader
from utils.logger import Logger
from utils.assertion import Assertion

logger = Logger.get_logger("TestBloodSubmit")
assertion = Assertion("TestBloodSubmit")


@allure.feature("血常规模块")
@allure.story("正常提交")
class TestBloodSubmit:
    """血常规录入 - 正常提交测试"""

    @allure.title("测试提交正常范围的血常规数据")
    @allure.description("使用正常范围的血常规指标，验证AI分析成功")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_submit_normal_blood(self, authenticated_page: Page):
        blood_data = DataLoader.get_test_data("blood/blood_data.yaml", "normal_blood")
        blood_page = BloodEntryPage(authenticated_page)
        blood_page.open()
        blood_page.submit_blood_entry(
            plt=blood_data["plt"],
            wbc=blood_data["wbc"],
            rbc=blood_data["rbc"],
            hgb=blood_data["hgb"]
        )
        assertion.assert_contains_text(
            blood_page, blood_page.SUCCESS_MESSAGE,
            blood_data["expected_result"],
            "血常规提交成功提示验证"
        )
        logger.info("血常规数据提交成功")
