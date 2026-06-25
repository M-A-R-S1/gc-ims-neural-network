# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'DatasetLabelEntry.ui'
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
import resources_rc

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
        self.button_labelDelete = QPushButton(DatasetLabelEntry)
        self.button_labelDelete.setObjectName(u"button_labelDelete")
        self.button_labelDelete.setMaximumSize(QSize(30, 16777215))
        self.button_labelDelete.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.button_labelDelete.setStyleSheet(u"QPushButton {\n"
"    background-color: transparent;\n"
"    border: none;\n"
"}")
        icon = QIcon()
        icon.addFile(u":/ui/_pics/icons/delete_grey.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.button_labelDelete.setIcon(icon)
        self.button_labelDelete.setIconSize(QSize(30, 30))

        self.horizontalLayout.addWidget(self.button_labelDelete)

        self.button_labelRename = QPushButton(DatasetLabelEntry)
        self.button_labelRename.setObjectName(u"button_labelRename")
        self.button_labelRename.setMaximumSize(QSize(30, 16777215))
        self.button_labelRename.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.button_labelRename.setStyleSheet(u"QPushButton {\n"
"    background-color: transparent;\n"
"    border: none;\n"
"	background-image: url(\"ui/_pics/icons/classifier_grey.png\");\n"
"}")
        icon1 = QIcon()
        icon1.addFile(u":/ui/_pics/icons/edit_grey.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.button_labelRename.setIcon(icon1)
        self.button_labelRename.setIconSize(QSize(30, 30))

        self.horizontalLayout.addWidget(self.button_labelRename)

        self.label_name = QLabel(DatasetLabelEntry)
        self.label_name.setObjectName(u"label_name")
        font = QFont()
        font.setFamilies([u"Lato"])
        font.setPointSize(13)
        font.setWeight(QFont.Light)
        self.label_name.setFont(font)
        self.label_name.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.label_name.setStyleSheet(u"border: None;\n"
"color: #ebebeb;\n"
"background-color: transparent;")

        self.horizontalLayout.addWidget(self.label_name)

        self.spectra_counter = QLabel(DatasetLabelEntry)
        self.spectra_counter.setObjectName(u"spectra_counter")
        self.spectra_counter.setMaximumSize(QSize(60, 16777215))
        self.spectra_counter.setFont(font)
        self.spectra_counter.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.spectra_counter.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.spectra_counter.setStyleSheet(u"border: None;\n"
"color: #ebebeb;\n"
"background-color: transparent;")
        self.spectra_counter.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout.addWidget(self.spectra_counter)


        self.retranslateUi(DatasetLabelEntry)

        QMetaObject.connectSlotsByName(DatasetLabelEntry)
    # setupUi

    def retranslateUi(self, DatasetLabelEntry):
        DatasetLabelEntry.setWindowTitle(QCoreApplication.translate("DatasetLabelEntry", u"Form", None))
        self.button_labelDelete.setText("")
        self.button_labelRename.setText("")
        self.label_name.setText(QCoreApplication.translate("DatasetLabelEntry", u"TextLabel", None))
        self.spectra_counter.setText(QCoreApplication.translate("DatasetLabelEntry", u"0x", None))
    # retranslateUi

