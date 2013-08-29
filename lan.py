__author__ = 'Jerzy Spendel'

import sys
import re
from Utils import Config
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from gui.main import Ui_MainWindow
from gui.selectwidget import Ui_Form
from gui.streamwidget import Ui_Form as Stream_Form
from gui.downloadwidget import Ui_Form as DStream_Form
from gui.aboutwidget import Ui_Form as About_Form
from gui.optionswidget import Ui_Form as Options_Form
from gui.generalsettingswidget import Ui_Form as GeneralSettings_Form
from gui.networksettingswidget import Ui_Form as NetworkSettings_Form
from NetProcesses import UploadProcess as UP
from NetProcesses import DownloadProcess as DP

class StreamWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
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

    def updatePercent(self, msg):
        self.ui.progressBar.setValue(msg)
        self.ui.progressBar.update()

    def makeBusy(self):
        self.ui.progressBar.setMinimum(0)
        self.ui.progressBar.setMaximum(0)
        self.ui.progressBar.update()

    def unmakeBusy(self):
        self.ui.progressBar.setMinimum(0)
        self.ui.progressBar.setMaximum(100)
        self.ui.progressBar.update()

    def initSignals(self):
        QObject.connect(self.ui.pushButton, SIGNAL('clicked()'), self.filedialog)
        QObject.connect(self.ui.pushButton_2, SIGNAL('clicked()'), self.stream)
        QObject.connect(self.uploadthread, SIGNAL('updatePercent(int)'), self.updatePercent)
        QObject.connect(self.uploadthread,SIGNAL('makeBusy()'), self.makeBusy)
        QObject.connect(self.uploadthread, SIGNAL('unmakeBusy()'), self.unmakeBusy)


class DownloadWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.ui = DStream_Form()
        self.downloadthread = DP()
        self.ui.setupUi(self)
        self.completer = None
        self.initUi()
        self.initSignals()

    def initUi(self):
        self.initModel()
        self.initCompleter()
        self.ui.listView.setModel(self.model)

    def initModel(self):
        words = []
        for contact in Config.openContacts():
            words.append(contact[1])
        self.model = QStringListModel(words)
    def initCompleter(self):
        self.completer = QCompleter(None, self.ui.lineEdit)
        self.completer.setModel(self.model)
        self.ui.lineEdit.setCompleter(self.completer)

    def setpath(self):
        dialog = QFileDialog()
        self.path = dialog.getExistingDirectory(self,'Select Directory')
        self.ui.label_3.setText(str(self.path))
        self.downloadthread.config(self.ui.lineEdit.text(), folderpath=self.path)

    def setfile(self):
        dialog = QFileDialog()
        self.filepath = dialog.getOpenFileName()

    def download(self):
        self.downloadthread.config(self.ui.lineEdit.text())
        self.downloadthread.start()

    def percentUpdate(self, msg):
        self.ui.progressBar.setValue(msg)
        self.ui.progressBar.update()

    def speedUpdate(self, msg):
        self.speed = msg
        self.ui.label_3.setText('<span style="color: green;">'+str(msg)+' kbps'+"</span>")

    def timeUpdate(self, msg):
        self.time = msg
        self.ui.label_4.setText('Time left: ' + str(self.time) + ' seconds')

    def test(self, msg):
        print(msg)

    def setIp(self,index):
        name = index.data(Qt.DisplayRole)
        ip = None
        for contact in Config.openContacts():
            if contact[1] == name:
                ip = contact[0]
        if ip is not None:
            self.ui.lineEdit.setText(ip)
        else:
            print('Couldn\'t get ip')
    def initSignals(self):
        QObject.connect(self.ui.pushButton_2, SIGNAL('clicked()'), self.setpath)
        QObject.connect(self.ui.pushButton_3, SIGNAL('clicked()'), self.setfile)
        QObject.connect(self.ui.pushButton, SIGNAL('clicked()'), self.download)
        QObject.connect(self.downloadthread.DM, SIGNAL('percentUpdate(int)'), self.percentUpdate)
        QObject.connect(self.downloadthread.DM, SIGNAL('timeUpdate(PyQt_PyObject)'), self.timeUpdate)
        QObject.connect(self.downloadthread.DM, SIGNAL('speedUpdate(int)'), self.speedUpdate)
        QObject.connect(self.completer, SIGNAL('activated(QString)'), self.test)
        QObject.connect(self.ui.listView, SIGNAL('clicked(QModelIndex)'),self.setIp)
class SelectWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)


class AboutWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.ui = About_Form()
        self.ui.setupUi(self)
        l = QLabel(self.ui.widget)
        print(self.ui.widget.width)
        pixmap = QPixmap(Config.data['GNU_PNG'])
        pixmap = pixmap.scaled(QSize(self.ui.widget.width(),self.ui.widget.height()))
        l.setPixmap(pixmap)
        self.initSignals()
        self.show()
        self.setWindowTitle('About')
    def close(self):
        self.hide()
        self.setParent(None)


    def initSignals(self):
        QObject.connect(self.ui.pushButton, SIGNAL('clicked()'), self.close)


class OptionsWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self,parent)
        self.ui = Options_Form()
        self.ui.setupUi(self)
        self.initUi()
        self.initSignals()
        self.show()

    def initUi(self):
        self.general = GeneralSettings()
        self.network = NetworkSettings()

        self.tab = self.general

        self.tab.setParent(self.ui.widget_2)

        self.ui.pushButton_2.setIcon(QIcon(Config.data['GENERAL_SETTINGS']))
        self.ui.pushButton_3.setIcon(QIcon(Config.data['NETWORK_SETTINGS']))
        QObject.connect(self.ui.pushButton_2, SIGNAL('clicked()'), self.generalsettings)
        QObject.connect(self.ui.pushButton_3, SIGNAL('clicked()'), self.networksettings)

        self.setWindowTitle('Options')
    def generalsettings(self):
        self.tab.setParent(None)
        self.tab = self.general
        self.tab.setParent(self.ui.widget_2)
        self.tab.show()

    def networksettings(self):
        self.tab.setParent(None)
        self.tab = self.network
        self.tab.setParent(self.ui.widget_2)
        self.tab.show()

    def save(self):
        threads = self.general.ui.horizontalSlider.sliderPosition()
        chunksize = self.general.ui.lineEdit.text()
        downspeed = self.network.ui.lineEdit_2.text()
        upspeed = self.network.ui.lineEdit_3.text()

        #Saving each property to file :)
        Config.changeProperty('THREADS', threads)
        Config.changeProperty('CHUNK_SIZE', chunksize)
        Config.changeProperty('DOWNLOAD_MAX',downspeed)
        Config.changeProperty('UPLOAD_MAX', upspeed)

        Config.saveContacts(self.general.ui.plainTextEdit.toPlainText())
        self.hide()
    def initSignals(self):
        QObject.connect(self.ui.pushButton, SIGNAL('clicked()'), self.save)

class GeneralSettings(QWidget):
    def __init__(self,parent=None):
        QWidget.__init__(self,parent)
        self.ui = GeneralSettings_Form()
        self.ui.setupUi(self)
        self.initUi()

    def initUi(self):
        self.makeContacts()
        self.makeThreads()
        self.makeChunksize()
        QObject.connect(self.ui.horizontalSlider, SIGNAL('sliderMoved(int)'), self.sliderMoved)
        QObject.connect(self.ui.plainTextEdit, SIGNAL('textChanged()'),self.textchanged)

    def textchanged(self):
        defaultText = """xxx.xxx.xxx.xxx - NAME (xses are IP address)

Each recipient has to be declared in new line. If you understand this than clear this box and fill it with your buddies :)
Example:
212.106.166.37 - Jerzy Spendel"""
        if self.ui.plainTextEdit.toPlainText() == '':
            pass
        elif self.ui.plainTextEdit.toPlainText() != defaultText:
            pass

    def sliderMoved(self,msg):
        self.ui.label_4.setText(str(msg))

    def makeContacts(self):
        text = ''
        for pair in Config.openContacts():
            text = text+pair[0]+' - '+pair[1]+'\n'
        self.ui.plainTextEdit.setPlainText(text)

    def makeThreads(self):
        self.ui.horizontalSlider.setValue(int(Config.data['THREADS']))
        self.ui.label_4.setText(Config.data['THREADS'])

    def makeChunksize(self):
        self.ui.lineEdit.setText(Config.data['CHUNK_SIZE'])

class NetworkSettings(QWidget):
    def __init__(self,parent=None):
        QWidget.__init__(self,parent)
        self.ui = NetworkSettings_Form()
        self.ui.setupUi(self)
        self.initUi()

    def initUi(self):
        self.makeUpSpeed()
        self.makeDownSpeed()

    def makeUpSpeed(self):
        self.ui.lineEdit_3.setText(str(Config.data['UPLOAD_MAX']))

    def makeDownSpeed(self):
        self.ui.lineEdit_2.setText(str(Config.data['DOWNLOAD_MAX']))

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.select = SelectWidget(self.ui.formLayoutWidget)
        self.initSignals()
        self.setupUi()
        self.show()

    def setupUi(self):
        self.toolBar = QToolBar(self)
        self.toolBar.setGeometry(QRect(0, 0, 300, 26))
        exitAction = QAction(QIcon(Config.data['EXIT_PNG']), 'Exit', self)
        exitAction.triggered.connect(qApp.exit)
        self.toolBar.addAction(exitAction)
        self.toolBar.addSeparator()

        configureAction = QAction(QIcon(Config.data['CONFIGURE_PNG']), 'Configure', self)
        configureAction.triggered.connect(self.options)
        self.toolBar.addAction(configureAction)
        self.toolBar.addSeparator()

        aboutAction = QAction(QIcon(Config.data['ABOUT_PNG']), 'About', self)
        aboutAction.triggered.connect(self.about)
        self.toolBar.addAction(aboutAction)

        self.setWindowTitle('LanTransfer')
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

    def about(self):
        self.ab = AboutWidget()
        print('about...')

    def options(self):
        self.opt = OptionsWidget()
        print('Options...')

    def initSignals(self):
        QObject.connect(self.select.ui.pushButton, SIGNAL('clicked()'), self.changeToUploadMode)
        QObject.connect(self.select.ui.pushButton_2, SIGNAL('clicked()'), self.changeToDownloadMode)
        QObject.connect(self.ui.pushButton, SIGNAL('clicked()'), self.changeToMainMode)
        QObject.connect(self.ui.actionAbout_this_program, SIGNAL('triggered()'), self.about)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    okienko = MainWindow()
    app.exec_()