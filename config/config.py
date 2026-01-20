# 测试环境配置
BASE_URL = "http://101.200.193.143/"

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
