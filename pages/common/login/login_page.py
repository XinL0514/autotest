from pages.base_page import BasePage
from config.config import BASE_URL
from utils.element import Element


class LoginPage(BasePage):
    """Aixmy 平台登录页面"""

    # 首页
    MY_AVATAR = Element("role", ("img", "my"), desc="我的头像入口")
    LOGIN_ENTRY_TEXT = Element("text", "立即登录，开始创作", desc="立即登录入口文字")

    # 登录
    EMPLOYEE_ID_INPUT = Element("role", ("textbox", "请输入您的工号"), desc="工号输入框")
    PASSWORD_INPUT = Element("role", ("textbox", "请输入密码"), desc="密码输入框")
    LOGIN_BUTTON = Element("role", ("button", "登录"), desc="登录按钮", exact=True)

    def open(self):
        self.navigate(f"{BASE_URL}")

    def login(self, employee_id: str, password: str):
        self.click(self.MY_AVATAR)
        self.click(self.LOGIN_ENTRY_TEXT)
        self.fill(self.EMPLOYEE_ID_INPUT, employee_id)
        self.press(self.EMPLOYEE_ID_INPUT, "Tab")
        self.fill(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)
        self.page.wait_for_timeout(1000)

    def wait_until_logged_in(self, timeout: int = 10000):
        self._get_locator(self.LOGIN_ENTRY_TEXT).wait_for(state="hidden", timeout=timeout)
