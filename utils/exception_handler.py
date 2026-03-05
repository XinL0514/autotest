"""统一异常处理装饰器

用于统一处理 BasePage 方法中的异常，减少重复代码
"""
import functools
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

                # 尝试获取定位器描述（第一个参数通常是 locator）
                loc_desc = None
                if args and hasattr(self, '_get_locator_description'):
                    try:
                        loc_desc = self._get_locator_description(args[0])
                        # 只在双定位器方法中尝试获取第二个定位器
                        if len(args) > 1:
                            second_arg = args[1]
                            is_locator = (
                                hasattr(second_arg, '__class__') and second_arg.__class__.__name__ == 'Element'
                                or isinstance(second_arg, tuple)
                                or (isinstance(second_arg, str) and
                                    (second_arg.startswith(('/', '#', '.', 'iframe', 'button', 'input')) or '//' in second_arg))
                            )
                            if is_locator:
                                try:
                                    target_desc = self._get_locator_description(second_arg)
                                    loc_desc = f"{loc_desc} -> {target_desc}"
                                except Exception:
                                    pass
                    except Exception:
                        loc_desc = str(args[0]) if args else "未知元素"

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


class FrameExceptionHandler(BaseExceptionHandler):
    """iframe 操作专用异常处理装饰器"""

    @staticmethod
    def handle_frame_exception(operation_name: str = None, return_on_error: Any = None):
        """处理 iframe 操作异常

        Args:
            operation_name: 操作名称
            return_on_error: 发生错误时的返回值
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(self, frame_locator, element_locator, *args, **kwargs):
                logger = getattr(self, 'logger', None)

                # 获取元素描述
                loc_desc = None
                if hasattr(self, '_get_locator_description'):
                    try:
                        loc_desc = self._get_locator_description(element_locator)
                    except Exception:
                        loc_desc = str(element_locator)

                error_context = f"iframe={frame_locator}, element={loc_desc}"

                try:
                    return func(self, frame_locator, element_locator, *args, **kwargs)
                except Exception as e:
                    return BaseExceptionHandler._handle_exception(
                        e,
                        operation_name or func.__name__,
                        error_context,
                        logger,
                        return_on_error,
                        raise_assertion=True
                    )

            return wrapper
        return decorator
