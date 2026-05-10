# _*_ coding:utf-8 _*_
# Copyright (C) 2024-2024 shiyi0x7f,Inc.All Rights Reserved
# @Time : 2024/12/6 上午8:16
# @Author: shiyi0x7f
import os
import webbrowser
import random
from PyQt5.QtCore import Qt,pyqtSignal
from PyQt5.QtWidgets import (QVBoxLayout, QFrame, \
    QTableWidgetItem, QHeaderView, \
    QHBoxLayout, QWidget, QCheckBox,QLabel,QLineEdit,QListWidget,QListWidgetItem,
   QComboBox)
from qfluentwidgets import (SearchLineEdit,StateToolTip,TeachingTip,RoundMenu,Action,
                            TeachingTipTailPosition,TableWidget,SmoothMode,MenuAnimationType,
                            ComboBox,InfoBar,InfoBarPosition,CheckBox,PopUpAniStackedWidget,EditableComboBox,
                            BodyLabel,CommandBar)
from qfluentwidgets import FluentIcon as FIF
from ..tools.olib_search import OlibSearcherV4
from ..common.style_sheet import StyleSheet
from ..common.config import cfg,Languages,SearchMode,Extensions
from loguru import logger

class SearchInterface(QFrame):
    sig_download_start = pyqtSignal(list)
    def __init__(self,obj_name):
        super().__init__()
        self.setObjectName(obj_name)
        self.books = None
        self.add_cb = False #添加命令行标志
        # 初始化布局
        self.layout = QVBoxLayout(self)
        self.initUI()
        self.bind()

    def initUI(self):
        #初始化搜索框
        self.accurate_CheckBox = CheckBox()
        self.accurate_CheckBox.setText("精准搜索")
        self.searchLineEdit = SearchLineEdit()
        self.searchLineEdit.setPlaceholderText("请输入书名进行搜索")
        self.searchLineEdit.setFixedWidth(self.width() // 2)# 宽度设为容器的一半

        #初始化工具栏
        hbox = QHBoxLayout()
        #语言选项
        self.langComboBox = ComboBox()
        for k,v in Languages.items():
            self.langComboBox.addItem(k,userData=v)
        #搜索选项
        self.searchComboBox = ComboBox()
        for k,v in SearchMode.items():
            self.searchComboBox.addItem(k,userData=v)
        #排序选项
        self.extComboBox = ComboBox()
        for k, v in Extensions.items():
            self.extComboBox.addItem(k, userData=v)

        hbox.addWidget(self.accurate_CheckBox)
        hbox.addWidget(self.searchComboBox)
        hbox.addWidget(self.langComboBox)
        hbox.addWidget(self.extComboBox)


        #初始化展示页
        self.tableWidget = TableWidget()
        self.tableWidget.setSortingEnabled(True)
        self.tableWidget.setBorderVisible(True)
        self.tableWidget.setBorderRadius(8)
        self.tableWidget.setColumnCount(5)
        self.tableWidget.scrollDelagate.verticalSmoothScroll.setSmoothMode(
            SmoothMode.NO_SMOOTH) #禁用高分辨率滑动
        self.tableWidget.setEditTriggers(TableWidget.NoEditTriggers)
        self.tableWidget.verticalHeader().hide()
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.setHorizontalHeaderLabels(
            ['书名', '年份', '作者', '大小', '格式'])


        #添加组件
        self.init_combo_box()
        self.layout.addWidget(self.searchLineEdit,alignment=Qt.AlignTop|Qt.AlignHCenter)
        self.layout.addLayout(hbox)
        self.layout.addWidget(self.tableWidget)


    def bind(self):
        self.searchLineEdit.searchSignal.connect(self.search)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.searchLineEdit.setFixedWidth(self.width() // 2)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Return or e.key() == Qt.Key_Enter:
            self.search()
    def init_combo_box(self):
        self.searchComboBox.setCurrentIndex(cfg.searchMode.value)
        self.extComboBox.setCurrentIndex(cfg.extensions.value)
        self.langComboBox.setCurrentIndex(cfg.language.value)
        self.accurate_CheckBox.setChecked(cfg.accurate.value)

    def save_search_parameter(self):
        cfg.set(cfg.language,self.langComboBox.currentIndex())
        cfg.set(cfg.extensions,self.extComboBox.currentIndex())
        cfg.set(cfg.searchMode,self.searchComboBox.currentIndex())
        cfg.set(cfg.accurate,self.accurate_CheckBox.isChecked())

    def add_command_bar(self):
        hbox = QHBoxLayout()
        hbox.setStretch(0, 1)
        hbox.setStretch(1, 4)
        hbox.setStretch(2, 1)
        # 状态栏
        self.status_bar = BodyLabel()
        self.status_bar.setText("😀欢迎使用Olib~")
        self.status_bar.setAlignment(Qt.AlignCenter)
        # 工具栏
        command_bar_up = CommandBar()
        up = Action(FIF.LEFT_ARROW,'上一页',triggered=self.pre_page)
        command_bar_up.addAction(up)

        command_bar_down = CommandBar()
        down = Action(FIF.RIGHT_ARROW, '下一页',
                    triggered=self.next_page)

        command_bar_down.addAction(down)
        hbox.addWidget(command_bar_up,alignment=Qt.AlignCenter)
        hbox.addWidget(self.status_bar)
        hbox.addWidget(command_bar_down,alignment=Qt.AlignCenter)
        self.layout.addLayout(hbox)
        self.add_cb = True
    def next_page(self):
        pagination = self.searchEngine.pagination
        try:
            next = pagination['next']
            if next:
                self.search(next)
        except:
            pass

    def pre_page(self):
        pagination = self.searchEngine.pagination
        try:
            pre = pagination['before']
            if pre:
                self.search(pre)
        except:
            pass

    def set_status_bar(self):
        pagination = self.searchEngine.pagination
        current = pagination['current']
        total_pages =pagination['total_pages']
        words = ["希望喜欢读书的你，让自己的人生更加精彩！",
                 "希望学有所成的你能为这个社会增加一丝温暖~",
                 "学习路上，一往无前的你很酷！",
                 "现在你遇到的困难，未来一定会被解决。",
                 "美好的东西，不应该被功利所玷污。",
                 "不传播焦虑，不贩卖情绪，这是我的所愿！",
                 "这个软件会没有任何负担地陪伴你每个学习阶段。",
                 "软件永远不会收费，这是拾壹坚持的信念。",
                 "用知识丰富自己的人生，在书海中找到爱与勇气吧！"]
        word = random.choice(words)
        tip = f"[{current}/{total_pages}] {word}"
        self.status_bar.setText(tip)
    def search(self,page=None):
        self.tableWidget.clearContents()
        if not self.add_cb:
            self.add_command_bar()
        if self.searchLineEdit.text()!='':
            title = self.searchLineEdit.text()
            self.stp = StateToolTip("搜索中",f"正在搜索{title}~请耐心等待",self.parent())
            self.save_search_parameter()
            lang = Languages[self.langComboBox.currentText()]
            ext = Extensions[self.extComboBox.currentText()]
            mode = SearchMode[self.searchComboBox.currentText()]
            checked = cfg.accurate.value
            accurate_state = "1" if checked else None
            n = cfg.searchNums.value


            self.searchEngine = OlibSearcherV4(title,languages=lang,extensions=ext,page=page,order=mode,limit=str(n),e=accurate_state)
            self.searchEngine.sig_success.connect(self.show_books)
            self.searchEngine.sig_fail.connect(self.failed)
            self.searchEngine.finished.connect(lambda:self.searchEngine.deleteLater())
            self.searchEngine.start()
            self.stp.move(self.width() // 2, self.height() // 2)
            self.stp.show()
        else:
            self.createWarningInfoBar("书名为空","请输入书名后再进行搜索。")

    def contextMenuEvent(self,e):
        if self.books is None:
            return
        # 获取全局坐标
        global_pos = e.globalPos()
        # 转换为控件内坐标
        local_pos = self.tableWidget.mapFromGlobal(global_pos)
        # 获取行号
        row = self.tableWidget.rowAt(local_pos.y())-1

        # 如果点击的位置不在有效行范围内，直接返回
        if row == -1:
            print("未点击有效行")
            return
        self.menu = RoundMenu()
        if cfg.downloadSwitch.value==True:
            self.menu.addAction(Action(FIF.DOWNLOAD,"下载",triggered=lambda:self.download(row)))
        self.menu.addAction(Action(FIF.QUICK_NOTE,"预览",triggered=lambda:self.preview(row)))
        self.menu.addAction(Action(FIF.BOOK_SHELF,"打开书架",triggered=self.__open_folder))
        self.menu.addAction(Action(FIF.CLOUD,"云书架",triggered=self.__open_cloud_boolshelf))
        self.menu.addAction(Action(FIF.QUICK_NOTE,"微信读书",triggered=self.__open_weread))

        self.menu.exec(self.tableWidget.mapToGlobal(local_pos),aniType=MenuAnimationType.DROP_DOWN)

    def __open_folder(self):
        folder = cfg.downloadFolder.value
        os.startfile(folder)

    def __open_cloud_boolshelf(self):
        webbrowser.open('https://web.koodoreader.com/')

    def __open_weread(self):
        webbrowser.open('https://weread.qq.com/')

    def get_current_book(self,row):
        bookname = self.tableWidget.item(row,0).text()
        size = self.tableWidget.item(row,3).text()
        for book in self.books:
            title = book.get('title')
            filesize = book.get('filesizeString')
            if title == bookname and size == filesize:
                return book
        return None

    def download(self,row):
        book = self.get_current_book(row)
        if book:
            id_ = book.get('id')
            hash_ = book.get('hash')
            title = book.get('title')
            size = book.get('filesize')
            ext = book.get('extension')
            self.sig_download_start.emit([id_,hash_,title,ext,size])
        else:
            return

    def preview(self,row):
        book = self.get_current_book(row)
        if book:
            url = book.get('readOnlineUrl')
            if not url:
                self.createWarningInfoBar("预览不可用", "该书籍未提供预览链接。")
                return
            webbrowser.open(url)

    def show_books(self,books):
        self.books = books
        self.set_status_bar()
        self.stp.close()
        self.tableWidget.setRowCount(len(books))
        for i,book in enumerate(books):
            title = book['title']
            year = book['year']
            author = book['author']
            file_size = book['filesizeString']
            file_type = book['extension']
            item_title = QTableWidgetItem(title)
            item_title.setToolTip(title)
            self.tableWidget.setItem(i,0, item_title)
            self.tableWidget.setItem(i,1, QTableWidgetItem(year))
            item_author = QTableWidgetItem(author)
            item_author.setToolTip(author)
            self.tableWidget.setItem(i,2, item_author)
            self.tableWidget.setItem(i,3, QTableWidgetItem(file_size))
            self.tableWidget.setItem(i,4, QTableWidgetItem(file_type))
        self.tableWidget.setWordWrap(True)
        self.tableWidget.resizeRowsToContents()
    def failed(self,e):
        self.stp.close()
        self.tableWidget.clearContents()
        if e==0:
            logger.error("数据为空")
            self.createWarningInfoBar("结果为空","本次搜索结果为空，请更改搜索条件。")
        elif e==-1:
            logger.error("数据获取异常")
            self.createWarningInfoBar("未知异常",
                                      "请联系shiyi0x7f定位修复")
        elif e==-999:
            logger.error("违禁词")
            self.createWarningInfoBar("搜索词异常",
                                      "请修改搜索词！")
        elif e==999:
            self.createWarningInfoBar("速率限制",
                                      "服务器压力巨大，当前搜索限制为15次/分钟，请稍后再试。")

    def createWarningInfoBar(self,title,content,type_=None):
        if type_ is None:
            InfoBar.warning(
                title=title,
                content=content,
                orient=Qt.AlignHCenter,
                isClosable=False,   # disable close button
                position=InfoBarPosition.TOP_RIGHT,
                duration=2000,
                parent=self
            )
        else:
            InfoBar.success(
                title=title,
                content=content,
                orient=Qt.AlignHCenter,
                isClosable=False,  # disable close button
                position=InfoBarPosition.BOTTOM,
                duration=2000,
                parent=self
            )

