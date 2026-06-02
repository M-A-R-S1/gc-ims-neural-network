# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ClassifierWidget.ui'
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

class Ui_ClassifierWidget(object):
    def setupUi(self, ClassifierWidget):
        if not ClassifierWidget.objectName():
            ClassifierWidget.setObjectName(u"ClassifierWidget")
        ClassifierWidget.resize(1660, 993)
        font = QFont()
        font.setWeight(QFont.Black)
        ClassifierWidget.setFont(font)
        ClassifierWidget.setStyleSheet(u"background-color: #1d1d1d;")
        self.verticalLayout = QVBoxLayout(ClassifierWidget)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(40, 20, 20, 20)
        self.label_header = QLabel(ClassifierWidget)
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

        self.classifier_container = QWidget(ClassifierWidget)
        self.classifier_container.setObjectName(u"classifier_container")
        self.horizontalLayout = QHBoxLayout(self.classifier_container)
        self.horizontalLayout.setSpacing(100)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.classifier_list_container = QWidget(self.classifier_container)
        self.classifier_list_container.setObjectName(u"classifier_list_container")
        self.classifier_list_container.setMinimumSize(QSize(1000, 0))
        self.classifier_list_container.setMaximumSize(QSize(16777215, 16777215))
        self.classifier_list_container.setStyleSheet(u"")
        self.verticalLayout_5 = QVBoxLayout(self.classifier_list_container)
        self.verticalLayout_5.setSpacing(10)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(9, 30, -1, 9)
        self.classifier_list_inner_container = QWidget(self.classifier_list_container)
        self.classifier_list_inner_container.setObjectName(u"classifier_list_inner_container")
        self.classifier_list_inner_container.setMaximumSize(QSize(16777215, 16777215))
        self.classifier_list_inner_container.setFont(font)
        self.classifier_list_inner_container.setStyleSheet(u"QWidget {\n"
"	background-color: #2e2e2e;\n"
"	border: 1px solid #ff9000;\n"
"	border-radius: 10px;\n"
"}")
        self.verticalLayout_6 = QVBoxLayout(self.classifier_list_inner_container)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(1, 1, 1, 1)
        self.label_container_header_2 = QLabel(self.classifier_list_inner_container)
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

        self.scrollArea_classifier = QScrollArea(self.classifier_list_inner_container)
        self.scrollArea_classifier.setObjectName(u"scrollArea_classifier")
        self.scrollArea_classifier.setStyleSheet(u"border: 0px;\n"
"background-color: transparent;\n"
"")
        self.scrollArea_classifier.setWidgetResizable(True)
        self.scrollArea_classifier_Contents = QWidget()
        self.scrollArea_classifier_Contents.setObjectName(u"scrollArea_classifier_Contents")
        self.scrollArea_classifier_Contents.setGeometry(QRect(0, 0, 980, 786))
        self.gridLayout = QGridLayout(self.scrollArea_classifier_Contents)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setVerticalSpacing(10)
        self.verticalSpacer_2 = QSpacerItem(20, 585, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer_2, 0, 0, 1, 1)

        self.scrollArea_classifier.setWidget(self.scrollArea_classifier_Contents)

        self.verticalLayout_6.addWidget(self.scrollArea_classifier)


        self.verticalLayout_5.addWidget(self.classifier_list_inner_container)

        self.verticalLayout_5.setStretch(0, 1)

        self.horizontalLayout.addWidget(self.classifier_list_container)

        self.frame_new_classification = QFrame(self.classifier_container)
        self.frame_new_classification.setObjectName(u"frame_new_classification")
        self.frame_new_classification.setMinimumSize(QSize(500, 350))
        self.frame_new_classification.setMaximumSize(QSize(500, 400))
        self.frame_new_classification.setStyleSheet(u".QFrame  {\n"
"	background-color: #2e2e2e;\n"
"	border: 1px solid #ff9000;\n"
"	border-radius: 10px;\n"
"}\n"
"")
        self.frame_new_classification.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_new_classification.setFrameShadow(QFrame.Shadow.Raised)
        self.label_header_2 = QLabel(self.frame_new_classification)
        self.label_header_2.setObjectName(u"label_header_2")
        self.label_header_2.setGeometry(QRect(20, 20, 461, 41))
        self.label_header_2.setFont(font2)
        self.label_header_2.setStyleSheet(u"color: #ebebeb;\n"
"background-color: #2e2e2e;")
        self.label_header_2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lineEdit_name = QLineEdit(self.frame_new_classification)
        self.lineEdit_name.setObjectName(u"lineEdit_name")
        self.lineEdit_name.setGeometry(QRect(20, 110, 461, 41))
        self.lineEdit_name.setMaximumSize(QSize(500, 16777215))
        font3 = QFont()
        font3.setFamilies([u"Lato"])
        font3.setPointSize(14)
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
        self.pushButton_new_classification = QPushButton(self.frame_new_classification)
        self.pushButton_new_classification.setObjectName(u"pushButton_new_classification")
        self.pushButton_new_classification.setGeometry(QRect(20, 320, 461, 51))
        font4 = QFont()
        font4.setFamilies([u"Lato"])
        font4.setPointSize(20)
        font4.setWeight(QFont.Light)
        self.pushButton_new_classification.setFont(font4)
        self.pushButton_new_classification.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.pushButton_new_classification.setStyleSheet(u"QPushButton {\n"
"    border: 1px solid #00eaff;\n"
"    background-color: #232323; \n"
"    color: #00eaff;\n"
"    border-radius: 10px;\n"
"}\n"
"")
        self.label_model = QLabel(self.frame_new_classification)
        self.label_model.setObjectName(u"label_model")
        self.label_model.setGeometry(QRect(20, 170, 191, 30))
        self.label_model.setMinimumSize(QSize(0, 0))
        self.label_model.setMaximumSize(QSize(16777215, 16777215))
        font5 = QFont()
        font5.setFamilies([u"Lato"])
        font5.setPointSize(14)
        self.label_model.setFont(font5)
        self.label_model.setStyleSheet(u"color: #ebebeb;\n"
"background-color: #2e2e2e;")
        self.label_model.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.comboBox_sort_peaks = QComboBox(self.frame_new_classification)
        self.comboBox_sort_peaks.setObjectName(u"comboBox_sort_peaks")
        self.comboBox_sort_peaks.setGeometry(QRect(210, 170, 271, 31))
        self.comboBox_sort_peaks.setMinimumSize(QSize(200, 30))
        self.comboBox_sort_peaks.setMaximumSize(QSize(300, 16777215))
        self.comboBox_sort_peaks.setFont(font5)
        self.comboBox_sort_peaks.setStyleSheet(u"color: #ebebeb;\n"
"background-color: #232323;\n"
"border-top-left-radius: 0px;\n"
"border-top-right-radius: 0px;\n"
"border-bottom-left-radius: 0px;\n"
"border-bottom-right-radius: 0px;\n"
"padding-left: 10px;")
        self.label_open = QLabel(self.frame_new_classification)
        self.label_open.setObjectName(u"label_open")
        self.label_open.setGeometry(QRect(10, 280, 461, 28))
        font6 = QFont()
        font6.setFamilies([u"Lato"])
        font6.setPointSize(12)
        font6.setWeight(QFont.Light)
        font6.setKerning(True)
        self.label_open.setFont(font6)
        self.label_open.setStyleSheet(u"color: #9e9e9e;\n"
"background-color: #2e2e2e;")
        self.label_open.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout.addWidget(self.frame_new_classification)

        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 1)

        self.verticalLayout.addWidget(self.classifier_container, 0, Qt.AlignmentFlag.AlignLeft)


        self.retranslateUi(ClassifierWidget)

        QMetaObject.connectSlotsByName(ClassifierWidget)
    # setupUi

    def retranslateUi(self, ClassifierWidget):
        ClassifierWidget.setWindowTitle(QCoreApplication.translate("ClassifierWidget", u"Form", None))
        self.label_header.setText(QCoreApplication.translate("ClassifierWidget", u"Classifier", None))
        self.label_container_header_2.setText(QCoreApplication.translate("ClassifierWidget", u"Classifications", None))
        self.label_header_2.setText(QCoreApplication.translate("ClassifierWidget", u"Create new classification", None))
        self.lineEdit_name.setText("")
        self.lineEdit_name.setPlaceholderText(QCoreApplication.translate("ClassifierWidget", u"Classification name ...", None))
        self.pushButton_new_classification.setText(QCoreApplication.translate("ClassifierWidget", u"Start classification", None))
        self.label_model.setText(QCoreApplication.translate("ClassifierWidget", u"Classification model:", None))
        self.label_open.setText(QCoreApplication.translate("ClassifierWidget", u"This classification uses x consensus peaks.", None))
    # retranslateUi

