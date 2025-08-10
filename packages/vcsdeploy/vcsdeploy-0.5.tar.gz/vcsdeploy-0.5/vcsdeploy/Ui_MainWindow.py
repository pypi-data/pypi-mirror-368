# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/antocuni/pypy/misc/vcsdeploy/vcsdeploy/MainWindow.ui'
#
# Created: Fri Apr 13 11:44:44 2012
#      by: PyQt4 UI code generator 4.8.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(274, 127)
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Update Manager", None, QtGui.QApplication.UnicodeUTF8))
        self.gridLayout = QtGui.QGridLayout(MainWindow)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(MainWindow)
        self.label.setText(QtGui.QApplication.translate("MainWindow", "Current Version", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.lblCurrentVersion = QtGui.QLabel(MainWindow)
        self.lblCurrentVersion.setText(QtGui.QApplication.translate("MainWindow", "Version ...", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCurrentVersion.setObjectName(_fromUtf8("lblCurrentVersion"))
        self.gridLayout.addWidget(self.lblCurrentVersion, 1, 1, 1, 1)
        self.label_2 = QtGui.QLabel(MainWindow)
        self.label_2.setText(QtGui.QApplication.translate("MainWindow", "Update to", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 1)
        self.cmbUpdateTo = QtGui.QComboBox(MainWindow)
        self.cmbUpdateTo.setEditable(False)
        self.cmbUpdateTo.setFrame(True)
        self.cmbUpdateTo.setObjectName(_fromUtf8("cmbUpdateTo"))
        self.gridLayout.addWidget(self.cmbUpdateTo, 3, 1, 1, 1)
        self.btnUpdate = QtGui.QPushButton(MainWindow)
        self.btnUpdate.setText(QtGui.QApplication.translate("MainWindow", "Update", None, QtGui.QApplication.UnicodeUTF8))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/view-refresh.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnUpdate.setIcon(icon)
        self.btnUpdate.setObjectName(_fromUtf8("btnUpdate"))
        self.gridLayout.addWidget(self.btnUpdate, 4, 1, 1, 1)
        self.btnQuit = QtGui.QPushButton(MainWindow)
        self.btnQuit.setText(QtGui.QApplication.translate("MainWindow", "Quit", None, QtGui.QApplication.UnicodeUTF8))
        self.btnQuit.setObjectName(_fromUtf8("btnQuit"))
        self.gridLayout.addWidget(self.btnQuit, 5, 1, 1, 1)
        self.lblCurrentRevision = QtGui.QLabel(MainWindow)
        self.lblCurrentRevision.setText(QtGui.QApplication.translate("MainWindow", "Current Revision", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCurrentRevision.setObjectName(_fromUtf8("lblCurrentRevision"))
        self.gridLayout.addWidget(self.lblCurrentRevision, 2, 0, 1, 1)
        self.lblCurrentRevisionValue = QtGui.QLabel(MainWindow)
        self.lblCurrentRevisionValue.setText(QtGui.QApplication.translate("MainWindow", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCurrentRevisionValue.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.lblCurrentRevisionValue.setObjectName(_fromUtf8("lblCurrentRevisionValue"))
        self.gridLayout.addWidget(self.lblCurrentRevisionValue, 2, 1, 1, 1)
        self.imgLogo = QtGui.QLabel(MainWindow)
        self.imgLogo.setAutoFillBackground(True)
        self.imgLogo.setText(QtGui.QApplication.translate("MainWindow", "Logo", None, QtGui.QApplication.UnicodeUTF8))
        self.imgLogo.setObjectName(_fromUtf8("imgLogo"))
        self.gridLayout.addWidget(self.imgLogo, 0, 0, 1, 2)

        self.retranslateUi(MainWindow)
        QtCore.QObject.connect(self.btnQuit, QtCore.SIGNAL(_fromUtf8("clicked()")), MainWindow.close)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        pass

import vcsdeploy_rc
