# _*_ coding:utf-8 _*_
# Copyright (C) 2024-2024 shiyi0x7f,Inc.All Rights Reserved
# @Time : 2024/12/4 下午9:49
# @Author: shiyi0x7f
from loguru import logger
try:
    from .mod_env import get_env
except ImportError:
    from mod_env import get_env
import sys
import os

def setup_logger():
    env = get_env()  # 小写
    logger.remove()

    # windowed 模式下 sys.stdout/stderr 可能为 None（GUI 无控制台）
    has_console = sys.stdout is not None

    fmt = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"

    if env == 'dev':
        if has_console:
            logger.add(sys.stdout, level="DEBUG", format=fmt)
        logger.add("app_debug.log", level="DEBUG",
                   rotation="1 MB", retention="10 days", compression="zip",
                   format=fmt)
    elif env == 'prod':
        if has_console:
            logger.add(sys.stdout, level="INFO", format=fmt)
        else:
            # 打包后的 GUI 应用也保留文件日志便于排查
            logger.add("app.log", level="INFO",
                       rotation="5 MB", retention="7 days",
                       format=fmt)
    else:
        if has_console:
            logger.add(sys.stdout, level="DEBUG", format=fmt)
        logger.add("app_debug.log", level="DEBUG",
                   rotation="1 MB", retention="10 days",
                   format=fmt)

    logger.info(f"current env: {env}")
    # 可以根据需要配置更多的处理器，比如发送邮件、记录到数据库等
if __name__ == '__main__':
    setup_logger()