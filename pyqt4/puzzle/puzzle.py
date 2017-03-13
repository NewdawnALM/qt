#!/usr/bin/env python
# coding: utf-8

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys
import os
import random
import math
import copy

# sys.path.append('./gen-py')
# from game import EightDigital
from gen_py.game import EightDigital

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
import socket

remote_ip = '123.207.108.119'
remote_port = 9091
custom_steps = {
    2 * 2 : [6, 6],
    2 * 3 : [12, 21],
    2 * 4 : [18, 36],
    2 * 5 : [16, 55],
    3 * 3 : [16, 31],
    3 * 4 : [12, ],
    3 * 5 : [11, ],
    4 * 4 : [10, ],
    4 * 5 : [9, ],
    5 * 5 : [9, ],
}

def rpcRandNums(max_num, row, col):
    '''通过 EightDigital 的 getRandomState 接口生成 [0, max_num] 内的随机数字序列，
    以 list 形式返回, 参数 row, col 只是因为 rpc 的接口参数需要'''
    try:
        if type(max_num) != int or max_num <= 0 or max_num > 25:
            return (-1, )

        _socket = TSocket.TSocket(remote_ip, remote_port)
        _socket.setTimeout(500)
        transport = TTransport.TBufferedTransport(_socket)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        client = EightDigital.Client(protocol)

        chess = ''
        for i in xrange(1, max_num + 1):
            if i < 10:
                chess += str(i)
            else:
                chess += chr(ord('a') + (i - 10))
        chess += '0'
        start = EightDigital.EDState(chess=chess, row=row, col=col)
        
        transport.open()
        retRandomState = client.getRandomState(start, custom_steps[row * col][0])
        transport.close()

        if retRandomState.res.code == 0:
            ll = []
            for c in retRandomState.randomState.chess:
                d = int(c) if c.isdigit() else ord(c) - ord('a') + 10
                ll.append(d - 1)
            ll[ll.index(-1)] = max_num
            return (0, ll)
        else:
            return (retRandomState.res.code, retRandomState.res.msg)

    except Thrift.TException, ex:
        if str(ex).find('Could not connect to ') != -1:
            ex = '无法连接到服务器'
        return (-2, ex)
    except socket.timeout, ex:
        return (-3, ex)
    except socket.error, ex:
        return (-4, ex)
    except Exception, ex:
        return (-5, ex)
    except:
        return (-6, 'unkown exception')
    finally:
        transport.close()   # must close manually

def rpcSolution(listChess, row, col, msWaitTime=1000):
    '''通过 EightDigital 的 getSolution 接口获取结果，参数 listChess 为 [3, 7, 8, 0, 2,..., ] 形式的list，row 和 col 分别为行和列'''
    try:
        if type(listChess) != list:
            return (-1, )

        _socket = TSocket.TSocket(remote_ip, remote_port)
        _socket.setTimeout(5000)
        transport = TTransport.TBufferedTransport(_socket)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        client = EightDigital.Client(protocol)

        listChess = copy.deepcopy(listChess)
        for i in xrange(len(listChess)):
            listChess[i] += 1
        listChess[listChess.index(row * col)] = 0
        strChess = ''
        for d in listChess:
            c = str(d) if d < 10 else chr(ord('a') + (d - 10))
            strChess += str(c)
        start = EightDigital.EDState(chess=strChess, row=row, col=col)
        strChess = ''
        for i in xrange(1, row * col):
            c = str(i) if i < 10 else chr(ord('a') + (i - 10))
            strChess += c
        strChess += '0'
        end = EightDigital.EDState(chess=strChess, row=row, col=col)

        transport.open()
        retSolution = client.getSolution(start, end, msWaitTime)
        transport.close()

        if retSolution.res.code == 0:
            return (0, retSolution.directions)
        else:
            return (retSolution.res.code, retSolution.res.msg)

    except Thrift.TException, ex:
        if str(ex).find('Could not connect to ') != -1:
            ex = '无法连接到服务器'
        return (-2, ex)
    except socket.timeout, ex:
        return (-3, ex)
    except socket.error, ex:
        return (-4, ex)
    except Exception, ex:
        return (-5, ex)
    except:
        return (-6, 'unkown exception')
    finally:
        transport.close()   # must close manually


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


