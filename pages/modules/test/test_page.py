from pages.base_page import BasePage
from config.config import BASE_URL, DEFAULT_UPLOAD_FILE_NAME
from utils.element import Element
from utils.logger import Logger
logger = Logger.get_logger("MarPage")



class TestPage(BasePage):
    __test__ = False
    TESTFREAM = Element("text", "Frames Test", desc="Fream入口", exact=True)
    TESTIFREAM = Element("text", "IFrames Test", desc="IFream入口", exact=True)
    FRAMELOCATOR = '[src="index.htm"] >> nth=0'
    FREAMLINK = Element("role",("link","Link Test"), desc="Fream链接")    
    IFRAEMCLICK = Element("role",("button","Click me"))
    IFRAEMCLICKTEXT = ("#checkRecord")
    UPLOADFILEBTN = Element("role",("link", "File Upload Test"), desc="上传文件按钮")
    UPLOADFILEINPUT = ("#file")
    TESTJUMPBTN = Element("role",("heading", "Sahi Tests"), desc="test")
    JUMPBTN = Element("text",("Window Open Test"), desc="跳转按钮", exact=True)
    VER = "[name='top']"
    HOVERPAGE = Element("role", ("link", "Mouse over"), desc="悬停入口")
    DRAGPAGE = Element("role", ("link", "Drag Drop Test"), desc="拖拽入口")

    
    
    def open(self):
        """打开页面（已登录状态下直接访问）"""
        self.navigate(f"{BASE_URL}")
    
    def click_test_frame(self):
        self.click(self.TESTIFREAM)

    def switch_to_test_frame(self):
        self.switch_to_frame(self.FRAMELOCATOR)
        
    def click_test_verify_button(self):
        self.click(self.IFRAEMCLICK)
        
    def get_test_verify_button_text(self):
        return self.get_text(self.IFRAEMCLICKTEXT)
    
    def frame_click_link(self):
        self.frame_click(self.FRAMELOCATOR, self.FREAMLINK)


    def click_switch_to_upload_file_page(self):
        self.click(self.UPLOADFILEBTN)
    
    def click_upload_file_input(self, file_name: str = DEFAULT_UPLOAD_FILE_NAME):
        self.file_choose_file(self.UPLOADFILEINPUT, file_name)
        
    def click_test_jump_button(self):
        self.click(self.TESTJUMPBTN)
        
    def jump_to_new_page(self):
        new_page = self.click_and_handle_new_page(self.JUMPBTN)
        return new_page
    
    def verify_page(self):
       return self.is_visible(self.VER)
   
    def click_hover_page(self):
       self.click(self.HOVERPAGE)
        
    def click_drag_page(self):
       self.click(self.DRAGPAGE)

        

    # def get_test_frame_text(self):
    #     return self.get_text(self.TESTFREAM)
    
