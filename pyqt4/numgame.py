#!/usr/bin/env python
# coding: utf-8

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys
import random

def randNums(left, right, num=None):
    '''生成 [left, right] 区间内的 num 个不重复的数字，以 list 形式返回
        若 num 为 None 则置 num 的值为 right - left + 1，即返回结果为 [left, right] 的随机序列'''
    if type(left) != int or type(right) != int or (num != None and type(num) != int):
        return None
    if left > right:
        left, right = right, left
    if num == None:
        num = right - left + 1
    if num <= 0:
        return []
    res = []
    numbers = [x for x in xrange(left, right + 1)]
    for x in xrange(num):
        i = random.randint(0, len(numbers) - 1)
        res.append(numbers[i])
        numbers.remove(numbers[i])
        if len(numbers) == 0:
            break
    return res


class RowAndCol(QDialog):
    """docstring for RowAndCol"""
    def __init__(self, _row, _col, title=u"设置行列数", *args, **kwargs):
        super(RowAndCol, self).__init__(*args, **kwargs)
        self.setWindowTitle(title)
        grid = QGridLayout(self)
        lbl = QLabel(u'行数(3~10)：')
        grid.addWidget(lbl, 0, 0)
        self.sbRow = QSpinBox()
        self.sbRow.setRange(3, 10)
        self.sbRow.setValue(_row)
        grid.addWidget(self.sbRow, 0, 1, 1, 2)
        lbl = QLabel(u'列数(3~10)：')
        grid.addWidget(lbl, 1, 0)
        self.sbCol = QSpinBox()
        self.sbCol.setRange(3, 10)
        self.sbCol.setValue(_col)
        grid.addWidget(self.sbCol, 1, 1, 1, 2)
        grid.setColumnStretch(1, 1)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        grid.addWidget(buttons, 2, 2)

    @staticmethod
    def getRowAndCol(_row, _col):
        dialog = RowAndCol(_row, _col)
        res = dialog.exec_()
        return (res, (dialog.sbRow.value(), dialog.sbCol.value()))


class MyLabel(QLabel):

    FRONTSIDE = 0
    BACKSIDE = 1
    HIDE = 2
    HIGHLIGHT = 3

    def __init__(self, *args, **kwargs):
        super(MyLabel, self).__init__(*args, **kwargs)
        self.setAlignment(Qt.AlignCenter)
        self.initStyle()

    def mousePressEvent(self, event):
        self.sthOfMousePress = self.myBgColor
        self.setMyStyle(myBgColor='rgb(85, 255, 255)')
        # self.setMyStyle(myBgColor='rgb(85, 255, 127)')

    def mouseReleaseEvent(self, event):
        self.emit(SIGNAL('clicked(PyQt_PyObject)'), self)
        self.setMyStyle(myBgColor=self.sthOfMousePress)

    def initStyle(self):
        self.myBgColor = 'rgb(255, 255, 127)'
        self.myColor = 'rgb(0, 170, 255)'
        self.myFont = '75 26pt "Axure Handwriting"'
        self.myHighlight = 'rgb(255, 0, 0)'
        self.myStatus = self.FRONTSIDE

    def setMyStyle(self, myBgColor=None, myColor=None, myHighlight=None, myFont=None):
        if myBgColor:
            self.myBgColor = myBgColor
        if myColor:
            self.myColor = myColor
        if myHighlight:
            self.myHighlight = myHighlight
        if myFont:
            self.myFont = myFont
        if self.myStatus == self.FRONTSIDE:
            self.showFrontSide()
        elif self.myStatus == self.BACKSIDE:
            self.showBackSide()
        elif self.myStatus == self.HIDE:
            self.setHide()
        elif self.myStatus == self.HIGHLIGHT:
            self.showHighlight()
        else:
            pass

    def showFrontSide(self):
        self.showStyle(self.myBgColor, self.myColor, self.myFont)
        self.myStatus = self.FRONTSIDE

    def showBackSide(self):
        self.showStyle(self.myBgColor, self.myBgColor, self.myFont)
        self.myStatus = self.BACKSIDE

    def showHighlight(self):
        self.showStyle(self.myBgColor, self.myHighlight, self.myFont)
        self.myStatus = self.HIGHLIGHT

    def showStyle(self, bgColor=None, color=None, font=None):
        styleSheet = ''
        if bgColor:
            styleSheet += 'background-color: ' + bgColor + ';'
        if color:
            styleSheet += 'color: ' + color + ';'
        if font:
            styleSheet += 'font: ' + font + ';'
        if styleSheet != '':
            self.setStyleSheet(styleSheet)

    def setHide(self):
        self.showStyle(bgColor='rgb(0, 0, 0)', color='rgb(0, 0, 0)')
        self.myStatus = self.HIDE

    def isHide(self):
        return self.myStatus == self.HIDE

    # 不起作用的，不知道该怎么处理好
    def drawCross(self):
        self.setAttribute(Qt.WA_PaintOutsidePaintEvent, True)
        painter = QPainter(self)
        painter.setPen(QPen(Qt.red, 3))
        halfWidthOfAxis = self.width() / 2.0
        halfHeightOfAxis = self.height() / 2.0
        centerX = self.x() + halfWidthOfAxis
        centerY = self.y() + halfHeightOfAxis
        painter.drawLine(centerX - halfWidthOfAxis, centerY - halfHeightOfAxis,
                        centerX + halfWidthOfAxis, centerY + halfHeightOfAxis)
        painter.drawLine(centerX + halfWidthOfAxis, centerY - halfHeightOfAxis,
                        centerX - halfWidthOfAxis, centerY + halfHeightOfAxis)


