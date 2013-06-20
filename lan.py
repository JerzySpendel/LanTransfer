from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys,os
from main import Ui_MainWindow
from selectwidget import Ui_Form
from streamwidget import Ui_Form as Stream_Form
from downloadwidget import Ui_Form as DStream_Form
from UploadProcess import UploadProcess as UP
from UploadProcess import DownloadProcess as DP
class StreamWidget(QWidget):
    def __init__(self,parent=None):
        QWidget.__init__(self,parent)
        self.uploadthread = UP()
        self.parent = parent
        self.ui = Stream_Form()
        self.ui.setupUi(self)
        self.initSignals()
        self.show()
    def filedialog(self):
        dialog = QFileDialog()
        self.path = dialog.getOpenFileName()
        self.ui.lineEdit.setText(self.path)
    def stream(self):
        path = self.ui.lineEdit.text()
        self.uploadthread.config(path)
        print('stream started')
        self.uploadthread.start()
    def initSignals(self):
        QObject.connect(self.ui.pushButton,SIGNAL('clicked()'),self.filedialog)
        QObject.connect(self.ui.pushButton_2,SIGNAL('clicked()'),self.stream)
class DownloadWidget(QWidget):
    def __init__(self,parent=None):
        QWidget.__init__(self,parent)
        self.ui = DStream_Form()
        self.downloadthread = DP()
        self.ui.setupUi(self)
        self.initSignals()
    def filedialog(self):
        dialog = QFileDialog()
        self.path = dialog.getOpenFileName()
        self.ui.label_3.setText(str(self.path))
    def download(self):
        self.downloadthread.config(self.ui.lineEdit.text())
        self.downloadthread.start()
    def initSignals(self):
        QObject.connect(self.ui.pushButton_2,SIGNAL('clicked()'),self.filedialog)
        QObject.connect(self.ui.pushButton,SIGNAL('clicked()'),self.download)
class SelectWidget(QWidget):
    def __init__(self,parent=None):
        QWidget.__init__(self,parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
    def test(self):
        print("test")


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.select = SelectWidget(self.ui.formLayoutWidget)
        self.initSignals()
        self.show()
    def changeToUploadMode(self):
        self.select.setParent(None)
        self.select = StreamWidget(self.ui.formLayoutWidget)
        self.select.show()
    def changeToDownloadMode(self):
        self.select.setParent(None)
        self.select = DownloadWidget(self.ui.formLayoutWidget)
        self.select.show()
    def changeToMainMode(self):
        self.select.setParent(None)
        self.select = SelectWidget(self.ui.formLayoutWidget)
        self.select.show()
        self.ui.formLayoutWidget.update()
        self.initSignals()
    def setPath(self):
        pass
    def initSignals(self):
        QObject.connect(self.select.ui.pushButton,SIGNAL('clicked()'),self.changeToUploadMode)
        QObject.connect(self.select.ui.pushButton_2,SIGNAL('clicked()'),self.changeToDownloadMode)
        QObject.connect(self.ui.pushButton,SIGNAL('clicked()'),self.changeToMainMode)
app = QApplication(sys.argv)
okienko = MainWindow()
app.exec_()