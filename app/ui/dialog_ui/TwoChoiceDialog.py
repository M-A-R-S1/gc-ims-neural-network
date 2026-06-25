# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'TwoChoiceDialog.ui'
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

class Ui_TwoChoiceDialog(object):
    def setupUi(self, TwoChoiceDialog):
        if not TwoChoiceDialog.objectName():
            TwoChoiceDialog.setObjectName(u"TwoChoiceDialog")
        TwoChoiceDialog.resize(600, 400)
        TwoChoiceDialog.setMinimumSize(QSize(600, 400))
        TwoChoiceDialog.setMaximumSize(QSize(600, 400))
        TwoChoiceDialog.setStyleSheet(u"background-color: #1d1d1d;")
        self.label_message = QLabel(TwoChoiceDialog)
        self.label_message.setObjectName(u"label_message")
        self.label_message.setGeometry(QRect(20, 230, 551, 81))
        font = QFont()
        font.setFamilies([u"Lato"])
        font.setPointSize(12)
        self.label_message.setFont(font)
        self.label_message.setStyleSheet(u"color: #9e9e9e;")
        self.label_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_message.setWordWrap(True)
        self.button_b = QPushButton(TwoChoiceDialog)
        self.button_b.setObjectName(u"button_b")
        self.button_b.setGeometry(QRect(440, 340, 131, 41))
        font1 = QFont()
        font1.setFamilies([u"Lato"])
        font1.setPointSize(13)
        self.button_b.setFont(font1)
        self.button_b.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.button_b.setStyleSheet(u"QPushButton {\n"
"    border: 1px solid #ff9000;\n"
"    background-color: #232323; \n"
"    color: #ff9000;\n"
"    border-radius: 10px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	background-color: #131313;\n"
"}")
        self.label_icon = QLabel(TwoChoiceDialog)
        self.label_icon.setObjectName(u"label_icon")
        self.label_icon.setEnabled(True)
        self.label_icon.setGeometry(QRect(190, 20, 201, 191))
        self.label_icon.setPixmap(QPixmap(u":/ui/_pics/icons/attention_orange.png"))
        self.label_icon.setScaledContents(True)
        self.label_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.button_no = QPushButton(TwoChoiceDialog)
        self.button_no.setObjectName(u"button_no")
        self.button_no.setGeometry(QRect(20, 340, 131, 41))
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
        self.button_a = QPushButton(TwoChoiceDialog)
        self.button_a.setObjectName(u"button_a")
        self.button_a.setGeometry(QRect(290, 340, 131, 41))
        self.button_a.setFont(font1)
        self.button_a.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.button_a.setStyleSheet(u"QPushButton {\n"
"    border: 1px solid #ff9000;\n"
"    background-color: #232323; \n"
"    color: #ff9000;\n"
"    border-radius: 10px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	background-color: #131313;\n"
"}")

        self.retranslateUi(TwoChoiceDialog)

        QMetaObject.connectSlotsByName(TwoChoiceDialog)
    # setupUi

    def retranslateUi(self, TwoChoiceDialog):
        TwoChoiceDialog.setWindowTitle(QCoreApplication.translate("TwoChoiceDialog", u"Dialog", None))
        self.label_message.setText(QCoreApplication.translate("TwoChoiceDialog", u"Message ...", None))
        self.button_b.setText(QCoreApplication.translate("TwoChoiceDialog", u"b", None))
        self.label_icon.setText("")
        self.button_no.setText(QCoreApplication.translate("TwoChoiceDialog", u"Cancel", None))
        self.button_a.setText(QCoreApplication.translate("TwoChoiceDialog", u"a", None))
    # retranslateUi

