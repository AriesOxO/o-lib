# _*_ coding:utf-8 _*_
# Copyright (C) 2024-2024 shiyi0x7f,Inc.All Rights Reserved
# @Time : 2024/12/6 上午8:16
# @Author: shiyi0x7f
import os

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QVBoxLayout, QFrame,
                             QHeaderView, QTableWidgetItem,
                             QProgressBar, QWidget, QHBoxLayout)
from loguru import logger as log
from qfluentwidgets import TableWidget, BodyLabel, TransparentToolButton, FluentIcon as FIF

from ..tools.olib_download import OlibDownloaderV4
from ..common.config import cfg
from ..utils import open_in_file_manager


class DownloadInterface(QFrame):
    finished = pyqtSignal(bool, str)
    sig_start = pyqtSignal(str)
    sig_rate_limit = pyqtSignal(bool)

    def __init__(self, obj_name):
        super().__init__()
        self.setObjectName(obj_name)
        # 跟踪每个下载任务: id -> {downloader, row, bookname}
        self._tasks = {}
        self._next_id = 0

        self.layout = QVBoxLayout(self)
        self.initUI()

    def initUI(self):
        self.tableWidget = TableWidget(self)
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setEditTriggers(TableWidget.NoEditTriggers)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.tableWidget.setHorizontalHeaderLabels(["书名", "进度", "速度", "操作"])
        self.layout.addWidget(self.tableWidget)

    def _find_row(self, task_id):
        """根据 task_id 查找当前行号（行会被删除所以需要动态查找）"""
        task = self._tasks.get(task_id)
        return task['row'] if task else None

    def _rebuild_row_indexes(self):
        """删除行后重建 task_id 到 row 的映射"""
        # 从表格的第一列文本反查
        new_map = {}
        for tid, info in list(self._tasks.items()):
            # 找到对应的行
            for r in range(self.tableWidget.rowCount()):
                item = self.tableWidget.item(r, 0)
                if item and item.data(Qt.UserRole) == tid:
                    info['row'] = r
                    new_map[tid] = info
                    break
        self._tasks = new_map

    def download(self, bookid, hashid, bookname, extension, size):
        task_id = self._next_id
        self._next_id += 1

        downloader = OlibDownloaderV4(bookid, hashid, bookname, extension, size)
        progressBar = QProgressBar()
        progressBar.setRange(0, 100)
        progressBar.setAlignment(Qt.AlignCenter)

        speedLabel = BodyLabel()
        speedLabel.setAlignment(Qt.AlignCenter)

        # 操作按钮容器
        op_widget = self._make_op_widget(task_id)

        downloader.sig_down_process.connect(lambda v, pb=progressBar: pb.setValue(v))
        downloader.speed.connect(lambda s, lbl=speedLabel: lbl.setText(f"{s} KB/s"))
        downloader.final.connect(lambda e, bn=bookname, tid=task_id: self._on_finish(tid, e, bn))
        downloader.sig_cancelled.connect(lambda tid=task_id: self._on_cancelled(tid))
        downloader.finished.connect(lambda dl=downloader: dl.deleteLater())
        downloader.sig_start.connect(lambda: self._on_started(task_id, bookname, progressBar, speedLabel, op_widget))
        downloader.sig_rate_limit.connect(self._on_rate_limit)

        self._tasks[task_id] = {
            'downloader': downloader,
            'row': None,
            'bookname': bookname,
            'state': 'pending',
            'progressBar': progressBar,
            'speedLabel': speedLabel,
            'op_widget': op_widget,
        }
        downloader.start()

    def _make_op_widget(self, task_id):
        w = QWidget()
        h = QHBoxLayout(w)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(2)

        cancel_btn = TransparentToolButton(FIF.CLOSE)
        cancel_btn.setToolTip("取消下载")
        cancel_btn.clicked.connect(lambda: self._cancel_task(task_id))

        folder_btn = TransparentToolButton(FIF.FOLDER)
        folder_btn.setToolTip("打开下载文件夹")
        folder_btn.clicked.connect(lambda: open_in_file_manager(cfg.downloadFolder.value))

        remove_btn = TransparentToolButton(FIF.DELETE)
        remove_btn.setToolTip("从列表移除")
        remove_btn.clicked.connect(lambda: self._remove_task(task_id))

        h.addWidget(cancel_btn)
        h.addWidget(folder_btn)
        h.addWidget(remove_btn)
        return w

    def _add_download_item(self, task_id, title, progress_bar, speed_label, op_widget):
        row = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row)
        item_title = QTableWidgetItem(title)
        item_title.setData(Qt.UserRole, task_id)
        self.tableWidget.setItem(row, 0, item_title)
        self.tableWidget.setCellWidget(row, 1, progress_bar)
        self.tableWidget.setCellWidget(row, 2, speed_label)
        self.tableWidget.setCellWidget(row, 3, op_widget)
        self._tasks[task_id]['row'] = row

    def _on_started(self, task_id, bookname, pb, sl, op):
        self._add_download_item(task_id, bookname, pb, sl, op)
        log.info(f"下载页接收到开始: {bookname}")
        self._tasks[task_id]['state'] = 'running'
        self.sig_start.emit(bookname)

    def _on_finish(self, task_id, success, bookname):
        task = self._tasks.get(task_id)
        if task:
            task['state'] = 'done' if success else 'failed'
        self.finished.emit(success, bookname)

    def _on_cancelled(self, task_id):
        task = self._tasks.get(task_id)
        if task:
            task['state'] = 'cancelled'
            row = task['row']
            if row is not None:
                item = self.tableWidget.item(row, 0)
                if item:
                    item.setText(f"{item.text()} (已取消)")

    def _on_rate_limit(self, _):
        self.sig_rate_limit.emit(True)

    def _cancel_task(self, task_id):
        task = self._tasks.get(task_id)
        if not task:
            return
        if task['state'] == 'running':
            task['downloader'].cancel()
        elif task['state'] in ('done', 'failed', 'cancelled'):
            # 已完成的任务按取消按钮相当于移除
            self._remove_task(task_id)

    def _remove_task(self, task_id):
        task = self._tasks.get(task_id)
        if not task:
            return
        # 进行中的任务先取消
        if task['state'] == 'running':
            task['downloader'].cancel()
        row = task['row']
        if row is not None:
            self.tableWidget.removeRow(row)
        self._tasks.pop(task_id, None)
        self._rebuild_row_indexes()
