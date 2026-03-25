# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'DatasetWidget.ui'
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
    QScrollArea, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_DatasetWidget(object):
    def setupUi(self, DatasetWidget):
        if not DatasetWidget.objectName():
            DatasetWidget.setObjectName(u"DatasetWidget")
        DatasetWidget.resize(1536, 989)
        font = QFont()
        font.setWeight(QFont.Black)
        DatasetWidget.setFont(font)
        DatasetWidget.setStyleSheet(u"background-color: #1d1d1d;")
        self.verticalLayout = QVBoxLayout(DatasetWidget)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(40, 20, 20, 20)
        self.label_header = QLabel(DatasetWidget)
        self.label_header.setObjectName(u"label_header")
        self.label_header.setMaximumSize(QSize(16777215, 80))
        font1 = QFont()
        font1.setFamilies([u"Lato"])
        font1.setPointSize(35)
        font1.setKerning(True)
        self.label_header.setFont(font1)
        self.label_header.setStyleSheet(u"color: #ebebeb;")
        self.label_header.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout.addWidget(self.label_header, 0, Qt.AlignmentFlag.AlignTop)

        self.label_subheader = QLabel(DatasetWidget)
        self.label_subheader.setObjectName(u"label_subheader")
        self.label_subheader.setMaximumSize(QSize(1500, 200))
        font2 = QFont()
        font2.setFamilies([u"Lato"])
        font2.setPointSize(15)
        font2.setWeight(QFont.Light)
        font2.setKerning(True)
        self.label_subheader.setFont(font2)
        self.label_subheader.setStyleSheet(u"color: #9e9e9e;")
        self.label_subheader.setScaledContents(False)
        self.label_subheader.setAlignment(Qt.AlignmentFlag.AlignJustify|Qt.AlignmentFlag.AlignVCenter)
        self.label_subheader.setWordWrap(True)

        self.verticalLayout.addWidget(self.label_subheader, 0, Qt.AlignmentFlag.AlignTop)

        self.dataset_container = QWidget(DatasetWidget)
        self.dataset_container.setObjectName(u"dataset_container")
        self.horizontalLayout = QHBoxLayout(self.dataset_container)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.labels_outer_container = QWidget(self.dataset_container)
        self.labels_outer_container.setObjectName(u"labels_outer_container")
        self.labels_outer_container.setMaximumSize(QSize(500, 16777215))
        self.labels_outer_container.setStyleSheet(u"")
        self.verticalLayout_2 = QVBoxLayout(self.labels_outer_container)
        self.verticalLayout_2.setSpacing(10)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(9, 30, -1, 9)
        self.labels_inner_container = QWidget(self.labels_outer_container)
        self.labels_inner_container.setObjectName(u"labels_inner_container")
        self.labels_inner_container.setMaximumSize(QSize(16777215, 16777215))
        self.labels_inner_container.setFont(font)
        self.labels_inner_container.setStyleSheet(u"QWidget {\n"
"	background-color: #2e2e2e;\n"
"	border: 1px solid #ff9000;\n"
"	border-radius: 10px;\n"
"}")
        self.verticalLayout_3 = QVBoxLayout(self.labels_inner_container)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(1, 1, 1, 1)
        self.label_container_header = QLabel(self.labels_inner_container)
        self.label_container_header.setObjectName(u"label_container_header")
        self.label_container_header.setMinimumSize(QSize(0, 50))
        self.label_container_header.setMaximumSize(QSize(16777215, 50))
        font3 = QFont()
        font3.setFamilies([u"Lato"])
        font3.setPointSize(25)
        self.label_container_header.setFont(font3)
        self.label_container_header.setStyleSheet(u"border: 0px;\n"
"border-bottom: 1px solid #ff9000;\n"
"border-top-left-radius: 10px;\n"
"border-top-right-radius: 10px;\n"
"border-bottom-left-radius: 0px;\n"
"border-bottom-right-radius: 0px;\n"
"background-color: #232323;")
        self.label_container_header.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_3.addWidget(self.label_container_header)

        self.scrollArea_labels = QScrollArea(self.labels_inner_container)
        self.scrollArea_labels.setObjectName(u"scrollArea_labels")
        self.scrollArea_labels.setStyleSheet(u"border: 0px;\n"
"border-radius: 0px;")
        self.scrollArea_labels.setWidgetResizable(True)
        self.scrollArea_labels_Contents = QWidget()
        self.scrollArea_labels_Contents.setObjectName(u"scrollArea_labels_Contents")
        self.scrollArea_labels_Contents.setGeometry(QRect(0, 0, 480, 626))
        self.verticalLayout_4 = QVBoxLayout(self.scrollArea_labels_Contents)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalSpacer = QSpacerItem(20, 605, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer)

        self.scrollArea_labels.setWidget(self.scrollArea_labels_Contents)

        self.verticalLayout_3.addWidget(self.scrollArea_labels)

        self.button_add_label = QPushButton(self.labels_inner_container)
        self.button_add_label.setObjectName(u"button_add_label")
        self.button_add_label.setMinimumSize(QSize(0, 50))
        self.button_add_label.setMaximumSize(QSize(16777215, 50))
        self.button_add_label.setFont(font3)
        self.button_add_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.button_add_label.setAutoFillBackground(False)
        self.button_add_label.setStyleSheet(u"border: 0px;\n"
"border-top: 1px solid #ff9000;\n"
"border-top-left-radius: 0px;\n"
"border-top-right-radius: 0px;\n"
"border-bottom-left-radius: 10px;\n"
"border-bottom-right-radius: 10px;\n"
"background-color: #232323;")
        icon = QIcon()
        icon.addFile(u"ui/_pics/icons/add_circle_white.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.button_add_label.setIcon(icon)
        self.button_add_label.setIconSize(QSize(35, 35))

        self.verticalLayout_3.addWidget(self.button_add_label)


        self.verticalLayout_2.addWidget(self.labels_inner_container)

        self.label_labelcounter = QLabel(self.labels_outer_container)
        self.label_labelcounter.setObjectName(u"label_labelcounter")
        self.label_labelcounter.setMaximumSize(QSize(16777215, 30))
        font4 = QFont()
        font4.setFamilies([u"Lato"])
        font4.setPointSize(15)
        font4.setWeight(QFont.Light)
        self.label_labelcounter.setFont(font4)
        self.label_labelcounter.setStyleSheet(u"color: #9e9e9e;")
        self.label_labelcounter.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_2.addWidget(self.label_labelcounter)

        self.verticalLayout_2.setStretch(0, 1)

        self.horizontalLayout.addWidget(self.labels_outer_container)

        self.spectra_container = QWidget(self.dataset_container)
        self.spectra_container.setObjectName(u"spectra_container")
        self.spectra_container.setMaximumSize(QSize(500, 16777215))
        self.spectra_container.setStyleSheet(u"")

        self.horizontalLayout.addWidget(self.spectra_container)

        self.preview_container = QWidget(self.dataset_container)
        self.preview_container.setObjectName(u"preview_container")
        self.preview_container.setStyleSheet(u"")

        self.horizontalLayout.addWidget(self.preview_container)


        self.verticalLayout.addWidget(self.dataset_container)

        self.verticalLayout.setStretch(2, 1)

        self.retranslateUi(DatasetWidget)

        QMetaObject.connectSlotsByName(DatasetWidget)
    # setupUi

    def retranslateUi(self, DatasetWidget):
        DatasetWidget.setWindowTitle(QCoreApplication.translate("DatasetWidget", u"Form", None))
        self.label_header.setText(QCoreApplication.translate("DatasetWidget", u"Dataset and labels", None))
        self.label_subheader.setText(QCoreApplication.translate("DatasetWidget", u"<html><head/><body><p>The Dataset and the corresponding labels of this project are defined here. The dataset is defined as the total number of GC-IMS spectra used in this project. Each of these spectra must be assigned to a label of your choice. For exampel: If you are analyzing different honey spectra, you would use the destinct honey types as labels, such as \u201acanola\u2018, \u201aacacia\u2018 ,manuka\u2018 ... ect. Correct labeling is of uttermost importance, since the calssification algorithm needs this information to work properly!</p></body></html>", None))
        self.label_container_header.setText(QCoreApplication.translate("DatasetWidget", u"Labels", None))
        self.button_add_label.setText(QCoreApplication.translate("DatasetWidget", u"Add label", None))
        self.label_labelcounter.setText(QCoreApplication.translate("DatasetWidget", u"0 labels", None))
    # retranslateUi

