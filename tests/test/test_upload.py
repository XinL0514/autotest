import allure
from playwright.sync_api import Page
from pages.modules.test.test_page import TestPage
from utils.logger import Logger
from utils.assertion import Assertion
logger = Logger.get_logger("TestUpload")
assertion = Assertion("TestUpload")


@allure.feature("上传文件")
class TestUpload:
    @allure.story("上传文件")
    @allure.title("测试上传文件")
    @allure.description("点击上传文件按钮，验证上传文件页面是否显示")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_upload_file(self, page: Page):
        test_page = TestPage(page)
        test_page.open()
        test_page.click_switch_to_upload_file_page()
        # 等待原生上传窗口出来
        test_page.wait_for_selector(test_page.UPLOADFILEINPUT, timeout=5000)
        url = test_page.page.url
        logger.info(f"上传文件页面URL: {url}")
        test_page.click_upload_file_input("upload_sample.txt")
        uploaded_value = test_page.get_input_value(test_page.UPLOADFILEINPUT, timeout=5000)
        assertion.assert_true(bool(uploaded_value), "上传后文件输入框应包含文件路径")
        
