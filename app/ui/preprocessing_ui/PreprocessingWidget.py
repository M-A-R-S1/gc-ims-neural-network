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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_PreprocessingWidget(object):
    def setupUi(self, PreprocessingWidget):
        if not PreprocessingWidget.objectName():
            PreprocessingWidget.setObjectName(u"PreprocessingWidget")
        PreprocessingWidget.resize(1729, 1095)
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
        self.label_subheader.setMinimumSize(QSize(0, 40))
        self.label_subheader.setMaximumSize(QSize(1500, 200))
        font2 = QFont()
        font2.setFamilies([u"Lato"])
        font2.setPointSize(14)
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

        self.options_container = QWidget(self.preprocessing_container)
        self.options_container.setObjectName(u"options_container")
        self.options_container.setMaximumSize(QSize(400, 16777215))
        self.options_container.setStyleSheet(u"")
        self.verticalLayout_7 = QVBoxLayout(self.options_container)
        self.verticalLayout_7.setSpacing(15)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(-1, 80, -1, -1)
        self.options_inner_container = QWidget(self.options_container)
        self.options_inner_container.setObjectName(u"options_inner_container")
        self.options_inner_container.setMaximumSize(QSize(16777215, 16777215))
        self.options_inner_container.setFont(font)
        self.options_inner_container.setStyleSheet(u"")
        self.verticalLayout_5 = QVBoxLayout(self.options_inner_container)
        self.verticalLayout_5.setSpacing(6)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(1, 1, 1, 1)
        self.options_container_header = QLabel(self.options_inner_container)
        self.options_container_header.setObjectName(u"options_container_header")
        self.options_container_header.setMinimumSize(QSize(0, 60))
        font4 = QFont()
        font4.setFamilies([u"Lato"])
        font4.setPointSize(25)
        font4.setBold(False)
        self.options_container_header.setFont(font4)
        self.options_container_header.setStyleSheet(u"border-bottom: 1px solid #666666;\n"
"color: #ebebeb;")

        self.verticalLayout_5.addWidget(self.options_container_header)

        self.label_retentiontime = QLabel(self.options_inner_container)
        self.label_retentiontime.setObjectName(u"label_retentiontime")
        self.label_retentiontime.setMinimumSize(QSize(0, 50))
        self.label_retentiontime.setMaximumSize(QSize(16777215, 40))
        font5 = QFont()
        font5.setFamilies([u"Lato"])
        font5.setPointSize(20)
        font5.setWeight(QFont.Light)
        self.label_retentiontime.setFont(font5)
        self.label_retentiontime.setStyleSheet(u"color: #ebebeb;")

        self.verticalLayout_5.addWidget(self.label_retentiontime)

        self.widget_retentiontime_inputs = QWidget(self.options_inner_container)
        self.widget_retentiontime_inputs.setObjectName(u"widget_retentiontime_inputs")
        self.widget_retentiontime_inputs.setMinimumSize(QSize(0, 0))
        self.widget_retentiontime_inputs.setMaximumSize(QSize(16777215, 16777215))
        self.horizontalLayout_2 = QHBoxLayout(self.widget_retentiontime_inputs)
        self.horizontalLayout_2.setSpacing(20)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, -1, 0, 6)
        self.lineEdit_retention_start_cut = QLineEdit(self.widget_retentiontime_inputs)
        self.lineEdit_retention_start_cut.setObjectName(u"lineEdit_retention_start_cut")
        self.lineEdit_retention_start_cut.setMinimumSize(QSize(0, 40))
        self.lineEdit_retention_start_cut.setMaximumSize(QSize(150, 16777215))
        font6 = QFont()
        font6.setFamilies([u"Lato"])
        font6.setPointSize(13)
        self.lineEdit_retention_start_cut.setFont(font6)
        self.lineEdit_retention_start_cut.setStyleSheet(u"QLineEdit {\n"
"    border: 1px solid #ff9000;\n"
"    background-color: #232323; \n"
"    color: #9e9e9e;\n"
"    border-radius: 10px;\n"
"   padding-left: 10px;\n"
"}\n"
"")

        self.horizontalLayout_2.addWidget(self.lineEdit_retention_start_cut)

        self.lineEdit_retention_end_cut = QLineEdit(self.widget_retentiontime_inputs)
        self.lineEdit_retention_end_cut.setObjectName(u"lineEdit_retention_end_cut")
        self.lineEdit_retention_end_cut.setMinimumSize(QSize(0, 40))
        self.lineEdit_retention_end_cut.setMaximumSize(QSize(150, 16777215))
        self.lineEdit_retention_end_cut.setFont(font6)
        self.lineEdit_retention_end_cut.setStyleSheet(u"QLineEdit {\n"
"    border: 1px solid #ff9000;\n"
"    background-color: #232323; \n"
"    color: #9e9e9e;\n"
"    border-radius: 10px;\n"
"   padding-left: 10px;\n"
"}\n"
"")

        self.horizontalLayout_2.addWidget(self.lineEdit_retention_end_cut)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)


        self.verticalLayout_5.addWidget(self.widget_retentiontime_inputs)

        self.label_drifttime = QLabel(self.options_inner_container)
        self.label_drifttime.setObjectName(u"label_drifttime")
        self.label_drifttime.setMinimumSize(QSize(0, 50))
        self.label_drifttime.setFont(font5)
        self.label_drifttime.setStyleSheet(u"color: #ebebeb;")
        self.label_drifttime.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft)

        self.verticalLayout_5.addWidget(self.label_drifttime)

        self.widget_drifttime_inputs = QWidget(self.options_inner_container)
        self.widget_drifttime_inputs.setObjectName(u"widget_drifttime_inputs")
        self.widget_drifttime_inputs.setMinimumSize(QSize(0, 0))
        self.widget_drifttime_inputs.setStyleSheet(u"")
        self.horizontalLayout_3 = QHBoxLayout(self.widget_drifttime_inputs)
        self.horizontalLayout_3.setSpacing(20)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, -1, 0, 6)
        self.lineEdit_drift_start_cut = QLineEdit(self.widget_drifttime_inputs)
        self.lineEdit_drift_start_cut.setObjectName(u"lineEdit_drift_start_cut")
        self.lineEdit_drift_start_cut.setMinimumSize(QSize(0, 40))
        self.lineEdit_drift_start_cut.setMaximumSize(QSize(150, 16777215))
        self.lineEdit_drift_start_cut.setFont(font6)
        self.lineEdit_drift_start_cut.setStyleSheet(u"QLineEdit {\n"
"    border: 1px solid #ff9000;\n"
"    background-color: #232323; \n"
"    color: #9e9e9e;\n"
"    border-radius: 10px;\n"
"   padding-left: 10px;\n"
"}\n"
"")

        self.horizontalLayout_3.addWidget(self.lineEdit_drift_start_cut)

        self.lineEdit_drift_end_cut = QLineEdit(self.widget_drifttime_inputs)
        self.lineEdit_drift_end_cut.setObjectName(u"lineEdit_drift_end_cut")
        self.lineEdit_drift_end_cut.setMinimumSize(QSize(0, 40))
        self.lineEdit_drift_end_cut.setMaximumSize(QSize(150, 16777215))
        self.lineEdit_drift_end_cut.setFont(font6)
        self.lineEdit_drift_end_cut.setStyleSheet(u"QLineEdit {\n"
"    border: 1px solid #ff9000;\n"
"    background-color: #232323; \n"
"    color: #9e9e9e;\n"
"    border-radius: 10px;\n"
"   padding-left: 10px;\n"
"}\n"
"")

        self.horizontalLayout_3.addWidget(self.lineEdit_drift_end_cut)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)


        self.verticalLayout_5.addWidget(self.widget_drifttime_inputs)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_5.addItem(self.verticalSpacer_2)

        self.start_processing_container = QWidget(self.options_inner_container)
        self.start_processing_container.setObjectName(u"start_processing_container")
        self.start_processing_container.setMinimumSize(QSize(0, 180))
        self.start_processing_container.setStyleSheet(u"background-color: #2e2e2e;")
        self.verticalLayout_6 = QVBoxLayout(self.start_processing_container)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(30, 30, 30, 30)
        self.pushButton_start_processing = QPushButton(self.start_processing_container)
        self.pushButton_start_processing.setObjectName(u"pushButton_start_processing")
        self.pushButton_start_processing.setMinimumSize(QSize(0, 50))
        font7 = QFont()
        font7.setFamilies([u"Lato"])
        font7.setPointSize(20)
        self.pushButton_start_processing.setFont(font7)
        self.pushButton_start_processing.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.pushButton_start_processing.setStyleSheet(u"QPushButton {\n"
"    border: 1px solid #00eaff;\n"
"    background-color: #232323; \n"
"    color: #00eaff;\n"
"    border-radius: 10px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"background-color: #131313;\n"
"}")

        self.verticalLayout_6.addWidget(self.pushButton_start_processing)

        self.label_processing_info = QLabel(self.start_processing_container)
        self.label_processing_info.setObjectName(u"label_processing_info")
        font8 = QFont()
        font8.setFamilies([u"Lato"])
        font8.setPointSize(10)
        self.label_processing_info.setFont(font8)
        self.label_processing_info.setStyleSheet(u"color: #9e9e9e;")
        self.label_processing_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_processing_info.setWordWrap(True)

        self.verticalLayout_6.addWidget(self.label_processing_info)


        self.verticalLayout_5.addWidget(self.start_processing_container)


        self.verticalLayout_7.addWidget(self.options_inner_container)

        self.label_process_info = QLabel(self.options_container)
        self.label_process_info.setObjectName(u"label_process_info")
        self.label_process_info.setEnabled(True)
        self.label_process_info.setMinimumSize(QSize(0, 70))
        font9 = QFont()
        font9.setFamilies([u"Lato"])
        font9.setPointSize(12)
        font9.setItalic(False)
        self.label_process_info.setFont(font9)
        self.label_process_info.setStyleSheet(u"border: 1.5px dashed #00eaff;\n"
"background-color: #232323; \n"
"color: #00eaff;\n"
"margin-bottom: 10px;")
        self.label_process_info.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_7.addWidget(self.label_process_info)


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

        self.pushButton_toggle_canvas_area = QPushButton(self.preview_container)
        self.pushButton_toggle_canvas_area.setObjectName(u"pushButton_toggle_canvas_area")
        self.pushButton_toggle_canvas_area.setEnabled(False)
        self.pushButton_toggle_canvas_area.setMinimumSize(QSize(0, 50))
        self.pushButton_toggle_canvas_area.setFont(font7)
        self.pushButton_toggle_canvas_area.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.pushButton_toggle_canvas_area.setStyleSheet(u"QPushButton {\n"
"    border: 1px solid #666666;\n"
"    background-color: #232323; \n"
"    color: #666666;\n"
"    border-radius: 10px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"background-color: #131313;\n"
"}")

        self.verticalLayout_8.addWidget(self.pushButton_toggle_canvas_area)


        self.horizontalLayout.addWidget(self.preview_container)


        self.verticalLayout.addWidget(self.preprocessing_container)

        self.verticalLayout.setStretch(2, 1)

        self.retranslateUi(PreprocessingWidget)

        QMetaObject.connectSlotsByName(PreprocessingWidget)
    # setupUi

    def retranslateUi(self, PreprocessingWidget):
        PreprocessingWidget.setWindowTitle(QCoreApplication.translate("PreprocessingWidget", u"Form", None))
        self.label_header.setText(QCoreApplication.translate("PreprocessingWidget", u"Preprocessing", None))
        self.label_subheader.setText(QCoreApplication.translate("PreprocessingWidget", u"<html><head/><body><p>This step processes the raw spectra of the dataset. Preprocessing involves the following tasks:<br/>- Retention- and Drifttime region of interest<br/>- Background noise reduction<br/>- Application of a smoothing filter</p></body></html>", None))
        self.label_container_header.setText(QCoreApplication.translate("PreprocessingWidget", u"Dataset", None))
        self.options_container_header.setText(QCoreApplication.translate("PreprocessingWidget", u"Region of interest", None))
        self.label_retentiontime.setText(QCoreApplication.translate("PreprocessingWidget", u"Retentiontime [s]", None))
        self.lineEdit_retention_start_cut.setPlaceholderText(QCoreApplication.translate("PreprocessingWidget", u"Start ", None))
        self.lineEdit_retention_end_cut.setText("")
        self.lineEdit_retention_end_cut.setPlaceholderText(QCoreApplication.translate("PreprocessingWidget", u"End", None))
        self.label_drifttime.setText(QCoreApplication.translate("PreprocessingWidget", u"Drifttime [ms]", None))
        self.lineEdit_drift_start_cut.setPlaceholderText(QCoreApplication.translate("PreprocessingWidget", u"Start ", None))
        self.lineEdit_drift_end_cut.setText("")
        self.lineEdit_drift_end_cut.setPlaceholderText(QCoreApplication.translate("PreprocessingWidget", u"End", None))
        self.pushButton_start_processing.setText(QCoreApplication.translate("PreprocessingWidget", u"Start preprocessing", None))
        self.label_processing_info.setText(QCoreApplication.translate("PreprocessingWidget", u"This will start the preprocessing of the dataset. Notice that this task may take a while, depending on the size of the dataset and the used computer.", None))
        self.label_process_info.setText(QCoreApplication.translate("PreprocessingWidget", u"All spectra processed", None))
        self.label_preview.setText(QCoreApplication.translate("PreprocessingWidget", u"Spectrum preview", None))
        self.pushButton_toggle_canvas_area.setText(QCoreApplication.translate("PreprocessingWidget", u"Show region of interest", None))
    # retranslateUi

