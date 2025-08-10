import logging
import json
import os
import sys
from datetime import datetime

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)


# --------------------------------------------------------------
# 1. 自定义控制台彩色格式
# --------------------------------------------------------------
class ColorFormatter(logging.Formatter):
    """为控制台输出加 ANSI 颜色"""

    COLORS = {
        logging.DEBUG: "\033[36m",  # 青
        logging.INFO: "\033[32m",  # 绿
        logging.WARNING: "\033[33m",  # 黄
        logging.ERROR: "\033[31m",  # 红
        logging.CRITICAL: "\033[35m",  # 紫
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelno, "")
        reset = self.RESET
        # 时间 | 级别 | 文件名:行号 | 消息
        return (
            f"{color}{datetime.fromtimestamp(record.created):%m-%d %H:%M:%S} "
            f"{record.levelname:<8} "
            f"{record.filename}:{record.lineno} "
            f"| {record.getMessage()}{reset}"
        )


# --------------------------------------------------------------
# 2. JSON 文件格式
# --------------------------------------------------------------
class JSONFormatter(logging.Formatter):
    """每条日志转为一行 JSON"""

    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "ts": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "file": f"{record.filename}:{record.lineno}",
            "func": record.funcName,
            "msg": record.getMessage(),
            "thread": record.threadName,
        }
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj, ensure_ascii=False)


# --------------------------------------------------------------
# 3. 统一封装
# --------------------------------------------------------------
def get_logger(name: str = "app", level: int = logging.DEBUG) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:  # 避免重复添加
        return logger

    logger.setLevel(level)

    # 控制台 Handler
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(ColorFormatter())
    logger.addHandler(console)

    # 文件 Handler（按天滚动，保留 30 天）
    from logging.handlers import TimedRotatingFileHandler

    file_handler = TimedRotatingFileHandler(
        filename=os.path.join(LOG_DIR, "app.log"),
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8",
    )
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)

    return logger


logger = get_logger()

# --------------------------------------------------------------
# 4. 示例
# --------------------------------------------------------------
if __name__ == "__main__":
    log = get_logger("demo")
    log.debug("debug 信息")
    log.info("普通信息")
    log.warning("⚠️ 警告")
    log.error("❌ 错误", exc_info=True)
