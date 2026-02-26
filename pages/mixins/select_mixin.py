import allure
from utils.element import Element
from utils.exception_handler import ExceptionHandler
from typing import Union, Tuple


class SelectMixin:
    """下拉选择操作：原生 select 和自定义下拉组件"""

    @allure.step("选择下拉选项")
    @ExceptionHandler.handle_playwright_exception("选择下拉选项")
    def select_option(self, locator: Union[str, Tuple[str, str], Element],
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
        element = locator if isinstance(locator, Element) else None
        final_timeout = self._resolve_timeout(timeout, element)

        if label is not None:
            self.logger.info(f"尝试选择下拉选项: {loc_desc}, label={label}")
            result = self._get_locator(locator).select_option(label=label, timeout=final_timeout)
        elif value is not None:
            self.logger.info(f"尝试选择下拉选项: {loc_desc}, value={value}")
            result = self._get_locator(locator).select_option(value=value, timeout=final_timeout)
        elif index is not None:
            self.logger.info(f"尝试选择下拉选项: {loc_desc}, index={index}")
            result = self._get_locator(locator).select_option(index=index, timeout=final_timeout)
        else:
            raise ValueError("必须提供 value、label 或 index 中的至少一个参数")

        self.logger.info(f"成功选择下拉选项: {loc_desc}, 选中值: {result}")
        return result

    @allure.step("选择自定义下拉选项")
    @ExceptionHandler.handle_playwright_exception("选择自定义下拉选项")
    def click_select_option(self, trigger_locator: Union[str, Tuple[str, str], Element],
                            option_locator: Union[str, Tuple[str, str], Element],
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

        trigger_element = trigger_locator if isinstance(trigger_locator, Element) else None
        final_timeout = self._resolve_timeout(timeout, trigger_element)

        self.logger.info(f"点击下拉触发器: {trigger_desc}")
        self._get_locator(trigger_locator).click(timeout=final_timeout)

        option_element = option_locator if isinstance(option_locator, Element) else None
        option_timeout = self._resolve_timeout(timeout, option_element)

        option_loc = self._get_locator(option_locator)
        option_loc.wait_for(state="visible", timeout=option_timeout)

        if option_text:
            self.logger.info(f"在 {option_desc} 中查找文本: {option_text}")
            option_loc.get_by_text(option_text, exact=True).click(timeout=option_timeout)
        else:
            option_loc.click(timeout=option_timeout)

        self.logger.info(f"成功选择自定义下拉选项: {trigger_desc} -> {option_text or option_desc}")
