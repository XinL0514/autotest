from typing import TYPE_CHECKING

from playwright.sync_api import Page
from config.config import TIMEOUT
from utils.logger import Logger
from pages.mixins.locator_mixin import LocatorMixin
from pages.mixins.action_mixin import ActionMixin
from pages.mixins.select_mixin import SelectMixin
from pages.mixins.file_mixin import FileMixin
from pages.mixins.window_mixin import WindowMixin
from pages.mixins.navigation_mixin import NavigationMixin
from pages.mixins.dialog_mixin import DialogMixin
from pages.mixins.drag_mixin import DragMixin

if TYPE_CHECKING:
    from pages.frame_context import FrameContext


class BasePage(LocatorMixin, ActionMixin, SelectMixin, FileMixin,
               WindowMixin, NavigationMixin, DialogMixin, DragMixin):
    """页面基类，通过 Mixin 组合所有页面操作能力"""

    def __init__(self, page: Page):
        self.page = page
        self.timeout = TIMEOUT
        self.logger = Logger.get_logger(self.__class__.__name__)

    def locator(self, locator, context=None):
        """公开 Locator 解析能力，便于测试中结合 Playwright expect 使用。"""
        return self._get_locator(locator, context=context)

    def frame(self, frame_css: str) -> 'FrameContext':
        """返回 frame 上下文代理，支持与普通页面完全相同的操作方式。

        Usage:
            frame = self.frame('[src="index.htm"]')
            frame.click(ELEMENT)          # 与普通 self.click() 完全相同
            assertion.assert_has_text(frame, ELEMENT, "expected", "描述")

            # frame 操作完成后直接用 self 回到主页面，无需切换
            self.click(MAIN_ELEMENT)
        """
        from pages.frame_context import FrameContext
        return FrameContext(self, frame_css)