def isDirectInverse(x, y):
    if type(x) != int or type(y) != int:
        return False
    if x > y:
        x, y = y, x
    if x % 2 == 0:
        return y == x + 1
    return False


def simplifyDirection(listDirections):
    if type(listDirections) != list:
        raise Exception("not list!")
    after = []
    cur_idx = 0
    while cur_idx < len(listDirections):
        if cur_idx + 1 < len(listDirections) and isDirectInverse(listDirections[cur_idx], listDirections[cur_idx + 1]):
            cur_idx += 2
        else:
            after.append(listDirections[cur_idx])
            cur_idx += 1
    if len(after) == len(listDirections):
        return after
    else:
        return simplifyDirection(after)


def isImage(img):
    ext_name = os.path.splitext(img)[1]
    ext_name = ext_name[1:]
    if ext_name in ['rgb','gif','pbm','pgm','ppm','tiff','rast','xbm','jpeg','jpg','bmp','png',
                    'RGB','GIF','PBM','PGM','PPM','TIFF','RAST','XBM','JPEG','JPG','BMP','PNG']:
        return True
    else:
        return False


class RowAndCol(QDialog):
    """docstring for RowAndCol"""
    def __init__(self, _row, _col, title=u"设置拼图的行和列", *args, **kwargs):
        super(RowAndCol, self).__init__(*args, **kwargs)
        self.setWindowTitle(title)
        grid = QGridLayout(self)
        lbl = QLabel(u'行数(2~5)：')
        grid.addWidget(lbl, 0, 0)
        self.sbRow = QSpinBox()
        self.sbRow.setRange(2, 5)
        self.sbRow.setValue(_row)
        grid.addWidget(self.sbRow, 0, 1, 1, 2)
        lbl = QLabel(u'列数(2~5)：')
        grid.addWidget(lbl, 1, 0)
        self.sbCol = QSpinBox()
        self.sbCol.setRange(2, 5)
        self.sbCol.setValue(_col)
        grid.addWidget(self.sbCol, 1, 1, 1, 2)
        grid.setColumnStretch(1, 1)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        grid.addWidget(buttons, 2, 2)

    @staticmethod
    def getRowAndCol(_row=3, _col=3):
        dialog = RowAndCol(_row, _col)
        res = dialog.exec_()
        return (res, (dialog.sbRow.value(), dialog.sbCol.value()))


class ImageLabel(QLabel):
    """docstring for ImageLabel"""
    def __init__(self, rowId=-1, colId=-1, *args, **kwargs):
        super(ImageLabel, self).__init__(*args, **kwargs)
        self.setScaledContents(True)
        self.rowId = rowId
        self.colId = colId

    def setImage(self, img):
        pixmap = QPixmap.fromImage(img.scaled(self.width(), self.height()))
        self.setPixmap(pixmap)

    def mousePressEvent(self, event):
        self.emit(SIGNAL('clicked(PyQt_PyObject)'), self)


