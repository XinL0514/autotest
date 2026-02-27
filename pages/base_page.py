from playwright.sync_api import Page
from config.config import TIMEOUT
from utils.logger import Logger
from pages.mixins.locator_mixin import LocatorMixin
from pages.mixins.action_mixin import ActionMixin
from pages.mixins.select_mixin import SelectMixin
from pages.mixins.file_mixin import FileMixin
from pages.mixins.window_mixin import WindowMixin
from pages.mixins.navigation_mixin import NavigationMixin
from pages.mixins.iframe_mixin import IframeMixin
from pages.mixins.dialog_mixin import DialogMixin
from pages.mixins.drag_mixin import DragMixin


class BasePage(LocatorMixin, ActionMixin, SelectMixin, FileMixin,
               WindowMixin, NavigationMixin, IframeMixin, DialogMixin, DragMixin):
    """页面基类，通过 Mixin 组合所有页面操作能力"""

    def __init__(self, page: Page):
        self.page = page
        self.timeout = TIMEOUT
        self.logger = Logger.get_logger(self.__class__.__name__)
