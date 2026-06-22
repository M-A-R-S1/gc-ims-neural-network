# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'CreateLabelDialog.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QWidget)

class Ui_CreateLabelDialog(object):
    def setupUi(self, CreateLabelDialog):
        if not CreateLabelDialog.objectName():
            CreateLabelDialog.setObjectName(u"CreateLabelDialog")
        CreateLabelDialog.resize(400, 220)
        CreateLabelDialog.setMinimumSize(QSize(400, 220))
        CreateLabelDialog.setMaximumSize(QSize(400, 220))
        CreateLabelDialog.setStyleSheet(u"background-color: #1d1d1d;")
        self.lineEdit_label_name = QLineEdit(CreateLabelDialog)
        self.lineEdit_label_name.setObjectName(u"lineEdit_label_name")
        self.lineEdit_label_name.setGeometry(QRect(20, 70, 361, 41))
        font = QFont()
        font.setFamilies([u"Lato"])
        font.setPointSize(13)
        self.lineEdit_label_name.setFont(font)
        self.lineEdit_label_name.setStyleSheet(u"QLineEdit {\n"
"    border: 1px solid #ff9000;\n"
"    background-color: #232323; \n"
"    color: #9e9e9e;\n"
"    border-radius: 10px;\n"
"   padding-left: 10px;\n"
"}\n"
"")
        self.label_dialog_text = QLabel(CreateLabelDialog)
        self.label_dialog_text.setObjectName(u"label_dialog_text")
        self.label_dialog_text.setGeometry(QRect(20, 10, 361, 41))
        self.label_dialog_text.setFont(font)
        self.label_dialog_text.setStyleSheet(u"color: #9e9e9e;")
        self.button_ok = QPushButton(CreateLabelDialog)
        self.button_ok.setObjectName(u"button_ok")
        self.button_ok.setGeometry(QRect(280, 150, 101, 41))
        font1 = QFont()
        font1.setFamilies([u"Lato"])
        font1.setPointSize(13)
        font1.setWeight(QFont.Light)
        self.button_ok.setFont(font1)
        self.button_ok.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.button_ok.setStyleSheet(u"QPushButton {\n"
"    border: 1px solid #00eaff;\n"
"    background-color: #232323; \n"
"    color: #00eaff;\n"
"    border-radius: 10px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	background-color: #131313;\n"
"}")
        self.button_cancel = QPushButton(CreateLabelDialog)
        self.button_cancel.setObjectName(u"button_cancel")
        self.button_cancel.setGeometry(QRect(20, 150, 101, 41))
        self.button_cancel.setFont(font)
        self.button_cancel.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.button_cancel.setStyleSheet(u"QPushButton {\n"
"    border: 1px solid #9e9e9e;\n"
"    background-color: #232323; \n"
"    color: #9e9e9e;\n"
"    border-radius: 10px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	background-color: #131313;\n"
"}\n"
"")

        self.retranslateUi(CreateLabelDialog)

        QMetaObject.connectSlotsByName(CreateLabelDialog)
    # setupUi

    def retranslateUi(self, CreateLabelDialog):
        CreateLabelDialog.setWindowTitle(QCoreApplication.translate("CreateLabelDialog", u"Dialog", None))
        self.lineEdit_label_name.setPlaceholderText(QCoreApplication.translate("CreateLabelDialog", u"Label name ...", None))
        self.label_dialog_text.setText(QCoreApplication.translate("CreateLabelDialog", u"Specify the new label name", None))
        self.button_ok.setText(QCoreApplication.translate("CreateLabelDialog", u"Add", None))
        self.button_cancel.setText(QCoreApplication.translate("CreateLabelDialog", u"Cancel", None))
    # retranslateUi

