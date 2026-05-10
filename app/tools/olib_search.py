# _*_ coding:utf-8 _*_
# Copyright (C) 2023-2023 shiyi0x7f,Inc.All Rights Reserved
# @Time : 2023/6/7 20:20
# @Author: shiyi0x7f
import time
from json import JSONDecodeError

import requests
from PyQt5.QtCore import pyqtSignal, QThread
from loguru import logger as log

from ..common.errors import SearchError
from ..utils import get_domain, get_uuid


class OlibSearcherV4(QThread):
    sig_success = pyqtSignal(list)
    sig_fail = pyqtSignal(int)

    def __init__(self, bookname, languages=None, extensions=None, page=None,
                 order="bestmatch", limit="100", e=None, yearFrom=None, yearTo=None):
        super().__init__()
        self.page = page
        self.bookname = bookname
        self.languages = languages
        self.extensions = extensions
        self.order = order
        self.limit = limit
        self.e = e
        self.yearFrom = yearFrom
        self.yearTo = yearTo
        self.pagination = None

    def run(self):
        self.book_from_my_api()

    def book_from_my_api(self):
        t1 = time.time()
        domain = get_domain()
        if not domain:
            log.warning("服务器地址未配置")
            self.sig_fail.emit(SearchError.CONFIG_MISSING)
            return

        api_search = f'{domain}/getbooks'
        log.info(f"{api_search} 当前第{self.page}页")
        json_data = {
            "bookname": self.bookname,
            "page": self.page,
            "languages": self.languages,
            "extensions": self.extensions,
            "order": self.order,
            "limit": self.limit,
            "e": self.e,
            "yearFrom": self.yearFrom,
            "yearTo": self.yearTo,
        }
        headers = {"UUID": get_uuid()}

        # 1. 网络请求
        try:
            resp = requests.post(api_search, json=json_data, headers=headers, timeout=15)
        except requests.RequestException as e:
            log.error(f"搜索网络错误: {e}")
            self.sig_fail.emit(SearchError.NETWORK_ERROR)
            return
        log.info(f"从服务端接收到数据,耗时{time.time() - t1:.2f}s")

        # 2. HTTP 状态
        if resp.status_code == 429:
            self.sig_fail.emit(SearchError.RATE_LIMIT)
            return
        if resp.status_code != 200:
            log.warning(f"搜索返回非 200: {resp.status_code}")
            self.sig_fail.emit(SearchError.UNKNOWN)
            return

        # 3. JSON 解析
        try:
            data = resp.json()
        except (JSONDecodeError, ValueError) as e:
            log.error(f"搜索响应 JSON 解析失败: {e}")
            self.sig_fail.emit(SearchError.PARSE_ERROR)
            return

        # 4. 业务处理
        success = data.get('success')
        if success == 1:
            books = data.get('books') or []
            if books:
                log.success("数据接收成功，开始传送数据")
                self.pagination = data.get('pagination')
                self.sig_success.emit(books)
            else:
                log.warning("数据为空")
                self.sig_fail.emit(SearchError.EMPTY_RESULT)
        else:
            # 业务失败，可能是关键词被过滤
            log.warning(f"搜索业务失败: {data}")
            # success 字段存在但不为 1 时更可能是违禁词
            if success is not None:
                self.sig_fail.emit(SearchError.BLOCKED_KEYWORD)
            else:
                self.sig_fail.emit(SearchError.UNKNOWN)


if __name__ == '__main__':
    zs = OlibSearcherV4("三体", languages=["english"], limit="10", e="1")
    res = zs.book_from_my_api()
    print(res)
