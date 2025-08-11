import logging
from .paths import LOG_FILE_PATH

def setup_logging():
    # 确保日志目录存在
    LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)

    # 设置日志格式
    log_format = "%(asctime)s - %(levelname)s - %(message)s"

    # 配置全局日志
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler(LOG_FILE_PATH, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )