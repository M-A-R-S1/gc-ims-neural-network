# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'DatasetSubEntry.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QSizePolicy,
    QWidget)

class Ui_DatasetSubEntry(object):
    def setupUi(self, DatasetSubEntry):
        if not DatasetSubEntry.objectName():
            DatasetSubEntry.setObjectName(u"DatasetSubEntry")
        DatasetSubEntry.resize(389, 50)
        DatasetSubEntry.setMinimumSize(QSize(0, 50))
        DatasetSubEntry.setMaximumSize(QSize(16777215, 50))
        DatasetSubEntry.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        DatasetSubEntry.setStyleSheet(u"QWidget {\n"
"	background-color: #2e2e2e;\n"
"	border-bottom: 1px solid #666666;\n"
"	border-radius: 0px;\n"
"}\n"
"\n"
"QWidget:hover {\n"
"	background-color: #131313;\n"
"}")
        self.horizontalLayout = QHBoxLayout(DatasetSubEntry)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(20, -1, -1, -1)
        self.label_name = QLabel(DatasetSubEntry)
        self.label_name.setObjectName(u"label_name")
        font = QFont()
        font.setFamilies([u"Lato"])
        font.setPointSize(13)
        font.setWeight(QFont.Light)
        font.setItalic(True)
        self.label_name.setFont(font)
        self.label_name.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.label_name.setStyleSheet(u"border: None;\n"
"color: #ebebeb;\n"
"background-color: transparent;")

        self.horizontalLayout.addWidget(self.label_name)

        self.label_peak_counter = QLabel(DatasetSubEntry)
        self.label_peak_counter.setObjectName(u"label_peak_counter")
        self.label_peak_counter.setEnabled(True)
        self.label_peak_counter.setMaximumSize(QSize(55, 16777215))
        self.label_peak_counter.setFont(font)
        self.label_peak_counter.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.label_peak_counter.setStyleSheet(u"border: None;\n"
"color: #ebebeb;\n"
"background-color: transparent;")
        self.label_peak_counter.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout.addWidget(self.label_peak_counter)


        self.retranslateUi(DatasetSubEntry)

        QMetaObject.connectSlotsByName(DatasetSubEntry)
    # setupUi

    def retranslateUi(self, DatasetSubEntry):
        DatasetSubEntry.setWindowTitle(QCoreApplication.translate("DatasetSubEntry", u"Form", None))
        self.label_name.setText(QCoreApplication.translate("DatasetSubEntry", u"- Sub Textlabel", None))
        self.label_peak_counter.setText(QCoreApplication.translate("DatasetSubEntry", u"0x", None))
    # retranslateUi

