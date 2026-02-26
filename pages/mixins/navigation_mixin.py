import allure
from utils.exception_handler import ExceptionHandler


class NavigationMixin:
    """浏览器导航操作：后退、前进"""

    @allure.step("浏览器后退")
    @ExceptionHandler.handle_playwright_exception("浏览器后退")
    def go_back(self, wait_for_load: bool = True, wait_until: str = "domcontentloaded", timeout: int = None):
        """浏览器后退到上一页

        Args:
            wait_for_load: 是否等待页面加载完成，默认 True
            wait_until: 页面加载等待策略（domcontentloaded/load/networkidle）
            timeout: 可选超时时间（毫秒），优先级：timeout 参数 > self.timeout
        """
        final_timeout = self._resolve_timeout(timeout)
        self.logger.info("浏览器后退到上一页")
        self.page.go_back(timeout=final_timeout)

        if wait_for_load:
            self.logger.info(f"等待页面加载完成，策略: {wait_until}")
            self.page.wait_for_load_state(wait_until, timeout=final_timeout)

        self.logger.info(f"成功后退到: {self.page.url}")

    @allure.step("浏览器前进")
    @ExceptionHandler.handle_playwright_exception("浏览器前进")
    def go_forward(self, wait_for_load: bool = True, wait_until: str = "domcontentloaded", timeout: int = None):
        """浏览器前进到下一页

        Args:
            wait_for_load: 是否等待页面加载完成，默认 True
            wait_until: 页面加载等待策略（domcontentloaded/load/networkidle）
            timeout: 可选超时时间（毫秒），优先级：timeout 参数 > self.timeout
        """
        final_timeout = self._resolve_timeout(timeout)
        self.logger.info("浏览器前进到下一页")
        self.page.go_forward(timeout=final_timeout)

        if wait_for_load:
            self.logger.info(f"等待页面加载完成，策略: {wait_until}")
            self.page.wait_for_load_state(wait_until, timeout=final_timeout)

        self.logger.info(f"成功前进到: {self.page.url}")
