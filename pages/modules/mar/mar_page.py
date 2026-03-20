from pages.base_page import BasePage
from config.config import BASE_URL
from utils.element import Element


class MarPage(BasePage):
    """用药记录页面"""

    MAR_TAB_BUTTON = Element(
        "role", ("button", "用药记录"),
        desc="用药记录Tab按钮"
    )

    ADD_MAR_BUTTON = Element(
        "role", ("button", "添加用药记录"),
        desc="添加用药记录按钮"
    )

    MAR_NAME_INPUT = Element("role", ("textbox", "药物名称"), desc="药物名称输入框")
    MAR_DOSAGE_INPUT = Element("role", ("textbox", "剂量"), desc="剂量输入框")
    MAR_FREQUENCY_INPUT = Element("role", ("textbox", "用药频率"), desc="用药频率输入框")
    MAR_PURPOSE_INPUT = Element("role", ("textbox", "用药目的"), desc="用药目的输入框")
    MAR_SIDE_EFFECTS_INPUT = Element("role", ("textbox", "副作用"), desc="副作用输入框")

    MAR_STILL_USING_CHECKBOX = Element("role", ("checkbox", "当前仍在使用"), desc="当前仍在使用复选框")

    SAVE_MAR_BUTTON = Element("role", ("button", "保存"), desc="保存按钮", exact=True)

    MEDICATION_NAME = Element("role", ("heading",), desc="药物名称标题", last=True)

    CANCEL_BUTTON = Element("role", ("button", "取消"), desc="取消按钮")

    DELETE_LAST_MEDICATION_BUTTON = Element("role", ("button", "删除"), desc="删除药物按钮--最后一个", last=True)
    DELETE_FIRST_MEDICATION_BUTTON = Element("role", ("button", "删除"), desc="删除药物按钮--第一个", first=True)
    DELETE_SUCCESS_BUTTON = Element("text", "用药记录删除成功", desc="删除成功提示", exact=True)

    DIALOG_DELETE_BUTTON = Element("role", ("button", "确定"), desc="对话框确定按钮")
    DIALOG_CANCEL_BUTTON = Element("role", ("button", "取消"), desc="对话框取消按钮")

    FIRST_MAR_RECORD = Element("css", ".mar-record-item", desc="第一条用药记录", first=True)
    SECOND_MAR_RECORD = Element("css", ".mar-record-item", desc="第二条用药记录", nth=1)
    ACTIVE_MAR_RECORD = Element(
        "css", ".mar-record-item",
        desc="第一条正在使用的用药记录",
        filter_params={"has_text": "正在使用"},
        first=True
    )

    def open(self):
        self.navigate(f"{BASE_URL}")

    def click_mar_tab(self):
        self.click(self.MAR_TAB_BUTTON)

    def add_medication_record(self, name: str, dosage: str = "", frequency: str = "",
                             purpose: str = "", side_effects: str = ""):
        self.click(self.ADD_MAR_BUTTON)
        self.fill(self.MAR_NAME_INPUT, name)
        self.fill(self.MAR_DOSAGE_INPUT, dosage)
        self.fill(self.MAR_FREQUENCY_INPUT, frequency)
        self.fill(self.MAR_PURPOSE_INPUT, purpose)
        self.fill(self.MAR_SIDE_EFFECTS_INPUT, side_effects)
        return self.is_checked(self.MAR_STILL_USING_CHECKBOX)

    def click_save_btn(self):
        self.click(self.SAVE_MAR_BUTTON)

    def get_medication_name(self):
        return self.get_text(self.MEDICATION_NAME)

    def delete_last_medication(self):
        self.click_and_accept_dialog(self.DELETE_LAST_MEDICATION_BUTTON)
        return self.is_visible(self.DELETE_SUCCESS_BUTTON)

    def delete_first_medication(self):
        self.click(self.DELETE_FIRST_MEDICATION_BUTTON)
        self.click_and_accept_dialog(self.DIALOG_DELETE_BUTTON)
