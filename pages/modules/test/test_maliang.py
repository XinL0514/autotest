import re

from playwright.sync_api import expect

from pages.base_page import BasePage
from config.config import BASE_URL
from utils.element import Element


class MaliangPage(BasePage):
    SELECT_A = Element("text", "图像生成", exact=True, desc="图像生成入口")
    SELECT_B = Element("role", ("button", "模板"), desc="模版按钮")
    SELECT_C = Element("role", ("button", "添加新模板"), desc="添加新模版入口")
    SELECT_D = Element("role", ("textbox", "标题（title）"), desc="请输入模板标题")
    SELECT_E = Element("role", ("button", "生成ID"), desc="生成ID")
    SELECT_F = Element("role", ("button", "上传封面"), desc="上传封面")
    SELECT_F_INPUT = Element(
        "xpath",
        "//input[@placeholder='请输入封面 URL 或上传图片']/following-sibling::input[@type='file']",
        desc="封面图片文件输入框",
    )
    SELECT_G = Element("role", ("textbox", "描述（desc）"), desc="请输入模板描述")
    SELECT_H = Element("css", ".chat-grid-wrap", desc="输入文案，或通过下方按钮添加输入框/下拉框组件")
    SELECT_I = Element("role", ("button", "确定添加模板"), desc="确定添加模板")
    SELECT_J = Element("xpath", '//button[@class="rounded-md p-1 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600"]', desc="取消")
    SELECT_K = Element("xpath", '//button[@class="inline-flex items-center gap-2 rounded-lg bg-[#eaf3ff] px-3 py-2.5 text-[#2b6cb0] transition-colors hover:bg-[#deecff]"]', desc="下面的图像生成入口")
    SELECT_L = Element("role", ("button", "保存"), desc="保存")
    SELECT_M = Element("placeholder", "请输入封面 URL 或上传图片", desc="封面 URL 输入框")

    DEFAULT_OPTION_INDEX = 3
    DEFAULT_OPTION_VALUE = "o3"
    COVER_URL_PATTERN = re.compile(r"^https?://")

    def open(self):
        """打开页面（已登录状态下直接访问）"""
        self.navigate(f"{BASE_URL}")

    def upload_cover_image(self, image_path: str, timeout: int = None):
        """上传封面图片并等待服务端回填 cover URL。"""
        self.file_set_input_files(self.SELECT_F_INPUT, image_path, timeout=timeout)

        final_timeout = self._resolve_timeout(timeout, self._get_element(self.SELECT_M))
        self.logger.info("等待封面上传完成并回填 URL")
        expect(self.locator(self.SELECT_M)).to_have_value(self.COVER_URL_PATTERN, timeout=final_timeout)
        self.logger.info(f"封面上传完成: {self.get_input_value(self.SELECT_M)}")

    def add_template(self, title: str, wengan: str, image_path: str = None):
        """添加一个模板

        Args:
            title: 模板标题（风格标题）
            wengan: 文案描述（用于描述字段和文案输入区）
            image_path: 封面图片的绝对路径；为 None 时跳过上传
        """
        self.click(self.SELECT_A)
        self.click(self.SELECT_B)
        self.click(self.SELECT_C)
        self.fill(self.SELECT_D, title)
        self.click(self.SELECT_E)
        if image_path:
            self.upload_cover_image(image_path)
        self.fill(self.SELECT_G, wengan)
        self.fill(self.SELECT_H, wengan)
        self.click(self.SELECT_I)
        self.click(self.SELECT_J)
        self.click(self.SELECT_K)
        self.click(self.SELECT_L)

    def click_select_button(self, index: int = None):
        target_index = self.DEFAULT_OPTION_INDEX if index is None else index
        self.select_option(self.SELECT_BUTTON, index=target_index)
