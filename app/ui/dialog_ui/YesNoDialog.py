# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'YesNoDialog.ui'
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

class Ui_YesNoDialog(object):
    def setupUi(self, YesNoDialog):
        if not YesNoDialog.objectName():
            YesNoDialog.setObjectName(u"YesNoDialog")
        YesNoDialog.resize(400, 400)
        YesNoDialog.setMinimumSize(QSize(400, 400))
        YesNoDialog.setMaximumSize(QSize(400, 400))
        YesNoDialog.setStyleSheet(u"background-color: #1d1d1d;")
        self.label_message = QLabel(YesNoDialog)
        self.label_message.setObjectName(u"label_message")
        self.label_message.setGeometry(QRect(20, 200, 361, 121))
        font = QFont()
        font.setFamilies([u"Lato"])
        font.setPointSize(12)
        self.label_message.setFont(font)
        self.label_message.setStyleSheet(u"color: #9e9e9e;")
        self.label_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_message.setWordWrap(True)
        self.button_yes = QPushButton(YesNoDialog)
        self.button_yes.setObjectName(u"button_yes")
        self.button_yes.setGeometry(QRect(280, 340, 101, 41))
        font1 = QFont()
        font1.setFamilies([u"Lato"])
        font1.setPointSize(13)
        self.button_yes.setFont(font1)
        self.button_yes.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.button_yes.setStyleSheet(u"QPushButton {\n"
"    border: 1px solid #00eaff;\n"
"    background-color: #232323; \n"
"    color: #00eaff;\n"
"    border-radius: 10px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	background-color: #131313;\n"
"}")
        self.label_icon = QLabel(YesNoDialog)
        self.label_icon.setObjectName(u"label_icon")
        self.label_icon.setEnabled(True)
        self.label_icon.setGeometry(QRect(120, 20, 161, 161))
        self.label_icon.setPixmap(QPixmap(u":/ui/_pics/icons/attention_orange.png"))
        self.label_icon.setScaledContents(True)
        self.label_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.button_no = QPushButton(YesNoDialog)
        self.button_no.setObjectName(u"button_no")
        self.button_no.setGeometry(QRect(20, 340, 101, 41))
        self.button_no.setFont(font1)
        self.button_no.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.button_no.setStyleSheet(u"QPushButton {\n"
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

        self.retranslateUi(YesNoDialog)

        QMetaObject.connectSlotsByName(YesNoDialog)
    # setupUi

    def retranslateUi(self, YesNoDialog):
        YesNoDialog.setWindowTitle(QCoreApplication.translate("YesNoDialog", u"Dialog", None))
        self.label_message.setText(QCoreApplication.translate("YesNoDialog", u"Message ...", None))
        self.button_yes.setText(QCoreApplication.translate("YesNoDialog", u"Yes", None))
        self.label_icon.setText("")
        self.button_no.setText(QCoreApplication.translate("YesNoDialog", u"No", None))
    # retranslateUi

