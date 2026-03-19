import allure
from pathlib import Path
from pages.mixins.locator_mixin import LocatorInput
from utils.exception_handler import ExceptionHandler
from typing import Union
from config.config import UPLOAD_FILES_DIR

UploadSinglePath = Union[str, Path]
UploadPathInput = Union[UploadSinglePath, list[UploadSinglePath], tuple[UploadSinglePath, ...]]


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

    def _normalize_upload_paths(self, file_path: UploadPathInput) -> Union[str, list[str]]:
        """标准化上传路径：统一转换为绝对路径，并验证文件存在"""
        if isinstance(file_path, (str, Path)):
            return self.build_upload_file_path(str(file_path))

        if isinstance(file_path, (list, tuple)):
            if not file_path:
                raise ValueError("file_path 文件列表不能为空")
            normalized_paths = []
            for one_path in file_path:
                if not isinstance(one_path, (str, Path)):
                    raise ValueError(f"file_path 列表中的元素必须是字符串或 Path，当前类型: {type(one_path)}")
                normalized_paths.append(self.build_upload_file_path(str(one_path)))
            return normalized_paths

        raise ValueError(f"file_path 类型不支持: {type(file_path)}")

    @allure.step("直接操作H5的 input[type='file'] 元素上传文件")
    @ExceptionHandler.handle_playwright_exception("直接操作H5的 input[type='file'] 元素上传文件")
    def file_set_input_files(self, locator: LocatorInput, file_path: UploadPathInput, timeout: int = None):
        """直接操作H5的 input[type='file'] 元素上传文件

        Args:
            locator: 文件上传输入框的定位器
            file_path: 文件路径，单个字符串或多个文件的列表
            timeout: 可选超时时间（毫秒）
        """
        normalized_file_path = self._normalize_upload_paths(file_path)
        loc_desc = self._get_locator_description(locator)
        file_info = normalized_file_path if isinstance(normalized_file_path, str) else f"{len(normalized_file_path)} 个文件"
        self.logger.info(f"尝试直接操作H5的 input[type='file'] 元素上传文件: {loc_desc}, 文件: {file_info}")

        self._run_locator_method(locator, "set_input_files", normalized_file_path, timeout=timeout)
        self.logger.info(f"成功直接操作H5的 input[type='file'] 元素上传文件: {file_info}")

    @allure.step("点击按钮触发原生文件选择对话框并上传文件")
    @ExceptionHandler.handle_playwright_exception("点击按钮触发原生文件选择对话框并上传文件")
    def file_choose_file(self, locator: LocatorInput, file_path: UploadPathInput, timeout: int = None):
        """点击按钮触发原生文件选择对话框并上传文件

        适用于自定义上传按钮（非 input[type='file']），点击按钮触发原生文件选择对话框并上传文件。

        Args:
            locator: 触发文件选择的按钮定位器
            file_path: 文件路径，单个字符串或多个文件的列表
            timeout: 可选超时时间（毫秒）
        """
        normalized_file_path = self._normalize_upload_paths(file_path)
        loc_desc = self._get_locator_description(locator)
        file_info = normalized_file_path if isinstance(normalized_file_path, str) else f"{len(normalized_file_path)} 个文件"
        self.logger.info(f"尝试点击按钮触发原生文件选择对话框并上传文件: {loc_desc}, 文件: {file_info}")

        final_timeout = self._resolve_timeout(timeout, self._get_element(locator))

        with self.page.expect_file_chooser(timeout=final_timeout) as fc_info:
            self._run_locator_method(locator, "click", timeout=timeout)

        file_chooser = fc_info.value
        self.logger.info("捕获到文件选择对话框")
        file_chooser.set_files(normalized_file_path, timeout=final_timeout)
        self.logger.info(f"成功点击按钮触发原生文件选择对话框并上传文件: {file_info}")
