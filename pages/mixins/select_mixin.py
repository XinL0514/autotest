import allure
from pages.mixins.locator_mixin import LocatorInput
from utils.exception_handler import ExceptionHandler


class SelectMixin:
    """下拉选择操作：原生 select 和自定义下拉组件"""

    @allure.step("选择下拉选项")
    @ExceptionHandler.handle_playwright_exception("选择下拉选项")
    def select_option(self, locator: LocatorInput,
                      value: str = None, label: str = None, index: int = None, timeout: int = None) -> list:
        """选择 <select> 下拉框的选项 - 支持按 value、label 或 index 选择

        Args:
            locator: 定位器
            value: 按 option 的 value 属性选择
            label: 按 option 的显示文本选择
            index: 按 option 的索引选择（从 0 开始）
            timeout: 可选超时时间（毫秒）

        Returns:
            被选中的 option 的 value 列表
        """
        loc_desc = self._get_locator_description(locator)
        options_count = sum(option is not None for option in (value, label, index))
        if options_count == 0:
            raise ValueError("必须提供 value、label 或 index 中的至少一个参数")
        if options_count > 1:
            raise ValueError("value、label、index 参数互斥，只能传一个")

        if label is not None:
            self.logger.info(f"尝试选择下拉选项: {loc_desc}, label={label}")
            result = self._run_locator_method(locator, "select_option", timeout=timeout, label=label)
        elif value is not None:
            self.logger.info(f"尝试选择下拉选项: {loc_desc}, value={value}")
            result = self._run_locator_method(locator, "select_option", timeout=timeout, value=value)
        else:
            self.logger.info(f"尝试选择下拉选项: {loc_desc}, index={index}")
            result = self._run_locator_method(locator, "select_option", timeout=timeout, index=index)

        self.logger.info(f"成功选择下拉选项: {loc_desc}, 选中值: {result}")
        return result

    @allure.step("选择自定义下拉选项")
    @ExceptionHandler.handle_playwright_exception("选择自定义下拉选项")
    def click_select_option(self, trigger_locator: LocatorInput,
                            option_locator: LocatorInput,
                            option_text: str = None, timeout: int = None):
        """点击自定义下拉组件并选择选项（适用于 antd Select、Element UI Select 等）

        操作流程：点击触发器 → 等待下拉面板出现 → 点击目标选项

        Args:
            trigger_locator: 下拉触发器的定位器
            option_locator: 目标选项的定位器，或选项列表容器（配合 option_text 使用）
            option_text: 可选，选项的显示文本
            timeout: 可选超时时间（毫秒）
        """
        trigger_desc = self._get_locator_description(trigger_locator)
        option_desc = self._get_locator_description(option_locator)

        self.logger.info(f"点击下拉触发器: {trigger_desc}")
        self._run_locator_method(trigger_locator, "click", timeout=timeout)

        option_loc = self._get_locator(option_locator)
        option_timeout = self._resolve_timeout(timeout, self._get_element(option_locator))
        self._run_locator_method(option_locator, "wait_for", timeout=timeout, state="visible")

        if option_text:
            self.logger.info(f"在 {option_desc} 中查找文本: {option_text}")
            option_loc.get_by_text(option_text, exact=True).click(timeout=option_timeout)
        else:
            option_loc.click(timeout=option_timeout)

        self.logger.info(f"成功选择自定义下拉选项: {trigger_desc} -> {option_text or option_desc}")
