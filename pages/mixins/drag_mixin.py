import allure
from utils.element import Element
from utils.exception_handler import ExceptionHandler
from typing import Union, Tuple


class DragMixin:
    """拖拽操作"""

    @allure.step("拖拽元素到目标位置")
    @ExceptionHandler.handle_playwright_exception("拖拽元素")
    def drag_to(self, source_locator: Union[str, Tuple[str, str], Element],
                target_locator: Union[str, Tuple[str, str], Element],
                source_position: dict = None, target_position: dict = None,
                force: bool = False, timeout: int = None):
        """将元素拖拽到目标元素位置

        Args:
            source_locator: 源元素定位器
            target_locator: 目标元素定位器
            source_position: 可选，源元素的抓取位置，如 {"x": 0, "y": 0}
            target_position: 可选，目标元素的释放位置，如 {"x": 0, "y": 0}
            force: 是否强制拖拽（跳过可操作性检查），默认 False
            timeout: 可选超时时间（毫秒）
        """
        source_desc = self._get_locator_description(source_locator)
        target_desc = self._get_locator_description(target_locator)
        self.logger.info(f"尝试拖拽元素: {source_desc} -> {target_desc}")

        element = source_locator if isinstance(source_locator, Element) else None
        final_timeout = self._resolve_timeout(timeout, element)

        drag_options = {"timeout": final_timeout}
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

    @allure.step("使用鼠标操作拖拽元素")
    @ExceptionHandler.handle_playwright_exception("使用鼠标拖拽元素")
    def drag_by_mouse(self, source_locator: Union[str, Tuple[str, str], Element],
                      target_locator: Union[str, Tuple[str, str], Element],
                      timeout: int = None):
        """使用鼠标操作进行拖拽（drag_to 不生效时的替代方案）

        Args:
            source_locator: 源元素定位器
            target_locator: 目标元素定位器
            timeout: 可选超时时间（毫秒）
        """
        source_desc = self._get_locator_description(source_locator)
        target_desc = self._get_locator_description(target_locator)
        self.logger.info(f"使用鼠标拖拽元素: {source_desc} -> {target_desc}")

        element = source_locator if isinstance(source_locator, Element) else None
        final_timeout = self._resolve_timeout(timeout, element)

        source = self._get_locator(source_locator)
        target = self._get_locator(target_locator)
        source.wait_for(state="visible", timeout=final_timeout)
        target.wait_for(state="visible", timeout=final_timeout)

        source_box = source.bounding_box()
        target_box = target.bounding_box()

        if not source_box or not target_box:
            raise AssertionError("无法获取元素位置信息")

        source_x = source_box["x"] + source_box["width"] / 2
        source_y = source_box["y"] + source_box["height"] / 2
        target_x = target_box["x"] + target_box["width"] / 2
        target_y = target_box["y"] + target_box["height"] / 2

        self.logger.info(f"移动鼠标到源元素: ({source_x}, {source_y})")
        self.page.mouse.move(source_x, source_y)
        self.logger.info("按下鼠标左键")
        self.page.mouse.down()
        self.logger.info(f"移动鼠标到目标元素: ({target_x}, {target_y})")
        self.page.mouse.move(target_x, target_y)
        self.logger.info("释放鼠标左键")
        self.page.mouse.up()

        self.logger.info(f"成功使用鼠标拖拽: {source_desc} -> {target_desc}")
