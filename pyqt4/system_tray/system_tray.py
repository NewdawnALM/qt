#!/usr/bin/env python
# coding: utf-8

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys
import requests
# import redis
import json


class SystemTray(QMainWindow):
    """My SystemTray, includes translator and functions of getting commands quickly."""

    YDERRORCODE = {
        0: u'正常',
        20: u'要翻译的文本过长',
        30: u'无法进行有效的翻译',
        40: u'不支持的语言类型',
        50: u'无效的key',
        60: u'无词典结果，仅在获取词典结果生效'
    }

    def __init__(self, title="SystemTray", size=[600, 500]):
        super(SystemTray, self).__init__()
        self.initSelf(title, size)
        self.initUI()

    def initSelf(self, title, size):
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon('./images/window_icon.jpg'))
        self.resize(size[0], size[1])
        self.showOnCenter()

        self.clipboard = QApplication.clipboard()
        self.translateUrl = "http://fanyi.youdao.com/openapi.do?keyfrom=Newdawn&key=784637548&type=data&doctype=json&version=1.1&q="

    def initUI(self):
        self.initBoard()
        self.statusbar = self.statusBar()
        self.initAction()
        self.initTrayIcon()

    def initBoard(self):
        board = QWidget()
        mainLayout = QVBoxLayout()

        gbox = QGroupBox(u'翻译设置')
        grid = QGridLayout()
        self.cbImmediatelyTranslate = QCheckBox(u'翻译剪切板中的内容')
        self.cbImmediatelyTranslate.setChecked(True)
        self.cbImmediatelyTranslate.stateChanged.connect(self.translateOption)
        grid.addWidget(self.cbImmediatelyTranslate, 0, 0, 1, 2)
        label = QLabel(u'字数限制：')
        label.setAlignment(Qt.AlignRight)
        grid.addWidget(label, 0, 3)
        self.sbWordLimit = QSpinBox()
        self.sbWordLimit.setRange(1, 800)
        self.sbWordLimit.setValue(200)
        self.sbWordLimit.valueChanged.connect(lambda x: self.slotWordLimitChange(self.sbWordLimit.value()))
        grid.addWidget(self.sbWordLimit, 0, 4)

        self.label_1 = QLabel(u'输入要翻译的文本：')
        grid.addWidget(self.label_1, 1, 0)
        self.textTranslate = QTextEdit()
        grid.addWidget(self.textTranslate, 2, 0, 3, 6)
        self.btnTranslate = QPushButton(u'翻译')
        self.btnTranslate.clicked.connect(self.btnClicked)
        grid.addWidget(self.btnTranslate, 6, 5)
        self.label_1.hide()
        self.textTranslate.hide()
        self.btnTranslate.hide()

        label = QLabel(u'显示方式：')
        label.setAlignment(Qt.AlignRight)
        grid.addWidget(label, 6, 0)
        self.cbbTranslateShowType = QComboBox()
        self.cbbTranslateShowType.addItem(QIcon(u'./images/messagebox.png'), u'弹窗显示')
        self.cbbTranslateShowType.addItem(self.style().standardIcon(QStyle.SP_MessageBoxInformation), u'系统通知')
        self.cbbTranslateShowType.currentIndexChanged.connect(lambda x: self.slotShowTypeChange(self.cbbTranslateShowType.currentIndex()))
        grid.addWidget(self.cbbTranslateShowType, 6, 1)

        self.cbShowTranslateDeatil = QCheckBox(u'显示详细的翻译结果')
        self.cbShowTranslateDeatil.clicked.connect(lambda x: self.slotShowDetailChange(self.cbShowTranslateDeatil.isChecked()))
        self.cbShowTranslateDeatil.setChecked(True)
        grid.addWidget(self.cbShowTranslateDeatil, 6, 3)

        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)
        grid.setColumnStretch(4, 1)
        grid.setColumnStretch(5, 1)
        gbox.setLayout(grid)
        mainLayout.addWidget(gbox)

        gbox = QGroupBox(u'快速复制命令到剪切板')
        grid = QGridLayout()
        label = QLabel(u'历史命令（history）：')
        grid.addWidget(label, 0, 0)
        self.cbbHistoryCommands = QComboBox()
        grid.addWidget(self.cbbHistoryCommands, 1, 0)
        gbox.setLayout(grid)
        mainLayout.addWidget(gbox)

        mainLayout.addStretch(1)
        board.setLayout(mainLayout)
        self.setCentralWidget(board)

    def slotShowTypeChange(self, index):
    	self.cbbTranslateShowType.setCurrentIndex(index)
    	if index == 0:
    		self.actMessagebox.setChecked(True)
    	else:
    		self.actSystemMessage.setChecked(True)

    def slotShowDetailChange(self, bShowDeatil):
    	if bShowDeatil == True:
    		self.actShowDetail.setChecked(True)
    		self.cbShowTranslateDeatil.setChecked(True)
    	else:
    		self.actShowDetail.setChecked(False)
    		self.cbShowTranslateDeatil.setChecked(False)

    def slotWordLimitChange(self, wordLen):
    	if wordLen in [100, 200, 400]:
    		self.sbWordLimit.setValue(wordLen)
    	if wordLen == 100:
    		self.actWordLimit_1.setChecked(True)
    	elif wordLen == 200:
    		self.actWordLimit_2.setChecked(True)
    	elif wordLen == 400:
    		self.actWordLimit_3.setChecked(True)
    	else:
    		self.actWordLimit_4.setChecked(True)
    		self.actWordLimit_4.setText(('其它(' + str(wordLen) + ')').decode('utf8'))
    		self.show()

    def initAction(self):
        self.actTranslate = QAction(QIcon('./images/youdao.jpg'), u'立即翻译', self)
        self.actTranslate.setShortcut('ctrl+alt+f')
        self.actTranslate.triggered.connect(self.translate_clipboard)

        menuShowType = QMenu(u'显示方式', self)
        ag = QActionGroup(self, exclusive=True)
        self.actMessagebox = QAction(QIcon(u'./images/messagebox.png'), u'弹窗显示', menuShowType, checkable=True)
        self.actMessagebox.triggered.connect(lambda x: self.slotShowTypeChange(0))
        self.actMessagebox.setChecked(True)
        self.actSystemMessage = QAction(self.style().standardIcon(QStyle.SP_MessageBoxInformation), u'系统通知', menuShowType, checkable=True)
        self.actSystemMessage.triggered.connect(lambda x: self.slotShowTypeChange(1))
        menuShowType.addActions([ag.addAction(self.actMessagebox), ag.addAction(self.actSystemMessage)])

        menuTranslateOption = QMenu(u'翻译设置', self)
        menuTranslateOption.setIcon(QIcon(u'./images/config.png'))
        self.actShowDetail = QAction(u'显示详细结果', menuTranslateOption, checkable=True)
        self.actShowDetail.triggered.connect(lambda x: self.slotShowDetailChange(self.actShowDetail.isChecked()))
        self.actShowDetail.setChecked(True)

        menuWordLimit = QMenu(u'字数限制', self)
        ag = QActionGroup(self, exclusive=True)
        self.actWordLimit_1 = QAction(u'100', menuWordLimit, checkable=True)
        self.actWordLimit_1.triggered.connect(lambda x: self.slotWordLimitChange(100))
        self.actWordLimit_2 = QAction(u'200', menuWordLimit, checkable=True)
        self.actWordLimit_2.triggered.connect(lambda x: self.slotWordLimitChange(200))
        self.actWordLimit_2.setChecked(True)
        self.actWordLimit_3 = QAction(u'400', menuWordLimit, checkable=True)
        self.actWordLimit_3.triggered.connect(lambda x: self.slotWordLimitChange(400))
        self.actWordLimit_4 = QAction(u'其它', menuWordLimit, checkable=True)
        self.actWordLimit_4.triggered.connect(lambda x: self.slotWordLimitChange(1))
        menuWordLimit.addActions([ag.addAction(self.actWordLimit_1), ag.addAction(self.actWordLimit_2), ag.addAction(self.actWordLimit_3), ag.addAction(self.actWordLimit_4)])

        menubar = self.menuBar()
        menuTranslate = menubar.addMenu(u'翻译')
        menuTranslate.addAction(self.actTranslate)
        menuTranslateOption.addMenu(menuShowType)
        menuTranslateOption.addAction(self.actShowDetail)
        menuTranslateOption.addMenu(menuWordLimit)
        menuTranslate.addMenu(menuTranslateOption)

        commandsMenu = menubar.addMenu(u'commands设置')

    def initTrayIcon(self):
        menuTrayIcon = QMenu(self)
        menuTrayIcon.addAction(self.actTranslate)
        
        menuTranslateOption = QMenu(u'翻译设置', self)
        menuTranslateOption.setIcon(QIcon(u'./images/config.png'))
        menuShowType = QMenu(u'显示方式', self)
        menuShowType.addActions([self.actMessagebox, self.actSystemMessage])
        menuTranslateOption.addMenu(menuShowType)
        menuTranslateOption.addAction(self.actShowDetail)
        menuWordLimit = QMenu(u'字数限制', self)
        menuWordLimit.addActions([self.actWordLimit_1, self.actWordLimit_2, self.actWordLimit_3, self.actWordLimit_4])
        menuTranslateOption.addMenu(menuWordLimit)

        menuTrayIcon.addMenu(menuTranslateOption)
        # menuTrayIcon.addAction(QAction("Minimize", self, triggered=self.showMinimized))
        menuTrayIcon.addSeparator()
        menuTrayIcon.addAction(QAction(QIcon('./images/qt.png'), u"打开主面板", self, triggered=self.showNormal))
        menuTrayIcon.addAction(QAction(QIcon('./images/quit.png'), u"退出", self, triggered=qApp.quit))

        self.trayIcon = QSystemTrayIcon(QIcon('./images/tray_icon.jpg'), self)
        self.trayIcon.setContextMenu(menuTrayIcon)
        self.trayIcon.show()

    def btnClicked(self):
        self.translateText(self.textTranslate.toPlainText())

    def translateOption(self):
        if self.cbImmediatelyTranslate.isChecked():
            self.label_1.hide()
            self.textTranslate.hide()
            self.btnTranslate.hide()
        else:
            self.label_1.show()
            self.textTranslate.show()
            self.btnTranslate.show()

    def translate(self, text):
        if len(text) > self.sbWordLimit.value():
            return (1, u'翻译的文本长度超过字数限制！')
        text = (str(text.toUtf8())).strip()
        if text == '':
        	return (2, u'翻译的字符串中没有实际的字符（只包含空格/tab/换行等）')
        req = self.translateUrl + text
        r = requests.get(req)
        if r.ok != True:
            return (r.status_code, QString(u'网络错误，url请求失败'))
        else:
            u_dict = json.loads(r.text)
            errorCode = u_dict['errorCode']
            if errorCode != 0:
                return (errorCode, QString(self.YDERRORCODE[errorCode]))
            else:
                res = QString(u'')
                if u_dict.has_key('translation'):
                    res += u"<翻译>:  "
                    for x in u_dict['translation']:
                        res = res + x + ", "
                    res = (
                        res[:-2] + "\n") if res[-2:] == ", " else (res + "\n")
                if u_dict.has_key('basic'):
                    if u_dict['basic'].has_key('explains'):
                        res += u"<解释>:  "
                        for x in u_dict['basic']['explains']:
                            res = res + x + ", "
                        res = (
                            res[:-2] + "\n") if res[-2:] == ", " else (res + "\n")
                if self.cbShowTranslateDeatil.isChecked():
                    if u_dict.has_key('web'):
                        res += u"<网络用语>:  \n"
                        for d in u_dict['web']:
                            if d.has_key('key'):
                                res = res + u"  <关键词>:  " + d['key'] + "\n"
                                if d.has_key('value'):
                                    res = res + u"  <意思>:  "
                                    for v in d['value']:
                                        res = res + v + ", "
                                    res = (
                                        res[:-2] + "\n") if res[-2:] == ", " else (res + "\n")
                return (errorCode, res)

    def translateText(self, text):
    	if type(text) == type(QString()):
    		text = text.simplified()
    	elif type(text) == str:
    		text = text.strip()
        result = self.translate(text)
        showType = self.cbbTranslateShowType.currentIndex()
        if result[0] != 0:
            title = QString(u'翻译出错')
            self.showTranslateResult(title, result[1], QMessageBox.Warning)
        else:
            title = (text[0:20] + u'....' if len(text)
                     >= 20 else text) + u" 的翻译结果 "
            self.showTranslateResult(title, result[1], QMessageBox.Information)

    def translate_clipboard(self):
        clip_data = self.clipboard.mimeData()
        if clip_data.hasText():
            src = clip_data.text()
            self.translateText(src)
        else:
            QMessageBox.information(self, u'提示', u'剪切板中的内容为空，无法翻译！')

    def showTranslateResult(self, title, content, icon):
        showType = self.cbbTranslateShowType.currentIndex()
        if showType == 0:
            # 至关重要的一句，否则当关闭messagebox的窗口时，整个程序自动退出！
            QApplication.setQuitOnLastWindowClosed(False)
            QMessageBox(QMessageBox.Icon(icon), title, content).exec_()
        elif showType == 1:
            self.trayIcon.showMessage(title, content, QSystemTrayIcon.MessageIcon(icon))
        else:
            pass

    def showOnCenter(self):
        screen = QDesktopWidget().screenGeometry()
        self.move((screen.width() - self.width()) / 2,
                  (screen.height() - self.height()) / 2)

    def closeEvent(self, event):
        if self.trayIcon.isVisible():
            self.trayIcon.showMessage(u'隐藏', u'在任务栏按钮可打开主窗口', QSystemTrayIcon.MessageIcon(QMessageBox.Information), 1000)
            self.hide()
            event.ignore()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    tray = SystemTray()
    # tray.show()
    sys.exit(app.exec_())
