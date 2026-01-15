import allure
from playwright.sync_api import Page, TimeoutError, Locator
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
