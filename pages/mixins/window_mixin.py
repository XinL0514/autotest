import allure
from pages.mixins.locator_mixin import LocatorInput
from utils.exception_handler import ExceptionHandler


class WindowMixin:
    """多窗口/标签页操作"""

    @allure.step("点击并处理新窗口")
    @ExceptionHandler.handle_playwright_exception("点击并处理新窗口")
    def click_and_handle_new_page(self, locator: LocatorInput,
                                   wait_for_load: bool = True, wait_until: str = "domcontentloaded", timeout: int = None):
        """点击元素并获取新打开的页面对象

        Args:
            locator: 会触发打开新页面的元素定位器
            wait_for_load: 是否等待新页面加载完成，默认 True
            wait_until: 页面加载等待策略（domcontentloaded/load/networkidle）
            timeout: 可选超时时间（毫秒）

        Returns:
            新页面的 Page 对象
        """
        loc_desc = self._get_locator_description(locator)
        self.logger.info(f"尝试点击元素并处理新窗口: {loc_desc}")

        final_timeout = self._resolve_timeout(timeout, self._get_element(locator))

        with self.page.context.expect_page(timeout=final_timeout) as new_page_info:
            self._run_locator_method(locator, "click", timeout=timeout)

        new_page = new_page_info.value
        self.logger.info(f"成功获取新页面: {new_page.url}")

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
        """
        pages = self.page.context.pages
        self.logger.info(f"当前打开的页面数: {len(pages)}")
        for i, page in enumerate(pages):
            self.logger.debug(f"  页面 {i}: {page.url}")
        return pages

    @allure.step("关闭所有新窗口（保留原窗口）")
    def close_all_new_windows(self):
        """关闭除当前页面外的所有其他页面"""
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

        Returns:
            最新的 Page 对象
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
            url_pattern: URL 中包含的字符串
            switch_current: 是否切换当前页面（更新 self.page），默认 True

        Returns:
            匹配到的 Page 对象

        Raises:
            AssertionError: 未找到匹配的页面
        """
        all_pages = self.page.context.pages
        self.logger.info(f"在 {len(all_pages)} 个页面中查找包含 '{url_pattern}' 的 URL")

        for i, page in enumerate(all_pages):
            self.logger.debug(f"  页面 {i}: {page.url}")

        matched_page = None
        for page in all_pages:
            if url_pattern in page.url:
                matched_page = page
                break

        if matched_page is None:
            error_msg = f"未找到包含 '{url_pattern}' 的页面\n当前打开的页面:\n"
            for i, page in enumerate(all_pages):
                error_msg += f"  [{i}] {page.url}\n"
            self.logger.error(error_msg)
            raise AssertionError(error_msg)

        self.logger.info(f"找到匹配页面: {matched_page.url}")

        if switch_current:
            self.logger.info(f"切换当前页面到: {matched_page.url}")
            self.page = matched_page

        return matched_page

    @allure.step("获取指定 URL 的页面对象")
    def get_page_by_url(self, url_pattern: str):
        """通过 URL 特征获取页面对象（不切换当前页面）

        Args:
            url_pattern: URL 中包含的字符串

        Returns:
            匹配到的 Page 对象
        """
        return self.switch_to_page_by_url(url_pattern, switch_current=False)
