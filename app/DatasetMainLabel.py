# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'DatasetMainLabel.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QWidget)

class Ui_DatasetLabelEntry(object):
    def setupUi(self, DatasetLabelEntry):
        if not DatasetLabelEntry.objectName():
            DatasetLabelEntry.setObjectName(u"DatasetLabelEntry")
        DatasetLabelEntry.resize(389, 50)
        DatasetLabelEntry.setMinimumSize(QSize(0, 50))
        DatasetLabelEntry.setMaximumSize(QSize(16777215, 50))
        DatasetLabelEntry.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        DatasetLabelEntry.setStyleSheet(u"QWidget {\n"
"	background-color: #2e2e2e;\n"
"	border-bottom: 1px solid #666666;\n"
"}\n"
"\n"
"QWidget:hover {\n"
"	background-color: #131313;\n"
"}")
        self.horizontalLayout = QHBoxLayout(DatasetLabelEntry)
        self.horizontalLayout.setSpacing(15)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_name = QLabel(DatasetLabelEntry)
        self.label_name.setObjectName(u"label_name")
        font = QFont()
        font.setFamilies([u"Lato"])
        font.setPointSize(15)
        font.setWeight(QFont.Light)
        self.label_name.setFont(font)
        self.label_name.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.label_name.setStyleSheet(u"border: None;\n"
"color: #ebebeb;\n"
"background-color: transparent;")

        self.horizontalLayout.addWidget(self.label_name)

        self.button_open_close = QPushButton(DatasetLabelEntry)
        self.button_open_close.setObjectName(u"button_open_close")
        self.button_open_close.setMaximumSize(QSize(30, 16777215))
        self.button_open_close.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.button_open_close.setStyleSheet(u"QPushButton {\n"
"    background-color: transparent;\n"
"    border: none;\n"
"	background-image: url(\"ui/_pics/icons/classifier_grey.png\");\n"
"}")
        icon = QIcon()
        icon.addFile(u"ui/_pics/icons/chevron_right_white.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.button_open_close.setIcon(icon)
        self.button_open_close.setIconSize(QSize(30, 30))

        self.horizontalLayout.addWidget(self.button_open_close)


        self.retranslateUi(DatasetLabelEntry)

        QMetaObject.connectSlotsByName(DatasetLabelEntry)
    # setupUi

    def retranslateUi(self, DatasetLabelEntry):
        DatasetLabelEntry.setWindowTitle(QCoreApplication.translate("DatasetLabelEntry", u"Form", None))
        self.label_name.setText(QCoreApplication.translate("DatasetLabelEntry", u"Main Label", None))
        self.button_open_close.setText("")
    # retranslateUi

