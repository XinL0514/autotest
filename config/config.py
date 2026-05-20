import os
from pathlib import Path

# 测试环境配置
BASE_URL = "https://aixmy.miaobi.cn/#/home/profile"

# 超时时间(毫秒)
TIMEOUT = 30000

# 浏览器无头模式
HEADLESS = False
# # 有头模式运行
#   pytest --headed

#   # 无头模式运行
#   pytest

#   方法3: 指定浏览器

#   # 有头模式 + Chrome
#   pytest --headed --browser chromium

#   # 有头模式 + Firefox
#   pytest --headed --browser firefox

# 日志配置
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_TO_CONSOLE = False  # 是否输出到控制台
LOG_TO_FILE = True  # 是否输出到文件

# 上传文件配置（可通过环境变量覆盖）
PROJECT_ROOT = Path(__file__).resolve().parent.parent
UPLOAD_FILES_DIR = PROJECT_ROOT / "test_data" / "files"
DEFAULT_UPLOAD_FILE_NAME = os.getenv("UPLOAD_FILE_NAME", "upload_sample.txt")

# 认证配置（仅从环境变量读取，避免将账号写入仓库）
AUTH_USERNAME_ENV = "AUTOTEST_AUTH_USERNAME"
AUTH_PASSWORD_ENV = "AUTOTEST_AUTH_PASSWORD"
AUTH_STATE_TTL_SECONDS = int(os.getenv("AUTOTEST_AUTH_TTL_SECONDS", "3600"))
ENABLE_AUTH_VALIDATION = os.getenv("AUTOTEST_AUTH_VALIDATE", "0").lower() in {
    "1",
    "true",
    "yes",
    "on",
}
