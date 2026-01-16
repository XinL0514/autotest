import logging
from pathlib import Path
from datetime import datetime
from config.config import LOG_LEVEL, LOG_TO_CONSOLE, LOG_TO_FILE


class Logger:
    """日志工具类,用于记录测试执行过程"""

    # 类级别的handler,确保全局只创建一次
    _handlers_initialized = False
    _file_handler = None
    _console_handler = None

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, LOG_LEVEL))
        # 禁止日志传播到父logger,避免重复输出
        self.logger.propagate = False

        # 初始化类级别的handlers(只执行一次)
        if not Logger._handlers_initialized:
            Logger._setup_class_handlers()

        # 为当前logger添加共享的handlers
        if not self.logger.handlers:
            if Logger._file_handler:
                self.logger.addHandler(Logger._file_handler)
            if Logger._console_handler:
                self.logger.addHandler(Logger._console_handler)

    @classmethod
    def _setup_class_handlers(cls):
        """配置类级别的日志处理器(全局只执行一次)"""
        # 日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # 文件handler - 根据配置决定是否启用
        if LOG_TO_FILE:
            log_dir = Path(__file__).parent.parent / "logs"
            log_dir.mkdir(exist_ok=True)
            log_file = log_dir / f"test_{datetime.now().strftime('%Y%m%d')}.log"
            cls._file_handler = logging.FileHandler(log_file, encoding='utf-8')
            cls._file_handler.setLevel(logging.DEBUG)
            cls._file_handler.setFormatter(formatter)

        # 控制台handler - 根据配置决定是否启用
        if LOG_TO_CONSOLE:
            cls._console_handler = logging.StreamHandler()
            cls._console_handler.setLevel(getattr(logging, LOG_LEVEL))
            cls._console_handler.setFormatter(formatter)

        cls._handlers_initialized = True

    def debug(self, message: str):
        """调试信息"""
        self.logger.debug(message)

    def info(self, message: str):
        """一般信息"""
        self.logger.info(message)

    def warning(self, message: str):
        """警告信息"""
        self.logger.warning(message)

    def error(self, message: str):
        """错误信息"""
        self.logger.error(message)

    @classmethod
    def get_logger(cls, name: str = "TestLogger"):
        """获取日志实例(类方法,方便直接调用)"""
        return cls(name)
