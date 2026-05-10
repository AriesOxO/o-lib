# _*_ coding:utf-8 _*_
# Copyright (C) 2026-2026 shiyi0x7f,Inc.All Rights Reserved
# 跨平台文件系统工具
import os
import subprocess
import sys
from pathlib import Path
from loguru import logger


def open_in_file_manager(path: str | os.PathLike) -> bool:
    """
    在系统文件管理器中打开指定路径。
    Windows: 资源管理器
    macOS: Finder
    Linux: 默认文件管理器（通过 xdg-open）
    返回是否成功。
    """
    p = Path(path)
    if not p.exists():
        logger.warning(f"路径不存在，无法打开: {p}")
        return False
    try:
        if sys.platform == 'win32':
            os.startfile(str(p))  # type: ignore[attr-defined]
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', str(p)])
        else:
            subprocess.Popen(['xdg-open', str(p)])
        return True
    except Exception as e:
        logger.error(f"打开文件管理器失败: {e}")
        return False


def default_download_dir() -> Path:
    """返回平台默认下载目录。"""
    home = Path.home()
    # 优先使用系统 Downloads 目录
    downloads = home / 'Downloads'
    if downloads.exists():
        return downloads / 'Olib'
    return home / 'Olib'
