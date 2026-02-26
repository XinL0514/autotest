import allure
from pathlib import Path
from utils.element import Element
from utils.exception_handler import ExceptionHandler
from typing import Union, Tuple
from config.config import UPLOAD_FILES_DIR


class FileMixin:
    """文件上传操作"""

    def build_upload_file_path(self, file_name: str) -> str:
        """根据文件名构建上传文件绝对路径（固定目录: test_data/files）"""
        path = Path(file_name)
        if not path.is_absolute():
            path = UPLOAD_FILES_DIR / file_name

        resolved_path = path.resolve()
        if not resolved_path.exists():
            raise FileNotFoundError(
                f"上传文件不存在: {resolved_path}。"
                f"请将文件放到目录: {UPLOAD_FILES_DIR}"
            )

        return str(resolved_path)

    @allure.step("上传文件")
    @ExceptionHandler.handle_playwright_exception("上传文件")
    def file_set_input_files(self, locator: Union[str, Tuple[str, str], Element], file_path: Union[str, list], timeout: int = None):
        """直接操作 input[type='file'] 元素上传文件

        Args:
            locator: 文件上传输入框的定位器
            file_path: 文件路径，单个字符串或多个文件的列表
            timeout: 可选超时时间（毫秒）
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

        适用于自定义上传按钮（非 input[type='file']）。

        Args:
            locator: 触发文件选择的按钮定位器
            file_path: 文件路径，单个字符串或多个文件的列表
            timeout: 可选超时时间（毫秒）
        """
        loc_desc = self._get_locator_description(locator)
        file_info = file_path if isinstance(file_path, str) else f"{len(file_path)} 个文件"
        self.logger.info(f"尝试点击按钮并上传文件: {loc_desc}, 文件: {file_info}")

        element = locator if isinstance(locator, Element) else None
        final_timeout = self._resolve_timeout(timeout, element)

        with self.page.expect_file_chooser() as fc_info:
            self._get_locator(locator).click(timeout=final_timeout)

        file_chooser = fc_info.value
        self.logger.info("捕获到文件选择对话框")
        file_chooser.set_files(file_path)
        self.logger.info(f"成功上传文件: {file_info}")
