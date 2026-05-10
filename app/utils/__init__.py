# _*_ coding:utf-8 _*_
# Copyright (C) 2024-2024 shiyi0x7f,Inc.All Rights Reserved
# @Time : 2024/12/4 下午9:47
# @Author: shiyi0x7f
from .mod_env import get_env
from .mod_domain import get_domain
from .mod_log import setup_logger
from .mod_check import CheckUpdate
from .mod_uuid import get_uuid
from .mod_fs import open_in_file_manager, default_download_dir
from .mod_history import SearchHistory
from .mod_favorites import Favorites