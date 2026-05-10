# _*_ coding:utf-8 _*_
# Copyright (C) 2024-2024 shiyi0x7f,Inc.All Rights Reserved
# @Time : 2024/12/20 下午9:21
# @Author: shiyi0x7f
from .mod_env import get_env
from ..common.config import TESTHOST,PRODHOST,DEVHOST
from loguru import logger

def get_domain():
    env = get_env()
    if env == 'dev':
        host = DEVHOST
        scheme = 'http'
    elif env == 'test':
        host = TESTHOST
        scheme = 'https'
    else:
        host = PRODHOST
        scheme = 'https'

    if not host:
        logger.warning(f"服务器地址未配置 (env={env})，请通过环境变量 OLIB_{env.upper()}_HOST 设置")
        return ''
    return f'{scheme}://{host}'