import allure
from pages.mixins.locator_mixin import LocatorInput
from utils.exception_handler import ExceptionHandler
from typing import Optional


class DialogMixin:
    """JavaScript 对话框处理"""

    @allure.step("点击元素并接受对话框")
    @ExceptionHandler.handle_playwright_exception("点击元素并接受对话框")
    def click_and_accept_dialog(self, locator: LocatorInput,
                                message_check: str = None, timeout: int = None):
        """点击元素并自动接受弹出的对话框（点击"确定"）

        Args:
            locator: 会触发对话框的元素定位器
            message_check: 可选，验证对话框文本是否包含指定内容
            timeout: 可选超时时间（毫秒）
        """
        return self.click_and_handle_dialog(locator, accept=True, message_check=message_check, timeout=timeout)

    @allure.step("点击元素并取消对话框")
    @ExceptionHandler.handle_playwright_exception("点击元素并取消对话框")
    def click_and_dismiss_dialog(self, locator: LocatorInput,
                                 message_check: str = None, timeout: int = None):
        """点击元素并自动取消弹出的对话框（点击"取消"）

        Args:
            locator: 会触发对话框的元素定位器
            message_check: 可选，验证对话框文本是否包含指定内容
            timeout: 可选超时时间（毫秒）
        """
        return self.click_and_handle_dialog(locator, accept=False, message_check=message_check, timeout=timeout)

    @allure.step("点击元素并处理对话框")
    @ExceptionHandler.handle_playwright_exception("点击元素并处理对话框")
    def click_and_handle_dialog(self, locator: LocatorInput,
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

        final_timeout = self._resolve_timeout(timeout, self._get_element(locator))
        dialog_state = {"message": None, "error": None, "handled": False}

        def _handle_dialog(dialog):
            dialog_state["handled"] = True
            dialog_message = dialog.message
            dialog_state["message"] = dialog_message
            self.logger.info(f"捕获到对话框，类型: {dialog.type}, 内容: {dialog_message}")

            try:
                if message_check and message_check not in dialog_message:
                    error_msg = f"对话框文本验证失败\n期望包含: {message_check}\n实际内容: {dialog_message}"
                    self.logger.error(error_msg)
                    dialog.dismiss()
                    dialog_state["error"] = AssertionError(error_msg)
                    return

                if accept:
                    dialog.accept()
                    self.logger.info("已接受对话框")
                else:
                    dialog.dismiss()
                    self.logger.info("已取消对话框")
            except Exception as error:
                dialog_state["error"] = error

        self.page.once("dialog", _handle_dialog)
        try:
            with self.page.expect_event("dialog", timeout=final_timeout):
                self._run_locator_method(locator, "click", timeout=timeout)
        finally:
            if not dialog_state["handled"]:
                self.page.remove_listener("dialog", _handle_dialog)

        if dialog_state["error"]:
            raise dialog_state["error"]

        self.logger.info(f"对话框处理完成: {loc_desc}")
        return dialog_state["message"]