class PuzzleGame(QMainWindow):

    image_dir = QString(u'')
    origin_image_file = './images/plate.jpg'

    def __init__(self, title=u"拼图游戏"):
        super(PuzzleGame, self).__init__()
        self.initSelf(title)
        self.initUI()

    def initSelf(self, title):
        self.setWindowTitle(title)
        self.showOnCenter()

    def initUI(self):
        self.statusbar = self.statusBar()
        self.initBoard()
        self.initMenu()

    def initMenu(self):
        self.menubar = self.menuBar()
        menuOpt = self.menubar.addMenu(u'设置')
        actSelectImage = QAction(u'选择图片', self)
        actSelectImage.setShortcut('ctrl+I')
        actSelectImage.triggered.connect(self.selectImage)
        menuOpt.addAction(actSelectImage)
        actSetRowAndCol = QAction(u'设置行列数', self)
        actSetRowAndCol.setShortcut('ctrl+P')
        actSetRowAndCol.triggered.connect(self.setRowAndCol)
        menuOpt.addAction(actSetRowAndCol)
        menuHelp = self.menubar.addMenu(u'帮助')
        actAutoPuzzle = QAction(u'自动拼图', self)
        actAutoPuzzle.setShortcut('ctrl+H')
        actAutoPuzzle.triggered.connect(self.autoPuzzle)
        menuHelp.addAction(actAutoPuzzle)

        actDebug = QAction(u'debug', self)
        actDebug.setShortcut('ctrl+d')
        actDebug.triggered.connect(self.mydebug)
        # menuHelp.addAction(actDebug)
        self.mydebug_count = True

    def mydebug(self):
        if self.mydebug_count == True:
            self.mydebug_count = False
        else:
            self.mydebug_count = True

    def autoPuzzle(self):
        if hasattr(self, 'actionIgnore') and self.actionIgnore == True:
            return
        if hasattr(self, 'autoPuzzleIgnore') and self.autoPuzzleIgnore == True:
            return
        self.statusbar.showMessage(u'请稍等，正在向远端请求....')
        ret = rpcSolution(self.rand_labelIds, self.row, self.col)
        if ret[0] != 0:
            # print "before:", self.stepRecords
            self.stepRecords = simplifyDirection(self.stepRecords)
            # print "after:", self.stepRecords
            reverse_stepRecords = []
            for i in xrange(len(self.stepRecords) - 1, -1, -1):
                d = self.stepRecords[i] + 1 if self.stepRecords[i] % 2 == 0 else self.stepRecords[i] - 1
                reverse_stepRecords.append(d)
            ret = rpcSolution(self.origin_lableIds, self.row, self.col)
            if ret[0] != 0:
                qstr = QString(str('很抱歉，电脑无法找到可行路径o(╯□╰)o，错误详情：' + str(ret[1])).decode('utf8'))
                self.statusbar.showMessage(qstr)
                return
            ret = (0, reverse_stepRecords + ret[1])
        self.directions = ret[1]
        # print 'self.directions:', self.directions
        self.timer = QBasicTimer()
        self.mouseIgnore = True
        self.keyIgnore = True
        self.actionIgnore = True
        self.autoPuzzleIgnore = True
        self.timer.start(500, self)

    def timerEvent(self, event):
        if hasattr(self, 'timer') and event.timerId() == self.timer.timerId():
            if len(self.directions) == 0:
                self.stepRecords = []       # 要在这里才清空的！
                self.timer.stop()
                self.mouseIgnore = False
                self.keyIgnore = False
                self.actionIgnore = False
                self.autoPuzzleIgnore = False
                return
            self.statusbar.showMessage(u'自动拼图中....')
            direct = self.directions[0]
            if direct == 0:
                self.moveUp()
            elif direct == 1:
                self.moveDown()
            elif direct == 2:
                self.moveLeft()
            elif direct == 3:
                self.moveRight()
            self.judgeComplete()
            self.directions.remove(self.directions[0])
        elif hasattr(self, 'final_block_timer') and event.timerId() == self.final_block_timer.timerId():
            self.completePuzzle()
            self.final_block_timer.stop()
        elif hasattr(self, 'statusbar_timer') and event.timerId() == self.statusbar_timer.timerId():
            pass
        else:
            super(PuzzleGame, self).timerEvent(event)

    def selectImage(self):
        if hasattr(self, 'actionIgnore') and self.actionIgnore == True:
            return
        image_file = QFileDialog.getOpenFileName(caption=u'请选择拼图的图片：', directory=PuzzleGame.image_dir)
        if image_file != '':
            if self.loadImage(str(image_file.toUtf8())) == True:
                self.myRender()
                PuzzleGame.image_dir = QFileInfo(image_file).path()
                return True
        return False

    def setRowAndCol(self):
        if hasattr(self, 'actionIgnore') and self.actionIgnore == True:
            return
        res = RowAndCol.getRowAndCol()
        if res[0] == QDialog.Accepted:
            _row, _col = res[1]
            self.initBoard(_row, _col, loadImg=False)

    def initBoard(self, row=2, col=2, isRandom=True, loadImg=True):
        self.board = QWidget()
        self.loadLabel(row, col, isRandom)
        self.setCentralWidget(self.board)
        if loadImg == True:
            if os.path.isfile(PuzzleGame.origin_image_file):
                self.loadImage(PuzzleGame.origin_image_file)
            else:
                if self.selectImage() == False:
                    QMessageBox.information(self, u'再见', u'需要选择好任意一张图片才能进行游戏的哦～')
                    sys.exit(0)
                return
        if loadImg == True:
            self.myRender()
        else:
            self.myRender(labelOnly=True)
        self.stepRecords = []
        self.origin_lableIds = copy.deepcopy(self.rand_labelIds)
        if isRandom == True:
            self.statusbar.showMessage(u'')

    def loadLabel(self, row, col, isRandom=True):
        self.row = row
        self.col = col
        self.lables = []
        self.grid = QGridLayout()
        self.grid.setMargin(1)
        self.grid.setSpacing(1)
        for r in range(0, self.row):
            for c in range(0, self.col):
                lbl = ImageLabel(r, c)
                self.connect(lbl, SIGNAL("clicked(PyQt_PyObject)"), self.judgeMove)
                lbl.num = r * self.col + c
                self.lables.append(lbl)
        self.max_num = self.row * self.col - 1
        if isRandom == True:
            ret = rpcRandNums(self.max_num, self.row, self.col)
            if ret[0] == 0:
                self.rand_labelIds = ret[1]
            else:
                self.rand_labelIds = randNums(0, self.max_num - 1)
                self.rand_labelIds.append(self.max_num)  #
        else:
            self.rand_labelIds = [i for i in xrange(self.max_num + 1)]
        for i in xrange(len(self.rand_labelIds)):
            self.grid.addWidget(self.lables[self.rand_labelIds[i]], i / self.col, i % self.col)
        if isRandom == True:
            self.lables[-1].hide()          # 有些bug无论怎样也搞不清楚，只能避开
        self.board.setLayout(self.grid)

    def judgeMove(self, label):
        if hasattr(self, 'mouseIgnore') and self.mouseIgnore == True:
            return
        index = self.rand_labelIds.index(label.num)
        if index % self.col != 0 and self.rand_labelIds[index - 1] == self.max_num:
            self.moveLeft()
        elif (index + 1) % self.col != 0 and self.rand_labelIds[index + 1] == self.max_num:
            self.moveRight()
        elif index >= self.col and self.rand_labelIds[index - self.col] == self.max_num:
            self.moveUp()
        elif index + self.col <= self.max_num and self.rand_labelIds[index + self.col] == self.max_num:
            self.moveDown()
        self.judgeComplete()

    def loadImage(self, img):
        if not os.path.exists(img):
            QMessageBox.warning(self, u'文件不存在', u'文件不存在！')
            return False
        if isImage(img) == False:
            QMessageBox.warning(self, u'获取图片失败', u'选择的文件不是图片类型')
            return False
        img = QString(img.decode('utf8'))
        self.image = QImage(img)
        self.setWindowIcon(QIcon(img))
        self.hide()
        self.show()
        return True

    def myRender(self, labelOnly=False):
        img_width = self.image.width() / self.col
        img_height = self.image.height() / self.row
        if labelOnly == True:
            for lbl in self.lables:
                lbl.setImage(self.image.copy(img_width * lbl.colId, img_height * lbl.rowId, img_width, img_height))
        else:
            self.board.setMinimumSize(self.image.width(), self.image.height())
            self.board.setMaximumSize(self.image.width(), self.image.height())
            self.setMinimumWidth(self.board.width())
            self.setMinimumHeight(self.board.height() + self.statusbar.height())
            self.setMaximumWidth(self.board.width())
            self.setMaximumHeight(self.board.height() + self.statusbar.height())
            for lbl in self.lables:
                lbl.setImage(self.image.copy(img_width * lbl.colId, img_height * lbl.rowId, img_width, img_height))
            self.showOnCenter()

    def keyPressEvent(self, event):
        if hasattr(self, 'keyIgnore') and self.keyIgnore == True:
            return
        key = event.key()  # 捕获按键
        if key == Qt.Key_Up or key == Qt.Key_W:
            self.moveUp()
        elif key == Qt.Key_Down or key == Qt.Key_S:
            self.moveDown()
        elif key == Qt.Key_Left or key == Qt.Key_A:
            self.moveLeft()
        elif key == Qt.Key_Right or key == Qt.Key_D:
            self.moveRight()
        else:
            super(PuzzleGame, self).keyPressEvent(event)
            return
        self.judgeComplete()

    def completePuzzle(self):
        self.statusbar.showMessage(u'已完成拼图')
        reply = QMessageBox.question(self, u'拼图完成', u'恭喜，已拼成原图，很厉害哦～是否进入下一轮？', u'进入下一轮', u'再玩一次', u'退出游戏')
        if reply == 2:
            self.close()
            QMessageBox.information(self, u'再见', u'期待下次再见~')
        elif reply == 1:
            self.initBoard(self.row, self.col, loadImg=False)
        elif reply == 0:
            rowIncrease = True
            if self.row >= self.col:
                rowIncrease = False
            increase = min(min(self.row, self.col) + 1, 5)
            if rowIncrease == True:
                self.initBoard(increase, self.col, loadImg=False)
            else:
                self.initBoard(self.row, increase, loadImg=False)
        self.mouseIgnore = False
        self.keyIgnore = False
        self.actionIgnore = False
        self.autoPuzzleIgnore = False

    def judgeComplete(self):
        if self.rand_labelIds == sorted(self.rand_labelIds):
            
            self.mouseIgnore = True
            self.keyIgnore = True
            self.actionIgnore = True
            self.autoPuzzleIgnore = True

            self.final_block = ImageLabel(self.row - 1, self.col - 1)
            img_width = self.image.width() / self.col
            img_height = self.image.height() / self.row
            self.final_block.setImage(self.image.copy(img_width * self.final_block.colId, img_height * self.final_block.rowId, img_width, img_height))
            self.grid.addWidget(self.final_block, self.final_block.rowId, self.final_block.colId)
            self.final_block_timer = QBasicTimer()
            self.final_block_timer.start(200, self)
            # self.initBoard(self.row, self.col, isRandom=False,loadImg=False)  # 不熟悉 QGridLayout，只好这样来重新加载所有标签块了

    def moveUp(self):
        blank_idx = self.rand_labelIds.index(self.max_num)
        if blank_idx + self.col <= self.max_num:
            self.grid.addWidget(self.lables[self.rand_labelIds[blank_idx + self.col]], blank_idx / self.col, blank_idx % self.col)
            self.rand_labelIds[blank_idx], self.rand_labelIds[blank_idx + self.col] = self.rand_labelIds[blank_idx + self.col], self.rand_labelIds[blank_idx]
            self.stepRecords.append(0)

    def moveDown(self):
        blank_idx = self.rand_labelIds.index(self.max_num)
        if blank_idx >= self.col:
            self.grid.addWidget(self.lables[self.rand_labelIds[blank_idx - self.col]], blank_idx / self.col, blank_idx % self.col)
            self.rand_labelIds[blank_idx], self.rand_labelIds[blank_idx - self.col] = self.rand_labelIds[blank_idx - self.col], self.rand_labelIds[blank_idx]
            self.stepRecords.append(1)

    def moveLeft(self):
        blank_idx = self.rand_labelIds.index(self.max_num)
        if (blank_idx + 1) % self.col != 0:
            self.grid.addWidget(self.lables[self.rand_labelIds[blank_idx + 1]], blank_idx / self.col, blank_idx % self.col)
            self.rand_labelIds[blank_idx], self.rand_labelIds[blank_idx + 1] = self.rand_labelIds[blank_idx + 1], self.rand_labelIds[blank_idx]
            self.stepRecords.append(2)

    def moveRight(self):
        blank_idx = self.rand_labelIds.index(self.max_num)
        if blank_idx % self.col != 0:
            self.grid.addWidget(self.lables[self.rand_labelIds[blank_idx - 1]], blank_idx / self.col, blank_idx % self.col)
            self.rand_labelIds[blank_idx], self.rand_labelIds[blank_idx - 1] = self.rand_labelIds[blank_idx - 1], self.rand_labelIds[blank_idx]
            self.stepRecords.append(3)

    def showOnCenter(self):
        screen = QDesktopWidget().screenGeometry()
        self.move((screen.width() - self.width()) / 2,
                  (screen.height() - self.height()) / 2)

    def closeEvent(self, event):
        pass


def main():
    app = QApplication(sys.argv)
    w = PuzzleGame()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
