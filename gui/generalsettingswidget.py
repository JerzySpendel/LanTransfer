# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'general_settings.ui'
#
# Created: Thu Aug 29 12:40:33 2013
#      by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(362, 232)
        self.frame = QtGui.QFrame(Form)
        self.frame.setGeometry(QtCore.QRect(0, 0, 361, 231))
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.label = QtGui.QLabel(self.frame)
        self.label.setEnabled(True)
        self.label.setGeometry(QtCore.QRect(10, 10, 141, 20))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(self.frame)
        self.label_2.setGeometry(QtCore.QRect(10, 40, 141, 21))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalSlider = QtGui.QSlider(self.frame)
        self.horizontalSlider.setGeometry(QtCore.QRect(170, 10, 161, 21))
        self.horizontalSlider.setMinimum(1)
        self.horizontalSlider.setMaximum(10)
        self.horizontalSlider.setProperty("value", 1)
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName(_fromUtf8("horizontalSlider"))
        self.lineEdit = QtGui.QLineEdit(self.frame)
        self.lineEdit.setGeometry(QtCore.QRect(170, 40, 161, 21))
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.label_4 = QtGui.QLabel(self.frame)
        self.label_4.setGeometry(QtCore.QRect(340, 10, 16, 20))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.label_3 = QtGui.QLabel(self.frame)
        self.label_3.setGeometry(QtCore.QRect(10, 100, 331, 16))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.plainTextEdit = QtGui.QPlainTextEdit(self.frame)
        self.plainTextEdit.setGeometry(QtCore.QRect(10, 120, 321, 101))
        self.plainTextEdit.setObjectName(_fromUtf8("plainTextEdit"))
        self.checkBox = QtGui.QCheckBox(self.frame)
        self.checkBox.setGeometry(QtCore.QRect(170, 70, 21, 19))
        self.checkBox.setText(_fromUtf8(""))
        self.checkBox.setObjectName(_fromUtf8("checkBox"))
        self.label_5 = QtGui.QLabel(self.frame)
        self.label_5.setGeometry(QtCore.QRect(10, 70, 131, 16))
        self.label_5.setObjectName(_fromUtf8("label_5"))

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.label.setText(_translate("Form", "Max amount of threads:", None))
        self.label_2.setText(_translate("Form", "Size of chunk (in bytes): ", None))
        self.lineEdit.setText(_translate("Form", "1024", None))
        self.label_4.setText(_translate("Form", "1", None))
        self.label_3.setText(_translate("Form", "Contact list (save here your most common recipients):", None))
        self.plainTextEdit.setPlainText(_translate("Form", "xxx.xxx.xxx.xxx - NAME (xses are IP address)\n"
"\n"
"Each recipient has to be declared in new line. If you understand this than clear this box and fill it with your buddies :)\n"
"Example:\n"
"212.106.166.37 - Jerzy Spendel", None))
        self.label_5.setText(_translate("Form", "Compress files", None))

