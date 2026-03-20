from pages.base_page import BasePage
from config.config import BASE_URL
from utils.element import Element
from typing import Optional


class BloodEntryPage(BasePage):
    """血常规录入页面对象"""

    BLOOD_ENTRY_BUTTON = Element("role", ("button", "血常规录入"), desc="血常规录入按钮")
    SUBMIT_BUTTON = Element("role", ("button", "开始AI智能分析"), desc="提交AI分析按钮")

    PLT_INPUT = Element("css", "#plt", desc="血小板输入框")
    WBC_INPUT = Element("css", "#wbc", desc="白细胞输入框")
    RBC_INPUT = Element("css", "#rbc", desc="红细胞输入框")
    HGB_INPUT = Element("css", "#hgb", desc="血红蛋白输入框")
    TEST_DATE_INPUT = Element("css", "#test_date", desc="检测日期输入框")
    ERROR_MESSAGE = Element("css", ".text-sm.mt-1.text-red-800", desc="错误消息")
    SUCCESS_MESSAGE = Element("css", ".text-sm.mt-1.text-green-800", desc="成功消息")

    def open(self):
        self.navigate(f"{BASE_URL}")

    def click_blood_entry_button(self):
        self.click(self.BLOOD_ENTRY_BUTTON)

    def fill_blood_data(self, plt: str = "", wbc: str = "", rbc: str = "",
                        hgb: str = "", test_date: Optional[str] = None):
        if plt:
            self.fill(self.PLT_INPUT, plt)
        if wbc:
            self.fill(self.WBC_INPUT, wbc)
        if rbc:
            self.fill(self.RBC_INPUT, rbc)
        if hgb:
            self.fill(self.HGB_INPUT, hgb)
        if test_date:
            self.fill(self.TEST_DATE_INPUT, test_date)

    def submit_blood_data(self):
        self.click(self.SUBMIT_BUTTON)

    def submit_blood_entry(self, plt: str = "", wbc: str = "", rbc: str = "",
                           hgb: str = "", test_date: Optional[str] = None):
        self.click_blood_entry_button()
        self.fill_blood_data(plt, wbc, rbc, hgb, test_date)
        self.submit_blood_data()

    def get_error_message(self) -> str:
        return self.get_text(self.ERROR_MESSAGE)

    def get_success_message(self) -> str:
        return self.get_text(self.SUCCESS_MESSAGE)

    def is_error_message_visible(self) -> bool:
        return self.is_visible(self.ERROR_MESSAGE)

    def is_success_message_visible(self) -> bool:
        return self.is_visible(self.SUCCESS_MESSAGE)
