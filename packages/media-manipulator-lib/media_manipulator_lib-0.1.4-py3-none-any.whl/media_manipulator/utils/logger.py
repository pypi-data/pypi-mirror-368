import logging
import colorlog

SUCCESS_LEVEL_NUM = 25  # Between INFO (20) and WARNING (30)
logging.addLevelName(SUCCESS_LEVEL_NUM, "SUCCESS")

def success(self, message, *args, **kwargs):
    if self.isEnabledFor(SUCCESS_LEVEL_NUM):
        self._log(SUCCESS_LEVEL_NUM, message, args, **kwargs)

logging.Logger.success = success

formatter = colorlog.ColoredFormatter(
    fmt="%(log_color)s%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d (%(funcName)s) - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'yellow',
        'WARNING': 'bold_yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
        'SUCCESS': 'green',
    }
)

handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = colorlog.getLogger("video_editing_service")
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)  # Change to INFO/ERROR for production
