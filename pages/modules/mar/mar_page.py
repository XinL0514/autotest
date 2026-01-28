from pages.base_page import BasePage
from config.config import BASE_URL
from utils.element import Element
from utils.logger import Logger
logger = Logger.get_logger("MarPage")
class MarPage(BasePage):
    """用药记录页面

    演示三种定位器使用方式：
    1. 旧方式 - 元组定位器（仍然支持）
    2. 新方式 - Element 配置类（推荐）
    3. 混合使用 - 展示向后兼容性
    """

    # ========== 方式1: 旧方式 - 元组定位器（仍然支持） ==========
    MAR_TAB_BUTTON_OLD = ("button", "用药记录")
    ADD_MAR_BUTTON_OLD = ("button", "添加用药记录")

    # ========== 方式2: 新方式 - Element 配置类（推荐） ==========

    # 基础用法：role 定位器
    MAR_TAB_BUTTON = Element(
        "role", ("button", "用药记录"),
        desc="用药记录Tab按钮"
    )

    ADD_MAR_BUTTON = Element(
        "role", ("button", "添加用药记录"),
        desc="添加用药记录按钮"
    )
    
    

    # 使用 placeholder 定位输入框
    MAR_NAME_INPUT = Element("role", ("textbox", "药物名称"), desc="药物名称输入框")

    MAR_DOSAGE_INPUT = Element("role", ("textbox", "剂量"), desc="剂量输入框")
    

    MAR_FREQUENCY_INPUT = Element("role", ("textbox", "用药频率"), desc="用药频率输入框")

    MAR_PURPOSE_INPUT = Element("role", ("textbox", "用药目的"), desc="用药目的输入框")

    MAR_SIDE_EFFECTS_INPUT = Element("role", ("textbox", "副作用"), desc="副作用输入框")

    # 使用 label 定位复选框
    MAR_STILL_USING_CHECKBOX = Element("role", ("checkbox", "当前仍在使用"), desc="当前仍在使用复选框")

    # 使用 exact 参数精确匹配
    SAVE_MAR_BUTTON = Element("role", ("button", "保存"), desc="保存按钮", exact=True)  # 精确匹配，避免匹配到 "保存并继续"
    
    MEDICATION_NAME = Element("role", ("heading", "test"), desc="药物名称", nth=-1)

    CANCEL_BUTTON = Element("role", ("button", "取消"), desc="取消按钮")
    
    DELETE_LAST_MEDICATION_BUTTON = Element("role", ("button", "删除"), desc="删除药物按钮--最后一个", last=True)
    DELETE_FIRST_MEDICATION_BUTTON = Element("role", ("button", "删除"), desc="删除药物按钮--第一个", first=True)
    DELETE_SUCCESS_BUTTON = Element("text", "用药记录删除成功", desc="删除成功按钮", exact=True)
    
    DIALOG_DELETE_BUTTON = (("button", "确定"))
    DIALOG_CANCEL_BUTTON = (("button", "取消"))

    # ========== 高级用法：使用 filter 和 nth ==========

    # 获取第一条用药记录（使用 first）
    FIRST_MAR_RECORD = Element(
        "css", ".mar-record-item",
        desc="第一条用药记录",
        first=True
    )

    # 获取第二条用药记录（使用 nth）
    SECOND_MAR_RECORD = Element(
        "css", ".mar-record-item",
        desc="第二条用药记录",
        nth=1  # 索引从 0 开始
    )

    # 使用 filter 筛选包含特定文本的记录
    ACTIVE_MAR_RECORD = Element(
        "css", ".mar-record-item",
        desc="第一条正在使用的用药记录",
        filter_params={"has_text": "正在使用"},
        first=True
    )
    
    BUTTON_ADD_MAR_TEST = Element(
        "role", ("link", "地图"),
        desc="测试"
    )
    
    BUTTON_ADD_MAR_TEST_VISIBLE = Element(
        "css", ".internet-search-icon",
        desc="测试"
    )
    
    BUTTON_ADD_MAR_TEST_CLICK = Element(
        "css", ".svg_2cDwx.ai-search-btn-svg_vi_CZ",
        desc="AI"
    )



    def open(self):
        """打开页面（已登录状态下直接访问）"""
        self.navigate(f"{BASE_URL}")
        # self.page.wait_for_timeout(3000)
        
    def test_fun1(self):
        return self.is_visible(self.BUTTON_ADD_MAR_TEST)

    def click_mar_tab(self):
        """点击用药记录tab按钮 - 展示新旧两种方式"""
        # 新方式（推荐）：直接传递 Element 对象
        # return self.click_and_handle_new_page(self.BUTTON_ADD_MAR_TEST_CLICK)
        self.click(self.MAR_TAB_BUTTON)
        # self.click(self.BUTTON_ADD_MAR_TEST)
        # return self.page
    def test_fun(self):
        visible = self.is_visible(self.BUTTON_ADD_MAR_TEST_VISIBLE)
        # logger.info(f"搜索visible: {visible}")
        aivisable = self.is_visible(self.BUTTON_ADD_MAR_TEST_CLICK)
        # logger.info(f"AI可见: {aivisable}")
        return visible, aivisable
        # self.page.wait_for_timeout(3000)

    def add_medication_record(self, name: str, dosage: str = "", frequency: str = "",
                             purpose: str = "", side_effects: str = ""):
        """添加用药记录 - 展示 Element 配置类的完整使用

        Args:
            name: 药物名称
            dosage: 剂量
            frequency: 用药频率
            purpose: 用药目的
            side_effects: 副作用
            still_using: 是否当前仍在使用
        """
        # 点击添加按钮
        self.click(self.ADD_MAR_BUTTON)
        # 填充表单（自动使用元素描述信息）
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
        # self.click(self.DELETE_LAST_MEDICATION_BUTTON)
        self.click_and_accept_dialog(self.DELETE_LAST_MEDICATION_BUTTON)
        return self.is_visible(self.DELETE_SUCCESS_BUTTON)
        
    def delete_first_medication(self):
        self.click(self.DELETE_FIRST_MEDICATION_BUTTON)
        self.click_and_accept_dialog(self.DIALOG_DELETE_BUTTON)
        
        

