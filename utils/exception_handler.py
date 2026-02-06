"""统一异常处理装饰器

用于统一处理 BasePage 方法中的异常，减少重复代码
"""
import functools
from playwright.sync_api import TimeoutError
from typing import Callable, Any


class ExceptionHandler:
    """异常处理装饰器类"""

    @staticmethod
    def handle_playwright_exception(
        operation_name: str = None,
        return_on_error: Any = None,
        raise_assertion: bool = True
    ):
        """统一处理 Playwright 操作异常的装饰器

        Args:
            operation_name: 操作名称（如 "点击元素"、"填充元素"），用于错误消息
            return_on_error: 发生错误时的返回值（用于 is_visible 等查询方法）
            raise_assertion: 是否将 TimeoutError 转换为 AssertionError（默认 True）

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
                # 获取 logger（假设 self 有 logger 属性）
                logger = getattr(self, 'logger', None)

                # 尝试获取定位器描述（第一个参数通常是 locator）
                loc_desc = None
                if args and hasattr(self, '_get_locator_description'):
                    try:
                        loc_desc = self._get_locator_description(args[0])
                        # 只在双定位器方法中尝试获取第二个定位器
                        # 双定位器方法特征：第二个参数也是定位器类型（不是 str/int/dict 等普通类型）
                        if len(args) > 1:
                            second_arg = args[1]
                            # 检查第二个参数是否是定位器（Element/tuple/定位器字符串）
                            # 排除普通字符串（text参数）、数字、字典等
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
                    # 执行原始方法
                    return func(self, *args, **kwargs)

                except TimeoutError as e:
                    # 处理超时异常
                    error_msg = f"{operation_name or func.__name__}超时"
                    if loc_desc:
                        error_msg += f": {loc_desc}"

                    if logger:
                        logger.error(error_msg)

                    # 根据配置决定是否转换为 AssertionError
                    if raise_assertion:
                        raise AssertionError(error_msg) from e
                    elif return_on_error is not None:
                        return return_on_error
                    else:
                        raise

                except AssertionError:
                    # AssertionError 直接向上抛出（可能来自内部验证）
                    raise

                except Exception as e:
                    # 处理其他异常
                    error_msg = f"{operation_name or func.__name__}失败"
                    if loc_desc:
                        error_msg += f": {loc_desc}"
                    error_msg += f", 错误: {str(e)}"

                    if logger:
                        logger.error(error_msg)

                    # 其他异常根据配置决定返回值或抛出
                    if return_on_error is not None:
                        return return_on_error
                    else:
                        raise

            return wrapper
        return decorator


class FrameExceptionHandler:
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

                try:
                    return func(self, frame_locator, element_locator, *args, **kwargs)

                except TimeoutError:
                    error_msg = f"{operation_name or func.__name__}超时"
                    error_msg += f": iframe={frame_locator}, element={loc_desc}"

                    if logger:
                        logger.error(error_msg)

                    if return_on_error is not None:
                        return return_on_error
                    else:
                        raise AssertionError(error_msg)

                except AssertionError:
                    raise

                except Exception as e:
                    error_msg = f"{operation_name or func.__name__}失败"
                    error_msg += f": iframe={frame_locator}, element={loc_desc}, 错误: {str(e)}"

                    if logger:
                        logger.error(error_msg)

                    if return_on_error is not None:
                        return return_on_error
                    else:
                        raise

            return wrapper
        return decorator
