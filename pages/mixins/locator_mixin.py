from typing import Any, Optional, Union

from playwright.sync_api import Locator
from utils.element import Element

LocatorInput = Union[str, Element]


class LocatorMixin:
    """定位器相关方法：解析 timeout、构建 Locator"""

    def _resolve_timeout(self, timeout: int = None, element: Element = None) -> int:
        """解析 timeout 优先级：方法参数 > Element.timeout > BasePage.timeout"""
        if timeout is not None:
            return timeout
        if element is not None and element.timeout is not None:
            return element.timeout
        return self.timeout

    def _get_locator(self, locator: LocatorInput, context=None) -> Locator:
        """智能定位器：自动识别定位器类型并返回 Playwright Locator

        Args:
            locator: 定位器，支持两种格式：
                - Element 对象（推荐）: Element("role", ("button", "登录"), desc="登录按钮")
                - 字符串 "#id" 或 ".class": 使用 CSS 选择器
                - 字符串 "//xpath": 使用 XPath
            context: 定位上下文（Page 或 FrameLocator），默认使用 self.page
        """
        ctx = context or self.page
        if isinstance(locator, Element):
            return self._build_locator_from_element(locator, ctx)
        elif isinstance(locator, str):
            if locator.startswith(("//", "(", "./")):
                self.logger.info(f"使用 XPath 定位器: {locator}")
                return ctx.locator(f"xpath={locator}")
            else:
                self.logger.info(f"使用 CSS 定位器: {locator}")
                return ctx.locator(locator)
        else:
            raise ValueError(f"不支持的定位器类型: {type(locator)}, 值: {locator}")

    def _get_locator_description(self, locator: LocatorInput) -> str:
        """获取定位器的描述字符串（用于日志）"""
        if isinstance(locator, Element):
            return locator.get_description()
        else:
            return f"'{locator}'"

    def _build_locator_from_element(self, element: Element, context=None) -> Locator:
        """根据 Element 配置构建 Locator（支持所有 Playwright 定位方式 + 链式操作）"""
        base_locator = self._get_base_locator(element, context)

        if element.filter_params:
            self.logger.info(f"应用 filter: {element.filter_params}")
            base_locator = base_locator.filter(**element.filter_params)

        if element.first:
            self.logger.info("应用 first()")
            base_locator = base_locator.first
        elif element.last:
            self.logger.info("应用 last()")
            base_locator = base_locator.last
        elif element.nth is not None:
            self.logger.info(f"应用 nth({element.nth})")
            base_locator = base_locator.nth(element.nth)

        return base_locator

    def _get_base_locator(self, element: Element, context=None) -> Locator:
        """根据 Element 的定位方式创建基础 Locator

        支持：role, text, placeholder, label, testid, title, alt_text, css, xpath
        """
        ctx = context or self.page
        by = element.by
        value = element.value
        exact = element.exact

        if by == "role":
            if isinstance(value, tuple) and len(value) == 2:
                role, name = value
                return ctx.get_by_role(role, name=name, exact=exact)
            elif isinstance(value, tuple) and len(value) == 1:
                return ctx.get_by_role(value[0])
            else:
                raise ValueError(f"Role 定位器格式错误: {value}")
        elif by == "text":
            return ctx.get_by_text(value, exact=exact)
        elif by == "placeholder":
            return ctx.get_by_placeholder(value, exact=exact)
        elif by == "label":
            return ctx.get_by_label(value, exact=exact)
        elif by == "testid":
            return ctx.get_by_test_id(value)
        elif by == "title":
            return ctx.get_by_title(value, exact=exact)
        elif by == "alt_text":
            return ctx.get_by_alt_text(value, exact=exact)
        elif by == "css":
            return ctx.locator(value)
        elif by == "xpath":
            return ctx.locator(f"xpath={value}")
        else:
            raise ValueError(f"不支持的定位方式: {by}")

    def _get_element(self, locator: LocatorInput) -> Optional[Element]:
        """从定位器参数中提取 Element 对象（若不是 Element 则返回 None）"""
        return locator if isinstance(locator, Element) else None

    def _run_locator_method(
        self,
        locator: LocatorInput,
        method_name: str,
        *args: Any,
        timeout: int = None,
        context=None,
        use_timeout: bool = True,
        **kwargs: Any,
    ) -> Any:
        """统一执行 Locator 方法，集中处理 timeout、context 与调用分发"""
        method_kwargs = dict(kwargs)
        if use_timeout:
            final_timeout = self._resolve_timeout(timeout, self._get_element(locator))
            method_kwargs.setdefault("timeout", final_timeout)

        target_locator = self._get_locator(locator, context=context)
        method = getattr(target_locator, method_name)
        return method(*args, **method_kwargs)
