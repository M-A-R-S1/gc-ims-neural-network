# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ConsensusPeakWidget.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_ConsensusPeakWidget(object):
    def setupUi(self, ConsensusPeakWidget):
        if not ConsensusPeakWidget.objectName():
            ConsensusPeakWidget.setObjectName(u"ConsensusPeakWidget")
        ConsensusPeakWidget.resize(1519, 1018)
        font = QFont()
        font.setWeight(QFont.Black)
        ConsensusPeakWidget.setFont(font)
        ConsensusPeakWidget.setStyleSheet(u"background-color: #1d1d1d;")
        self.verticalLayout = QVBoxLayout(ConsensusPeakWidget)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(40, 20, 20, 20)
        self.label_header = QLabel(ConsensusPeakWidget)
        self.label_header.setObjectName(u"label_header")
        self.label_header.setMaximumSize(QSize(16777215, 80))
        font1 = QFont()
        font1.setFamilies([u"Lato"])
        font1.setPointSize(35)
        font1.setKerning(True)
        self.label_header.setFont(font1)
        self.label_header.setStyleSheet(u"color: #ebebeb;")
        self.label_header.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout.addWidget(self.label_header)

        self.consensuspeak_container = QWidget(ConsensusPeakWidget)
        self.consensuspeak_container.setObjectName(u"consensuspeak_container")
        self.horizontalLayout = QHBoxLayout(self.consensuspeak_container)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.consensus_peak_container = QWidget(self.consensuspeak_container)
        self.consensus_peak_container.setObjectName(u"consensus_peak_container")
        self.consensus_peak_container.setMinimumSize(QSize(950, 0))
        self.consensus_peak_container.setMaximumSize(QSize(950, 16777215))
        self.consensus_peak_container.setStyleSheet(u"")
        self.verticalLayout_5 = QVBoxLayout(self.consensus_peak_container)
        self.verticalLayout_5.setSpacing(9)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(9, 30, -1, 9)
        self.consensus_peak_inner_container = QWidget(self.consensus_peak_container)
        self.consensus_peak_inner_container.setObjectName(u"consensus_peak_inner_container")
        self.consensus_peak_inner_container.setMaximumSize(QSize(16777215, 16777215))
        self.consensus_peak_inner_container.setFont(font)
        self.consensus_peak_inner_container.setStyleSheet(u"QWidget {\n"
"	background-color: #2e2e2e;\n"
"	border: 1px solid #ff9000;\n"
"	border-radius: 10px;\n"
"}")
        self.verticalLayout_6 = QVBoxLayout(self.consensus_peak_inner_container)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(1, 1, 1, 1)
        self.label_container_header_2 = QLabel(self.consensus_peak_inner_container)
        self.label_container_header_2.setObjectName(u"label_container_header_2")
        self.label_container_header_2.setMinimumSize(QSize(0, 60))
        self.label_container_header_2.setMaximumSize(QSize(16777215, 60))
        font2 = QFont()
        font2.setFamilies([u"Lato"])
        font2.setPointSize(25)
        self.label_container_header_2.setFont(font2)
        self.label_container_header_2.setStyleSheet(u"border: 0px;\n"
"border-bottom: 1px solid #ff9000;\n"
"border-top-left-radius: 10px;\n"
"border-top-right-radius: 10px;\n"
"border-bottom-left-radius: 0px;\n"
"border-bottom-right-radius: 0px;\n"
"background-color: #232323;\n"
"color: #ebebeb;")
        self.label_container_header_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_6.addWidget(self.label_container_header_2)

        self.scrollArea_peak = QScrollArea(self.consensus_peak_inner_container)
        self.scrollArea_peak.setObjectName(u"scrollArea_peak")
        self.scrollArea_peak.setStyleSheet(u"border: 0px;\n"
"background-color: transparent;\n"
"")
        self.scrollArea_peak.setWidgetResizable(True)
        self.scrollArea_peak_Contents = QWidget()
        self.scrollArea_peak_Contents.setObjectName(u"scrollArea_peak_Contents")
        self.scrollArea_peak_Contents.setGeometry(QRect(0, 0, 930, 811))
        self.gridLayout = QGridLayout(self.scrollArea_peak_Contents)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setVerticalSpacing(10)
        self.verticalSpacer_2 = QSpacerItem(20, 585, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer_2, 0, 0, 1, 1)

        self.scrollArea_peak.setWidget(self.scrollArea_peak_Contents)

        self.verticalLayout_6.addWidget(self.scrollArea_peak)


        self.verticalLayout_5.addWidget(self.consensus_peak_inner_container)

        self.verticalLayout_5.setStretch(0, 1)

        self.horizontalLayout.addWidget(self.consensus_peak_container)

        self.preview_container = QWidget(self.consensuspeak_container)
        self.preview_container.setObjectName(u"preview_container")
        self.preview_container.setStyleSheet(u"")
        self.verticalLayout_7 = QVBoxLayout(self.preview_container)
        self.verticalLayout_7.setSpacing(6)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.label_preview = QLabel(self.preview_container)
        self.label_preview.setObjectName(u"label_preview")
        self.label_preview.setMaximumSize(QSize(16777215, 40))
        self.label_preview.setFont(font2)
        self.label_preview.setStyleSheet(u"color: #ebebeb;")
        self.label_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_7.addWidget(self.label_preview)

        self.preview_image = QWidget(self.preview_container)
        self.preview_image.setObjectName(u"preview_image")
        self.preview_image.setStyleSheet(u"background-color: #191919;\n"
" border: none;")

        self.verticalLayout_7.addWidget(self.preview_image)

        self.pushButton_toggle_peak_marker = QPushButton(self.preview_container)
        self.pushButton_toggle_peak_marker.setObjectName(u"pushButton_toggle_peak_marker")
        self.pushButton_toggle_peak_marker.setEnabled(True)
        self.pushButton_toggle_peak_marker.setMinimumSize(QSize(0, 60))
        self.pushButton_toggle_peak_marker.setMaximumSize(QSize(16777215, 16777215))
        font3 = QFont()
        font3.setFamilies([u"Lato"])
        font3.setPointSize(20)
        self.pushButton_toggle_peak_marker.setFont(font3)
        self.pushButton_toggle_peak_marker.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.pushButton_toggle_peak_marker.setMouseTracking(True)
        self.pushButton_toggle_peak_marker.setTabletTracking(False)
        self.pushButton_toggle_peak_marker.setStyleSheet(u"QPushButton {\n"
"    border: 1px solid #ff9000;\n"
"    background-color: #232323; \n"
"    color: #ff9000;\n"
"    border-radius: 10px;\n"
"	margin-top: 10px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"background-color: #131313;\n"
"}")
        self.pushButton_toggle_peak_marker.setAutoDefault(False)

        self.verticalLayout_7.addWidget(self.pushButton_toggle_peak_marker)


        self.horizontalLayout.addWidget(self.preview_container)


        self.verticalLayout.addWidget(self.consensuspeak_container)

        self.verticalLayout.setStretch(1, 1)

        self.retranslateUi(ConsensusPeakWidget)

        self.pushButton_toggle_peak_marker.setDefault(False)


        QMetaObject.connectSlotsByName(ConsensusPeakWidget)
    # setupUi

    def retranslateUi(self, ConsensusPeakWidget):
        ConsensusPeakWidget.setWindowTitle(QCoreApplication.translate("ConsensusPeakWidget", u"Form", None))
        self.label_header.setText(QCoreApplication.translate("ConsensusPeakWidget", u"Consensus peaks", None))
        self.label_container_header_2.setText(QCoreApplication.translate("ConsensusPeakWidget", u"Consensus peaks", None))
        self.label_preview.setText(QCoreApplication.translate("ConsensusPeakWidget", u"Spectrum preview", None))
        self.pushButton_toggle_peak_marker.setText(QCoreApplication.translate("ConsensusPeakWidget", u"Hide peak markers", None))
    # retranslateUi

