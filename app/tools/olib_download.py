# _*_ coding:utf-8 _*_
# Copyright (C) 2023-2023 shiyi0x7f,Inc.All Rights Reserved
# @Time : 2023/6/7 22:39
# @Author: shiyi0x7f
import os
import re
import time
import webbrowser

import requests
from PyQt5.QtCore import QThread, pyqtSignal
from loguru import logger as log

from ..common.config import cfg
from ..utils import get_domain, get_uuid


class OlibDownloaderV4(QThread):
    sig_down_process = pyqtSignal(int)
    sig_rate_limit = pyqtSignal(int)
    speed = pyqtSignal(float)
    final = pyqtSignal(bool)  # 是否下载完毕
    sig_start = pyqtSignal(bool)  # 是否开始下载
    sig_cancelled = pyqtSignal()  # 已取消

    def __init__(self, bookid, hashid, bookname, extension, size=None):
        super().__init__()
        self.bookid = bookid
        self.hashid = hashid
        # 修正文件名，避免不合法字符
        self.title = re.sub(r'[\/\\:*?"<>|&#!@=]', '', bookname)
        self.extension = extension
        self.path = cfg.downloadFolder.value
        self.remix_id = None
        self.remix_key = None
        self.size = size
        self._cancel_requested = False

    def cancel(self):
        """请求取消下载。线程会在下一次循环检查时退出并触发 sig_cancelled。"""
        self._cancel_requested = True
        log.info(f"下载取消请求已发送: {self.title}")

    def is_cancelled(self) -> bool:
        return self._cancel_requested

    def get_durl(self):
        domain = get_domain()
        if not domain:
            log.warning("服务器地址未配置")
            self.final.emit(False)
            return -1
        api_download = f'{domain}/getdownurl'
        json_data = {
            "remix_id": self.remix_id,
            "remix_key": self.remix_key,
            "bookid": self.bookid,
            "hashid": self.hashid,
            "source": "client",
        }
        headers = {"UUID": get_uuid()}
        try:
            resp = requests.post(api_download, json=json_data, headers=headers, timeout=10)
        except Exception as e:
            log.error(f"获取下载链接异常: {e}")
            self.final.emit(False)
            return -1
        if resp.status_code == 200:
            durl = resp.json().get('durl')
            self.handle_download(durl)
        elif resp.status_code == 429:
            self.sig_rate_limit.emit(999)
        else:
            self.final.emit(False)
            return -1

    def handle_download(self, durl):
        # 确保下载目录存在
        os.makedirs(self.path, exist_ok=True)
        absPath = os.path.abspath(self.path)
        sourceFile = os.path.join(absPath, f"{self.title}.{self.extension}")
        try:
            response = requests.get(durl, stream=True, timeout=30)
            self.sig_start.emit(True)
            self.download_file(response, sourceFile)
        except Exception as e:
            if type(e) is requests.exceptions.ConnectionError:
                webbrowser.open(durl)
            else:
                log.error(f"下载文件错误{type(e)} {e}")
                self.final.emit(False)

    def download_file(self, response, src):
        log.info("开始下载文件")
        read = 0
        csize = 1024
        file_size = int(self.size) if self.size else int(response.headers.get('content-length', 1))
        start_time = time.time()
        # 使用 'wb' 而不是 'ab'，避免失败重试时文件损坏
        with open(src, 'wb') as f:
            for chunk in response.iter_content(chunk_size=csize):
                if self._cancel_requested:
                    log.info(f"下载被用户取消: {self.title}")
                    f.close()
                    # 删除部分下载的文件
                    try:
                        os.remove(src)
                    except OSError:
                        pass
                    self.sig_cancelled.emit()
                    return
                if chunk:
                    f.write(chunk)
                    read += len(chunk)
                    read = min(read, file_size)
                    self.update_progress(read, file_size, start_time)
        self.final.emit(True)

    def update_progress(self, read, file_size, start_time):
        current_time = time.time()
        process = int(read / file_size * 100)
        if current_time - start_time > 1:
            download_speed = read / 1024 / (current_time - start_time)
            self.speed.emit(round(download_speed, 2))
        self.sig_down_process.emit(process)

    def run(self):
        try:
            down = self.handle_repeat_file()
            if down:
                self.get_durl()
        except Exception as e:
            log.error(f"get_durl error: {e}")

    def handle_repeat_file(self):
        repeat = self.check_repeat_files()
        if repeat:
            mode = cfg.reapeatFiles.value
            if mode:
                log.info("重名了，自动跳过")
                return False
            else:
                log.info("重名了，自动重命名")
                self.title += str(int(time.time()))
        return True

    def check_repeat_files(self):
        # 目录不存在时认为无重名
        if not os.path.isdir(self.path):
            return False
        files = os.listdir(self.path)
        file_name = f"{self.title}.{self.extension}"
        return file_name in files


if __name__ == '__main__':
    zd = OlibDownloaderV4("2468699", "94c2b8", "C++", "pdf")
    zd.start()
    zd.wait()
