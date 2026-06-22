# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ProgressDialog.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QLabel, QProgressBar,
    QPushButton, QSizePolicy, QWidget)

class Ui_ProgressDialog(object):
    def setupUi(self, ProgressDialog):
        if not ProgressDialog.objectName():
            ProgressDialog.setObjectName(u"ProgressDialog")
        ProgressDialog.resize(800, 350)
        ProgressDialog.setMinimumSize(QSize(800, 350))
        ProgressDialog.setMaximumSize(QSize(800, 350))
        ProgressDialog.setStyleSheet(u"background-color: #1d1d1d;")
        self.button_no = QPushButton(ProgressDialog)
        self.button_no.setObjectName(u"button_no")
        self.button_no.setGeometry(QRect(320, 260, 151, 41))
        font = QFont()
        font.setFamilies([u"Lato"])
        font.setPointSize(13)
        self.button_no.setFont(font)
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
        self.progressBar = QProgressBar(ProgressDialog)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setGeometry(QRect(30, 160, 731, 16))
        self.progressBar.setMinimumSize(QSize(0, 0))
        font1 = QFont()
        font1.setFamilies([u"Lato"])
        self.progressBar.setFont(font1)
        self.progressBar.setStyleSheet(u"")
        self.progressBar.setValue(0)
        self.progressBar.setTextVisible(False)
        self.label_header = QLabel(ProgressDialog)
        self.label_header.setObjectName(u"label_header")
        self.label_header.setGeometry(QRect(0, 40, 791, 41))
        font2 = QFont()
        font2.setFamilies([u"Lato"])
        font2.setPointSize(25)
        self.label_header.setFont(font2)
        self.label_header.setStyleSheet(u"color: #ebebeb;")
        self.label_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_subheader = QLabel(ProgressDialog)
        self.label_subheader.setObjectName(u"label_subheader")
        self.label_subheader.setGeometry(QRect(0, 90, 791, 21))
        font3 = QFont()
        font3.setFamilies([u"Lato"])
        font3.setPointSize(14)
        font3.setWeight(QFont.Light)
        self.label_subheader.setFont(font3)
        self.label_subheader.setStyleSheet(u"color: #ebebeb;")
        self.label_subheader.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_percent = QLabel(ProgressDialog)
        self.label_percent.setObjectName(u"label_percent")
        self.label_percent.setGeometry(QRect(430, 180, 331, 21))
        font4 = QFont()
        font4.setFamilies([u"Lato"])
        font4.setPointSize(12)
        font4.setBold(False)
        self.label_percent.setFont(font4)
        self.label_percent.setStyleSheet(u"color: #ebebeb;")
        self.label_percent.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.label_time_remaining = QLabel(ProgressDialog)
        self.label_time_remaining.setObjectName(u"label_time_remaining")
        self.label_time_remaining.setGeometry(QRect(30, 180, 361, 21))
        font5 = QFont()
        font5.setFamilies([u"Lato"])
        font5.setPointSize(12)
        font5.setWeight(QFont.Light)
        font5.setStyleStrategy(QFont.PreferDefault)
        self.label_time_remaining.setFont(font5)
        self.label_time_remaining.setStyleSheet(u"color: #ebebeb;")
        self.label_time_remaining.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.retranslateUi(ProgressDialog)

        QMetaObject.connectSlotsByName(ProgressDialog)
    # setupUi

    def retranslateUi(self, ProgressDialog):
        ProgressDialog.setWindowTitle(QCoreApplication.translate("ProgressDialog", u"Dialog", None))
        self.button_no.setText(QCoreApplication.translate("ProgressDialog", u"Cancle", None))
        self.label_header.setText(QCoreApplication.translate("ProgressDialog", u"Dataset preprocessing", None))
        self.label_subheader.setText(QCoreApplication.translate("ProgressDialog", u"This may take a while, please wait.", None))
        self.label_percent.setText(QCoreApplication.translate("ProgressDialog", u"0 %", None))
        self.label_time_remaining.setText(QCoreApplication.translate("ProgressDialog", u"time remaining: calculating ...", None))
    # retranslateUi

