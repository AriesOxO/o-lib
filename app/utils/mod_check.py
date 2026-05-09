# _*_ coding:utf-8 _*_
# Copyright (C) 2024-2024 shiyi0x7f,Inc.All Rights Reserved
# @Time : 2024/12/20 下午8:33
# @Author: shiyi0x7f
import requests
import webbrowser
from loguru import logger
from PyQt5.QtCore import QThread, pyqtSignal
from qfluentwidgets import Dialog

from .mod_domain import get_domain
from ..common.config import cfg, VERSION


class UpdateCheckWorker(QThread):
    """异步获取服务端配置，避免阻塞 UI"""
    finished_with_config = pyqtSignal(object)  # dict | None

    def run(self):
        domain = get_domain()
        if not domain:
            logger.warning("服务器地址未配置，跳过更新检查")
            self.finished_with_config.emit(None)
            return
        try:
            resp = requests.get(f'{domain}/OlibServer', timeout=5)
            self.finished_with_config.emit(resp.json())
        except Exception as e:
            logger.warning(f"获取服务端配置失败: {e}")
            self.finished_with_config.emit(None)


class CheckUpdate:
    """
    版本更新与公告检查器。
    支持两种模式：
    - 同步模式（向后兼容）：构造时直接请求，阻塞当前线程
    - 异步模式：调用 check_async() 通过 QThread 执行，通过回调处理结果
    """

    def __init__(self, async_mode: bool = False):
        self.__config = None
        self._worker = None
        if not async_mode:
            self.__fetch_config_sync()

    def __fetch_config_sync(self):
        domain = get_domain()
        if not domain:
            logger.warning("服务器地址未配置，跳过更新检查")
            return
        try:
            resp = requests.get(f'{domain}/OlibServer', timeout=5)
            self.__config = resp.json()
        except Exception as e:
            logger.warning(f"获取服务端配置失败: {e}")
            self.__config = None

    def check_async(self, on_done):
        """异步获取服务端配置，完成后回调 on_done(self)"""
        self._worker = UpdateCheckWorker()
        def _handle(config):
            self.__config = config
            try:
                on_done(self)
            finally:
                self._worker.deleteLater()
                self._worker = None
        self._worker.finished_with_config.connect(_handle)
        self._worker.start()

    def __get_version_status(self):
        if self.__config is None:
            return 0
        client_ver = VERSION
        server_vers = self.__config.get('Versions')
        if not server_vers:
            return 0
        latest = server_vers[-1]
        versions = [ver.get('version') for ver in server_vers]
        latest_ver = versions[-1]
        cfg.set(cfg.latestVersion, latest_ver)
        forced = latest.get('forcedUpdate')
        if latest_ver != client_ver and client_ver in versions:  # 保证在已有版本内
            logger.warning(f"当前版本不是最新版本 客户端{client_ver} 服务端{latest_ver}")
            if forced:
                return 2  # 强制更新
            else:
                return 1  # 可跳过更新
        return 0  # 最新版本无操作

    def get_notice(self):
        if self.__config is None:
            return {'show': False, 'title': '', 'content': ''}
        server_notice = self.__config.get('Notice')
        return server_notice if server_notice else {'show': False, 'title': '', 'content': ''}

    def get_update_url(self):
        if self.__config is None:
            return None
        return self.__config.get('UpdateUrl')

    def handle_version(self):
        n = self.__get_version_status()
        if n == 1:
            update_window = Dialog("更新选项", "新版本功能更加丰富稳定哦~")
            update_window.yesButton.setText("立即更新")
            update_window.cancelButton.setText("下次再说")
            if update_window.exec_():
                self.update_()
                exit(0)
            else:
                cfg.set(cfg.updateMode, False)
        elif n == 2:
            forcedUpdateWin = Dialog("强制更新", "是否进入更新界面")
            if forcedUpdateWin.exec_():
                logger.info("开始强制更新")
                self.update_()
            else:
                logger.warning("取消强制更新")
            exit(0)

    def update_(self):
        update_url = self.get_update_url()
        if update_url:
            webbrowser.open(update_url)
        else:
            logger.warning("更新链接不可用")
