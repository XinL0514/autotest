from pages.base_page import BasePage
from config.config import BASE_URL
from utils.element import Element


class LoginPage(BasePage):
    USERNAME_INPUT = Element("css", "#username", desc="用户名输入框")
    PASSWORD_INPUT = Element("css", "#password", desc="密码输入框")
    LOGIN_BUTTON = Element("css", '[type="submit"]', desc="登录按钮")
    ERROR_MESSAGE = Element("css", "p.text-sm.mt-1.text-red-800", desc="错误消息")
    LOGIN_SUCCESS = Element("css", "p.text-sm.mt-1.text-green-800", desc="成功消息")
    HOME_READY_MARKER = Element("role", ("button", "用药记录"), desc="登录后首页标记")

    def open(self):
        self.navigate(f"{BASE_URL}")

    def login(self, username: str, password: str):
        self.fill(self.USERNAME_INPUT, username)
        self.fill(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)

    def wait_until_logged_in(self, timeout: int = 10000):
        self.wait_for_selector(self.HOME_READY_MARKER, timeout=timeout)

    def get_error_message(self) -> str:
        return self.get_text(self.ERROR_MESSAGE)

    def get_success_message(self) -> str:
        return self.get_text(self.LOGIN_SUCCESS)
