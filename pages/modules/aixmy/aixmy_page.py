import re
from pages.base_page import BasePage
from utils.element import Element


AIXMY_URL = "https://aixmy.miaobi.cn/#/home"


class AixmyPage(BasePage):
    """Aixmy 平台页面"""

    # 首页
    MY_AVATAR = Element("role", ("img", "my"), desc="我的头像入口")
    LOGIN_ENTRY_TEXT = Element("text", "立即登录，开始创作", desc="立即登录入口文字")

    # 登录
    EMPLOYEE_ID_INPUT = Element("role", ("textbox", "请输入您的工号"), desc="工号输入框")
    PASSWORD_INPUT = Element("role", ("textbox", "请输入密码"), desc="密码输入框")
    LOGIN_BUTTON = Element("role", ("button", "登录"), desc="登录按钮", exact=True)

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

    def open(self):
        self.navigate(AIXMY_URL)

    def click_my_avatar(self):
        self.click(self.MY_AVATAR)

    def click_login_entry(self):
        self.click(self.LOGIN_ENTRY_TEXT)

    def login(self, employee_id: str, password: str):
        self.fill(self.EMPLOYEE_ID_INPUT, employee_id)
        self.press(self.EMPLOYEE_ID_INPUT, "Tab")
        self.fill(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)

    def click_start_class(self):
        self.click(self.START_CLASS_BUTTON)

    def click_first_work(self):
        self.click(self.FIRST_WORK_THUMBNAIL)

    def launch_courseware(self):
        self.click(self.LAUNCH_COURSEWARE_BUTTON)
        self.click(self.AUTO_ROOM_NUMBER_BUTTON)
        self.page.wait_for_timeout(1000)
        self.click(self.ENTER_ROOM_BUTTON)
        self.page.wait_for_timeout(5000)

    def get_classroom_frame(self):
        return self.frame(self.CLASSROOM_IFRAME)

    def send_wentu_prompt(self, prompt_text: str):
        """在 iframe 课堂内点击文生图工具并发送提示词"""
        classroom = self.get_classroom_frame()
        classroom.click(self.WENTU_TOOL)
        # classroom.click(self.EDITOR_INPUT)
        self.page.wait_for_timeout(1000)
        classroom.type(self.EDITOR_INPUT, prompt_text)  # 逐字输入，不会先清空
        classroom.click(self.SEND_BUTTON)

    def close_classroom(self):
        self.click(self.CLASSENDS)
