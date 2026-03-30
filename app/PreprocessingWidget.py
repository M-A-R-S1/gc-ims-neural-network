# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'PreprocessingWidget.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QScrollArea,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_PreprocessingWidget(object):
    def setupUi(self, PreprocessingWidget):
        if not PreprocessingWidget.objectName():
            PreprocessingWidget.setObjectName(u"PreprocessingWidget")
        PreprocessingWidget.resize(1536, 989)
        font = QFont()
        font.setWeight(QFont.Black)
        PreprocessingWidget.setFont(font)
        PreprocessingWidget.setStyleSheet(u"background-color: #1d1d1d;")
        self.verticalLayout = QVBoxLayout(PreprocessingWidget)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(40, 20, 20, 20)
        self.label_header = QLabel(PreprocessingWidget)
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

        self.label_subheader = QLabel(PreprocessingWidget)
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

        self.preprocessing_container = QWidget(PreprocessingWidget)
        self.preprocessing_container.setObjectName(u"preprocessing_container")
        self.horizontalLayout = QHBoxLayout(self.preprocessing_container)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.dataset_container = QWidget(self.preprocessing_container)
        self.dataset_container.setObjectName(u"dataset_container")
        self.dataset_container.setMaximumSize(QSize(500, 16777215))
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
        self.scrollArea_dataset_Contents.setGeometry(QRect(0, 0, 480, 676))
        self.verticalLayout_4 = QVBoxLayout(self.scrollArea_dataset_Contents)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalSpacer = QSpacerItem(20, 585, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer)

        self.scrollArea_dataset.setWidget(self.scrollArea_dataset_Contents)

        self.verticalLayout_3.addWidget(self.scrollArea_dataset)


        self.verticalLayout_2.addWidget(self.dataset_inner_container)

        self.verticalLayout_2.setStretch(0, 1)

        self.horizontalLayout.addWidget(self.dataset_container)

        self.options_container = QWidget(self.preprocessing_container)
        self.options_container.setObjectName(u"options_container")
        self.options_container.setMaximumSize(QSize(600, 16777215))
        self.options_container.setStyleSheet(u"")

        self.horizontalLayout.addWidget(self.options_container)

        self.preview_container = QWidget(self.preprocessing_container)
        self.preview_container.setObjectName(u"preview_container")
        self.preview_container.setStyleSheet(u"")
        self.verticalLayout_8 = QVBoxLayout(self.preview_container)
        self.verticalLayout_8.setSpacing(10)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(-1, 40, -1, -1)
        self.label_preview = QLabel(self.preview_container)
        self.label_preview.setObjectName(u"label_preview")
        self.label_preview.setMaximumSize(QSize(16777215, 40))
        self.label_preview.setFont(font3)
        self.label_preview.setStyleSheet(u"color: #ebebeb;")
        self.label_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_8.addWidget(self.label_preview)

        self.preview_image = QWidget(self.preview_container)
        self.preview_image.setObjectName(u"preview_image")
        self.preview_image.setStyleSheet(u"background-color: #191919;\n"
" border: none;")

        self.verticalLayout_8.addWidget(self.preview_image)


        self.horizontalLayout.addWidget(self.preview_container)


        self.verticalLayout.addWidget(self.preprocessing_container)

        self.verticalLayout.setStretch(2, 1)

        self.retranslateUi(PreprocessingWidget)

        QMetaObject.connectSlotsByName(PreprocessingWidget)
    # setupUi

    def retranslateUi(self, PreprocessingWidget):
        PreprocessingWidget.setWindowTitle(QCoreApplication.translate("PreprocessingWidget", u"Form", None))
        self.label_header.setText(QCoreApplication.translate("PreprocessingWidget", u"Preprocessing", None))
        self.label_subheader.setText(QCoreApplication.translate("PreprocessingWidget", u"<html><head/><body><p>This step processes the raw spectra of the dataset. Preprocessing involves the following tasks:<br/>- Retention- and Drifttime cut<br/>- Background noise reduction<br/>- Application of a smoothing filter</p></body></html>", None))
        self.label_container_header.setText(QCoreApplication.translate("PreprocessingWidget", u"Dataset", None))
        self.label_preview.setText(QCoreApplication.translate("PreprocessingWidget", u"Spectrum preview", None))
    # retranslateUi

