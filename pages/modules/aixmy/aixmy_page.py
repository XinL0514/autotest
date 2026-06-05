import re

from pages.base_page import BasePage
from utils.element import Element
from config.config import BASE_URL
from apis.aixmy.aixmy_api import AixmyApiClient


class AixmyPage(BasePage):
    """Aixmy 平台页面"""

    # 课程列表
    START_CLASS_BUTTON = Element("role", ("button", "开始上课"), desc="开始上课按钮")
    FIRST_WORK_THUMBNAIL = Element("css", ".work-item > .work-thumbnail", desc="第一个课件缩略图", first=True)

    # 课件启动弹窗
    LAUNCH_COURSEWARE_BUTTON = Element("role", ("button", "启动课件，开始上课"), desc="启动课件按钮")
    AUTO_ROOM_NUMBER_BUTTON = Element("role", ("button", "自动生成房间号"), desc="自动生成房间号按钮")
    ENTER_ROOM_BUTTON = Element("role", ("button", "立即进入"), desc="立即进入按钮")

    # 课堂关闭
    CLASSENDS = Element("text", "下课", desc="下课按钮")

    # iframe 内元素（供 frame() 使用的 Element 定义）
    WENTU_TOOL = Element("text", "文生图", exact=True, desc="文生图工具入口",
                         filter_params={"has_text": re.compile(r"^文生图$")}, first=True)
    EDITOR_INPUT = Element("css", ".message-input-container-h5-center [contenteditable='true']", desc="文生图提示词输入框")
    SEND_BUTTON = Element("css", ".message-input-button-send-btn", desc="发送按钮")
    REGENERATE_BUTTON = Element("text", "重新生成", desc="重新生成按钮（图片生成完成的标志）")

    # iframe CSS selector（plain string）
    CLASSROOM_IFRAME = "iframe"

    def __init__(self, page):
        super().__init__(page)
        self.room_key: str | None = None
        self._cached_token: str | None = None

    # ------------------------------------------------------------------
    # 内部：网络响应监听，捕获 roomKey 和 token
    # ------------------------------------------------------------------

    def _on_request(self, request) -> None:
        if "maliang.miaobi.cn" not in request.url:
            return
        auth = request.headers.get("authorization") or request.headers.get("Authorization")
        if auth and auth.startswith("Bearer ") and not self._cached_token:
            self._cached_token = auth[len("Bearer "):]
            self.logger.info("auth token captured from request header")

    def _on_response(self, response) -> None:
        if "maliang.miaobi.cn" not in response.url:
            return
        auth = response.request.headers.get("authorization") or response.request.headers.get("Authorization")
        if auth and auth.startswith("Bearer "):
            self._cached_token = auth[len("Bearer "):]
        try:
            data = response.json()
            room_key = (
                (data.get("data") or {}).get("roomKey")
                or data.get("roomKey")
            )
            if room_key:
                self.room_key = str(room_key)
                self.logger.info(f"roomKey captured: {self.room_key}")
        except Exception:
            pass

    # ------------------------------------------------------------------
    # 页面操作
    # ------------------------------------------------------------------

    def open(self):
        self.navigate(BASE_URL)

    def wait_until_ready(self, timeout: int = 60000):
        self.wait_for_selector(self.START_CLASS_BUTTON, timeout=timeout)

    def click_start_class(self):
        self.click(self.START_CLASS_BUTTON)

    def click_first_work(self):
        self.click(self.FIRST_WORK_THUMBNAIL)

    def launch_courseware(self):
        self.click(self.LAUNCH_COURSEWARE_BUTTON)
        self.page.on("request", self._on_request)
        self.page.on("response", self._on_response)
        try:
            self.click(self.AUTO_ROOM_NUMBER_BUTTON)
            self.page.wait_for_timeout(1000)
            self.click(self.ENTER_ROOM_BUTTON)
            self.page.wait_for_timeout(5000)
        finally:
            self.page.remove_listener("request", self._on_request)
            self.page.remove_listener("response", self._on_response)

    def get_classroom_frame(self):
        return self.frame(self.CLASSROOM_IFRAME)

    def send_wentu_prompt(self, prompt_text: str):
        classroom = self.get_classroom_frame()
        classroom.click(self.WENTU_TOOL)
        self.page.wait_for_timeout(1000)
        classroom.type(self.EDITOR_INPUT, prompt_text)
        classroom.click(self.SEND_BUTTON)

    def close_classroom(self):
        self.click(self.CLASSENDS)

    def get_api_client(self) -> AixmyApiClient:
        return AixmyApiClient(self.page, self.room_key, self._cached_token)

    def end_class_via_api(self) -> bool:
        return self.get_api_client().end_class()