class NumGame(QMainWindow):

    def __init__(self, title=u"记忆方块", size=[600, 600]):
        super(NumGame, self).__init__()
        self.initSelf(title, size)
        self.initUI()
        self.startGame()

    def initSelf(self, title, size):
        self.setWindowTitle(title)
        # self.setWindowIcon(QIcon(u'numgame.png'))
        self.setMinimumSize(size[0], size[1])
        self.showOnCenter()

    def initUI(self):
        self.initBoard()
        self.statusbar = self.statusBar()
        self.level = 1
        self.refreshStatusbar()
        self.initMenu()

    def refreshStatusbar(self):
        self.statusbar.showMessage(u'第' + str(self.level) + u'关')

    def initMenu(self):
        self.menubar = self.menuBar()
        menuOpt = self.menubar.addMenu(u'设置')
        menuSquare = menuOpt.addMenu(u'方块')
        actSquareBgColor = QAction(u'背景颜色', self)
        actSquareBgColor.triggered.connect(self.setSquareBgColor)
        menuSquare.addAction(actSquareBgColor)
        actSquareColor = QAction(u'字体颜色', self)
        actSquareColor.triggered.connect(self.setSquareColor)
        menuSquare.addAction(actSquareColor)
        actSetRowAndCol = QAction(u'行列数', self)
        actSetRowAndCol.triggered.connect(self.setRowAndCol)
        menuSquare.addAction(actSetRowAndCol)

        self.actAutoNextRound = QAction(u'自动进入下一轮', menuOpt, checkable=True)
        menuOpt.addAction(self.actAutoNextRound)

        menuHelp = self.menubar.addMenu(u'帮助')
        actNextSquare = QAction(u'提示下一块', self)
        actNextSquare.triggered.connect(self.showNextSquare)
        menuHelp.addAction(actNextSquare)
        actShowRemain = QAction(u'查看剩下所有的方块号', self)
        actShowRemain.triggered.connect(self.showRemain)
        menuHelp.addAction(actShowRemain)
        actTutorial = QAction(u'游戏玩法', self)
        actTutorial.triggered.connect(self.showTutorial)
        menuHelp.addAction(actTutorial)

    def setRowAndCol(self):
        reply = QMessageBox.question(self, u'提示', u'设置行列数将会使游戏重头开始，是否继续？', QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.No:
            return
        res = RowAndCol.getRowAndCol(_row=self.myRow if hasattr(self, 'myRow') else 5,
                                    _col=self.myCol if hasattr(self, 'myCol') else 5,)
        if res[0] == QDialog.Accepted:
            self.myRow, self.myCol = res[1]
            self.initBoard()
            self.startGame()
            self.level = 1
            self.refreshStatusbar()

    def setSquareBgColor(self):
        bgColor = QColorDialog.getColor()
        if bgColor.isValid():
            self.squareBgColor = bgColor.name()
            for i in range(self.current_num, self.totalNum + 1):
                self.squares[self.ids[i - 1]].setMyStyle(myBgColor=bgColor.name())

    def setSquareColor(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.squareColor = color.name()
            for i in range(self.current_num, self.totalNum + 1):
                self.squares[self.ids[i - 1]].setMyStyle(myColor=color.name())

    def showNextSquare(self):
        if self.current_num == 1:
            QMessageBox.information(self, u'提示下一块', u'游戏还没有开始，请先点击1号方块以开始游戏')
        else:
            self.squares[self.ids[self.current_num - 1]].showHighlight()

    def showRemain(self):
        for i in range(self.current_num, self.totalNum + 1):
            self.squares[self.ids[i - 1]].showFrontSide()
        self.isStart = False

    def showTutorial(self):
        QMessageBox.information(self, u'游戏教程', u'在游戏开始前记住所有已编好号的方块的位置，然后点击1号方块开始游戏；游戏开始后所有方块的编号会隐藏起来，你需要根据记忆从小到大（也就是按照2,3,4...的顺序）依次点击方块，每当点击正确时，该方块会消失，否则游戏结束，可以重新开始；当点击完当前面板的所有方块后可以进入下一轮。在游戏任何时刻都可以在菜单栏中的设置菜单里进行方块字体颜色、背景颜色以及面板显示的方块的行列数的设置；在游戏过程中也可以通过帮助菜单得到下一步的提示。')

    def initBoard(self):
        board = QWidget()
        board.setStyleSheet('background-color: rgb(0, 0, 0);')
        self.squares = []
        grid = QGridLayout()
        __row = self.myRow if hasattr(self, 'myRow') else 5
        __col = self.myCol if hasattr(self, 'myCol') else 5
        for r in range(0, __row):
            for c in range(0, __col):
                lbl = MyLabel()
                self.connect(lbl, SIGNAL('clicked(PyQt_PyObject)'), self.numClick)
                self.squares.append(lbl)
                grid.addWidget(lbl, r, c)
        board.setLayout(grid)
        self.setCentralWidget(board)

    def numClick(self, label):
        if label.isHide() == True:
            return
        if int(label.text()) != self.current_num:
            for i in range(self.current_num, self.totalNum + 1):
                self.squares[self.ids[i - 1]].showFrontSide()
            # label.drawCross()
            reply = QMessageBox.question(
                self, 'Game over', u'是否再来一次？', QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.startGame(self.totalNum)
            else:
                self.close()
                QMessageBox.information(self, u'再见', u'期待你下一次的到来~')
        else:
            if self.isStart == False:
                for i in range(self.current_num, self.totalNum + 1):
                    self.squares[self.ids[i - 1]].showBackSide()
                self.isStart = True
            # label.hide()
            label.setHide()
            if self.current_num == len(self.squares):
                reply = QMessageBox.information(self, u'已通关', u'恭喜你已通过所有关卡，是否从头再玩一次？', QMessageBox.Yes, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.level = 1
                    self.refreshStatusbar()
                    self.startGame()
                else:
                    self.close()
                    QMessageBox.information(self, u'再见', u'期待你下一次的到来~')
            elif self.current_num == self.totalNum:
                if self.actAutoNextRound.isChecked() or QMessageBox.information(self, u'通关', u'进入下一关？', QMessageBox.Yes, QMessageBox.No) == QMessageBox.Yes:
                    self.startGame(self.totalNum + 1)
                    self.level += 1
                    self.refreshStatusbar()
                else:
                    self.startGame(self.totalNum)
            else:
                self.current_num += 1

    def startGame(self, square_num=3):
        # self.initBoard()
        if square_num > len(self.squares):
            QMessageBox.warning(self, u'警告', u'方块数量超出面板容量！')
            square_num = len(self.squares)
        self.totalNum = square_num
        for square in self.squares:
            square.setHide()
        self.ids = randNums(0, len(self.squares) - 1, self.totalNum)
        num = 1
        for idx in self.ids:
            lbl = self.squares[idx]
            lbl.setText(str(num))
            num += 1
            if hasattr(self, 'squareBgColor'):
                lbl.setMyStyle(myBgColor=self.squareBgColor)
            if hasattr(self, 'squareColor'):
                lbl.setMyStyle(myColor=self.squareColor)
            lbl.showFrontSide()
            # 因为startGame会多次调用，所以信号和槽的绑定不能放在这里！否则该信号会多次调用同样的函数
            # self.connect(lbl, SIGNAL('clicked(PyQt_PyObject)'), self.numClick)
        self.current_num = 1
        self.isStart = False

    def showOnCenter(self):
        screen = QDesktopWidget().screenGeometry()
        self.move((screen.width() - self.width()) / 2,
                  (screen.height() - self.height()) / 2)

    def closeEvent(self, event):
        pass


def main():
    app = QApplication(sys.argv)
    w = NumGame()
    w.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
