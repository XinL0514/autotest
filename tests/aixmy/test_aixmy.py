import allure
from playwright.sync_api import Page
from pages.modules.aixmy.aixmy_page import AixmyPage
from utils.data_loader import DataLoader
from utils.logger import Logger
from utils.assertion import Assertion

logger = Logger.get_logger("TestAixmy")
assertion = Assertion("TestAixmy")


@allure.feature("Aixmy 平台")
class TestAixmy:

    @allure.story("文生图")
    @allure.title("登录后进入课堂并使用文生图功能")
    @allure.description("完整流程：登录 → 开始上课 → 选择课件 → 进入课堂 → iframe 内发送文生图提示词")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_wentu_in_classroom(self, page: Page):
        data = DataLoader.get_test_data("aixmy/aixmy_data.yaml", "wentu_test")
        aixmy_page = AixmyPage(page)

        aixmy_page.open()
        aixmy_page.click_my_avatar()
        aixmy_page.click_login_entry()
        aixmy_page.login(data["employee_id"], data["password"])

        aixmy_page.click_start_class()
        aixmy_page.click_first_work()
        aixmy_page.launch_courseware()

        aixmy_page.send_wentu_prompt(data["prompt_text"])

        classroom = aixmy_page.get_classroom_frame()
        # 等待图片生成完成（重新生成按钮出现即代表生成成功），最长等 60 秒
        classroom.wait_for_selector(aixmy_page.REGENERATE_BUTTON, timeout=60000)
        assertion.assert_is_display(classroom, aixmy_page.REGENERATE_BUTTON, "文生图生成完成，重新生成按钮可见")

        aixmy_page.close_classroom()
        aixmy_page.page.wait_for_timeout(5000)
