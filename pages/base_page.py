import allure
from playwright.sync_api import Page, Locator, FrameLocator
from config.config import TIMEOUT
from utils.logger import Logger
from utils.element import Element
from utils.exception_handler import ExceptionHandler, FrameExceptionHandler
from typing import Union, Tuple, Optional


class BasePage:
    """页面基类,封装通用的页面操作方法"""

    def __init__(self, page: Page):
        self.page = page
        self.timeout = TIMEOUT
        self.logger = Logger(self.__class__.__name__)

    def _resolve_timeout(self, timeout: int = None, element: Element = None) -> int:
        """解析 timeout 优先级：方法参数 > Element.timeout > BasePage.timeout

        Args:
            timeout: 方法级别的 timeout 参数
            element: Element 对象（如果有）

        Returns:
            最终使用的 timeout 值
        """
        if timeout is not None:
            return timeout
        if element is not None and element.timeout is not None:
            return element.timeout
        return self.timeout

    def _get_locator(self, locator: Union[str, Tuple[str, str], Element], context=None) -> Locator:
        """智能定位器：自动识别定位器类型并返回 Playwright Locator

        Args:
            locator: 定位器，支持三种格式：
                - Element 对象（推荐）: Element("role", ("button", "登录"), desc="登录按钮")
                - 元组 ("role", "name"): 使用 get_by_role
                - 字符串 "#id" 或 ".class": 使用 CSS 选择器
                - 字符串 "//xpath": 使用 XPath
            context: 定位上下文（Page 或 FrameLocator），默认使用 self.page

        Returns:
            Playwright Locator 对象

        Examples:
            # Element 对象（推荐）
            LOGIN_BTN = Element("role", ("button", "登录"), desc="登录按钮")
            locator = self._get_locator(LOGIN_BTN)

            # Role 定位器
            locator = self._get_locator(("button", "提交"))

            # CSS 定位器
            locator = self._get_locator("#submit-btn")

            # XPath 定位器
            locator = self._get_locator("//button[@id='submit']")
        """
        ctx = context or self.page
        # 处理 Element 对象
        if isinstance(locator, Element):
            return self._build_locator_from_element(locator, ctx)
        # 元组形式：使用 get_by_role
        elif isinstance(locator, tuple):
            if len(locator) == 1:
                role = locator[0]
                self.logger.debug(f"使用 Role 定位器: role={role}")
                return ctx.get_by_role(role)
            elif len(locator) == 2:
                role, name = locator
                self.logger.debug(f"使用 Role 定位器: role={role}, name={name}")
                return ctx.get_by_role(role, name=name)
            else:
                raise ValueError(f"元组定位器长度必须是 1 或 2，当前长度: {len(locator)}, 值: {locator}")
        # 字符串形式：判断是 XPath 还是 CSS
        elif isinstance(locator, str):
            if locator.startswith(("//", "(", "./")):
                # XPath 定位器
                self.logger.debug(f"使用 XPath 定位器: {locator}")
                return ctx.locator(f"xpath={locator}")
            else:
                # CSS 选择器
                self.logger.debug(f"使用 CSS 定位器: {locator}")
                return ctx.locator(locator)
        else:
            raise ValueError(f"不支持的定位器类型: {type(locator)}, 值: {locator}")

    def _get_locator_description(self, locator: Union[str, Tuple[str, str], Element]) -> str:
        """获取定位器的描述字符串（用于日志）

        Args:
            locator: 定位器

        Returns:
            定位器的描述字符串
        """
        if isinstance(locator, Element):
            return locator.get_description()
        elif isinstance(locator, tuple):
            if len(locator) == 1:
                return f"Role({locator[0]})"
            elif len(locator) == 2:
                role, name = locator
                return f"Role({role}, '{name}')"
            else:
                raise ValueError(f"元组定位器长度必须是 1 或 2，当前长度: {len(locator)}, 值: {locator}")
        else:
            return f"'{locator}'"

    def _build_locator_from_element(self, element: Element, context=None) -> Locator:
        """根据 Element 配置构建 Locator（支持所有 Playwright 定位方式 + 链式操作）

        Args:
            element: Element 配置对象
            context: 定位上下文（Page 或 FrameLocator），默认使用 self.page

        Returns:
            Playwright Locator 对象
        """
        # self.logger.debug(f"构建定位器: {element.get_description()}")

        # 1. 根据定位方式获取基础 Locator
        base_locator = self._get_base_locator(element, context)

        # 2. 应用 filter() 筛选
        if element.filter_params:
            self.logger.debug(f"应用 filter: {element.filter_params}")
            base_locator = base_locator.filter(**element.filter_params)

        # 3. 应用 nth/first/last
        if element.first:
            self.logger.debug("应用 first()")
            base_locator = base_locator.first
        elif element.last:
            self.logger.debug("应用 last()")
            base_locator = base_locator.last
        elif element.nth is not None:
            self.logger.debug(f"应用 nth({element.nth})")
            base_locator = base_locator.nth(element.nth)

        return base_locator

    def _get_base_locator(self, element: Element, context=None) -> Locator:
        """根据定位方式创建基础 Locator

        支持 Playwright 所有定位方式：
        - role: get_by_role
        - text: get_by_text
        - placeholder: get_by_placeholder
        - label: get_by_label
        - testid: get_by_test_id
        - title: get_by_title
        - alt_text: get_by_alt_text
        - css: locator (CSS)
        - xpath: locator (XPath)

        Args:
            element: Element 配置对象
            context: 定位上下文（Page 或 FrameLocator），默认使用 self.page
        """
        ctx = context or self.page
        by = element.by
        value = element.value
        exact = element.exact

        # Role 定位器（特殊处理，支持多参数）
        if by == "role":
            if isinstance(value, tuple) and len(value) == 2:
                role, name = value
                return ctx.get_by_role(role, name=name, exact=exact)
            elif isinstance(value, tuple) and len(value) == 1:
                return ctx.get_by_role(value[0])
            else:
                raise ValueError(f"Role 定位器格式错误: {value}")

        # 文本定位器
        elif by == "text":
            return ctx.get_by_text(value, exact=exact)

        # Placeholder 定位器
        elif by == "placeholder":
            return ctx.get_by_placeholder(value, exact=exact)

        # Label 定位器
        elif by == "label":
            return ctx.get_by_label(value, exact=exact)

        # Test ID 定位器
        elif by == "testid":
            return ctx.get_by_test_id(value)

        # Title 定位器
        elif by == "title":
            return ctx.get_by_title(value, exact=exact)

        # Alt Text 定位器
        elif by == "alt_text":
            return ctx.get_by_alt_text(value, exact=exact)

        # CSS 选择器
        elif by == "css":
            return ctx.locator(value)

        # XPath 选择器
        elif by == "xpath":
            return ctx.locator(f"xpath={value}")

        else:
            raise ValueError(f"不支持的定位方式: {by}")

    # ========== 基础页面操作 ==========

    @allure.step("导航到页面")
    @ExceptionHandler.handle_playwright_exception("导航到页面")
    def navigate(self, url: str, wait_until: str = "domcontentloaded"):
        """导航到指定URL

        Args:
            url: 目标 URL
            wait_until: 页面加载等待策略，可选值：
                - "domcontentloaded": 等待 DOMContentLoaded 事件（默认，推荐）
                - "load": 等待 load 事件（包括所有资源）
                - "networkidle": 等待网络空闲（可能在某些 SPA 应用中卡住）
        """
        self.logger.info(f"导航到页面: {url}, 等待策略: {wait_until}")
        self.page.goto(url, wait_until=wait_until)
        self.logger.info(f"成功加载页面: {url}")

    @allure.step("点击元素")
    @ExceptionHandler.handle_playwright_exception("点击元素")
    def click(self, locator: Union[str, Tuple[str, str], Element], timeout: int = None):
        """智能点击元素 - 支持 CSS/XPath 字符串、Role 元组或 Element 对象

        Args:
            locator: 定位器，支持：
                - Element: Element("role", ("button", "提交"), desc="提交按钮")
                - CSS: "#id" 或 ".class"
                - XPath: "//button[@id='submit']"
                - Role: ("button", "提交")
            timeout: 可选的超时时间（毫秒），优先级：timeout 参数 > Element.timeout > self.timeout
        """
        loc_desc = self._get_locator_description(locator)
        self.logger.info(f"尝试点击元素: {loc_desc}")

        element = locator if isinstance(locator, Element) else None
        final_timeout = self._resolve_timeout(timeout, element)

        self._get_locator(locator).click(timeout=final_timeout)
        self.logger.info(f"成功点击元素: {loc_desc}")

    @allure.step("填充元素")
    @ExceptionHandler.handle_playwright_exception("填充元素")
    def fill(self, locator: Union[str, Tuple[str, str], Element], text: str, timeout: int = None):
        """智能填充输入框 - 支持 CSS/XPath 字符串、Role 元组或 Element 对象

        Args:
            locator: 定位器，支持：
                - Element: Element("placeholder", "请输入用户名", desc="用户名输入框")
                - CSS: "#username" 或 ".input-field"
                - XPath: "//input[@name='username']"
                - Role: ("textbox", "用户名")
            text: 要填充的文本
            timeout: 可选的超时时间（毫秒），优先级：timeout 参数 > Element.timeout > self.timeout
        """
        loc_desc = self._get_locator_description(locator)
        self.logger.info(f"尝试填充元素: {loc_desc}, 内容: {text}")

        element = locator if isinstance(locator, Element) else None
        final_timeout = self._resolve_timeout(timeout, element)

        self._get_locator(locator).fill(text, timeout=final_timeout)
        self.logger.info(f"成功填充元素: {loc_desc}")

    @allure.step("获取元素文本")
    @ExceptionHandler.handle_playwright_exception("获取元素文本")
    def get_text(self, locator: Union[str, Tuple[str, str], Element], timeout: int = None) -> str:
        """智能获取元素文本 - 支持 CSS/XPath 字符串、Role 元组或 Element 对象

        Args:
            locator: 定位器，支持：
                - Element: Element("text", "欢迎回来", desc="欢迎语")
                - CSS: ".title" 或 "#heading"
                - XPath: "//h1[@class='title']"
                - Role: ("heading", "页面标题")
            timeout: 可选的超时时间（毫秒），优先级：timeout 参数 > Element.timeout > self.timeout

        Returns:
            元素的文本内容
        """
        loc_desc = self._get_locator_description(locator)
        self.logger.info(f"尝试获取元素文本: {loc_desc}")

        element = locator if isinstance(locator, Element) else None
        final_timeout = self._resolve_timeout(timeout, element)

        text = self._get_locator(locator).text_content(timeout=final_timeout)
        self.logger.info(f"成功获取文本: {loc_desc}, 内容: {text}")
        return text

    @allure.step("检查元素可见性")
    @ExceptionHandler.handle_playwright_exception("检查元素可见性", return_on_error=False, raise_assertion=False)
    def is_visible(self, locator: Union[str, Tuple[str, str], Element]) -> bool:
        """智能检查元素是否可见 - 支持 CSS/XPath 字符串、Role 元组或 Element 对象

        Args:
            locator: 定位器，支持：
                - Element: Element("role", ("dialog",), desc="弹窗")
                - CSS: ".modal" 或 "#popup"
                - XPath: "//div[@class='modal']"
                - Role: ("dialog", "确认弹窗")

        Returns:
            True 表示可见，False 表示不可见
        """
        loc_desc = self._get_locator_description(locator)
        visible = self._get_locator(locator).is_visible()
        if visible:
            self.logger.info(f"元素可见: {loc_desc}")
        else:
            self.logger.warning(f"元素不可见: {loc_desc}")
        return visible

    @allure.step("等待元素出现")
    @ExceptionHandler.handle_playwright_exception("等待元素出现")
    def wait_for_selector(self, locator: Union[str, Tuple[str, str], Element], timeout: int = None):
        """智能等待元素出现 - 支持 CSS/XPath 字符串、Role 元组或 Element 对象

        Args:
            locator: 定位器，支持：
                - Element: Element("css", ".loading", desc="加载动画")
                - CSS: ".loading" 或 "#spinner"
                - XPath: "//div[@class='loading']"
                - Role: ("status", "加载中")
            timeout: 可选的超时时间（毫秒），优先级：timeout 参数 > Element.timeout > self.timeout
        """
        loc_desc = self._get_locator_description(locator)
        self.logger.info(f"等待元素出现: {loc_desc}")

        element = locator if isinstance(locator, Element) else None
        final_timeout = self._resolve_timeout(timeout, element)

        self._get_locator(locator).wait_for(state="visible", timeout=final_timeout)
        self.logger.info(f"元素已出现: {loc_desc}")

    @allure.step("检查元素是否选中")
    @ExceptionHandler.handle_playwright_exception("检查元素是否选中", return_on_error=False, raise_assertion=False)
    def is_checked(self, locator: Union[str, Tuple[str, str], Element]) -> bool:
        """智能检查元素是否选中 - 支持 CSS/XPath 字符串、Role 元组或 Element 对象

        Args:
            locator: 定位器，支持：
                - Element: Element("label", "记住我", desc="记住密码复选框")
                - CSS: "#remember-me" 或 ".checkbox"
                - XPath: "//input[@type='checkbox']"
                - Role: ("checkbox", "记住我")

        Returns:
            True 表示选中，False 表示未选中
        """
        loc_desc = self._get_locator_description(locator)
        checked = self._get_locator(locator).is_checked()
        if checked:
            self.logger.info(f"元素已选中: {loc_desc}")
        else:
            self.logger.warning(f"元素未选中: {loc_desc}")
        return checked

    @allure.step("选中元素")
    @ExceptionHandler.handle_playwright_exception("选中元素")
    def check(self, locator: Union[str, Tuple[str, str], Element], timeout: int = None):
        """智能选中元素 - 支持 CSS/XPath 字符串、Role 元组或 Element 对象

        Args:
            locator: 定位器，支持：
                - Element: Element("label", "记住我", desc="记住密码复选框")
                - CSS: "#remember" 或 ".agree-checkbox"
                - XPath: "//input[@name='remember']"
                - Role: ("checkbox", "记住我")
            timeout: 可选的超时时间（毫秒），优先级：timeout 参数 > Element.timeout > self.timeout
        """
        loc_desc = self._get_locator_description(locator)
        self.logger.info(f"尝试选中元素: {loc_desc}")

        element = locator if isinstance(locator, Element) else None
        final_timeout = self._resolve_timeout(timeout, element)

        self._get_locator(locator).check(timeout=final_timeout)
        self.logger.info(f"成功选中元素: {loc_desc}")

    @allure.step("取消选中元素")
    @ExceptionHandler.handle_playwright_exception("取消选中元素")
    def uncheck(self, locator: Union[str, Tuple[str, str], Element], timeout: int = None):
        """智能取消选中元素 - 支持 CSS/XPath 字符串、Role 元组或 Element 对象

        Args:
            locator: 定位器，支持：
                - Element: Element("label", "记住我", desc="记住密码复选框")
                - CSS: "#remember" 或 ".agree-checkbox"
                - XPath: "//input[@name='remember']"
                - Role: ("checkbox", "记住我")
            timeout: 可选的超时时间（毫秒），优先级：timeout 参数 > Element.timeout > self.timeout
        """
        loc_desc = self._get_locator_description(locator)
        self.logger.info(f"尝试取消选中元素: {loc_desc}")

        element = locator if isinstance(locator, Element) else None
        final_timeout = self._resolve_timeout(timeout, element)

        self._get_locator(locator).uncheck(timeout=final_timeout)
        self.logger.info(f"成功取消选中元素: {loc_desc}")

    # ========== 文件上传操作 ==========

    @allure.step("上传文件")
    @ExceptionHandler.handle_playwright_exception("上传文件")
    def file_set_input_files(self, locator: Union[str, Tuple[str, str], Element], file_path: Union[str, list], timeout: int = None):
        """智能上传文件 - 支持 CSS/XPath 字符串、Role 元组或 Element 对象

        适用场景：直接操作 input[type='file'] 元素

        Args:
            locator: 文件上传输入框的定位器，支持：
                - Element: Element("css", "input[type='file']", desc="文件上传框")
                - CSS: "input[type='file']" 或 "#file-upload"
                - XPath: "//input[@type='file']"
                - Role: ("button", "上传文件")
            file_path: 要上传的文件路径，支持：
                - 单个文件: "/path/to/file.pdf"
                - 多个文件: ["/path/to/file1.pdf", "/path/to/file2.jpg"]
            timeout: 可选的超时时间（毫秒），优先级：timeout 参数 > Element.timeout > self.timeout

        Examples:
            # 上传单个文件
            self.file_set_input_files("input[type='file']", "/Users/test/document.pdf")

            # 使用 Element 对象上传文件
            FILE_INPUT = Element("css", "input[type='file']", desc="文件上传框")
            self.file_set_input_files(FILE_INPUT, "/Users/test/image.jpg")

            # 上传多个文件
            files = ["/Users/test/file1.pdf", "/Users/test/file2.jpg"]
            self.file_set_input_files("input[type='file']", files)
        """
        loc_desc = self._get_locator_description(locator)
        file_info = file_path if isinstance(file_path, str) else f"{len(file_path)} 个文件"
        self.logger.info(f"尝试上传文件到元素: {loc_desc}, 文件: {file_info}")

        element = locator if isinstance(locator, Element) else None
        final_timeout = self._resolve_timeout(timeout, element)

        self._get_locator(locator).set_input_files(file_path, timeout=final_timeout)
        self.logger.info(f"成功上传文件: {file_info}")

    @allure.step("点击按钮并上传文件")
    @ExceptionHandler.handle_playwright_exception("点击按钮并上传文件")
    def file_choose_file(self, locator: Union[str, Tuple[str, str], Element], file_path: Union[str, list], timeout: int = None):
        """点击按钮触发文件选择对话框并上传文件

        适用场景：
        - 点击按钮后弹出系统文件选择对话框
        - 自定义的上传按钮（非 input[type='file']）
        - 需要先点击才能触发文件选择的场景

        Args:
            locator: 触发文件选择的按钮定位器，支持：
                - Element: Element("role", ("button", "上传文件"), desc="上传按钮")
                - CSS: "button.upload-btn" 或 "#upload-button"
                - XPath: "//button[text()='上传文件']"
                - Role: ("button", "上传文件")
            file_path: 要上传的文件路径，支持：
                - 单个文件: "/path/to/file.pdf"
                - 多个文件: ["/path/to/file1.pdf", "/path/to/file2.jpg"]
            timeout: 可选的超时时间（毫秒），优先级：timeout 参数 > Element.timeout > self.timeout

        Examples:
            # 点击上传按钮并选择文件
            self.file_choose_file(("button", "上传文件"), "/Users/test/document.pdf")

            # 使用 Element 对象
            UPLOAD_BTN = Element("role", ("button", "选择文件"), desc="上传按钮")
            self.file_choose_file(UPLOAD_BTN, "/Users/test/image.jpg")

            # 上传多个文件
            files = ["/Users/test/file1.pdf", "/Users/test/file2.jpg"]
            self.file_choose_file("button#upload", files)
        """
        loc_desc = self._get_locator_description(locator)
        file_info = file_path if isinstance(file_path, str) else f"{len(file_path)} 个文件"
        self.logger.info(f"尝试点击按钮并上传文件: {loc_desc}, 文件: {file_info}")

        element = locator if isinstance(locator, Element) else None
        final_timeout = self._resolve_timeout(timeout, element)

        # 监听文件选择器事件
        with self.page.expect_file_chooser() as fc_info:
            self._get_locator(locator).click(timeout=final_timeout)

        file_chooser = fc_info.value
        self.logger.info(f"捕获到文件选择对话框")

        # 设置文件
        file_chooser.set_files(file_path)
        self.logger.info(f"成功上传文件: {file_info}")

    # ========== 新窗口/新标签页处理 ==========

    @allure.step("点击并处理新窗口")
    @ExceptionHandler.handle_playwright_exception("点击并处理新窗口")
    def click_and_handle_new_page(self, locator: Union[str, Tuple[str, str], Element],
                                   wait_for_load: bool = True, wait_until: str = "domcontentloaded", timeout: int = None):
        """点击元素并获取新打开的页面对象

        适用场景：
        - 点击按钮/链接会打开新标签页
        - target="_blank" 的链接
        - window.open() 打开的新窗口

        Args:
            locator: 定位器（会触发打开新页面的元素）
            wait_for_load: 是否等待新页面加载完成，默认 True
            wait_until: 页面加载等待策略，可选值：
                - "domcontentloaded": 等待 DOMContentLoaded 事件（默认，推荐）
                - "load": 等待 load 事件（包括所有资源）
                - "networkidle": 等待网络空闲（可能在某些 SPA 应用中卡住）
            timeout: 可选的超时时间（毫秒），优先级：timeout 参数 > Element.timeout > self.timeout

        Returns:
            新页面的 Page 对象

        Examples:
            # 点击"在新标签页打开"按钮
            new_page = self.click_and_handle_new_page(("button", "在新标签页打开"))

            # 在新页面操作
            new_page.click("#some-button")

            # 关闭新页面
            new_page.close()

            # 使用 load 策略等待所有资源
            new_page = self.click_and_handle_new_page(("button", "打开"), wait_until="load")
        """
        loc_desc = self._get_locator_description(locator)
        self.logger.info(f"尝试点击元素并处理新窗口: {loc_desc}")

        element = locator if isinstance(locator, Element) else None
        final_timeout = self._resolve_timeout(timeout, element)

        # 监听新页面事件
        with self.page.context.expect_page() as new_page_info:
            self._get_locator(locator).click(timeout=final_timeout)

        new_page = new_page_info.value
        self.logger.info(f"成功获取新页面: {new_page.url}")

        # 等待新页面加载完成
        if wait_for_load:
            self.logger.info(f"等待新页面加载完成，策略: {wait_until}")
            new_page.wait_for_load_state(wait_until, timeout=final_timeout)
            self.logger.info(f"新页面加载完成: {new_page.url}")

        return new_page

    @allure.step("获取所有打开的页面")
    def get_all_pages(self):
        """获取当前上下文中所有打开的页面

        Returns:
            所有 Page 对象的列表

        Examples:
            pages = self.get_all_pages()
            print(f"当前打开了 {len(pages)} 个页面")
        """
        pages = self.page.context.pages
        self.logger.info(f"当前打开的页面数: {len(pages)}")
        for i, page in enumerate(pages):
            self.logger.debug(f"  页面 {i}: {page.url}")
        return pages

    @allure.step("关闭所有新窗口（保留原窗口）")
    def close_all_new_windows(self):
        """关闭除当前页面外的所有其他页面

        Examples:
            # 打开了多个新窗口后，统一关闭
            self.close_all_new_windows()
        """
        current_page = self.page
        all_pages = self.page.context.pages

        closed_count = 0
        for page in all_pages:
            if page != current_page:
                self.logger.info(f"关闭页面: {page.url}")
                page.close()
                closed_count += 1

        self.logger.info(f"已关闭 {closed_count} 个新窗口")

    @allure.step("切换到最新打开的页面")
    def switch_to_latest_page(self):
        """切换到最新打开的页面（更新 self.page）

        注意：这会改变当前 BasePage 对象的 page 属性

        Returns:
            最新的 Page 对象

        Examples:
            # 点击按钮打开了新页面
            self.click(("button", "打开新页面"))

            # 切换到新页面
            self.switch_to_latest_page()

            # 现在所有操作都在新页面上
            self.click("#some-button")
        """
        all_pages = self.page.context.pages
        if len(all_pages) > 1:
            latest_page = all_pages[-1]
            self.logger.info(f"切换到最新页面: {latest_page.url}")
            self.page = latest_page
            return latest_page
        else:
            self.logger.warning("只有一个页面，无需切换")
            return self.page

    @allure.step("通过 URL 特征切换页面")
    def switch_to_page_by_url(self, url_pattern: str, switch_current: bool = True):
        """通过 URL 包含的字符串查找并切换到对应页面

        Args:
            url_pattern: URL 中包含的字符串（如 "map"、"/@12966061" 等）
            switch_current: 是否切换当前页面（更新 self.page），默认 True

        Returns:
            匹配到的 Page 对象

        Raises:
            AssertionError: 未找到匹配的页面

        Examples:
            # 通过域名关键词切换到地图页面
            map_page = self.switch_to_page_by_url("map")

            # 通过路径特征切换
            detail_page = self.switch_to_page_by_url("/@12966061")

            # 只查找不切换
            target_page = self.switch_to_page_by_url("map", switch_current=False)
        """
        all_pages = self.page.context.pages
        self.logger.info(f"在 {len(all_pages)} 个页面中查找包含 '{url_pattern}' 的 URL")

        # 打印所有页面 URL（用于调试）
        for i, page in enumerate(all_pages):
            self.logger.debug(f"  页面 {i}: {page.url}")

        # 查找匹配的页面
        matched_page = None
        for page in all_pages:
            if url_pattern in page.url:
                matched_page = page
                break

        # 检查是否找到匹配的页面
        if matched_page is None:
            error_msg = f"未找到包含 '{url_pattern}' 的页面\n当前打开的页面:\n"
            for i, page in enumerate(all_pages):
                error_msg += f"  [{i}] {page.url}\n"
            self.logger.error(error_msg)
            raise AssertionError(error_msg)

        self.logger.info(f"找到匹配页面: {matched_page.url}")

        # 是否切换当前页面
        if switch_current:
            self.logger.info(f"切换当前页面到: {matched_page.url}")
            self.page = matched_page

        return matched_page

    @allure.step("获取指定 URL 的页面对象")
    def get_page_by_url(self, url_pattern: str):
        """通过 URL 特征获取页面对象（不切换当前页面）

        这是 switch_to_page_by_url(switch_current=False) 的便捷方法

        Args:
            url_pattern: URL 中包含的字符串

        Returns:
            匹配到的 Page 对象

        Examples:
            # 获取地图页面对象（不切换）
            map_page = self.get_page_by_url("map")

            # 可以创建新的页面对象来操作
            from pages.modules.map.map_page import MapPage
            map_page_obj = MapPage(map_page)
            map_page_obj.search_location("北京")
        """
        return self.switch_to_page_by_url(url_pattern, switch_current=False)

    # ========== 浏览器导航操作 ==========

    @allure.step("浏览器后退")
    @ExceptionHandler.handle_playwright_exception("浏览器后退")
    def go_back(self, wait_for_load: bool = True, wait_until: str = "domcontentloaded"):
        """浏览器后退到上一页

        Args:
            wait_for_load: 是否等待页面加载完成，默认 True
            wait_until: 页面加载等待策略，可选值：
                - "domcontentloaded": 等待 DOMContentLoaded 事件（默认，推荐）
                - "load": 等待 load 事件（包括所有资源）
                - "networkidle": 等待网络空闲（可能在某些 SPA 应用中卡住）

        Examples:
            # 后退到上一页
            self.go_back()

            # 后退但不等待加载完成
            self.go_back(wait_for_load=False)

            # 后退并等待所有资源加载
            self.go_back(wait_until="load")
        """
        self.logger.info("浏览器后退到上一页")
        self.page.go_back(timeout=self.timeout)

        if wait_for_load:
            self.logger.info(f"等待页面加载完成，策略: {wait_until}")
            self.page.wait_for_load_state(wait_until, timeout=self.timeout)

        self.logger.info(f"成功后退到: {self.page.url}")

    @allure.step("浏览器前进")
    @ExceptionHandler.handle_playwright_exception("浏览器前进")
    def go_forward(self, wait_for_load: bool = True, wait_until: str = "domcontentloaded"):
        """浏览器前进到下一页

        Args:
            wait_for_load: 是否等待页面加载完成，默认 True
            wait_until: 页面加载等待策略，可选值：
                - "domcontentloaded": 等待 DOMContentLoaded 事件（默认，推荐）
                - "load": 等待 load 事件（包括所有资源）
                - "networkidle": 等待网络空闲（可能在某些 SPA 应用中卡住）

        Examples:
            # 前进到下一页
            self.go_forward()

            # 前进但不等待加载完成
            self.go_forward(wait_for_load=False)

            # 前进并等待网络空闲
            self.go_forward(wait_until="networkidle")
        """
        self.logger.info("浏览器前进到下一页")
        self.page.go_forward(timeout=self.timeout)

        if wait_for_load:
            self.logger.info(f"等待页面加载完成，策略: {wait_until}")
            self.page.wait_for_load_state(wait_until, timeout=self.timeout)

        self.logger.info(f"成功前进到: {self.page.url}")

    # ========== iframe 处理 ==========

    def _build_frame_locator(self, frame: FrameLocator, element_locator: Union[str, Tuple[str, str], Element]):
        """在 iframe 中构建 Locator（支持所有定位方式）

        委托给 _get_locator，通过 context 参数将定位上下文切换为 frame。

        Args:
            frame: FrameLocator 对象
            element_locator: 元素定位器

        Returns:
            在 frame 中的 Locator 对象
        """
        return self._get_locator(element_locator, context=frame)

    @allure.step("切换到 iframe")
    @ExceptionHandler.handle_playwright_exception("切换到 iframe")
    def switch_to_frame(self, frame_locator: str) -> FrameLocator:
        """切换到指定的 iframe（返回 FrameLocator 对象）

        Args:
            frame_locator: iframe 的 CSS 选择器（如 "iframe#my-frame"、"iframe[name='content']"）

        Returns:
            FrameLocator 对象，可以在其中进行元素操作

        Examples:
            # 直接在 iframe 中操作
            frame = self.switch_to_frame("iframe#content-frame")
            frame.locator("button#submit").click()
        """
        self.logger.info(f"切换到 iframe: {frame_locator}")
        frame = self.page.frame_locator(frame_locator)
        self.logger.info(f"成功切换到 iframe: {frame_locator}")
        return frame

    @allure.step("在 iframe 中点击元素")
    @FrameExceptionHandler.handle_frame_exception("在 iframe 中点击元素")
    def frame_click(self, frame_locator: str, element_locator: Union[str, Tuple[str, str], Element], timeout: int = None):
        """在指定 iframe 中点击元素

        Args:
            frame_locator: iframe 的 CSS 选择器
            element_locator: iframe 内元素的定位器，支持：
                - Element 对象（推荐）- 支持所有定位方式（placeholder/label/testid 等）
                - CSS 选择器字符串
                - Role 元组
            timeout: 可选的超时时间（毫秒），优先级：timeout 参数 > Element.timeout > self.timeout

        Examples:
            # 使用 Element 对象（支持所有定位方式）
            LINK = Element("role", ("link", "提交"), desc="提交链接")
            self.frame_click("iframe#content", LINK)

            # 使用 placeholder 定位
            INPUT = Element("placeholder", "请输入", desc="输入框")
            self.frame_click("iframe#content", INPUT)

            # 使用 CSS 选择器
            self.frame_click("iframe#content", "button#submit")

            # 使用 Role 元组
            self.frame_click("iframe#content", ("button", "提交"))
        """
        loc_desc = self._get_locator_description(element_locator)
        self.logger.info(f"在 iframe '{frame_locator}' 中点击元素: {loc_desc}")

        element = element_locator if isinstance(element_locator, Element) else None
        final_timeout = self._resolve_timeout(timeout, element)

        # 获取 iframe 并构建 locator
        frame = self.page.frame_locator(frame_locator)
        locator = self._build_frame_locator(frame, element_locator)

        locator.click(timeout=final_timeout)
        self.logger.info(f"成功点击 iframe 中的元素: {loc_desc}")

    @allure.step("在 iframe 中填充元素")
    @FrameExceptionHandler.handle_frame_exception("在 iframe 中填充元素")
    def frame_fill(self, frame_locator: str, element_locator: Union[str, Tuple[str, str], Element], text: str, timeout: int = None):
        """在指定 iframe 中填充输入框

        Args:
            frame_locator: iframe 的 CSS 选择器
            element_locator: iframe 内元素的定位器，支持 Element 对象、CSS 选择器、Role 元组
            text: 要填充的文本
            timeout: 可选的超时时间（毫秒），优先级：timeout 参数 > Element.timeout > self.timeout

        Examples:
            # 使用 Element 对象（支持 placeholder 等所有定位方式）
            USERNAME = Element("placeholder", "请输入用户名", desc="用户名输入框")
            self.frame_fill("iframe#login-frame", USERNAME, "admin")

            # 使用 CSS 选择器
            self.frame_fill("iframe#login-frame", "input#username", "admin")
        """
        loc_desc = self._get_locator_description(element_locator)
        self.logger.info(f"在 iframe '{frame_locator}' 中填充元素: {loc_desc}, 内容: {text}")

        element = element_locator if isinstance(element_locator, Element) else None
        final_timeout = self._resolve_timeout(timeout, element)

        # 获取 iframe 并构建 locator
        frame = self.page.frame_locator(frame_locator)
        locator = self._build_frame_locator(frame, element_locator)

        locator.fill(text, timeout=final_timeout)
        self.logger.info(f"成功填充 iframe 中的元素: {loc_desc}")

    @allure.step("获取 iframe 中元素的文本")
    @FrameExceptionHandler.handle_frame_exception("获取 iframe 中元素的文本")
    def frame_get_text(self, frame_locator: str, element_locator: Union[str, Tuple[str, str], Element], timeout: int = None) -> str:
        """获取指定 iframe 中元素的文本

        Args:
            frame_locator: iframe 的 CSS 选择器
            element_locator: iframe 内元素的定位器，支持 Element 对象、CSS 选择器、Role 元组
            timeout: 可选的超时时间（毫秒），优先级：timeout 参数 > Element.timeout > self.timeout

        Returns:
            元素的文本内容

        Examples:
            # 使用 Element 对象
            TITLE = Element("css", "h1.title", desc="标题")
            title = self.frame_get_text("iframe#content", TITLE)

            # 使用 CSS 选择器
            title = self.frame_get_text("iframe#content", "h1.title")
        """
        loc_desc = self._get_locator_description(element_locator)
        self.logger.info(f"获取 iframe '{frame_locator}' 中元素文本: {loc_desc}")

        element = element_locator if isinstance(element_locator, Element) else None
        final_timeout = self._resolve_timeout(timeout, element)

        # 获取 iframe 并构建 locator
        frame = self.page.frame_locator(frame_locator)
        locator = self._build_frame_locator(frame, element_locator)

        text = locator.text_content(timeout=final_timeout)
        self.logger.info(f"成功获取文本: {text}")
        return text

    @allure.step("检查 iframe 中元素是否可见")
    @FrameExceptionHandler.handle_frame_exception("检查 iframe 中元素是否可见", return_on_error=False)
    def frame_is_visible(self, frame_locator: str, element_locator: Union[str, Tuple[str, str], Element]) -> bool:
        """检查指定 iframe 中元素是否可见

        Args:
            frame_locator: iframe 的 CSS 选择器
            element_locator: iframe 内元素的定位器，支持 Element 对象、CSS 选择器、Role 元组

        Returns:
            True 表示可见，False 表示不可见

        Examples:
            # 使用 Element 对象
            BUTTON = Element("role", ("button", "提交"), desc="提交按钮")
            visible = self.frame_is_visible("iframe#content", BUTTON)

            # 使用 CSS 选择器
            visible = self.frame_is_visible("iframe#content", "button#submit")
        """
        loc_desc = self._get_locator_description(element_locator)

        # 获取 iframe 并构建 locator
        frame = self.page.frame_locator(frame_locator)
        locator = self._build_frame_locator(frame, element_locator)

        visible = locator.is_visible()
        if visible:
            self.logger.info(f"iframe 中元素可见: {loc_desc}")
        else:
            self.logger.warning(f"iframe 中元素不可见: {loc_desc}")
        return visible

    @allure.step("等待 iframe 中元素出现")
    @FrameExceptionHandler.handle_frame_exception("等待 iframe 中元素出现")
    def frame_wait_for_selector(self, frame_locator: str, element_locator: Union[str, Tuple[str, str], Element], timeout: int = None):
        """等待 iframe 中元素出现

        Args:
            frame_locator: iframe 的 CSS 选择器
            element_locator: iframe 内元素的定位器，支持 Element 对象、CSS 选择器、Role 元组
            timeout: 可选的超时时间（毫秒），优先级：timeout 参数 > Element.timeout > self.timeout

        Examples:
            # 使用 Element 对象
            LOADING = Element("css", ".loading", desc="加载动画")
            self.frame_wait_for_selector("iframe#content", LOADING)

            # 使用 CSS 选择器
            self.frame_wait_for_selector("iframe#content", ".loading")
        """
        loc_desc = self._get_locator_description(element_locator)
        self.logger.info(f"等待 iframe '{frame_locator}' 中元素出现: {loc_desc}")

        element = element_locator if isinstance(element_locator, Element) else None
        final_timeout = self._resolve_timeout(timeout, element)

        # 获取 iframe 并构建 locator
        frame = self.page.frame_locator(frame_locator)
        locator = self._build_frame_locator(frame, element_locator)

        locator.wait_for(state="visible", timeout=final_timeout)
        self.logger.info(f"iframe 中元素已出现: {loc_desc}")

    # ========== JavaScript 对话框处理 ==========

    @allure.step("点击元素并接受对话框")
    def click_and_accept_dialog(self, locator: Union[str, Tuple[str, str], Element],
                                  message_check: str = None):
        """点击元素并自动接受弹出的对话框（点击"确定"按钮）

        适用场景：
        - JavaScript alert() 对话框
        - JavaScript confirm() 对话框（点击"确定"）
        - 删除操作的二次确认

        Args:
            locator: 定位器（会触发对话框的元素）
            message_check: 可选，验证对话框文本是否包含指定内容

        Examples:
            # 点击删除按钮并确定
            self.click_and_accept_dialog(("button", "删除"))

            # 点击删除并验证对话框文本
            self.click_and_accept_dialog(
                DELETE_BTN,
                message_check="确定要删除这条用药记录吗"
            )
        """
        return self.click_and_handle_dialog(locator, accept=True, message_check=message_check)

    @allure.step("点击元素并取消对话框")
    def click_and_dismiss_dialog(self, locator: Union[str, Tuple[str, str], Element],
                                   message_check: str = None):
        """点击元素并自动取消弹出的对话框（点击"取消"按钮）

        适用场景：
        - JavaScript confirm() 对话框（点击"取消"）
        - 测试取消删除的场景

        Args:
            locator: 定位器（会触发对话框的元素）
            message_check: 可选，验证对话框文本是否包含指定内容

        Examples:
            # 点击删除按钮但取消
            self.click_and_dismiss_dialog(("button", "删除"))

            # 点击删除并验证对话框文本后取消
            self.click_and_dismiss_dialog(
                DELETE_BTN,
                message_check="确定要删除"
            )
        """
        return self.click_and_handle_dialog(locator, accept=False, message_check=message_check)

    @allure.step("点击元素并处理对话框")
    @ExceptionHandler.handle_playwright_exception("点击元素并处理对话框")
    def click_and_handle_dialog(self, locator: Union[str, Tuple[str, str], Element],
                                 accept: bool = True, message_check: str = None, timeout: int = None) -> Optional[str]:
        """点击元素并处理弹出的 JavaScript 对话框（通用方法）

        适用场景：
        - JavaScript alert() 对话框
        - JavaScript confirm() 对话框
        - JavaScript prompt() 对话框

        Args:
            locator: 定位器（会触发对话框的元素）
            accept: True=点击"确定"，False=点击"取消"
            message_check: 可选，验证对话框文本是否包含指定内容
            timeout: 可选的超时时间（毫秒），优先级：timeout 参数 > Element.timeout > self.timeout

        Returns:
            对话框的完整文本内容，如果没有对话框则返回 None

        Raises:
            AssertionError: 对话框文本验证失败或对话框未出现

        Examples:
            # 点击删除并确定
            dialog_text = self.click_and_handle_dialog(DELETE_BTN, accept=True)

            # 点击删除并验证文本后确定
            self.click_and_handle_dialog(
                DELETE_BTN,
                accept=True,
                message_check="确定要删除这条用药记录吗"
            )
        """
        loc_desc = self._get_locator_description(locator)
        action_text = "接受" if accept else "取消"
        self.logger.info(f"尝试点击元素并{action_text}对话框: {loc_desc}")

        element = locator if isinstance(locator, Element) else None
        final_timeout = self._resolve_timeout(timeout, element)

        # 使用 expect_event 确保真正等待到 dialog 事件
        with self.page.expect_event("dialog", timeout=final_timeout) as dialog_info:
            self._get_locator(locator).click(timeout=final_timeout)

        # 获取 dialog 对象并处理
        dialog = dialog_info.value
        dialog_message = dialog.message
        self.logger.info(f"捕获到对话框，类型: {dialog.type}, 内容: {dialog_message}")

        # 验证对话框文本
        if message_check:
            if message_check not in dialog_message:
                error_msg = f"对话框文本验证失败\n期望包含: {message_check}\n实际内容: {dialog_message}"
                self.logger.error(error_msg)
                dialog.dismiss()
                raise AssertionError(error_msg)
            else:
                self.logger.info(f"对话框文本验证通过: '{message_check}' 存在于 '{dialog_message}'")

        # 处理对话框
        if accept:
            dialog.accept()
            self.logger.info(f"已接受对话框")
        else:
            dialog.dismiss()
            self.logger.info(f"已取消对话框")

        self.logger.info(f"对话框处理完成: {loc_desc}")
        return dialog_message

    # ========== 鼠标悬停和拖拽操作 ==========

    @allure.step("悬停到元素")
    @ExceptionHandler.handle_playwright_exception("悬停到元素")
    def hover(self, locator: Union[str, Tuple[str, str], Element], position: dict = None, force: bool = False, timeout: int = None):
        """悬停到元素上

        适用场景：
        - 显示下拉菜单
        - 触发悬停提示
        - 显示隐藏的操作按钮

        Args:
            locator: 定位器，支持：
                - Element: Element("css", "#menu-item", desc="菜单项")
                - CSS: "#menu-item" 或 ".hover-trigger"
                - XPath: "//div[@class='menu']"
                - Role: ("button", "更多操作")
            position: 可选，相对元素的悬停位置，如 {"x": 10, "y": 10}
            force: 是否强制悬停（跳过可操作性检查），默认 False
            timeout: 可选的超时时间（毫秒），优先级：timeout 参数 > Element.timeout > self.timeout

        Examples:
            # 基础悬停
            self.hover("#menu-item")

            # 使用 Element 对象
            MENU = Element("css", ".dropdown-trigger", desc="下拉菜单触发器")
            self.hover(MENU)

            # 悬停到元素的特定位置
            self.hover("#element", position={"x": 10, "y": 10})

            # 强制悬停（元素被遮挡时）
            self.hover("#element", force=True)
        """
        loc_desc = self._get_locator_description(locator)
        self.logger.info(f"尝试悬停到元素: {loc_desc}")

        element = locator if isinstance(locator, Element) else None
        final_timeout = self._resolve_timeout(timeout, element)

        hover_options = {"timeout": final_timeout}
        if position:
            hover_options["position"] = position
        if force:
            hover_options["force"] = force

        self._get_locator(locator).hover(**hover_options)
        self.logger.info(f"成功悬停到元素: {loc_desc}")

    @allure.step("拖拽元素到目标位置")
    @ExceptionHandler.handle_playwright_exception("拖拽元素")
    def drag_to(self, source_locator: Union[str, Tuple[str, str], Element],
                target_locator: Union[str, Tuple[str, str], Element],
                source_position: dict = None, target_position: dict = None, force: bool = False, timeout: int = None):
        """将元素拖拽到目标元素位置

        适用场景：
        - 拖拽排序
        - 拖拽上传
        - 拖拽移动元素

        Args:
            source_locator: 源元素定位器（要拖拽的元素）
            target_locator: 目标元素定位器（拖拽到的位置）
            source_position: 可选，源元素的抓取位置，如 {"x": 0, "y": 0}
            target_position: 可选，目标元素的释放位置，如 {"x": 0, "y": 0}
            force: 是否强制拖拽（跳过可操作性检查），默认 False
            timeout: 可选的超时时间（毫秒），优先级：timeout 参数 > Element.timeout > self.timeout

        Examples:
            # 基础拖拽
            self.drag_to("#source", "#target")

            # 使用 Element 对象
            SOURCE = Element("css", ".draggable-item", desc="可拖拽项")
            TARGET = Element("css", ".drop-zone", desc="放置区域")
            self.drag_to(SOURCE, TARGET)

            # 指定拖拽和释放位置
            self.drag_to("#source", "#target",
                        source_position={"x": 10, "y": 10},
                        target_position={"x": 20, "y": 20})

            # 强制拖拽
            self.drag_to("#source", "#target", force=True)
        """
        source_desc = self._get_locator_description(source_locator)
        target_desc = self._get_locator_description(target_locator)
        self.logger.info(f"尝试拖拽元素: {source_desc} -> {target_desc}")

        # 解析 timeout 优先级（优先使用 source 的 timeout）
        element = source_locator if isinstance(source_locator, Element) else None
        final_timeout = self._resolve_timeout(timeout, element)

        drag_options = {"timeout": final_timeout}
        if source_position:
            drag_options["source_position"] = source_position
        if target_position:
            drag_options["target_position"] = target_position
        if force:
            drag_options["force"] = force

        source = self._get_locator(source_locator)
        target = self._get_locator(target_locator)
        source.drag_to(target, **drag_options)

        self.logger.info(f"成功拖拽元素: {source_desc} -> {target_desc}")

    @allure.step("使用鼠标操作拖拽元素")
    @ExceptionHandler.handle_playwright_exception("使用鼠标拖拽元素")
    def drag_by_mouse(self, source_locator: Union[str, Tuple[str, str], Element],
                      target_locator: Union[str, Tuple[str, str], Element]):
        """使用鼠标操作进行拖拽（更精细的控制）

        适用场景：
        - drag_to() 方法不生效时的替代方案
        - 需要模拟真实鼠标拖拽行为
        - 复杂的拖拽场景

        Args:
            source_locator: 源元素定位器（要拖拽的元素）
            target_locator: 目标元素定位器（拖拽到的位置）

        Examples:
            # 使用鼠标拖拽
            self.drag_by_mouse("#source", "#target")

            # 使用 Element 对象
            SOURCE = Element("css", ".item", desc="拖拽项")
            TARGET = Element("css", ".zone", desc="目标区域")
            self.drag_by_mouse(SOURCE, TARGET)
        """
        source_desc = self._get_locator_description(source_locator)
        target_desc = self._get_locator_description(target_locator)
        self.logger.info(f"使用鼠标拖拽元素: {source_desc} -> {target_desc}")

        # 获取元素位置
        source = self._get_locator(source_locator)
        target = self._get_locator(target_locator)

        source_box = source.bounding_box()
        target_box = target.bounding_box()

        if not source_box or not target_box:
            raise AssertionError("无法获取元素位置信息")

        # 计算元素中心点
        source_x = source_box["x"] + source_box["width"] / 2
        source_y = source_box["y"] + source_box["height"] / 2
        target_x = target_box["x"] + target_box["width"] / 2
        target_y = target_box["y"] + target_box["height"] / 2

        # 执行鼠标拖拽
        self.logger.info(f"移动鼠标到源元素: ({source_x}, {source_y})")
        self.page.mouse.move(source_x, source_y)

        self.logger.info("按下鼠标左键")
        self.page.mouse.down()

        self.logger.info(f"移动鼠标到目标元素: ({target_x}, {target_y})")
        self.page.mouse.move(target_x, target_y)

        self.logger.info("释放鼠标左键")
        self.page.mouse.up()

        self.logger.info(f"成功使用鼠标拖拽: {source_desc} -> {target_desc}")

    @allure.step("悬停并等待元素出现")
    @ExceptionHandler.handle_playwright_exception("悬停并等待元素出现")
    def hover_and_wait(self, hover_locator: Union[str, Tuple[str, str], Element],
                       wait_locator: Union[str, Tuple[str, str], Element],
                       wait_timeout: int = None):
        """悬停到元素并等待另一个元素出现

        适用场景：
        - 悬停显示下拉菜单后，等待菜单项出现
        - 悬停显示工具提示后，等待提示内容加载

        Args:
            hover_locator: 要悬停的元素定位器
            wait_locator: 等待出现的元素定位器
            wait_timeout: 等待超时时间（毫秒），优先级：wait_timeout 参数 > Element.timeout > self.timeout

        Examples:
            # 悬停菜单并等待子菜单出现
            self.hover_and_wait("#menu-item", ".submenu")

            # 使用 Element 对象
            MENU = Element("css", ".menu-trigger", desc="菜单触发器")
            SUBMENU = Element("css", ".submenu", desc="子菜单")
            self.hover_and_wait(MENU, SUBMENU)
        """
        hover_desc = self._get_locator_description(hover_locator)
        wait_desc = self._get_locator_description(wait_locator)

        # 解析 hover 的 timeout
        hover_element = hover_locator if isinstance(hover_locator, Element) else None
        hover_timeout = self._resolve_timeout(None, hover_element)

        # 解析 wait 的 timeout
        wait_element = wait_locator if isinstance(wait_locator, Element) else None
        final_wait_timeout = self._resolve_timeout(wait_timeout, wait_element)

        self.logger.info(f"悬停到元素: {hover_desc}")
        self._get_locator(hover_locator).hover(timeout=hover_timeout)

        self.logger.info(f"等待元素出现: {wait_desc}")
        self._get_locator(wait_locator).wait_for(state="visible", timeout=final_wait_timeout)

        self.logger.info(f"悬停并等待成功: {hover_desc} -> {wait_desc}")
