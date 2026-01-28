import time
import datetime
"""
获取时间戳
"""
def timeStamp():
    timestamp = str(int(time.time()))
    # print(timestamp)
    return timestamp
# timeStamp()

"""
获取当前时间点
"""
def now_time():
    now = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d_%H:%M:%S')
    # print(now)
    return now
# now_time()