"""统一异常处理装饰器

用于统一处理 BasePage 方法中的异常，减少重复代码
"""
import functools
import inspect
from playwright.sync_api import TimeoutError
from typing import Callable, Any


class BaseExceptionHandler:
    """异常处理基类 - 提取通用异常处理逻辑"""

    @staticmethod
    def _handle_exception(
        exception: Exception,
        operation_name: str,
        error_context: str,
        logger,
        return_on_error: Any,
        raise_assertion: bool,
        fallback_on_unexpected_error: bool = False,
    ):
        """通用异常处理逻辑

        Args:
            exception: 捕获的异常
            operation_name: 操作名称
            error_context: 错误上下文（定位器描述等）
            logger: 日志对象
            return_on_error: 错误时返回值
            raise_assertion: 是否将 TimeoutError 转为 AssertionError
            fallback_on_unexpected_error:
                是否在非 TimeoutError 场景也返回 return_on_error。
                默认 False，避免吞掉真实错误。
        """
        if isinstance(exception, TimeoutError):
            error_msg = f"{operation_name}超时"
            if error_context:
                error_msg += f": {error_context}"

            if logger:
                logger.error(error_msg)

            if raise_assertion:
                raise AssertionError(error_msg) from exception
            elif return_on_error is not None:
                return return_on_error
            else:
                raise

        elif isinstance(exception, AssertionError):
            raise

        else:
            error_msg = f"{operation_name}失败"
            if error_context:
                error_msg += f": {error_context}"
            error_msg += f", 错误: {str(exception)}"

            if logger:
                logger.error(error_msg)

            if fallback_on_unexpected_error and return_on_error is not None:
                return return_on_error
            else:
                raise


class ExceptionHandler(BaseExceptionHandler):
    """异常处理装饰器类"""

    @staticmethod
    def handle_playwright_exception(
        operation_name: str = None,
        return_on_error: Any = None,
        raise_assertion: bool = True,
        fallback_on_unexpected_error: bool = False,
    ):
        """统一处理 Playwright 操作异常的装饰器

        Args:
            operation_name: 操作名称（如 "点击元素"、"填充元素"），用于错误消息
            return_on_error: 发生错误时的返回值（用于 is_visible 等查询方法）
            raise_assertion: 是否将 TimeoutError 转换为 AssertionError（默认 True）
            fallback_on_unexpected_error:
                是否对非 TimeoutError 也返回 return_on_error。
                默认 False，推荐保持默认值以避免误判通过。

        Examples:
            # 抛出异常的操作（如 click、fill）
            @ExceptionHandler.handle_playwright_exception("点击元素")
            def click(self, locator, timeout=None):
                loc_desc = self._get_locator_description(locator)
                self._get_locator(locator).click(timeout=timeout)

            # 返回布尔值的查询操作（如 is_visible）
            @ExceptionHandler.handle_playwright_exception("检查元素可见性", return_on_error=False, raise_assertion=False)
            def is_visible(self, locator):
                loc_desc = self._get_locator_description(locator)
                return self._get_locator(locator).is_visible()
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(self, *args, **kwargs):
                logger = getattr(self, 'logger', None)

                loc_desc = None
                if hasattr(self, '_get_locator_description'):
                    signature = inspect.signature(func)
                    bound = signature.bind_partial(self, *args, **kwargs)

                    locator_params = []
                    for param_name, value in list(bound.arguments.items())[1:]:
                        if param_name == 'locator' or param_name.endswith('_locator'):
                            locator_params.append((param_name, value))

                    if locator_params:
                        descriptions = []
                        for param_name, locator_value in locator_params:
                            try:
                                descriptions.append(self._get_locator_description(locator_value))
                            except Exception as parse_error:
                                fallback_desc = f"'{locator_value}'"
                                descriptions.append(f"{param_name}={fallback_desc}")
                                if logger:
                                    logger.warning(
                                        f"定位器描述解析失败: 参数={param_name}, 值={locator_value}, 错误={parse_error}"
                                    )

                        loc_desc = " -> ".join(descriptions)

                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    return BaseExceptionHandler._handle_exception(
                        e,
                        operation_name or func.__name__,
                        loc_desc,
                        logger,
                        return_on_error,
                        raise_assertion,
                        fallback_on_unexpected_error,
                    )

            return wrapper
        return decorator
