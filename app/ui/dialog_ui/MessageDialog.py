# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MessageDialog.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QLabel, QPushButton,
    QSizePolicy, QWidget)
import resources_rc

class Ui_MessageDialog(object):
    def setupUi(self, MessageDialog):
        if not MessageDialog.objectName():
            MessageDialog.setObjectName(u"MessageDialog")
        MessageDialog.resize(400, 400)
        MessageDialog.setMinimumSize(QSize(400, 400))
        MessageDialog.setMaximumSize(QSize(400, 400))
        MessageDialog.setStyleSheet(u"background-color: #1d1d1d;")
        self.label_message = QLabel(MessageDialog)
        self.label_message.setObjectName(u"label_message")
        self.label_message.setGeometry(QRect(20, 230, 361, 81))
        font = QFont()
        font.setFamilies([u"Lato"])
        font.setPointSize(12)
        self.label_message.setFont(font)
        self.label_message.setStyleSheet(u"color: #9e9e9e;")
        self.label_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_message.setWordWrap(True)
        self.button_ok = QPushButton(MessageDialog)
        self.button_ok.setObjectName(u"button_ok")
        self.button_ok.setGeometry(QRect(150, 340, 101, 41))
        font1 = QFont()
        font1.setFamilies([u"Lato"])
        font1.setPointSize(13)
        self.button_ok.setFont(font1)
        self.button_ok.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.button_ok.setStyleSheet(u"QPushButton {\n"
"    border: 1px solid #9e9e9e;\n"
"    background-color: #232323; \n"
"    color: #9e9e9e;\n"
"    border-radius: 10px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	background-color: #131313;\n"
"}\n"
"")
        self.label_icon = QLabel(MessageDialog)
        self.label_icon.setObjectName(u"label_icon")
        self.label_icon.setEnabled(True)
        self.label_icon.setGeometry(QRect(100, 20, 201, 191))
        self.label_icon.setPixmap(QPixmap(u":/ui/_pics/icons/error_magenta.png"))
        self.label_icon.setScaledContents(True)
        self.label_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.retranslateUi(MessageDialog)

        QMetaObject.connectSlotsByName(MessageDialog)
    # setupUi

    def retranslateUi(self, MessageDialog):
        MessageDialog.setWindowTitle(QCoreApplication.translate("MessageDialog", u"Dialog", None))
        self.label_message.setText(QCoreApplication.translate("MessageDialog", u"Message ...", None))
        self.button_ok.setText(QCoreApplication.translate("MessageDialog", u"Ok", None))
        self.label_icon.setText("")
    # retranslateUi

