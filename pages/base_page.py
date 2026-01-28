import allure
from playwright.sync_api import Page, TimeoutError, Locator, FrameLocator
from config.config import TIMEOUT
from utils.logger import Logger
from utils.element import Element
from typing import Union, Tuple


class BasePage:
    """页面基类,封装通用的页面操作方法"""

    def __init__(self, page: Page):
        self.page = page
        self.timeout = TIMEOUT
        self.logger = Logger(self.__class__.__name__)

    def _get_locator(self, locator: Union[str, Tuple[str, str], Element]) -> Locator:
        """智能定位器：自动识别定位器类型并返回 Playwright Locator

        Args:
            locator: 定位器，支持三种格式：
                - Element 对象（推荐）: Element("role", ("button", "登录"), desc="登录按钮")
                - 元组 ("role", "name"): 使用 get_by_role
                - 字符串 "#id" 或 ".class": 使用 CSS 选择器
                - 字符串 "//xpath": 使用 XPath

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
        # 处理 Element 对象
        if isinstance(locator, Element):
            return self._build_locator_from_element(locator)
        # 元组形式：使用 get_by_role
        elif isinstance(locator, tuple):
            role, name = locator
            self.logger.debug(f"使用 Role 定位器: role={role}, name={name}")
            return self.page.get_by_role(role, name=name)
        # 字符串形式：判断是 XPath 还是 CSS
        elif isinstance(locator, str):
            if locator.startswith(("//", "(", "./")):
                # XPath 定位器
                self.logger.debug(f"使用 XPath 定位器: {locator}")
                return self.page.locator(f"xpath={locator}")
            else:
                # CSS 选择器
                self.logger.debug(f"使用 CSS 定位器: {locator}")
                return self.page.locator(locator)
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
            role, name = locator
            return f"Role({role}, '{name}')"
        else:
            return f"'{locator}'"

    def _build_locator_from_element(self, element: Element) -> Locator:
        """根据 Element 配置构建 Locator（支持所有 Playwright 定位方式 + 链式操作）

        Args:
            element: Element 配置对象

        Returns:
            Playwright Locator 对象
        """
        # self.logger.debug(f"构建定位器: {element.get_description()}")

        # 1. 根据定位方式获取基础 Locator
        base_locator = self._get_base_locator(element)

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

    def _get_base_locator(self, element: Element) -> Locator:
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
        """
        by = element.by
        value = element.value
        exact = element.exact

        # Role 定位器（特殊处理，支持多参数）
        if by == "role":
            if isinstance(value, tuple) and len(value) == 2:
                role, name = value
                return self.page.get_by_role(role, name=name, exact=exact)
            elif isinstance(value, tuple) and len(value) == 1:
                return self.page.get_by_role(value[0])
            else:
                raise ValueError(f"Role 定位器格式错误: {value}")

        # 文本定位器
        elif by == "text":
            return self.page.get_by_text(value, exact=exact)

        # Placeholder 定位器
        elif by == "placeholder":
            return self.page.get_by_placeholder(value, exact=exact)

        # Label 定位器
        elif by == "label":
            return self.page.get_by_label(value, exact=exact)

        # Test ID 定位器
        elif by == "testid":
            return self.page.get_by_test_id(value)

        # Title 定位器
        elif by == "title":
            return self.page.get_by_title(value, exact=exact)

        # Alt Text 定位器
        elif by == "alt_text":
            return self.page.get_by_alt_text(value, exact=exact)

        # CSS 选择器
        elif by == "css":
            return self.page.locator(value)

        # XPath 选择器
        elif by == "xpath":
            return self.page.locator(f"xpath={value}")

        else:
            raise ValueError(f"不支持的定位方式: {by}")


    @allure.step("导航到页面: {url}")
    def navigate(self, url: str):
        """导航到指定URL"""
        try:
            self.logger.info(f"导航到页面: {url}")
            self.page.goto(url)
            self.logger.info(f"成功加载页面: {url}")
        except Exception as e:
            self.logger.error(f"导航失败: {url}, 错误: {str(e)}")
            raise

    @allure.step("点击元素")
    def click(self, locator: Union[str, Tuple[str, str], Element]):
        """智能点击元素 - 支持 CSS/XPath 字符串、Role 元组或 Element 对象

        Args:
            locator: 定位器，支持：
                - Element: Element("role", ("button", "提交"), desc="提交按钮")
                - CSS: "#id" 或 ".class"
                - XPath: "//button[@id='submit']"
                - Role: ("button", "提交")
        """
        try:
            loc_desc = self._get_locator_description(locator)
            self.logger.info(f"尝试点击元素: {loc_desc}")
            self._get_locator(locator).click(timeout=self.timeout)
            self.logger.info(f"成功点击元素: {loc_desc}")
        except TimeoutError:
            error_msg = f"元素未找到或不可点击: {loc_desc}"
            self.logger.error(error_msg)
            # 转换为 AssertionError，让 Allure 显示为 Failed (红色) 而非 Broken (黄色)
            raise AssertionError(error_msg)
        except Exception as e:
            self.logger.error(f"点击元素失败: {loc_desc}, 错误: {str(e)}")
            raise

    @allure.step("填充元素")
    def fill(self, locator: Union[str, Tuple[str, str], Element], text: str):
        """智能填充输入框 - 支持 CSS/XPath 字符串、Role 元组或 Element 对象

        Args:
            locator: 定位器，支持：
                - Element: Element("placeholder", "请输入用户名", desc="用户名输入框")
                - CSS: "#username" 或 ".input-field"
                - XPath: "//input[@name='username']"
                - Role: ("textbox", "用户名")
            text: 要填充的文本
        """
        try:
            loc_desc = self._get_locator_description(locator)
            self.logger.info(f"尝试填充元素: {loc_desc}, 内容: {text}")
            self._get_locator(locator).fill(text, timeout=self.timeout)
            self.logger.info(f"成功填充元素: {loc_desc}")
        except TimeoutError:
            error_msg = f"输入框未找到: {loc_desc}"
            self.logger.error(error_msg)
            # 转换为 AssertionError，让 Allure 显示为 Failed (红色)
            raise AssertionError(error_msg)
        except Exception as e:
            self.logger.error(f"填充元素失败: {loc_desc}, 错误: {str(e)}")
            raise

    @allure.step("获取元素文本")
    def get_text(self, locator: Union[str, Tuple[str, str], Element]) -> str:
        """智能获取元素文本 - 支持 CSS/XPath 字符串、Role 元组或 Element 对象

        Args:
            locator: 定位器，支持：
                - Element: Element("text", "欢迎回来", desc="欢迎语")
                - CSS: ".title" 或 "#heading"
                - XPath: "//h1[@class='title']"
                - Role: ("heading", "页面标题")

        Returns:
            元素的文本内容
        """
        try:
            loc_desc = self._get_locator_description(locator)
            self.logger.info(f"尝试获取元素文本: {loc_desc}")
            text = self._get_locator(locator).text_content(timeout=self.timeout)
            self.logger.info(f"成功获取文本: {loc_desc}, 内容: {text}")
            return text
        except TimeoutError:
            error_msg = f"元素未找到,无法获取文本: {loc_desc}"
            self.logger.error(error_msg)
            # 转换为 AssertionError，让 Allure 显示为 Failed (红色)
            raise AssertionError(error_msg)
        except Exception as e:
            self.logger.error(f"获取文本失败: {loc_desc}, 错误: {str(e)}")
            raise

    @allure.step("检查元素可见性")
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
        try:
            loc_desc = self._get_locator_description(locator)
            visible = self._get_locator(locator).is_visible()
            if visible:
                self.logger.info(f"元素可见: {loc_desc}")
            else:
                self.logger.warning(f"元素不可见: {loc_desc}")
            return visible
        except Exception as e:
            self.logger.error(f"检查元素可见性失败: {loc_desc}, 错误: {str(e)}")
            return False

    @allure.step("等待元素出现")
    def wait_for_selector(self, locator: Union[str, Tuple[str, str], Element]):
        """智能等待元素出现 - 支持 CSS/XPath 字符串、Role 元组或 Element 对象

        Args:
            locator: 定位器，支持：
                - Element: Element("css", ".loading", desc="加载动画")
                - CSS: ".loading" 或 "#spinner"
                - XPath: "//div[@class='loading']"
                - Role: ("status", "加载中")
        """
        try:
            loc_desc = self._get_locator_description(locator)
            self.logger.info(f"等待元素出现: {loc_desc}")
            self._get_locator(locator).wait_for(state="visible", timeout=self.timeout)
            self.logger.info(f"元素已出现: {loc_desc}")
        except TimeoutError:
            error_msg = f"等待超时,元素未出现: {loc_desc}"
            self.logger.error(error_msg)
            # 转换为 AssertionError，让 Allure 显示为 Failed (红色)
            raise AssertionError(error_msg)
        except Exception as e:
            self.logger.error(f"等待元素失败: {loc_desc}, 错误: {str(e)}")
            raise

    @allure.step("检查元素是否选中")
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
        try:
            loc_desc = self._get_locator_description(locator)
            checked = self._get_locator(locator).is_checked()
            if checked:
                self.logger.info(f"元素已选中: {loc_desc}")
            else:
                self.logger.warning(f"元素未选中: {loc_desc}")
            return checked
        except Exception as e:
            self.logger.error(f"检查元素是否选中失败: {loc_desc}, 错误: {str(e)}")
            return False

    @allure.step("选中元素")
    def check(self, locator: Union[str, Tuple[str, str], Element]):
        """智能选中元素 - 支持 CSS/XPath 字符串、Role 元组或 Element 对象

        Args:
            locator: 定位器，支持：
                - Element: Element("label", "记住我", desc="记住密码复选框")
                - CSS: "#remember" 或 ".agree-checkbox"
                - XPath: "//input[@name='remember']"
                - Role: ("checkbox", "记住我")
        """
        try:
            loc_desc = self._get_locator_description(locator)
            self.logger.info(f"尝试选中元素: {loc_desc}")
            self._get_locator(locator).check(timeout=self.timeout)
            self.logger.info(f"成功选中元素: {loc_desc}")
        except TimeoutError:
            error_msg = f"元素未找到: {loc_desc}"
            self.logger.error(error_msg)
            # 转换为 AssertionError，让 Allure 显示为 Failed (红色)
            raise AssertionError(error_msg)
        except Exception as e:
            self.logger.error(f"选中元素失败: {loc_desc}, 错误: {str(e)}")
            raise

    @allure.step("取消选中元素")
    def uncheck(self, locator: Union[str, Tuple[str, str], Element]):
        """智能取消选中元素 - 支持 CSS/XPath 字符串、Role 元组或 Element 对象

        Args:
            locator: 定位器，支持：
                - Element: Element("label", "记住我", desc="记住密码复选框")
                - CSS: "#remember" 或 ".agree-checkbox"
                - XPath: "//input[@name='remember']"
                - Role: ("checkbox", "记住我")
        """
        try:
            loc_desc = self._get_locator_description(locator)
            self.logger.info(f"尝试取消选中元素: {loc_desc}")
            self._get_locator(locator).uncheck(timeout=self.timeout)
            self.logger.info(f"成功取消选中元素: {loc_desc}")
        except TimeoutError:
            error_msg = f"元素未找到: {loc_desc}"
            self.logger.error(error_msg)
            # 转换为 AssertionError，让 Allure 显示为 Failed (红色)
            raise AssertionError(error_msg)
        except Exception as e:
            self.logger.error(f"取消选中元素失败: {loc_desc}, 错误: {str(e)}")
            raise

    @allure.step("上传文件")
    def file_setInputFiles(self, locator: Union[str, Tuple[str, str], Element], file_path: Union[str, list]):
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

        Examples:
            # 上传单个文件
            self.upload_file("input[type='file']", "/Users/test/document.pdf")

            # 使用 Element 对象上传文件
            FILE_INPUT = Element("css", "input[type='file']", desc="文件上传框")
            self.upload_file(FILE_INPUT, "/Users/test/image.jpg")

            # 上传多个文件
            files = ["/Users/test/file1.pdf", "/Users/test/file2.jpg"]
            self.upload_file("input[type='file']", files)
        """
        try:
            loc_desc = self._get_locator_description(locator)
            file_info = file_path if isinstance(file_path, str) else f"{len(file_path)} 个文件"
            self.logger.info(f"尝试上传文件到元素: {loc_desc}, 文件: {file_info}")
            self._get_locator(locator).set_input_files(file_path, timeout=self.timeout)
            self.logger.info(f"成功上传文件: {file_info}")
        except TimeoutError:
            error_msg = f"文件上传框未找到: {loc_desc}"
            self.logger.error(error_msg)
            # 转换为 AssertionError，让 Allure 显示为 Failed (红色)
            raise AssertionError(error_msg)
        except Exception as e:
            self.logger.error(f"上传文件失败: {loc_desc}, 错误: {str(e)}")
            raise

    @allure.step("点击按钮并上传文件")
    def file_filechooser(self, locator: Union[str, Tuple[str, str], Element], file_path: Union[str, list]):
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

        Examples:
            # 点击上传按钮并选择文件
            self.click_and_upload_file(("button", "上传文件"), "/Users/test/document.pdf")

            # 使用 Element 对象
            UPLOAD_BTN = Element("role", ("button", "选择文件"), desc="上传按钮")
            self.click_and_upload_file(UPLOAD_BTN, "/Users/test/image.jpg")

            # 上传多个文件
            files = ["/Users/test/file1.pdf", "/Users/test/file2.jpg"]
            self.click_and_upload_file("button#upload", files)
        """
        try:
            loc_desc = self._get_locator_description(locator)
            file_info = file_path if isinstance(file_path, str) else f"{len(file_path)} 个文件"
            self.logger.info(f"尝试点击按钮并上传文件: {loc_desc}, 文件: {file_info}")

            # 监听文件选择器事件
            with self.page.expect_file_chooser() as fc_info:
                self._get_locator(locator).click(timeout=self.timeout)

            file_chooser = fc_info.value
            self.logger.info(f"捕获到文件选择对话框")

            # 设置文件
            file_chooser.set_files(file_path)
            self.logger.info(f"成功上传文件: {file_info}")

        except TimeoutError:
            error_msg = f"按钮未找到或文件选择对话框未出现: {loc_desc}"
            self.logger.error(error_msg)
            # 转换为 AssertionError，让 Allure 显示为 Failed (红色)
            raise AssertionError(error_msg)
        except Exception as e:
            self.logger.error(f"点击按钮上传文件失败: {loc_desc}, 错误: {str(e)}")
            raise

    # ========== 新窗口/新标签页处理 ==========

    @allure.step("点击并处理新窗口")
    def click_and_handle_new_page(self, locator: Union[str, Tuple[str, str], Element],
                                   wait_for_load: bool = True):
        """点击元素并获取新打开的页面对象

        适用场景：
        - 点击按钮/链接会打开新标签页
        - target="_blank" 的链接
        - window.open() 打开的新窗口

        Args:
            locator: 定位器（会触发打开新页面的元素）
            wait_for_load: 是否等待新页面加载完成，默认 True

        Returns:
            新页面的 Page 对象

        Examples:
            # 点击"在新标签页打开"按钮
            new_page = self.click_and_handle_new_page(("button", "在新标签页打开"))

            # 在新页面操作
            new_page.click("#some-button")

            # 关闭新页面
            new_page.close()
        """
        try:
            loc_desc = self._get_locator_description(locator)
            self.logger.info(f"尝试点击元素并处理新窗口: {loc_desc}")

            # 监听新页面事件
            with self.page.context.expect_page() as new_page_info:
                self._get_locator(locator).click(timeout=self.timeout)

            new_page = new_page_info.value
            self.logger.info(f"成功获取新页面: {new_page.url}")

            # 等待新页面加载完成
            if wait_for_load:
                self.logger.info("等待新页面加载完成...")
                new_page.wait_for_load_state('networkidle', timeout=self.timeout)
                self.logger.info(f"新页面加载完成: {new_page.url}")

            return new_page

        except TimeoutError:
            error_msg = f"点击元素超时或新页面未打开: {loc_desc}"
            self.logger.error(error_msg)
            raise AssertionError(error_msg)
        except Exception as e:
            self.logger.error(f"处理新窗口失败: {loc_desc}, 错误: {str(e)}")
            raise

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
    def go_back(self, wait_for_load: bool = True):
        """浏览器后退到上一页

        Args:
            wait_for_load: 是否等待页面加载完成，默认 True

        Examples:
            # 后退到上一页
            self.go_back()

            # 后退但不等待加载完成
            self.go_back(wait_for_load=False)
        """
        try:
            self.logger.info("浏览器后退到上一页")
            self.page.go_back(timeout=self.timeout)

            if wait_for_load:
                self.logger.info("等待页面加载完成...")
                self.page.wait_for_load_state('networkidle', timeout=self.timeout)

            self.logger.info(f"成功后退到: {self.page.url}")
        except TimeoutError:
            error_msg = "浏览器后退操作超时"
            self.logger.error(error_msg)
            raise AssertionError(error_msg)
        except Exception as e:
            self.logger.error(f"浏览器后退失败, 错误: {str(e)}")
            raise

    @allure.step("浏览器前进")
    def go_forward(self, wait_for_load: bool = True):
        """浏览器前进到下一页

        Args:
            wait_for_load: 是否等待页面加载完成，默认 True

        Examples:
            # 前进到下一页
            self.go_forward()

            # 前进但不等待加载完成
            self.go_forward(wait_for_load=False)
        """
        try:
            self.logger.info("浏览器前进到下一页")
            self.page.go_forward(timeout=self.timeout)

            if wait_for_load:
                self.logger.info("等待页面加载完成...")
                self.page.wait_for_load_state('networkidle', timeout=self.timeout)

            self.logger.info(f"成功前进到: {self.page.url}")
        except TimeoutError:
            error_msg = "浏览器前进操作超时"
            self.logger.error(error_msg)
            raise AssertionError(error_msg)
        except Exception as e:
            self.logger.error(f"浏览器前进失败, 错误: {str(e)}")
            raise

    # ========== iframe 处理 ==========

    def _get_frame_element_selector(self, locator: Union[str, Tuple[str, str], Element]) -> str:
        """将定位器转换为 iframe 中可用的 CSS 选择器字符串

        Args:
            locator: 定位器（Element 对象、元组或字符串）

        Returns:
            CSS 选择器字符串
        """
        # Element 对象：转换为对应的选择器
        if isinstance(locator, Element):
            by = locator.by
            value = locator.value

            # Role 定位器
            if by == "role":
                if isinstance(value, tuple) and len(value) == 2:
                    role, name = value
                    # 使用 Playwright 的 role 选择器语法
                    return f"role={role}[name='{name}']"
                elif isinstance(value, tuple) and len(value) == 1:
                    return f"role={value[0]}"
            # Text 定位器
            elif by == "text":
                return f"text={value}"
            # CSS 选择器
            elif by == "css":
                return value
            # XPath 选择器
            elif by == "xpath":
                return f"xpath={value}"
            # 其他定位器类型暂不支持，抛出错误
            else:
                raise ValueError(f"iframe 中暂不支持 Element 的定位方式: {by}")

        # 元组形式：转换为 role 选择器
        elif isinstance(locator, tuple):
            role, name = locator
            return f"role={role}[name='{name}']"

        # 字符串形式：直接返回
        elif isinstance(locator, str):
            return locator

        else:
            raise ValueError(f"不支持的定位器类型: {type(locator)}")

    @allure.step("切换到 iframe: {frame_locator}")
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
        try:
            self.logger.info(f"切换到 iframe: {frame_locator}")
            frame = self.page.frame_locator(frame_locator)
            self.logger.info(f"成功切换到 iframe: {frame_locator}")
            return frame
        except Exception as e:
            self.logger.error(f"切换到 iframe 失败: {frame_locator}, 错误: {str(e)}")
            raise

    @allure.step("在 iframe 中点击元素")
    def frame_click(self, frame_locator: str, element_locator: Union[str, Tuple[str, str], Element]):
        """在指定 iframe 中点击元素

        Args:
            frame_locator: iframe 的 CSS 选择器
            element_locator: iframe 内元素的定位器，支持：
                - Element 对象（推荐）
                - CSS 选择器字符串
                - Role 元组

        Examples:
            # 使用 Element 对象
            LINK = Element("role", ("link", "提交"), desc="提交链接")
            self.frame_click("iframe#content", LINK)

            # 使用 CSS 选择器
            self.frame_click("iframe#content", "button#submit")

            # 使用 Role 元组
            self.frame_click("iframe#content", ("button", "提交"))
        """
        try:
            loc_desc = self._get_locator_description(element_locator)
            selector = self._get_frame_element_selector(element_locator)
            self.logger.info(f"在 iframe '{frame_locator}' 中点击元素: {loc_desc}")
            self.page.frame_locator(frame_locator).locator(selector).click(timeout=self.timeout)
            self.logger.info(f"成功点击 iframe 中的元素: {loc_desc}")
        except TimeoutError:
            error_msg = f"iframe 或元素未找到: iframe={frame_locator}, element={loc_desc}"
            self.logger.error(error_msg)
            raise AssertionError(error_msg)
        except Exception as e:
            self.logger.error(f"在 iframe 中点击元素失败, 错误: {str(e)}")
            raise

    @allure.step("在 iframe 中填充元素")
    def frame_fill(self, frame_locator: str, element_locator: Union[str, Tuple[str, str], Element], text: str):
        """在指定 iframe 中填充输入框

        Args:
            frame_locator: iframe 的 CSS 选择器
            element_locator: iframe 内元素的定位器，支持 Element 对象、CSS 选择器、Role 元组
            text: 要填充的文本

        Examples:
            # 使用 Element 对象
            USERNAME = Element("placeholder", "请输入用户名", desc="用户名输入框")
            self.frame_fill("iframe#login-frame", USERNAME, "admin")

            # 使用 CSS 选择器
            self.frame_fill("iframe#login-frame", "input#username", "admin")
        """
        try:
            loc_desc = self._get_locator_description(element_locator)
            selector = self._get_frame_element_selector(element_locator)
            self.logger.info(f"在 iframe '{frame_locator}' 中填充元素: {loc_desc}, 内容: {text}")
            self.page.frame_locator(frame_locator).locator(selector).fill(text, timeout=self.timeout)
            self.logger.info(f"成功填充 iframe 中的元素: {loc_desc}")
        except TimeoutError:
            error_msg = f"iframe 或元素未找到: iframe={frame_locator}, element={loc_desc}"
            self.logger.error(error_msg)
            raise AssertionError(error_msg)
        except Exception as e:
            self.logger.error(f"在 iframe 中填充元素失败, 错误: {str(e)}")
            raise

    @allure.step("获取 iframe 中元素的文本")
    def frame_get_text(self, frame_locator: str, element_locator: Union[str, Tuple[str, str], Element]) -> str:
        """获取指定 iframe 中元素的文本

        Args:
            frame_locator: iframe 的 CSS 选择器
            element_locator: iframe 内元素的定位器，支持 Element 对象、CSS 选择器、Role 元组

        Returns:
            元素的文本内容

        Examples:
            # 使用 Element 对象
            TITLE = Element("css", "h1.title", desc="标题")
            title = self.frame_get_text("iframe#content", TITLE)

            # 使用 CSS 选择器
            title = self.frame_get_text("iframe#content", "h1.title")
        """
        try:
            loc_desc = self._get_locator_description(element_locator)
            selector = self._get_frame_element_selector(element_locator)
            self.logger.info(f"获取 iframe '{frame_locator}' 中元素文本: {loc_desc}")
            text = self.page.frame_locator(frame_locator).locator(selector).text_content(timeout=self.timeout)
            self.logger.info(f"成功获取文本: {text}")
            return text
        except TimeoutError:
            error_msg = f"iframe 或元素未找到: iframe={frame_locator}, element={loc_desc}"
            self.logger.error(error_msg)
            raise AssertionError(error_msg)
        except Exception as e:
            self.logger.error(f"获取 iframe 中元素文本失败, 错误: {str(e)}")
            raise

    @allure.step("检查 iframe 中元素是否可见")
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
        try:
            loc_desc = self._get_locator_description(element_locator)
            selector = self._get_frame_element_selector(element_locator)
            visible = self.page.frame_locator(frame_locator).locator(selector).is_visible()
            if visible:
                self.logger.info(f"iframe 中元素可见: {loc_desc}")
            else:
                self.logger.warning(f"iframe 中元素不可见: {loc_desc}")
            return visible
        except Exception as e:
            self.logger.error(f"检查 iframe 中元素可见性失败, 错误: {str(e)}")
            return False

    @allure.step("等待 iframe 中元素出现")
    def frame_wait_for_selector(self, frame_locator: str, element_locator: Union[str, Tuple[str, str], Element]):
        """等待 iframe 中元素出现

        Args:
            frame_locator: iframe 的 CSS 选择器
            element_locator: iframe 内元素的定位器，支持 Element 对象、CSS 选择器、Role 元组

        Examples:
            # 使用 Element 对象
            LOADING = Element("css", ".loading", desc="加载动画")
            self.frame_wait_for_selector("iframe#content", LOADING)

            # 使用 CSS 选择器
            self.frame_wait_for_selector("iframe#content", ".loading")
        """
        try:
            loc_desc = self._get_locator_description(element_locator)
            selector = self._get_frame_element_selector(element_locator)
            self.logger.info(f"等待 iframe '{frame_locator}' 中元素出现: {loc_desc}")
            self.page.frame_locator(frame_locator).locator(selector).wait_for(state="visible", timeout=self.timeout)
            self.logger.info(f"iframe 中元素已出现: {loc_desc}")
        except TimeoutError:
            error_msg = f"等待超时, iframe 中元素未出现: iframe={frame_locator}, element={loc_desc}"
            self.logger.error(error_msg)
            raise AssertionError(error_msg)
        except Exception as e:
            self.logger.error(f"等待 iframe 中元素失败, 错误: {str(e)}")
            raise

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
    def click_and_handle_dialog(self, locator: Union[str, Tuple[str, str], Element],
                                 accept: bool = True, message_check: str = None) -> str:
        """点击元素并处理弹出的 JavaScript 对话框（通用方法）

        适用场景：
        - JavaScript alert() 对话框
        - JavaScript confirm() 对话框
        - JavaScript prompt() 对话框

        Args:
            locator: 定位器（会触发对话框的元素）
            accept: True=点击"确定"，False=点击"取消"
            message_check: 可选，验证对话框文本是否包含指定内容

        Returns:
            对话框的完整文本内容

        Raises:
            AssertionError: 对话框文本验证失败

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
        try:
            loc_desc = self._get_locator_description(locator)
            action_text = "接受" if accept else "取消"
            self.logger.info(f"尝试点击元素并{action_text}对话框: {loc_desc}")

            # 定义对话框处理函数
            def handle_dialog(dialog):
                dialog_message = dialog.message
                self.logger.info(f"捕获到对话框，类型: {dialog.type}, 内容: {dialog_message}")

                # 可选：验证对话框文本
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

            # 先注册监听器
            self.page.once("dialog", handle_dialog)

            # 再点击触发对话框
            self._get_locator(locator).click(timeout=self.timeout)

            # 等待对话框处理完成
            self.page.wait_for_timeout(500)

            self.logger.info(f"对话框处理完成: {loc_desc}")
            return None

        except TimeoutError:
            error_msg = f"点击元素超时或对话框未出现: {loc_desc}"
            self.logger.error(error_msg)
            raise AssertionError(error_msg)
        except Exception as e:
            self.logger.error(f"处理对话框失败: {loc_desc}, 错误: {str(e)}")
            raise

    # ========== 鼠标悬停和拖拽操作 ==========

    @allure.step("悬停到元素")
    def hover(self, locator: Union[str, Tuple[str, str], Element], position: dict = None, force: bool = False):
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
        try:
            loc_desc = self._get_locator_description(locator)
            self.logger.info(f"尝试悬停到元素: {loc_desc}")

            hover_options = {"timeout": self.timeout}
            if position:
                hover_options["position"] = position
            if force:
                hover_options["force"] = force

            self._get_locator(locator).hover(**hover_options)
            self.logger.info(f"成功悬停到元素: {loc_desc}")
        except TimeoutError:
            error_msg = f"元素未找到或不可悬停: {loc_desc}"
            self.logger.error(error_msg)
            raise AssertionError(error_msg)
        except Exception as e:
            self.logger.error(f"悬停失败: {loc_desc}, 错误: {str(e)}")
            raise

    @allure.step("拖拽元素到目标位置")
    def drag_to(self, source_locator: Union[str, Tuple[str, str], Element],
                target_locator: Union[str, Tuple[str, str], Element],
                source_position: dict = None, target_position: dict = None, force: bool = False):
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
        try:
            source_desc = self._get_locator_description(source_locator)
            target_desc = self._get_locator_description(target_locator)
            self.logger.info(f"尝试拖拽元素: {source_desc} -> {target_desc}")

            drag_options = {"timeout": self.timeout}
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
        except TimeoutError:
            error_msg = f"拖拽超时，源元素或目标元素未找到: {source_desc} -> {target_desc}"
            self.logger.error(error_msg)
            raise AssertionError(error_msg)
        except Exception as e:
            self.logger.error(f"拖拽失败: {source_desc} -> {target_desc}, 错误: {str(e)}")
            raise

    @allure.step("使用鼠标操作拖拽元素")
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
        try:
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
        except TimeoutError:
            error_msg = f"鼠标拖拽超时: {source_desc} -> {target_desc}"
            self.logger.error(error_msg)
            raise AssertionError(error_msg)
        except Exception as e:
            self.logger.error(f"鼠标拖拽失败: {source_desc} -> {target_desc}, 错误: {str(e)}")
            raise

    @allure.step("悬停并等待元素出现")
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
            wait_timeout: 等待超时时间（毫秒），默认使用 self.timeout

        Examples:
            # 悬停菜单并等待子菜单出现
            self.hover_and_wait("#menu-item", ".submenu")

            # 使用 Element 对象
            MENU = Element("css", ".menu-trigger", desc="菜单触发器")
            SUBMENU = Element("css", ".submenu", desc="子菜单")
            self.hover_and_wait(MENU, SUBMENU)
        """
        try:
            hover_desc = self._get_locator_description(hover_locator)
            wait_desc = self._get_locator_description(wait_locator)
            timeout = wait_timeout or self.timeout

            self.logger.info(f"悬停到元素: {hover_desc}")
            self._get_locator(hover_locator).hover(timeout=self.timeout)

            self.logger.info(f"等待元素出现: {wait_desc}")
            self._get_locator(wait_locator).wait_for(state="visible", timeout=timeout)

            self.logger.info(f"悬停并等待成功: {hover_desc} -> {wait_desc}")
        except TimeoutError:
            error_msg = f"悬停或等待超时: {hover_desc} -> {wait_desc}"
            self.logger.error(error_msg)
            raise AssertionError(error_msg)
        except Exception as e:
            self.logger.error(f"悬停并等待失败: {hover_desc} -> {wait_desc}, 错误: {str(e)}")
            raise
