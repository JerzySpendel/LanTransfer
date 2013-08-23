# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'network_settings.ui'
#
# Created: Thu Aug 22 18:55:23 2013
#      by: PyQt4 UI code generator 4.10.2
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
        Form.resize(361, 201)
        self.frame = QtGui.QFrame(Form)
        self.frame.setGeometry(QtCore.QRect(0, 0, 361, 201))
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.label_3 = QtGui.QLabel(self.frame)
        self.label_3.setGeometry(QtCore.QRect(10, 10, 151, 21))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.label_5 = QtGui.QLabel(self.frame)
        self.label_5.setGeometry(QtCore.QRect(10, 50, 151, 21))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.lineEdit_3 = QtGui.QLineEdit(self.frame)
        self.lineEdit_3.setGeometry(QtCore.QRect(170, 50, 161, 21))
        self.lineEdit_3.setObjectName(_fromUtf8("lineEdit_3"))
        self.lineEdit_2 = QtGui.QLineEdit(self.frame)
        self.lineEdit_2.setGeometry(QtCore.QRect(170, 10, 161, 21))
        self.lineEdit_2.setObjectName(_fromUtf8("lineEdit_2"))

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.label_3.setText(_translate("Form", "Download speed limit:", None))
        self.label_5.setText(_translate("Form", "Upload speed limit:", None))

