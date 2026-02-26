import allure
from playwright.sync_api import Page
from pages.modules.test.test_page import TestPage
from pages.common.uploadfile.upload_page import UploadPage
from utils.logger import Logger
logger = Logger.get_logger("TestUploadByNewPage")


@allure.feature("上传文件")
class TestUploadByNewPage:
    @allure.story("新窗口上传")
    @allure.title("测试新窗口上传文件")
    @allure.description("点击 File Upload Test 新开页面并执行上传")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_upload_file_in_new_window(self, page: Page):
        test_page = TestPage(page)
        test_page.open()
        upload_test_page = test_page.click_switch_to_upload_file_page()
        UploadPage(upload_test_page).click_upload_file_input()
        # test_page.click_test_verify_button()
        # test_page.frame_click_link()
        # text = test_page.get_test_verify_button_text()
        # logger.info(f"按钮文本: {text}")
        test_page.page.wait_for_load_state("domcontentloaded")
        # pages = test_page.get_page_by_url()
        # logger.info(f"页面数量: {len(pages)}")
        # test_page.click_test_frame_button()
        # test_page.click_test_frame_button()
