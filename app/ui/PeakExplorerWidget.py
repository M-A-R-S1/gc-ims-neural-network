# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'PeakExplorerWidget.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QGridLayout, QHBoxLayout,
    QLabel, QPushButton, QScrollArea, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_PeakExplorerWidget(object):
    def setupUi(self, PeakExplorerWidget):
        if not PeakExplorerWidget.objectName():
            PeakExplorerWidget.setObjectName(u"PeakExplorerWidget")
        PeakExplorerWidget.resize(1546, 993)
        font = QFont()
        font.setWeight(QFont.Black)
        PeakExplorerWidget.setFont(font)
        PeakExplorerWidget.setStyleSheet(u"background-color: #1d1d1d;")
        self.verticalLayout = QVBoxLayout(PeakExplorerWidget)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(40, 20, 20, 20)
        self.label_header = QLabel(PeakExplorerWidget)
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

        self.peakexplorer_container = QWidget(PeakExplorerWidget)
        self.peakexplorer_container.setObjectName(u"peakexplorer_container")
        self.horizontalLayout = QHBoxLayout(self.peakexplorer_container)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.dataset_container = QWidget(self.peakexplorer_container)
        self.dataset_container.setObjectName(u"dataset_container")
        self.dataset_container.setMaximumSize(QSize(450, 16777215))
        self.dataset_container.setStyleSheet(u"")
        self.verticalLayout_2 = QVBoxLayout(self.dataset_container)
        self.verticalLayout_2.setSpacing(10)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(9, 30, -1, 9)
        self.dataset_inner_container = QWidget(self.dataset_container)
        self.dataset_inner_container.setObjectName(u"dataset_inner_container")
        self.dataset_inner_container.setMaximumSize(QSize(16777215, 16777215))
        self.dataset_inner_container.setFont(font)
        self.dataset_inner_container.setStyleSheet(u"QWidget {\n"
"	background-color: #2e2e2e;\n"
"	border: 1px solid #ff9000;\n"
"	border-radius: 10px;\n"
"}")
        self.verticalLayout_3 = QVBoxLayout(self.dataset_inner_container)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(1, 1, 1, 1)
        self.label_container_header = QLabel(self.dataset_inner_container)
        self.label_container_header.setObjectName(u"label_container_header")
        self.label_container_header.setMinimumSize(QSize(0, 60))
        self.label_container_header.setMaximumSize(QSize(16777215, 60))
        font2 = QFont()
        font2.setFamilies([u"Lato"])
        font2.setPointSize(25)
        self.label_container_header.setFont(font2)
        self.label_container_header.setStyleSheet(u"border: 0px;\n"
"border-bottom: 1px solid #ff9000;\n"
"border-top-left-radius: 10px;\n"
"border-top-right-radius: 10px;\n"
"border-bottom-left-radius: 0px;\n"
"border-bottom-right-radius: 0px;\n"
"background-color: #232323;\n"
"color: #ebebeb;")
        self.label_container_header.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_3.addWidget(self.label_container_header)

        self.scrollArea_dataset = QScrollArea(self.dataset_inner_container)
        self.scrollArea_dataset.setObjectName(u"scrollArea_dataset")
        self.scrollArea_dataset.setStyleSheet(u"border: 0px;\n"
"background-color: transparent;\n"
"")
        self.scrollArea_dataset.setWidgetResizable(True)
        self.scrollArea_dataset_Contents = QWidget()
        self.scrollArea_dataset_Contents.setObjectName(u"scrollArea_dataset_Contents")
        self.scrollArea_dataset_Contents.setGeometry(QRect(0, 0, 430, 786))
        self.verticalLayout_4 = QVBoxLayout(self.scrollArea_dataset_Contents)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalSpacer = QSpacerItem(20, 585, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer)

        self.scrollArea_dataset.setWidget(self.scrollArea_dataset_Contents)

        self.verticalLayout_3.addWidget(self.scrollArea_dataset)


        self.verticalLayout_2.addWidget(self.dataset_inner_container)

        self.verticalLayout_2.setStretch(0, 1)

        self.horizontalLayout.addWidget(self.dataset_container)

        self.peak_container = QWidget(self.peakexplorer_container)
        self.peak_container.setObjectName(u"peak_container")
        self.peak_container.setMaximumSize(QSize(550, 16777215))
        self.peak_container.setStyleSheet(u"")
        self.verticalLayout_5 = QVBoxLayout(self.peak_container)
        self.verticalLayout_5.setSpacing(10)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(9, 30, -1, 9)
        self.peak_inner_container = QWidget(self.peak_container)
        self.peak_inner_container.setObjectName(u"peak_inner_container")
        self.peak_inner_container.setMaximumSize(QSize(16777215, 16777215))
        self.peak_inner_container.setFont(font)
        self.peak_inner_container.setStyleSheet(u"QWidget {\n"
"	background-color: #2e2e2e;\n"
"	border: 1px solid #ff9000;\n"
"	border-radius: 10px;\n"
"}")
        self.verticalLayout_6 = QVBoxLayout(self.peak_inner_container)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(1, 1, 1, 1)
        self.label_container_header_2 = QLabel(self.peak_inner_container)
        self.label_container_header_2.setObjectName(u"label_container_header_2")
        self.label_container_header_2.setMinimumSize(QSize(0, 60))
        self.label_container_header_2.setMaximumSize(QSize(16777215, 60))
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

        self.sorting_widget = QWidget(self.peak_inner_container)
        self.sorting_widget.setObjectName(u"sorting_widget")
        self.sorting_widget.setMinimumSize(QSize(0, 40))
        self.sorting_widget.setStyleSheet(u"border: 0px;")
        self.horizontalLayout_2 = QHBoxLayout(self.sorting_widget)
        self.horizontalLayout_2.setSpacing(15)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_sorting = QLabel(self.sorting_widget)
        self.label_sorting.setObjectName(u"label_sorting")
        self.label_sorting.setMinimumSize(QSize(0, 0))
        self.label_sorting.setMaximumSize(QSize(100, 16777215))
        font3 = QFont()
        font3.setFamilies([u"Lato"])
        font3.setPointSize(12)
        self.label_sorting.setFont(font3)
        self.label_sorting.setStyleSheet(u"color: #ebebeb;")
        self.label_sorting.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_2.addWidget(self.label_sorting)

        self.comboBox_sort_peaks = QComboBox(self.sorting_widget)
        self.comboBox_sort_peaks.addItem("")
        self.comboBox_sort_peaks.addItem("")
        self.comboBox_sort_peaks.addItem("")
        self.comboBox_sort_peaks.setObjectName(u"comboBox_sort_peaks")
        self.comboBox_sort_peaks.setMinimumSize(QSize(200, 30))
        self.comboBox_sort_peaks.setMaximumSize(QSize(200, 16777215))
        font4 = QFont()
        font4.setPointSize(12)
        self.comboBox_sort_peaks.setFont(font4)
        self.comboBox_sort_peaks.setStyleSheet(u"color: #ebebeb;\n"
"background-color: #232323;\n"
"border-top-left-radius: 0px;\n"
"border-top-right-radius: 0px;\n"
"border-bottom-left-radius: 0px;\n"
"border-bottom-right-radius: 0px;\n"
"padding-left: 10px;")

        self.horizontalLayout_2.addWidget(self.comboBox_sort_peaks)

        self.comboBox_sort_direction = QComboBox(self.sorting_widget)
        self.comboBox_sort_direction.addItem("")
        self.comboBox_sort_direction.addItem("")
        self.comboBox_sort_direction.setObjectName(u"comboBox_sort_direction")
        self.comboBox_sort_direction.setMinimumSize(QSize(100, 30))
        self.comboBox_sort_direction.setMaximumSize(QSize(100, 16777215))
        self.comboBox_sort_direction.setFont(font4)
        self.comboBox_sort_direction.setStyleSheet(u"color: #ebebeb;\n"
"background-color: #232323;\n"
"border-top-left-radius: 0px;\n"
"border-top-right-radius: 0px;\n"
"border-bottom-left-radius: 0px;\n"
"border-bottom-right-radius: 0px;\n"
"padding-left: 10px;")

        self.horizontalLayout_2.addWidget(self.comboBox_sort_direction)


        self.verticalLayout_6.addWidget(self.sorting_widget, 0, Qt.AlignmentFlag.AlignLeft)

        self.scrollArea_peak = QScrollArea(self.peak_inner_container)
        self.scrollArea_peak.setObjectName(u"scrollArea_peak")
        self.scrollArea_peak.setStyleSheet(u"border: 0px;\n"
"background-color: transparent;\n"
"")
        self.scrollArea_peak.setWidgetResizable(True)
        self.scrollArea_peak_Contents = QWidget()
        self.scrollArea_peak_Contents.setObjectName(u"scrollArea_peak_Contents")
        self.scrollArea_peak_Contents.setGeometry(QRect(0, 0, 530, 678))
        self.gridLayout = QGridLayout(self.scrollArea_peak_Contents)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setVerticalSpacing(10)
        self.verticalSpacer_2 = QSpacerItem(20, 585, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer_2, 0, 0, 1, 1)

        self.scrollArea_peak.setWidget(self.scrollArea_peak_Contents)

        self.verticalLayout_6.addWidget(self.scrollArea_peak)


        self.verticalLayout_5.addWidget(self.peak_inner_container)

        self.pushButton_export = QPushButton(self.peak_container)
        self.pushButton_export.setObjectName(u"pushButton_export")
        self.pushButton_export.setMinimumSize(QSize(0, 50))
        font5 = QFont()
        font5.setFamilies([u"Lato"])
        font5.setPointSize(20)
        self.pushButton_export.setFont(font5)
        self.pushButton_export.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.pushButton_export.setStyleSheet(u"QPushButton {\n"
"    border: 1px solid #00eaff;\n"
"    background-color: #232323; \n"
"    color: #00eaff;\n"
"    border-radius: 10px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"background-color: #131313;\n"
"}")

        self.verticalLayout_5.addWidget(self.pushButton_export)

        self.verticalLayout_5.setStretch(0, 1)

        self.horizontalLayout.addWidget(self.peak_container)

        self.preview_container = QWidget(self.peakexplorer_container)
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
        self.pushButton_toggle_peak_marker.setMinimumSize(QSize(0, 50))
        self.pushButton_toggle_peak_marker.setMaximumSize(QSize(16777215, 16777215))
        self.pushButton_toggle_peak_marker.setFont(font5)
        self.pushButton_toggle_peak_marker.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.pushButton_toggle_peak_marker.setMouseTracking(True)
        self.pushButton_toggle_peak_marker.setTabletTracking(False)
        self.pushButton_toggle_peak_marker.setStyleSheet(u"QPushButton {\n"
"    border: 1px solid #ff9000;\n"
"    background-color: #232323; \n"
"    color: #ff9000;\n"
"    border-radius: 10px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"background-color: #131313;\n"
"}")
        self.pushButton_toggle_peak_marker.setAutoDefault(False)

        self.verticalLayout_7.addWidget(self.pushButton_toggle_peak_marker)


        self.horizontalLayout.addWidget(self.preview_container)


        self.verticalLayout.addWidget(self.peakexplorer_container)

        self.verticalLayout.setStretch(1, 1)

        self.retranslateUi(PeakExplorerWidget)

        self.pushButton_toggle_peak_marker.setDefault(False)


        QMetaObject.connectSlotsByName(PeakExplorerWidget)
    # setupUi

    def retranslateUi(self, PeakExplorerWidget):
        PeakExplorerWidget.setWindowTitle(QCoreApplication.translate("PeakExplorerWidget", u"Form", None))
        self.label_header.setText(QCoreApplication.translate("PeakExplorerWidget", u"Peak Explorer", None))
        self.label_container_header.setText(QCoreApplication.translate("PeakExplorerWidget", u"Dataset", None))
        self.label_container_header_2.setText(QCoreApplication.translate("PeakExplorerWidget", u"Peaks", None))
        self.label_sorting.setText(QCoreApplication.translate("PeakExplorerWidget", u"Sorting:", None))
        self.comboBox_sort_peaks.setItemText(0, QCoreApplication.translate("PeakExplorerWidget", u"Drift time", None))
        self.comboBox_sort_peaks.setItemText(1, QCoreApplication.translate("PeakExplorerWidget", u"Retention time", None))
        self.comboBox_sort_peaks.setItemText(2, QCoreApplication.translate("PeakExplorerWidget", u"Active", None))

        self.comboBox_sort_direction.setItemText(0, QCoreApplication.translate("PeakExplorerWidget", u"ASC", None))
        self.comboBox_sort_direction.setItemText(1, QCoreApplication.translate("PeakExplorerWidget", u"DESC", None))

        self.pushButton_export.setText(QCoreApplication.translate("PeakExplorerWidget", u"Export peak data", None))
        self.label_preview.setText(QCoreApplication.translate("PeakExplorerWidget", u"Spectrum preview", None))
        self.pushButton_toggle_peak_marker.setText(QCoreApplication.translate("PeakExplorerWidget", u"Hide peak markers", None))
    # retranslateUi

