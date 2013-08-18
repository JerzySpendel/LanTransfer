__author__ = 'Jerzy Spendel'

import sys
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
        self.initSignals()

    def setpath(self):
        dialog = QFileDialog()
        self.path = dialog.getExistingDirectory(self,'Select Directory')
        self.ui.label_3.setText(str(self.path))
        self.downloadthread.config(self.ui.lineEdit.text(), path=self.path)

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
        self.ui.label_3.setText(str(msg)+' kbps')
    def timeUpdate(self, msg):
        self.time = msg
        self.ui.label_4.setText('Time left: ' + str(self.time) + ' seconds')

    def initSignals(self):
        QObject.connect(self.ui.pushButton_2, SIGNAL('clicked()'), self.setpath)
        QObject.connect(self.ui.pushButton_3, SIGNAL('clicked()'), self.setfile)
        QObject.connect(self.ui.pushButton, SIGNAL('clicked()'), self.download)
        QObject.connect(self.downloadthread.DM, SIGNAL('percentUpdate(int)'), self.percentUpdate)
        QObject.connect(self.downloadthread.DM, SIGNAL('timeUpdate(PyQt_PyObject)'), self.timeUpdate)
        QObject.connect(self.downloadthread.DM, SIGNAL('speedUpdate(int)'), self.speedUpdate)


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
        self.tab = GeneralSettings()

        self.tab.setParent(self.ui.widget_2)

        self.ui.pushButton_2.setIcon(QIcon(Config.data['GENERAL_SETTINGS']))
        self.ui.pushButton_3.setIcon(QIcon(Config.data['NETWORK_SETTINGS']))
        QObject.connect(self.ui.pushButton_2, SIGNAL('clicked()'), self.generalsettings)
        QObject.connect(self.ui.pushButton_3, SIGNAL('clicked()'), self.networksettings)

    def generalsettings(self):
        self.tab.setParent(None)
        self.tab = GeneralSettings(self.ui.widget_2)
        self.tab.show()

    def networksettings(self):
        self.tab.setParent(None)
        self.tab = NetworkSettings(self.ui.widget_2)
        self.tab.show()


    def updateAll(self):
        self.general.update()
        self.network.update()
        self.ui.widget_2.update()
        self.ui.widget_2.repaint()

    def close(self):
        pass
    def initSignals(self):
        QObject.connect(self.ui.pushButton, SIGNAL('clicked'), self.close)


class GeneralSettings(QWidget):
    def __init__(self,parent=None):
        QWidget.__init__(self,parent)
        self.ui = GeneralSettings_Form()
        self.ui.setupUi(self)


class NetworkSettings(QWidget):
    def __init__(self,parent=None):
        QWidget.__init__(self,parent)
        self.ui = NetworkSettings_Form()
        self.ui.setupUi(self)


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
    Config.init()
    app = QApplication(sys.argv)
    okienko = MainWindow()
    app.exec_()