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
    QHBoxLayout, QHeaderView, QLabel, QLayout,
    QLineEdit, QPushButton, QScrollArea, QSizePolicy,
    QSpacerItem, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QWidget)

class Ui_ClassifierWidget(object):
    def setupUi(self, ClassifierWidget):
        if not ClassifierWidget.objectName():
            ClassifierWidget.setObjectName(u"ClassifierWidget")
        ClassifierWidget.resize(1741, 993)
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
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.classifier_container.sizePolicy().hasHeightForWidth())
        self.classifier_container.setSizePolicy(sizePolicy)
        self.classifier_container.setMinimumSize(QSize(0, 0))
        self.horizontalLayout = QHBoxLayout(self.classifier_container)
        self.horizontalLayout.setSpacing(20)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.classifier_list_container = QWidget(self.classifier_container)
        self.classifier_list_container.setObjectName(u"classifier_list_container")
        sizePolicy.setHeightForWidth(self.classifier_list_container.sizePolicy().hasHeightForWidth())
        self.classifier_list_container.setSizePolicy(sizePolicy)
        self.classifier_list_container.setMinimumSize(QSize(0, 0))
        self.classifier_list_container.setMaximumSize(QSize(760, 16777215))
        self.classifier_list_container.setStyleSheet(u"")
        self.verticalLayout_5 = QVBoxLayout(self.classifier_list_container)
        self.verticalLayout_5.setSpacing(20)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(9, 30, -1, 9)
        self.classifier_list_inner_container = QWidget(self.classifier_list_container)
        self.classifier_list_inner_container.setObjectName(u"classifier_list_inner_container")
        sizePolicy.setHeightForWidth(self.classifier_list_inner_container.sizePolicy().hasHeightForWidth())
        self.classifier_list_inner_container.setSizePolicy(sizePolicy)
        self.classifier_list_inner_container.setMinimumSize(QSize(0, 0))
        self.classifier_list_inner_container.setMaximumSize(QSize(750, 16777215))
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
        self.scrollArea_classifier_Contents.setGeometry(QRect(0, 0, 740, 466))
        self.gridLayout = QGridLayout(self.scrollArea_classifier_Contents)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setVerticalSpacing(10)
        self.verticalSpacer_2 = QSpacerItem(20, 585, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer_2, 0, 0, 1, 1)

        self.scrollArea_classifier.setWidget(self.scrollArea_classifier_Contents)

        self.verticalLayout_6.addWidget(self.scrollArea_classifier)


        self.verticalLayout_5.addWidget(self.classifier_list_inner_container)

        self.frame_new_classification = QFrame(self.classifier_list_container)
        self.frame_new_classification.setObjectName(u"frame_new_classification")
        sizePolicy.setHeightForWidth(self.frame_new_classification.sizePolicy().hasHeightForWidth())
        self.frame_new_classification.setSizePolicy(sizePolicy)
        self.frame_new_classification.setMinimumSize(QSize(0, 300))
        self.frame_new_classification.setMaximumSize(QSize(750, 300))
        self.frame_new_classification.setStyleSheet(u".QFrame  {\n"
"	background-color: #2e2e2e;\n"
"	border: 1px solid #ff9000;\n"
"	border-radius: 10px;\n"
"}\n"
"")
        self.frame_new_classification.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_new_classification.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame_new_classification)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(30, 10, 30, 10)
        self.label_header_2 = QLabel(self.frame_new_classification)
        self.label_header_2.setObjectName(u"label_header_2")
        self.label_header_2.setFont(font2)
        self.label_header_2.setStyleSheet(u"color: #ebebeb;\n"
"background-color: #2e2e2e;")
        self.label_header_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_2.addWidget(self.label_header_2)

        self.lineEdit_name = QLineEdit(self.frame_new_classification)
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

        self.classification_model_container = QWidget(self.frame_new_classification)
        self.classification_model_container.setObjectName(u"classification_model_container")
        self.classification_model_container.setStyleSheet(u"background-color: #2e2e2e;")
        self.horizontalLayout_2 = QHBoxLayout(self.classification_model_container)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(-1, -1, 0, -1)
        self.label_model = QLabel(self.classification_model_container)
        self.label_model.setObjectName(u"label_model")
        self.label_model.setMinimumSize(QSize(0, 0))
        self.label_model.setMaximumSize(QSize(200, 40))
        font4 = QFont()
        font4.setFamilies([u"Lato"])
        font4.setPointSize(12)
        self.label_model.setFont(font4)
        self.label_model.setStyleSheet(u"color: #ebebeb;\n"
"background-color: #2e2e2e;")
        self.label_model.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_2.addWidget(self.label_model)

        self.comboBox_model = QComboBox(self.classification_model_container)
        self.comboBox_model.setObjectName(u"comboBox_model")
        self.comboBox_model.setMinimumSize(QSize(200, 40))
        self.comboBox_model.setMaximumSize(QSize(20000, 40))
        self.comboBox_model.setFont(font4)
        self.comboBox_model.setStyleSheet(u"QComboBox {\n"
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

        self.horizontalLayout_2.addWidget(self.comboBox_model)


        self.verticalLayout_2.addWidget(self.classification_model_container)

        self.label_consesus_peak_counter = QLabel(self.frame_new_classification)
        self.label_consesus_peak_counter.setObjectName(u"label_consesus_peak_counter")
        font5 = QFont()
        font5.setFamilies([u"Lato"])
        font5.setPointSize(12)
        font5.setWeight(QFont.Light)
        font5.setKerning(True)
        self.label_consesus_peak_counter.setFont(font5)
        self.label_consesus_peak_counter.setStyleSheet(u"color: #9e9e9e;\n"
"background-color: #2e2e2e;\n"
"margin-bottom: 5px;")
        self.label_consesus_peak_counter.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter)

        self.verticalLayout_2.addWidget(self.label_consesus_peak_counter)

        self.pushButton_new_classification = QPushButton(self.frame_new_classification)
        self.pushButton_new_classification.setObjectName(u"pushButton_new_classification")
        self.pushButton_new_classification.setMinimumSize(QSize(0, 50))
        font6 = QFont()
        font6.setFamilies([u"Lato"])
        font6.setPointSize(20)
        font6.setWeight(QFont.Light)
        self.pushButton_new_classification.setFont(font6)
        self.pushButton_new_classification.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.pushButton_new_classification.setStyleSheet(u"QPushButton {\n"
"    border: 1px solid #00eaff;\n"
"    background-color: #232323; \n"
"    color: #00eaff;\n"
"    border-radius: 10px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	background-color: #131313;\n"
"}")

        self.verticalLayout_2.addWidget(self.pushButton_new_classification)


        self.verticalLayout_5.addWidget(self.frame_new_classification)

        self.verticalLayout_5.setStretch(0, 1)

        self.horizontalLayout.addWidget(self.classifier_list_container)

        self.right_container = QWidget(self.classifier_container)
        self.right_container.setObjectName(u"right_container")
        self.verticalLayout_3 = QVBoxLayout(self.right_container)
        self.verticalLayout_3.setSpacing(40)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(-1, 30, -1, -1)
        self.frame_classification_details = QFrame(self.right_container)
        self.frame_classification_details.setObjectName(u"frame_classification_details")
        self.frame_classification_details.setMinimumSize(QSize(750, 0))
        self.frame_classification_details.setStyleSheet(u".QFrame  {\n"
"	background-color: #2e2e2e;\n"
"	border: 1px solid #ff9000;\n"
"	border-radius: 10px;\n"
"}\n"
"")
        self.frame_classification_details.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_classification_details.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.frame_classification_details)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.label_detail_header = QLabel(self.frame_classification_details)
        self.label_detail_header.setObjectName(u"label_detail_header")
        self.label_detail_header.setMinimumSize(QSize(0, 60))
        self.label_detail_header.setMaximumSize(QSize(16777215, 60))
        self.label_detail_header.setFont(font2)
        self.label_detail_header.setStyleSheet(u"color: #ebebeb;\n"
"background-color: #2e2e2e;")
        self.label_detail_header.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_4.addWidget(self.label_detail_header)

        self.details_container = QWidget(self.frame_classification_details)
        self.details_container.setObjectName(u"details_container")
        self.details_container.setStyleSheet(u"background-color: #2e2e2e;")
        self.verticalLayout_7 = QVBoxLayout(self.details_container)
        self.verticalLayout_7.setSpacing(20)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.tableWidget_results = QTableWidget(self.details_container)
        self.tableWidget_results.setObjectName(u"tableWidget_results")
        self.tableWidget_results.setFont(font4)
        self.tableWidget_results.setStyleSheet(u"border: none;\n"
"color: #ebebeb;")

        self.verticalLayout_7.addWidget(self.tableWidget_results)

        self.widget_confusion_matrix = QWidget(self.details_container)
        self.widget_confusion_matrix.setObjectName(u"widget_confusion_matrix")

        self.verticalLayout_7.addWidget(self.widget_confusion_matrix)

        self.verticalLayout_7.setStretch(0, 1)
        self.verticalLayout_7.setStretch(1, 2)

        self.verticalLayout_4.addWidget(self.details_container)


        self.verticalLayout_3.addWidget(self.frame_classification_details)

        self.pushButton_load_single_spectrum = QPushButton(self.right_container)
        self.pushButton_load_single_spectrum.setObjectName(u"pushButton_load_single_spectrum")
        self.pushButton_load_single_spectrum.setMinimumSize(QSize(0, 50))
        font7 = QFont()
        font7.setFamilies([u"Lato"])
        font7.setPointSize(20)
        self.pushButton_load_single_spectrum.setFont(font7)
        self.pushButton_load_single_spectrum.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.pushButton_load_single_spectrum.setStyleSheet(u"QPushButton {\n"
"    border: 1px solid #00eaff;\n"
"    background-color: #232323; \n"
"    color: #00eaff;\n"
"    border-radius: 10px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	background-color: #131313;\n"
"}")

        self.verticalLayout_3.addWidget(self.pushButton_load_single_spectrum)


        self.horizontalLayout.addWidget(self.right_container)


        self.verticalLayout.addWidget(self.classifier_container)


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
        self.label_model.setText(QCoreApplication.translate("ClassifierWidget", u"Classification model:", None))
        self.label_consesus_peak_counter.setText(QCoreApplication.translate("ClassifierWidget", u"This classification uses x consensus peaks.", None))
        self.pushButton_new_classification.setText(QCoreApplication.translate("ClassifierWidget", u"Start classification", None))
        self.label_detail_header.setText(QCoreApplication.translate("ClassifierWidget", u"Classification details", None))
        self.pushButton_load_single_spectrum.setText(QCoreApplication.translate("ClassifierWidget", u"Classify single spectrum", None))
    # retranslateUi

