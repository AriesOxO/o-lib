# _*_ coding:utf-8 _*_
# Copyright (C) 2025-2025 shiyi0x7f,Inc.All Rights Reserved
# @Time : 2025/1/8 下午8:07
# @Author: shiyi0x7f
import os
import uuid
from pathlib import Path

import psutil


_UUID_CACHE_FILE = Path.home() / '.olib_uuid'


def get_first_mac():
    interfaces = psutil.net_if_addrs()
    for interface, addrs in interfaces.items():
        for addr in addrs:
            # 查找以MAC地址格式出现的接口
            if addr.family == psutil.AF_LINK:
                if addr.address:
                    return addr.address
    return None


def get_uuid():
    namespace = uuid.NAMESPACE_DNS
    mac = get_first_mac()
    if mac:
        return str(uuid.uuid5(namespace, mac))
    # Fallback: 持久化一个随机 UUID 到用户目录
    try:
        if _UUID_CACHE_FILE.exists():
            cached = _UUID_CACHE_FILE.read_text(encoding='utf-8').strip()
            uuid.UUID(cached)  # 验证合法
            return cached
        new_uuid = str(uuid.uuid4())
        _UUID_CACHE_FILE.write_text(new_uuid, encoding='utf-8')
        return new_uuid
    except Exception:
        return str(uuid.uuid4())


if __name__ == '__main__':
    uid = get_uuid()
    print(uid)