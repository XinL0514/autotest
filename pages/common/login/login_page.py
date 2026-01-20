from pages.base_page import BasePage
from config.config import BASE_URL


class LoginPage(BasePage):
    USERNAME_INPUT = "#username"
    PASSWORD_INPUT = "#password"
    LOGIN_BUTTON = '[type = "submit"]'
    ERROR_MESSAGE = '[class = "text-sm mt-1 text-red-800"]'
    LOGIN_SUCCESS = '[class = "text-sm mt-1 text-green-800"]'

    def open(self):
        self.navigate(f"{BASE_URL}")

    def login(self, username: str, password: str):
        self.fill(self.USERNAME_INPUT, username)
        self.fill(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)
        

    def get_error_message(self) -> str:
        return self.get_text(self.ERROR_MESSAGE)
    
    def get_success_message(self) -> str:
        return self.get_text(self.LOGIN_SUCCESS)    
