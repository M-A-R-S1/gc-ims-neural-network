# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ModelWidget.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QGridLayout,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QScrollArea, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_ModelWidget(object):
    def setupUi(self, ModelWidget):
        if not ModelWidget.objectName():
            ModelWidget.setObjectName(u"ModelWidget")
        ModelWidget.resize(1741, 993)
        font = QFont()
        font.setWeight(QFont.Black)
        ModelWidget.setFont(font)
        ModelWidget.setStyleSheet(u"background-color: #1d1d1d;")
        self.verticalLayout = QVBoxLayout(ModelWidget)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(40, 20, 20, 20)
        self.label_header = QLabel(ModelWidget)
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

        self.model_container = QWidget(ModelWidget)
        self.model_container.setObjectName(u"model_container")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.model_container.sizePolicy().hasHeightForWidth())
        self.model_container.setSizePolicy(sizePolicy)
        self.model_container.setMinimumSize(QSize(0, 0))
        self.horizontalLayout = QHBoxLayout(self.model_container)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.model_list_container = QWidget(self.model_container)
        self.model_list_container.setObjectName(u"model_list_container")
        sizePolicy.setHeightForWidth(self.model_list_container.sizePolicy().hasHeightForWidth())
        self.model_list_container.setSizePolicy(sizePolicy)
        self.model_list_container.setMinimumSize(QSize(0, 0))
        self.model_list_container.setMaximumSize(QSize(550, 16777215))
        self.model_list_container.setStyleSheet(u"")
        self.verticalLayout_5 = QVBoxLayout(self.model_list_container)
        self.verticalLayout_5.setSpacing(20)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(9, 30, -1, 9)
        self.model_list_inner_container = QWidget(self.model_list_container)
        self.model_list_inner_container.setObjectName(u"model_list_inner_container")
        sizePolicy.setHeightForWidth(self.model_list_inner_container.sizePolicy().hasHeightForWidth())
        self.model_list_inner_container.setSizePolicy(sizePolicy)
        self.model_list_inner_container.setMinimumSize(QSize(0, 400))
        self.model_list_inner_container.setMaximumSize(QSize(16777215, 16777215))
        self.model_list_inner_container.setFont(font)
        self.model_list_inner_container.setStyleSheet(u"QWidget {\n"
"	background-color: #2e2e2e;\n"
"	border: 1px solid #ff9000;\n"
"	border-radius: 10px;\n"
"}")
        self.verticalLayout_6 = QVBoxLayout(self.model_list_inner_container)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(1, 1, 1, 1)
        self.label_container_header_2 = QLabel(self.model_list_inner_container)
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

        self.scrollArea_models = QScrollArea(self.model_list_inner_container)
        self.scrollArea_models.setObjectName(u"scrollArea_models")
        self.scrollArea_models.setStyleSheet(u"border: 0px;\n"
"background-color: transparent;\n"
"")
        self.scrollArea_models.setWidgetResizable(True)
        self.scrollArea_models_Contents = QWidget()
        self.scrollArea_models_Contents.setObjectName(u"scrollArea_models_Contents")
        self.scrollArea_models_Contents.setGeometry(QRect(0, 0, 530, 378))
        self.gridLayout = QGridLayout(self.scrollArea_models_Contents)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setVerticalSpacing(10)
        self.verticalSpacer_2 = QSpacerItem(20, 585, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer_2, 0, 0, 1, 1)

        self.scrollArea_models.setWidget(self.scrollArea_models_Contents)

        self.verticalLayout_6.addWidget(self.scrollArea_models)


        self.verticalLayout_5.addWidget(self.model_list_inner_container)

        self.frame_new_model = QFrame(self.model_list_container)
        self.frame_new_model.setObjectName(u"frame_new_model")
        sizePolicy.setHeightForWidth(self.frame_new_model.sizePolicy().hasHeightForWidth())
        self.frame_new_model.setSizePolicy(sizePolicy)
        self.frame_new_model.setMinimumSize(QSize(0, 370))
        self.frame_new_model.setMaximumSize(QSize(16777215, 370))
        self.frame_new_model.setStyleSheet(u".QFrame  {\n"
"	background-color: #2e2e2e;\n"
"	border: 1px solid #ff9000;\n"
"	border-radius: 10px;\n"
"}\n"
"")
        self.frame_new_model.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_new_model.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame_new_model)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(30, 10, 30, 10)
        self.label_header_2 = QLabel(self.frame_new_model)
        self.label_header_2.setObjectName(u"label_header_2")
        self.label_header_2.setFont(font2)
        self.label_header_2.setStyleSheet(u"color: #ebebeb;\n"
"background-color: #2e2e2e;")
        self.label_header_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_2.addWidget(self.label_header_2)

        self.lineEdit_name = QLineEdit(self.frame_new_model)
        self.lineEdit_name.setObjectName(u"lineEdit_name")
        self.lineEdit_name.setMinimumSize(QSize(0, 50))
        self.lineEdit_name.setMaximumSize(QSize(16777215, 16777215))
        font3 = QFont()
        font3.setFamilies([u"Lato"])
        font3.setPointSize(12)
        font3.setWeight(QFont.Light)
        self.lineEdit_name.setFont(font3)
        self.lineEdit_name.setStyleSheet(u"QLineEdit {\n"
"    border: 1px solid #ff9000;\n"
"    background-color: #232323; \n"
"    color: #9e9e9e;\n"
"    border-radius: 10px;\n"
"   padding-left: 10px;\n"
"}\n"
"")

        self.verticalLayout_2.addWidget(self.lineEdit_name)

        self.model_epoch_container = QWidget(self.frame_new_model)
        self.model_epoch_container.setObjectName(u"model_epoch_container")
        self.model_epoch_container.setStyleSheet(u"background-color: #2e2e2e;")
        self.horizontalLayout_2 = QHBoxLayout(self.model_epoch_container)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(9, -1, 0, -1)
        self.label_epochs = QLabel(self.model_epoch_container)
        self.label_epochs.setObjectName(u"label_epochs")
        self.label_epochs.setMinimumSize(QSize(0, 0))
        self.label_epochs.setMaximumSize(QSize(150, 40))
        font4 = QFont()
        font4.setFamilies([u"Lato"])
        font4.setPointSize(12)
        self.label_epochs.setFont(font4)
        self.label_epochs.setStyleSheet(u"color: #ebebeb;\n"
"background-color: #2e2e2e;")
        self.label_epochs.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_2.addWidget(self.label_epochs)

        self.comboBox_epochs = QComboBox(self.model_epoch_container)
        self.comboBox_epochs.addItem("")
        self.comboBox_epochs.addItem("")
        self.comboBox_epochs.addItem("")
        self.comboBox_epochs.addItem("")
        self.comboBox_epochs.addItem("")
        self.comboBox_epochs.addItem("")
        self.comboBox_epochs.setObjectName(u"comboBox_epochs")
        self.comboBox_epochs.setMinimumSize(QSize(200, 40))
        self.comboBox_epochs.setMaximumSize(QSize(20000, 40))
        self.comboBox_epochs.setFont(font4)
        self.comboBox_epochs.setStyleSheet(u"QComboBox {\n"
"    border: 1px solid #ff9000;\n"
"    background-color: #232323; \n"
"    color: #9e9e9e;\n"
"    border-radius: 10px;\n"
"    padding-left: 10px;\n"
"}\n"
"\n"
"QComboBox::drop-down {\n"
"	border-radius: 10px;\n"
"}\n"
"\n"
"    \n"
"\n"
"")

        self.horizontalLayout_2.addWidget(self.comboBox_epochs)


        self.verticalLayout_2.addWidget(self.model_epoch_container)

        self.model_device_container = QWidget(self.frame_new_model)
        self.model_device_container.setObjectName(u"model_device_container")
        self.model_device_container.setStyleSheet(u"background-color: #2e2e2e;")
        self.horizontalLayout_4 = QHBoxLayout(self.model_device_container)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(-1, -1, 0, -1)
        self.label_device = QLabel(self.model_device_container)
        self.label_device.setObjectName(u"label_device")
        self.label_device.setMinimumSize(QSize(0, 0))
        self.label_device.setMaximumSize(QSize(150, 40))
        self.label_device.setFont(font4)
        self.label_device.setStyleSheet(u"color: #ebebeb;\n"
"background-color: #2e2e2e;")
        self.label_device.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_4.addWidget(self.label_device)

        self.comboBox_device = QComboBox(self.model_device_container)
        self.comboBox_device.setObjectName(u"comboBox_device")
        self.comboBox_device.setMinimumSize(QSize(200, 40))
        self.comboBox_device.setMaximumSize(QSize(20000, 40))
        self.comboBox_device.setFont(font4)
        self.comboBox_device.setStyleSheet(u"QComboBox {\n"
"    border: 1px solid #ff9000;\n"
"    background-color: #232323; \n"
"    color: #9e9e9e;\n"
"    border-radius: 10px;\n"
"    padding-left: 10px;\n"
"}\n"
"\n"
"QComboBox::drop-down {\n"
"	border-radius: 10px;\n"
"}")

        self.horizontalLayout_4.addWidget(self.comboBox_device)


        self.verticalLayout_2.addWidget(self.model_device_container)

        self.label_model_info = QLabel(self.frame_new_model)
        self.label_model_info.setObjectName(u"label_model_info")
        font5 = QFont()
        font5.setFamilies([u"Lato"])
        font5.setPointSize(12)
        font5.setWeight(QFont.Light)
        font5.setKerning(True)
        self.label_model_info.setFont(font5)
        self.label_model_info.setStyleSheet(u"color: #9e9e9e;\n"
"background-color: #2e2e2e;\n"
"margin-bottom: 5px;")
        self.label_model_info.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)

        self.verticalLayout_2.addWidget(self.label_model_info)

        self.pushButton_train_model = QPushButton(self.frame_new_model)
        self.pushButton_train_model.setObjectName(u"pushButton_train_model")
        self.pushButton_train_model.setMinimumSize(QSize(0, 50))
        font6 = QFont()
        font6.setFamilies([u"Lato"])
        font6.setPointSize(20)
        font6.setWeight(QFont.Light)
        self.pushButton_train_model.setFont(font6)
        self.pushButton_train_model.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.pushButton_train_model.setStyleSheet(u"QPushButton {\n"
"    border: 1px solid #00eaff;\n"
"    background-color: #232323; \n"
"    color: #00eaff;\n"
"    border-radius: 10px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	background-color: #131313;\n"
"}")

        self.verticalLayout_2.addWidget(self.pushButton_train_model)


        self.verticalLayout_5.addWidget(self.frame_new_model)

        self.verticalLayout_5.setStretch(0, 1)

        self.horizontalLayout.addWidget(self.model_list_container)

        self.model_recon_container = QWidget(self.model_container)
        self.model_recon_container.setObjectName(u"model_recon_container")
        self.model_recon_container.setMinimumSize(QSize(550, 0))
        self.model_recon_container.setMaximumSize(QSize(550, 16777215))
        self.model_recon_container.setStyleSheet(u"")
        self.verticalLayout_7 = QVBoxLayout(self.model_recon_container)
        self.verticalLayout_7.setSpacing(10)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(9, 30, -1, 9)
        self.recon_inner_container = QWidget(self.model_recon_container)
        self.recon_inner_container.setObjectName(u"recon_inner_container")
        self.recon_inner_container.setMaximumSize(QSize(16777215, 16777215))
        self.recon_inner_container.setFont(font)
        self.recon_inner_container.setStyleSheet(u"QWidget {\n"
"	background-color: #2e2e2e;\n"
"	border: 1px solid #ff9000;\n"
"	border-radius: 10px;\n"
"}")
        self.verticalLayout_8 = QVBoxLayout(self.recon_inner_container)
        self.verticalLayout_8.setSpacing(0)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(1, 1, 1, 1)
        self.label_recon_header = QLabel(self.recon_inner_container)
        self.label_recon_header.setObjectName(u"label_recon_header")
        self.label_recon_header.setMinimumSize(QSize(0, 60))
        self.label_recon_header.setMaximumSize(QSize(16777215, 60))
        self.label_recon_header.setFont(font2)
        self.label_recon_header.setStyleSheet(u"border: 0px;\n"
"border-bottom: 1px solid #ff9000;\n"
"border-top-left-radius: 10px;\n"
"border-top-right-radius: 10px;\n"
"border-bottom-left-radius: 0px;\n"
"border-bottom-right-radius: 0px;\n"
"background-color: #232323;\n"
"color: #ebebeb;")
        self.label_recon_header.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_8.addWidget(self.label_recon_header)

        self.scrollArea_recon = QScrollArea(self.recon_inner_container)
        self.scrollArea_recon.setObjectName(u"scrollArea_recon")
        self.scrollArea_recon.setStyleSheet(u"border: 0px;\n"
"background-color: transparent;\n"
"")
        self.scrollArea_recon.setWidgetResizable(True)
        self.scrollArea_recon_Contents = QWidget()
        self.scrollArea_recon_Contents.setObjectName(u"scrollArea_recon_Contents")
        self.scrollArea_recon_Contents.setGeometry(QRect(0, 0, 530, 768))
        self.gridLayout_2 = QGridLayout(self.scrollArea_recon_Contents)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setVerticalSpacing(10)
        self.verticalSpacer_3 = QSpacerItem(20, 585, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer_3, 0, 0, 1, 1)

        self.scrollArea_recon.setWidget(self.scrollArea_recon_Contents)

        self.verticalLayout_8.addWidget(self.scrollArea_recon)


        self.verticalLayout_7.addWidget(self.recon_inner_container)

        self.verticalLayout_7.setStretch(0, 1)

        self.horizontalLayout.addWidget(self.model_recon_container)

        self.preview_container = QWidget(self.model_container)
        self.preview_container.setObjectName(u"preview_container")
        self.preview_container.setStyleSheet(u"")
        self.verticalLayout_9 = QVBoxLayout(self.preview_container)
        self.verticalLayout_9.setSpacing(6)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.label_preview = QLabel(self.preview_container)
        self.label_preview.setObjectName(u"label_preview")
        self.label_preview.setMaximumSize(QSize(16777215, 40))
        self.label_preview.setFont(font2)
        self.label_preview.setStyleSheet(u"color: #ebebeb;")
        self.label_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_9.addWidget(self.label_preview)

        self.preview_image = QWidget(self.preview_container)
        self.preview_image.setObjectName(u"preview_image")
        self.preview_image.setStyleSheet(u"background-color: #191919;\n"
" border: none;")

        self.verticalLayout_9.addWidget(self.preview_image)

        self.pushButton_toggle_peak_marker = QPushButton(self.preview_container)
        self.pushButton_toggle_peak_marker.setObjectName(u"pushButton_toggle_peak_marker")
        self.pushButton_toggle_peak_marker.setMinimumSize(QSize(0, 60))
        font7 = QFont()
        font7.setFamilies([u"Lato"])
        font7.setPointSize(20)
        self.pushButton_toggle_peak_marker.setFont(font7)
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

        self.verticalLayout_9.addWidget(self.pushButton_toggle_peak_marker)


        self.horizontalLayout.addWidget(self.preview_container)


        self.verticalLayout.addWidget(self.model_container)


        self.retranslateUi(ModelWidget)

        QMetaObject.connectSlotsByName(ModelWidget)
    # setupUi

    def retranslateUi(self, ModelWidget):
        ModelWidget.setWindowTitle(QCoreApplication.translate("ModelWidget", u"Form", None))
        self.label_header.setText(QCoreApplication.translate("ModelWidget", u"Model", None))
        self.label_container_header_2.setText(QCoreApplication.translate("ModelWidget", u"Models", None))
        self.label_header_2.setText(QCoreApplication.translate("ModelWidget", u"Train new model", None))
        self.lineEdit_name.setText("")
        self.lineEdit_name.setPlaceholderText(QCoreApplication.translate("ModelWidget", u"Model name ...", None))
        self.label_epochs.setText(QCoreApplication.translate("ModelWidget", u"Number of epochs", None))
        self.comboBox_epochs.setItemText(0, QCoreApplication.translate("ModelWidget", u"500", None))
        self.comboBox_epochs.setItemText(1, QCoreApplication.translate("ModelWidget", u"1000", None))
        self.comboBox_epochs.setItemText(2, QCoreApplication.translate("ModelWidget", u"1500", None))
        self.comboBox_epochs.setItemText(3, QCoreApplication.translate("ModelWidget", u"2000", None))
        self.comboBox_epochs.setItemText(4, QCoreApplication.translate("ModelWidget", u"3000", None))
        self.comboBox_epochs.setItemText(5, QCoreApplication.translate("ModelWidget", u"4000", None))

        self.label_device.setText(QCoreApplication.translate("ModelWidget", u"Training device", None))
        self.label_model_info.setText(QCoreApplication.translate("ModelWidget", u"This model will be trained on x peaks.", None))
        self.pushButton_train_model.setText(QCoreApplication.translate("ModelWidget", u"Start training", None))
        self.label_recon_header.setText(QCoreApplication.translate("ModelWidget", u"Model reconstructions", None))
        self.label_preview.setText(QCoreApplication.translate("ModelWidget", u"Spectrum preview", None))
        self.pushButton_toggle_peak_marker.setText(QCoreApplication.translate("ModelWidget", u"Hide markers", None))
    # retranslateUi

