# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'DatasetSpectrumEntry.ui'
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

class Ui_DatasetSpectrumEntry(object):
    def setupUi(self, DatasetSpectrumEntry):
        if not DatasetSpectrumEntry.objectName():
            DatasetSpectrumEntry.setObjectName(u"DatasetSpectrumEntry")
        DatasetSpectrumEntry.resize(389, 50)
        DatasetSpectrumEntry.setMinimumSize(QSize(0, 50))
        DatasetSpectrumEntry.setMaximumSize(QSize(16777215, 50))
        DatasetSpectrumEntry.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        DatasetSpectrumEntry.setStyleSheet(u"QWidget {\n"
"	background-color: #2e2e2e;\n"
"	border-bottom: 1px solid #666666;\n"
"}\n"
"\n"
"QWidget:hover {\n"
"	background-color: #131313;\n"
"}")
        self.horizontalLayout = QHBoxLayout(DatasetSpectrumEntry)
        self.horizontalLayout.setSpacing(15)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.button_spectrumDelete = QPushButton(DatasetSpectrumEntry)
        self.button_spectrumDelete.setObjectName(u"button_spectrumDelete")
        self.button_spectrumDelete.setMaximumSize(QSize(30, 16777215))
        self.button_spectrumDelete.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.button_spectrumDelete.setStyleSheet(u"QPushButton {\n"
"    background-color: transparent;\n"
"    border: none;\n"
"}")
        icon = QIcon()
        icon.addFile(u":/ui/_pics/icons/delete_grey.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.button_spectrumDelete.setIcon(icon)
        self.button_spectrumDelete.setIconSize(QSize(30, 30))

        self.horizontalLayout.addWidget(self.button_spectrumDelete)

        self.spectrum_name = QLabel(DatasetSpectrumEntry)
        self.spectrum_name.setObjectName(u"spectrum_name")
        font = QFont()
        font.setFamilies([u"Lato"])
        font.setPointSize(13)
        font.setWeight(QFont.Light)
        self.spectrum_name.setFont(font)
        self.spectrum_name.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.spectrum_name.setStyleSheet(u"border: None;\n"
"color: #ebebeb;\n"
"background-color: transparent;")

        self.horizontalLayout.addWidget(self.spectrum_name)


        self.retranslateUi(DatasetSpectrumEntry)

        QMetaObject.connectSlotsByName(DatasetSpectrumEntry)
    # setupUi

    def retranslateUi(self, DatasetSpectrumEntry):
        DatasetSpectrumEntry.setWindowTitle(QCoreApplication.translate("DatasetSpectrumEntry", u"Form", None))
        self.button_spectrumDelete.setText("")
        self.spectrum_name.setText(QCoreApplication.translate("DatasetSpectrumEntry", u"TextLabel", None))
    # retranslateUi

