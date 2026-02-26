import allure
from utils.element import Element
from utils.exception_handler import ExceptionHandler
from typing import Union, Tuple, Optional


class DialogMixin:
    """JavaScript 对话框处理"""

    @allure.step("点击元素并接受对话框")
    @ExceptionHandler.handle_playwright_exception("点击元素并接受对话框")
    def click_and_accept_dialog(self, locator: Union[str, Tuple[str, str], Element],
                                message_check: str = None):
        """点击元素并自动接受弹出的对话框（点击"确定"）

        Args:
            locator: 会触发对话框的元素定位器
            message_check: 可选，验证对话框文本是否包含指定内容
        """
        return self.click_and_handle_dialog(locator, accept=True, message_check=message_check)

    @allure.step("点击元素并取消对话框")
    @ExceptionHandler.handle_playwright_exception("点击元素并取消对话框")
    def click_and_dismiss_dialog(self, locator: Union[str, Tuple[str, str], Element],
                                 message_check: str = None):
        """点击元素并自动取消弹出的对话框（点击"取消"）

        Args:
            locator: 会触发对话框的元素定位器
            message_check: 可选，验证对话框文本是否包含指定内容
        """
        return self.click_and_handle_dialog(locator, accept=False, message_check=message_check)

    @allure.step("点击元素并处理对话框")
    @ExceptionHandler.handle_playwright_exception("点击元素并处理对话框")
    def click_and_handle_dialog(self, locator: Union[str, Tuple[str, str], Element],
                                accept: bool = True, message_check: str = None, timeout: int = None) -> Optional[str]:
        """点击元素并处理弹出的 JavaScript 对话框（通用方法）

        Args:
            locator: 会触发对话框的元素定位器
            accept: True=点击"确定"，False=点击"取消"
            message_check: 可选，验证对话框文本是否包含指定内容
            timeout: 可选超时时间（毫秒）

        Returns:
            对话框的完整文本内容

        Raises:
            AssertionError: 对话框文本验证失败
        """
        loc_desc = self._get_locator_description(locator)
        action_text = "接受" if accept else "取消"
        self.logger.info(f"尝试点击元素并{action_text}对话框: {loc_desc}")

        element = locator if isinstance(locator, Element) else None
        final_timeout = self._resolve_timeout(timeout, element)

        with self.page.expect_event("dialog", timeout=final_timeout) as dialog_info:
            self._get_locator(locator).click(timeout=final_timeout)

        dialog = dialog_info.value
        dialog_message = dialog.message
        self.logger.info(f"捕获到对话框，类型: {dialog.type}, 内容: {dialog_message}")

        if message_check:
            if message_check not in dialog_message:
                error_msg = f"对话框文本验证失败\n期望包含: {message_check}\n实际内容: {dialog_message}"
                self.logger.error(error_msg)
                dialog.dismiss()
                raise AssertionError(error_msg)
            else:
                self.logger.info(f"对话框文本验证通过: '{message_check}' 存在于 '{dialog_message}'")

        if accept:
            dialog.accept()
            self.logger.info("已接受对话框")
        else:
            dialog.dismiss()
            self.logger.info("已取消对话框")

        self.logger.info(f"对话框处理完成: {loc_desc}")
        return dialog_message
