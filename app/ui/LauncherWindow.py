# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'LauncherWindow.ui'
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
from PySide6.QtWidgets import (QApplication, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QStackedWidget, QWidget)
import resources_rc

class Ui_StartWidget(object):
    def setupUi(self, StartWidget):
        if not StartWidget.objectName():
            StartWidget.setObjectName(u"StartWidget")
        StartWidget.resize(849, 604)
        StartWidget.setMinimumSize(QSize(849, 604))
        StartWidget.setMaximumSize(QSize(849, 604))
        font = QFont()
        font.setKerning(True)
        StartWidget.setFont(font)
        StartWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        icon = QIcon()
        icon.addFile(u":/ui/_pics/logo_small.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        StartWidget.setWindowIcon(icon)
        StartWidget.setAutoFillBackground(False)
        StartWidget.setStyleSheet(u"background-color: rgb(29, 29, 29)")
        StartWidget.setLocale(QLocale(QLocale.English, QLocale.Germany))
        self.stackedWidget = QStackedWidget(StartWidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.setGeometry(QRect(0, 0, 849, 604))
        self.stackedWidget.setMinimumSize(QSize(849, 604))
        self.stackedWidget.setMaximumSize(QSize(849, 604))
        self.StartUpWindow = QWidget()
        self.StartUpWindow.setObjectName(u"StartUpWindow")
        self.label_create = QLabel(self.StartUpWindow)
        self.label_create.setObjectName(u"label_create")
        self.label_create.setGeometry(QRect(130, 550, 201, 28))
        font1 = QFont()
        font1.setFamilies([u"Lato"])
        font1.setPointSize(12)
        font1.setWeight(QFont.Light)
        font1.setKerning(True)
        self.label_create.setFont(font1)
        self.label_create.setStyleSheet(u"color: #9e9e9e;")
        self.label_create.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_subheader = QLabel(self.StartUpWindow)
        self.label_subheader.setObjectName(u"label_subheader")
        self.label_subheader.setGeometry(QRect(0, 260, 851, 31))
        font2 = QFont()
        font2.setFamilies([u"Lato"])
        font2.setPointSize(17)
        font2.setWeight(QFont.Light)
        font2.setKerning(True)
        self.label_subheader.setFont(font2)
        self.label_subheader.setStyleSheet(u"color: #9e9e9e;")
        self.label_subheader.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.button_open = QPushButton(self.StartUpWindow)
        self.button_open.setObjectName(u"button_open")
        self.button_open.setGeometry(QRect(520, 340, 200, 207))
        font3 = QFont()
        font3.setFamilies([u"Lato"])
        font3.setPointSize(120)
        font3.setKerning(True)
        self.button_open.setFont(font3)
        self.button_open.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.button_open.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.button_open.setStyleSheet(u"QPushButton {\n"
"    border: 1.5px dashed #ff9000;\n"
"    background-color: #232323; \n"
"    color: #ff9000;\n"
"    border-radius: 10px;\n"
"}\n"
"")
        icon1 = QIcon()
        icon1.addFile(u":/ui/_pics/icons/folder-orange.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.button_open.setIcon(icon1)
        self.button_open.setIconSize(QSize(100, 100))
        self.button_create = QPushButton(self.StartUpWindow)
        self.button_create.setObjectName(u"button_create")
        self.button_create.setGeometry(QRect(130, 340, 200, 207))
        self.button_create.setFont(font3)
        self.button_create.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.button_create.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.button_create.setStyleSheet(u"QPushButton {\n"
"    border: 1.5px dashed #00eaff;\n"
"    background-color: #232323; \n"
"    color: #00eaff;\n"
"    border-radius: 10px;\n"
"}\n"
"")
        icon2 = QIcon()
        icon2.addFile(u":/ui/_pics/icons/add_blue.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.button_create.setIcon(icon2)
        self.button_create.setIconSize(QSize(100, 100))
        self.label_logo_big = QLabel(self.StartUpWindow)
        self.label_logo_big.setObjectName(u"label_logo_big")
        self.label_logo_big.setGeometry(QRect(0, 50, 851, 131))
        self.label_logo_big.setStyleSheet(u"")
        self.label_logo_big.setPixmap(QPixmap(u":/ui/_pics/logo_big.png"))
        self.label_logo_big.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_header = QLabel(self.StartUpWindow)
        self.label_header.setObjectName(u"label_header")
        self.label_header.setGeometry(QRect(0, 210, 851, 51))
        font4 = QFont()
        font4.setFamilies([u"Lato"])
        font4.setPointSize(35)
        font4.setKerning(True)
        self.label_header.setFont(font4)
        self.label_header.setStyleSheet(u"color: #ebebeb;")
        self.label_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_open = QLabel(self.StartUpWindow)
        self.label_open.setObjectName(u"label_open")
        self.label_open.setGeometry(QRect(520, 550, 201, 28))
        self.label_open.setFont(font1)
        self.label_open.setStyleSheet(u"color: #9e9e9e;")
        self.label_open.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stackedWidget.addWidget(self.StartUpWindow)
        self.CreateNewProject = QWidget()
        self.CreateNewProject.setObjectName(u"CreateNewProject")
        self.label_subheader_2 = QLabel(self.CreateNewProject)
        self.label_subheader_2.setObjectName(u"label_subheader_2")
        self.label_subheader_2.setGeometry(QRect(0, 160, 851, 61))
        self.label_subheader_2.setFont(font2)
        self.label_subheader_2.setStyleSheet(u"color: #9e9e9e;")
        self.label_subheader_2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_header_2 = QLabel(self.CreateNewProject)
        self.label_header_2.setObjectName(u"label_header_2")
        self.label_header_2.setGeometry(QRect(0, 100, 851, 51))
        self.label_header_2.setFont(font4)
        self.label_header_2.setStyleSheet(u"color: #ebebeb;")
        self.label_header_2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lineEdit_project_name = QLineEdit(self.CreateNewProject)
        self.lineEdit_project_name.setObjectName(u"lineEdit_project_name")
        self.lineEdit_project_name.setGeometry(QRect(130, 280, 591, 41))
        font5 = QFont()
        font5.setFamilies([u"Lato"])
        font5.setPointSize(14)
        font5.setWeight(QFont.Light)
        self.lineEdit_project_name.setFont(font5)
        self.lineEdit_project_name.setStyleSheet(u"QLineEdit {\n"
"    border: 1px solid #ff9000;\n"
"    background-color: #232323; \n"
"    color: #9e9e9e;\n"
"    border-radius: 10px;\n"
"   padding-left: 10px;\n"
"}\n"
"")
        self.label_location = QLabel(self.CreateNewProject)
        self.label_location.setObjectName(u"label_location")
        self.label_location.setGeometry(QRect(130, 360, 591, 41))
        self.label_location.setFont(font5)
        self.label_location.setStyleSheet(u"QLabel  {\n"
"    border: 1px solid #ff9000;\n"
"    background-color: #232323; \n"
"    color: #9e9e9e;\n"
"    border-radius: 10px;\n"
"   padding-left: 50px;\n"
"}\n"
"")
        self.button_location = QPushButton(self.CreateNewProject)
        self.button_location.setObjectName(u"button_location")
        self.button_location.setGeometry(QRect(140, 360, 41, 41))
        self.button_location.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.button_location.setStyleSheet(u"QPushButton  {\n"
"    border: 0px solid;\n"
"    background-color: None; \n"
"}\n"
"")
        self.button_location.setIcon(icon1)
        self.button_location.setIconSize(QSize(32, 32))
        self.button_cancle = QPushButton(self.CreateNewProject)
        self.button_cancle.setObjectName(u"button_cancle")
        self.button_cancle.setGeometry(QRect(130, 530, 101, 41))
        self.button_cancle.setFont(font5)
        self.button_cancle.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.button_cancle.setStyleSheet(u"QPushButton {\n"
"    border: 1px solid #9e9e9e;\n"
"    background-color: #232323; \n"
"    color: #9e9e9e;\n"
"    border-radius: 10px;\n"
"}\n"
"")
        self.button_create_2 = QPushButton(self.CreateNewProject)
        self.button_create_2.setObjectName(u"button_create_2")
        self.button_create_2.setGeometry(QRect(620, 530, 101, 41))
        self.button_create_2.setFont(font5)
        self.button_create_2.setCursor(QCursor(Qt.CursorShape.ForbiddenCursor))
        self.button_create_2.setStyleSheet(u"QPushButton {\n"
"    border: 1px solid #00eaff;\n"
"    background-color: #232323; \n"
"    color: #00eaff;\n"
"    border-radius: 10px;\n"
"}\n"
"")
        self.label_error_name = QLabel(self.CreateNewProject)
        self.label_error_name.setObjectName(u"label_error_name")
        self.label_error_name.setGeometry(QRect(140, 330, 401, 20))
        font6 = QFont()
        font6.setFamilies([u"Lato"])
        font6.setPointSize(10)
        font6.setWeight(QFont.Light)
        font6.setKerning(True)
        self.label_error_name.setFont(font6)
        self.label_error_name.setStyleSheet(u"color: #ff4c4c;")
        self.label_error_name.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.stackedWidget.addWidget(self.CreateNewProject)
        QWidget.setTabOrder(self.button_create, self.button_open)
        QWidget.setTabOrder(self.button_open, self.lineEdit_project_name)
        QWidget.setTabOrder(self.lineEdit_project_name, self.button_location)
        QWidget.setTabOrder(self.button_location, self.button_cancle)
        QWidget.setTabOrder(self.button_cancle, self.button_create_2)

        self.retranslateUi(StartWidget)

        self.stackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(StartWidget)
    # setupUi

    def retranslateUi(self, StartWidget):
        StartWidget.setWindowTitle(QCoreApplication.translate("StartWidget", u"GC-IMS suite", None))
        self.label_create.setText(QCoreApplication.translate("StartWidget", u"create new project", None))
        self.label_subheader.setText(QCoreApplication.translate("StartWidget", u"Create or open a GC-IMS project", None))
        self.button_open.setText("")
        self.button_create.setText("")
        self.label_logo_big.setText("")
        self.label_header.setText(QCoreApplication.translate("StartWidget", u"Welcome", None))
        self.label_open.setText(QCoreApplication.translate("StartWidget", u"open existing project", None))
        self.label_subheader_2.setText(QCoreApplication.translate("StartWidget", u"<html><head/><body><p align=\"center\">Specify a project name and choose a project<br> saving location</p></body></html>", None))
        self.label_header_2.setText(QCoreApplication.translate("StartWidget", u"Create a new GC-IMS project", None))
        self.lineEdit_project_name.setText("")
        self.lineEdit_project_name.setPlaceholderText(QCoreApplication.translate("StartWidget", u"Project name ...", None))
        self.label_location.setText(QCoreApplication.translate("StartWidget", u"Project location ...", None))
        self.button_location.setText("")
        self.button_cancle.setText(QCoreApplication.translate("StartWidget", u"Back", None))
        self.button_create_2.setText(QCoreApplication.translate("StartWidget", u"Create", None))
        self.label_error_name.setText("")
    # retranslateUi

