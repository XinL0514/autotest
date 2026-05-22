import re

from pages.modules.aixmy.aixmy_page import AixmyPage
from utils.element import Element


class Img2ImgPage(AixmyPage):
    """图生图用例页面 — 元素与 tools/recordings/recording_20260521_181628.py 逐步对应。"""

    # ------------------------------------------------------------------
    # 主页面（录制步骤 1-5）
    # ------------------------------------------------------------------
    START_CLASS_BUTTON = Element("role", ("button", "开始上课"), desc="开始上课按钮")
    WORK_THUMBNAIL = Element("css", ".work-item > .work-thumbnail", desc="课件缩略图", first=True)
    LAUNCH_COURSEWARE_BUTTON = Element(
        "role", ("button", "启动课件，开始上课"), desc="启动课件按钮"
    )
    AUTO_ROOM_NUMBER_BUTTON = Element(
        "role", ("button", "自动生成房间号"), desc="自动生成房间号按钮"
    )
    ENTER_ROOM_BUTTON = Element("role", ("button", "立即进入"), desc="立即进入按钮")

    # ------------------------------------------------------------------
    # 课堂 iframe（录制步骤 6-12）
    # ------------------------------------------------------------------
    CLASSROOM_IFRAME = "iframe"

    WENTU_TOOL = Element(
        "css", "div", desc="文生图工具入口",
        filter_params={"has_text": re.compile(r"^文生图$")}, first=True,
    )
    # 录制为 #tinymce-editor-1779358609514（动态 ID），用前缀匹配保持稳定
    TINYMCE_EDITOR = Element(
        "css", "[id^='tinymce-editor-']", desc="课堂提示词编辑器（tinymce）"
    )
    EDITOR_INPUT = Element(
        "css", ".message-input-container-h5-center [contenteditable='true']",
        desc="课堂提示词输入框（contenteditable 兜底）",
    )
    SEND_BUTTON = Element("css", ".message-input-button-send-btn", desc="发送按钮")
    GENERATED_IMAGE = Element("css", "img", desc="文生图结果图片", nth=4)
    IMG2IMG_TOOL = Element("text", "图生图", desc="图生图工具入口")
    REGENERATE_BUTTON = Element("text", "重新生成", desc="图片生成完成标志")

    # ------------------------------------------------------------------
    # 主页面 — 下课（录制步骤 13）
    # ------------------------------------------------------------------
    CLASSENDS = Element(
        "css", "div", desc="下课按钮",
        filter_params={"has_text": re.compile(r"^下课$")}, nth=1,
    )

    # ------------------------------------------------------------------
    # 页面操作（与录制步骤一一对应）
    # ------------------------------------------------------------------

    def click_start_class(self):
        self.click(self.START_CLASS_BUTTON)

    def click_work_thumbnail(self):
        self.click(self.WORK_THUMBNAIL)

    def click_launch_courseware(self):
        self.click(self.LAUNCH_COURSEWARE_BUTTON)

    def click_auto_room_number(self):
        self.click(self.AUTO_ROOM_NUMBER_BUTTON)

    def click_enter_room(self):
        self.click(self.ENTER_ROOM_BUTTON)

    def enter_classroom(self):
        """录制步骤 1-5：开始上课 → 选课件 → 启动课件 → 生成房间号 → 进入课堂。"""
        self.click_start_class()
        self.click_work_thumbnail()
        self.launch_courseware()

    def _fill_editor(self, classroom, prompt_text: str):
        """优先使用录制中的 tinymce 编辑器，失败时回退 contenteditable。"""
        try:
            classroom.type(self.TINYMCE_EDITOR, prompt_text)
        except Exception:
            classroom.type(self.EDITOR_INPUT, prompt_text)

    def click_wentu_tool(self):
        self.get_classroom_frame().click(self.WENTU_TOOL)

    def fill_wentu_prompt(self, prompt_text: str):
        classroom = self.get_classroom_frame()
        self._fill_editor(classroom, prompt_text)

    def click_send(self):
        self.get_classroom_frame().click(self.SEND_BUTTON)

    def send_wentu_prompt(self, prompt_text: str):
        """录制步骤 6-8：文生图 → 输入提示词 → 发送。"""
        self.click_wentu_tool()
        self.page.wait_for_timeout(1000)
        self.fill_wentu_prompt(prompt_text)
        self.click_send()

    def click_generated_image(self):
        """录制步骤 9：点击文生图结果。"""
        self.get_classroom_frame().click(self.GENERATED_IMAGE)

    def click_img2img_tool(self):
        self.get_classroom_frame().click(self.IMG2IMG_TOOL)

    def fill_img2img_prompt(self, prompt_text: str):
        classroom = self.get_classroom_frame()
        self._fill_editor(classroom, prompt_text)

    def send_img2img_prompt(self, prompt_text: str):
        """录制步骤 10-12：图生图 → 输入提示词 → 发送。"""
        self.click_img2img_tool()
        self.page.wait_for_timeout(1000)
        self.fill_img2img_prompt(prompt_text)
        self.click_send()

    def wait_for_image_generated(self, timeout: int = 60000):
        self.get_classroom_frame().wait_for_selector(self.REGENERATE_BUTTON, timeout=timeout)

    def close_classroom(self):
        """录制步骤 13：UI 下课。"""
        self.click(self.CLASSENDS)
