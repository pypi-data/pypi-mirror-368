import os
import time
import datetime
import logging
import colorlog

from logging.handlers import TimedRotatingFileHandler
from ats_base.common import func

log_colors_config = {
    'DEBUG': 'white',  # cyan white
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'bold_red',
}


class LogFilter:
    @staticmethod
    def info_filter(record):
        if record.levelname == 'INFO':
            return True
        return False

    @staticmethod
    def error_filter(record):
        if record.levelname == 'ERROR':
            return True
        return False


class TimeLoggerRolloverHandler(TimedRotatingFileHandler):
    def __init__(self, filename, when='h', interval=1, backupCount=0, encoding=None, delay=False, utc=False,
                 atTime=None):
        super(TimeLoggerRolloverHandler, self).__init__(filename, when, interval, backupCount, encoding, delay, utc)

    def doRollover(self):
        """
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        currentTime = int(time.time())
        dstNow = time.localtime(currentTime)[-1]
        log_type = 'info' if self.level == 20 else 'error'
        dfn = f"test_{datetime.datetime.now().strftime('%Y-%m-%d')}.{log_type}.log"
        self.baseFilename = dfn
        if not self.delay:
            self.stream = self._open()
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            if dstNow != dstAtRollover:
                if not dstNow:
                    addend = -3600
                else:
                    addend = 3600
                newRolloverAt += addend
        self.rolloverAt = newRolloverAt


# 定义收集logger的级别
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 定义handler的输出格式
fmt = logging.Formatter("[%(asctime)s] - %(levelname)s: %(message)s")
color_fmt = colorlog.ColoredFormatter("[%(asctime)s] - %(levelname)s: %(message)s", log_colors=log_colors_config)

# 日志文件的handler
log_error_file = 'test_{}.error.log'.format(datetime.datetime.now().strftime('%Y-%m-%d'))
log_info_file = 'test_{}.info.log'.format(datetime.datetime.now().strftime('%Y-%m-%d'))
report_dir = func.makeDir(func.project_dir(), 'hist')

error_handler = TimeLoggerRolloverHandler(report_dir + os.sep + log_error_file
                                          , when='midnight', backupCount=7, encoding='utf8')
error_handler.addFilter(LogFilter.error_filter)
error_handler.setLevel(logging.ERROR)

info_handel = TimeLoggerRolloverHandler(report_dir + os.sep + log_info_file
                                        , when='midnight', backupCount=7, encoding='utf8')
info_handel.addFilter(LogFilter.info_filter)
info_handel.setLevel(logging.INFO)

# 配置控制台的handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

console_handler.setFormatter(color_fmt)
info_handel.setFormatter(fmt)
error_handler.setFormatter(fmt)

# 将logger添加到handler里面
logger.addHandler(console_handler)
logger.addHandler(info_handel)
logger.addHandler(error_handler)

