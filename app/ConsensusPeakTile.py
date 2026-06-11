# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ConsensusPeakTile.ui'
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
    QVBoxLayout, QWidget)

class Ui_ConsensusPeakTile(object):
    def setupUi(self, ConsensusPeakTile):
        if not ConsensusPeakTile.objectName():
            ConsensusPeakTile.setObjectName(u"ConsensusPeakTile")
        ConsensusPeakTile.resize(290, 84)
        ConsensusPeakTile.setMinimumSize(QSize(290, 72))
        ConsensusPeakTile.setMaximumSize(QSize(290, 84))
        ConsensusPeakTile.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        ConsensusPeakTile.setStyleSheet(u"#ConsensusPeakTile  {\n"
"	background-color: #1d1d1d;\n"
"	border: 1px solid #1d1d1d;\n"
"	border-radius: 5px;\n"
"}\n"
"\n"
"#ConsensusPeakTile:hover {\n"
"	background-color: #555555;\n"
"	border: 1px solid #323232;\n"
"	border-radius: 5px;\n"
"}\n"
"")
        self.horizontalLayout = QHBoxLayout(ConsensusPeakTile)
        self.horizontalLayout.setSpacing(15)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(6, 6, 6, 6)
        self.peak_window = QLabel(ConsensusPeakTile)
        self.peak_window.setObjectName(u"peak_window")
        self.peak_window.setMinimumSize(QSize(60, 60))
        self.peak_window.setMaximumSize(QSize(60, 60))

        self.horizontalLayout.addWidget(self.peak_window)

        self.text_container = QWidget(ConsensusPeakTile)
        self.text_container.setObjectName(u"text_container")
        self.text_container.setMinimumSize(QSize(0, 60))
        self.text_container.setMaximumSize(QSize(16777215, 60))
        self.verticalLayout_2 = QVBoxLayout(self.text_container)
        self.verticalLayout_2.setSpacing(3)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(6, 6, 0, 6)
        self.label_count_label = QLabel(self.text_container)
        self.label_count_label.setObjectName(u"label_count_label")
        font = QFont()
        font.setFamilies([u"Lato"])
        font.setPointSize(10)
        font.setWeight(QFont.Light)
        self.label_count_label.setFont(font)
        self.label_count_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.label_count_label.setStyleSheet(u"border: None;\n"
"color: #ebebeb;\n"
"background-color: transparent;")

        self.verticalLayout_2.addWidget(self.label_count_label)

        self.spectra_count_label = QLabel(self.text_container)
        self.spectra_count_label.setObjectName(u"spectra_count_label")
        self.spectra_count_label.setFont(font)
        self.spectra_count_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.spectra_count_label.setStyleSheet(u"border: None;\n"
"color: #ebebeb;\n"
"background-color: transparent;")

        self.verticalLayout_2.addWidget(self.spectra_count_label)

        self.position_label = QLabel(self.text_container)
        self.position_label.setObjectName(u"position_label")
        self.position_label.setFont(font)
        self.position_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.position_label.setStyleSheet(u"border: None;\n"
"color: #ebebeb;\n"
"background-color: transparent;")

        self.verticalLayout_2.addWidget(self.position_label)


        self.horizontalLayout.addWidget(self.text_container)


        self.retranslateUi(ConsensusPeakTile)

        QMetaObject.connectSlotsByName(ConsensusPeakTile)
    # setupUi

    def retranslateUi(self, ConsensusPeakTile):
        ConsensusPeakTile.setWindowTitle(QCoreApplication.translate("ConsensusPeakTile", u"Form", None))
        self.peak_window.setText(QCoreApplication.translate("ConsensusPeakTile", u"TextLabel", None))
        self.label_count_label.setText(QCoreApplication.translate("ConsensusPeakTile", u"In labels: X/X", None))
        self.spectra_count_label.setText(QCoreApplication.translate("ConsensusPeakTile", u"In spectra: X/X", None))
        self.position_label.setText(QCoreApplication.translate("ConsensusPeakTile", u"RT; XX.X - DT: XXX.XX", None))
    # retranslateUi

