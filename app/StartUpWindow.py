# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'StartUpWindow.ui'
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
from PySide6.QtWidgets import (QApplication, QLabel, QPushButton, QSizePolicy,
    QStackedWidget, QWidget)

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
        icon.addFile(u"ui/_pics/logo_small.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
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
        icon1.addFile(u"ui/_pics/icons/folder-orange.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
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
        icon2.addFile(u"ui/_pics/icons/add_blue.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.button_create.setIcon(icon2)
        self.button_create.setIconSize(QSize(100, 100))
        self.label_logo_big = QLabel(self.StartUpWindow)
        self.label_logo_big.setObjectName(u"label_logo_big")
        self.label_logo_big.setGeometry(QRect(0, 50, 851, 131))
        self.label_logo_big.setPixmap(QPixmap(u"ui/_pics/logo_big.png"))
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
        self.stackedWidget.addWidget(self.CreateNewProject)

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
    # retranslateUi

