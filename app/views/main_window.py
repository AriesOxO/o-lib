# _*_ coding:utf-8 _*_
# Copyright (C) 2024-2024 shiyi0x7f
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QStackedWidget, QHBoxLayout
from qfluentwidgets import (NavigationInterface, NavigationItemPosition,
                            toggleTheme, InfoBar, InfoBarPosition,
                            TeachingTip, TeachingTipTailPosition)
from qfluentwidgets import FluentIcon as FIF
from qframelesswindow import FramelessWindow, StandardTitleBar

from .searchInterface import SearchInterface
from .downloadInterface import DownloadInterface
from .setting_interface import SettingInterface
from ..common import resources  # noqa: F401
from ..common.style_sheet import StyleSheet
from ..common.config import cfg
from ..utils import CheckUpdate


class Window(FramelessWindow):
    def __init__(self):
        super().__init__()
        self.setObjectName("main_window")
        self.setTitleBar(StandardTitleBar(self))
        self.hBoxLayout = QHBoxLayout(self)
        self.navigationInterface = NavigationInterface(self, showMenuButton=True)
        self.stackWidget = QStackedWidget(self)

        self.searchInterface = SearchInterface("搜索页")
        self.searchInterface.sig_download_start.connect(self.start_download)
        self.downloadInterface = DownloadInterface("下载页")
        self.downloadInterface.finished.connect(self.download_result)
        self.downloadInterface.sig_rate_limit.connect(self.msg_rate_limit)
        self.downloadInterface.sig_start.connect(self.start_download_msg)
        self.settingInterface = SettingInterface("设置页")

        self.checkUpdate()
        self.initLayout()
        self.initNavigation()
        self.initWindow()
        StyleSheet.MAIN_WINDOW.apply(self)

    def checkUpdate(self):
        self._updater = CheckUpdate(async_mode=True)
        self._updater.check_async(self._on_update_checked)

    def _on_update_checked(self, checker):
        if cfg.checkUpdateAtStartUp.value:
            checker.handle_version()
        self.show_notice(checker.get_notice())

    def show_notice(self, notice):
        if notice.get('show'):
            InfoBar.warning(
                notice.get('title', ''),
                notice.get('content', ''),
                Qt.Vertical, True, 15000,
                InfoBarPosition.TOP, self,
            )

    def initLayout(self):
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, self.titleBar.height(), 0, 0)
        self.hBoxLayout.addWidget(self.navigationInterface)
        self.hBoxLayout.addWidget(self.stackWidget)
        self.hBoxLayout.setStretchFactor(self.stackWidget, 1)

    def initNavigation(self):
        self.navigationInterface.setCollapsible(True)
        self.addSubInterface('搜索页', FIF.SEARCH, self.searchInterface)
        self.addSubInterface('下载页', FIF.DOWNLOAD, self.downloadInterface, routeKey="Download")

        self.navigationInterface.addSeparator()
        self.addSubInterface("赞赏", FIF.HEART, routeKey="Like",
                             position=NavigationItemPosition.BOTTOM,
                             onClick=self.showMessageBox, select=False)
        self.addSubInterface("更改主题颜色", FIF.CONSTRACT, routeKey="Theme",
                             position=NavigationItemPosition.BOTTOM,
                             onClick=self.updateStyleSheet, select=False)
        self.addSubInterface('设置页', FIF.SETTING, self.settingInterface,
                             position=NavigationItemPosition.BOTTOM)
        self.stackWidget.currentChanged.connect(self.onCurrentInterfaceChanged)
        self.stackWidget.setCurrentIndex(0)

    def updateStyleSheet(self):
        toggleTheme(True)

    def initWindow(self):
        self.resize(900, 700)
        self.setWindowIcon(QIcon('resource/logo.png'))
        self.setWindowTitle('Olib 开源图书')
        self.titleBar.setAttribute(Qt.WA_StyledBackground)
        desktop = QApplication.desktop().availableGeometry()
        self.move(
            (desktop.width() - self.width()) // 2,
            (desktop.height() - self.height()) // 2,
        )

    def addSubInterface(self, text, icon, interface=None, routeKey=None,
                        position=NavigationItemPosition.TOP, parent=None,
                        onClick=None, select=False):
        def func():
            if onClick is not None:
                onClick()
            elif interface is not None:
                self.switchTo(interface)

        if interface is not None:
            self.stackWidget.addWidget(interface)
        self.navigationInterface.addItem(
            routeKey=interface.objectName() if interface is not None else routeKey,
            icon=icon, text=text, onClick=func, tooltip=text,
            position=position or NavigationItemPosition.TOP,
            parentRouteKey=parent.objectName() if parent else None,
            selectable=select,
        )

    def start_download_msg(self, title):
        InfoBar.success(title="下载开始",
                        content=f"{title} 下载开始，可以前往下载页查看。",
                        orient=Qt.AlignHCenter, isClosable=False,
                        position=InfoBarPosition.TOP_RIGHT,
                        duration=2000, parent=self)

    def msg_rate_limit(self, _):
        InfoBar.warning(title="下载限制",
                        content="当前服务器压力过大，限制为 5 次/分钟，请 1 分钟后再尝试。",
                        orient=Qt.AlignHCenter, isClosable=False,
                        position=InfoBarPosition.TOP_RIGHT,
                        duration=2000, parent=self)

    def start_download(self, data):
        bookid, hashid, bookname, extension, size = data
        self.downloadInterface.download(bookid, hashid, bookname, extension, size)

    def switchTo(self, widget):
        self.stackWidget.setCurrentWidget(widget)

    def onCurrentInterfaceChanged(self, index):
        widget = self.stackWidget.widget(index)
        self.navigationInterface.setCurrentItem(widget.objectName())

    def download_result(self, success, bookname):
        if success:
            InfoBar.success(title="下载成功",
                            content=f"🎉 {bookname} 下载成功",
                            isClosable=True,
                            position=InfoBarPosition.BOTTOM_RIGHT,
                            duration=2000, parent=self)
        else:
            InfoBar.error(title="下载失败",
                          content=f"{bookname} 下载失败",
                          isClosable=True,
                          position=InfoBarPosition.BOTTOM_RIGHT,
                          duration=2000, parent=self)

    def showMessageBox(self):
        content = ('Olib 一路走来，遇到了很多人\n'
                   '而今又很幸运地遇见了你\n'
                   '我们只希望尽一些绵薄之力\n'
                   '让更多人在繁杂尘世有一本书相伴\n'
                   '谢谢你的喜欢~')
        TeachingTip.create(target=self,
                           image=QPixmap(":/image/DONATE"),
                           title="❤感谢❤",
                           isClosable=True,
                           content=content,
                           duration=15000,
                           tailPosition=TeachingTipTailPosition.RIGHT_BOTTOM)


if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    w = Window()
    w.show()
    app.exec_()
