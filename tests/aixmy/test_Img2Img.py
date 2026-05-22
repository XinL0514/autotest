import allure
from playwright.sync_api import Page

from pages.modules.aixmy.Img2Img_page import Img2ImgPage
from utils.assertion import Assertion
from utils.data_loader import DataLoader

assertion = Assertion("TestImg2Img")


@allure.feature("Aixmy 平台")
class TestImg2Img:

    @allure.story("Img2Img")
    @allure.title("课堂内文生图后图生图")
    @allure.description(
        "开始上课 → 选课件 → 进入课堂 → 文生图 → 选图 → 图生图 → UI 下课"
    )
    @allure.severity(allure.severity_level.CRITICAL)
    def test_img2img_in_classroom(self, authenticated_page: Page, end_class):
        data = DataLoader.get_test_data("aixmy/Img2Img_data.yaml", "default")
        page_obj = Img2ImgPage(authenticated_page)

        page_obj.open()
        page_obj.enter_classroom()
        end_class(page_obj)

        page_obj.send_wentu_prompt(data["wentu_prompt"])
        page_obj.wait_for_image_generated()
        classroom = page_obj.get_classroom_frame()
        assertion.assert_is_display(
            classroom, page_obj.REGENERATE_BUTTON, "文生图生成完成"
        )

        page_obj.click_generated_image()
        page_obj.send_img2img_prompt(data["img2img_prompt"])
        page_obj.wait_for_image_generated()
        assertion.assert_is_display(
            classroom, page_obj.REGENERATE_BUTTON, "图生图生成完成"
        )

        page_obj.close_classroom()
        page_obj.page.wait_for_timeout(2000)
