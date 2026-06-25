# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ClassifierTile.ui'
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
    QSizePolicy, QWidget)
import resources_rc

class Ui_ClassifierTile(object):
    def setupUi(self, ClassifierTile):
        if not ClassifierTile.objectName():
            ClassifierTile.setObjectName(u"ClassifierTile")
        ClassifierTile.resize(1135, 50)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ClassifierTile.sizePolicy().hasHeightForWidth())
        ClassifierTile.setSizePolicy(sizePolicy)
        ClassifierTile.setMinimumSize(QSize(0, 50))
        ClassifierTile.setMaximumSize(QSize(16777215, 50))
        ClassifierTile.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        ClassifierTile.setStyleSheet(u"QWidget {\n"
"	background-color: #2e2e2e;\n"
"	border-bottom: 1px solid #666666;\n"
"    border-top-left-radius: 0px;\n"
"	border-top-right-radius: 0px;\n"
"	border-bottom-left-radius: 0px;\n"
"	border-bottom-right-radius: 0px;\n"
"}\n"
"\n"
"QWidget:hover {\n"
"	background-color: #131313;\n"
"}")
        self.horizontalLayout = QHBoxLayout(ClassifierTile)
        self.horizontalLayout.setSpacing(15)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.button_labelDelete = QPushButton(ClassifierTile)
        self.button_labelDelete.setObjectName(u"button_labelDelete")
        self.button_labelDelete.setMaximumSize(QSize(30, 16777215))
        self.button_labelDelete.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.button_labelDelete.setStyleSheet(u"QPushButton {\n"
"    background-color: transparent;\n"
"    border: none;\n"
"}")
        icon = QIcon()
        icon.addFile(u":/ui/_pics/icons/delete_grey.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.button_labelDelete.setIcon(icon)
        self.button_labelDelete.setIconSize(QSize(30, 30))

        self.horizontalLayout.addWidget(self.button_labelDelete)

        self.button_labelRename = QPushButton(ClassifierTile)
        self.button_labelRename.setObjectName(u"button_labelRename")
        self.button_labelRename.setMaximumSize(QSize(30, 16777215))
        self.button_labelRename.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.button_labelRename.setStyleSheet(u"QPushButton {\n"
"    background-color: transparent;\n"
"    border: none;\n"
"	background-image: url(\"ui/_pics/icons/classifier_grey.png\");\n"
"}")
        icon1 = QIcon()
        icon1.addFile(u":/ui/_pics/icons/edit_grey.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.button_labelRename.setIcon(icon1)
        self.button_labelRename.setIconSize(QSize(30, 30))

        self.horizontalLayout.addWidget(self.button_labelRename)

        self.label_name = QLabel(ClassifierTile)
        self.label_name.setObjectName(u"label_name")
        font = QFont()
        font.setFamilies([u"Lato"])
        font.setPointSize(13)
        font.setWeight(QFont.Light)
        self.label_name.setFont(font)
        self.label_name.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.label_name.setStyleSheet(u"border: None;\n"
"color: #ebebeb;\n"
"background-color: transparent;\n"
"")

        self.horizontalLayout.addWidget(self.label_name)

        self.label_model = QLabel(ClassifierTile)
        self.label_model.setObjectName(u"label_model")
        self.label_model.setFont(font)
        self.label_model.setStyleSheet(u"border: None;\n"
"color: #ebebeb;\n"
"background-color: transparent;")

        self.horizontalLayout.addWidget(self.label_model)

        self.label_result = QLabel(ClassifierTile)
        self.label_result.setObjectName(u"label_result")
        self.label_result.setMaximumSize(QSize(70, 16777215))
        font1 = QFont()
        font1.setFamilies([u"Lato"])
        font1.setPointSize(13)
        font1.setWeight(QFont.Light)
        font1.setKerning(True)
        self.label_result.setFont(font1)
        self.label_result.setStyleSheet(u"border: None;\n"
"color: #ebebeb;\n"
"background-color: transparent;")

        self.horizontalLayout.addWidget(self.label_result)


        self.retranslateUi(ClassifierTile)

        QMetaObject.connectSlotsByName(ClassifierTile)
    # setupUi

    def retranslateUi(self, ClassifierTile):
        ClassifierTile.setWindowTitle(QCoreApplication.translate("ClassifierTile", u"Form", None))
        self.button_labelDelete.setText("")
        self.button_labelRename.setText("")
        self.label_name.setText(QCoreApplication.translate("ClassifierTile", u"Name Text", None))
        self.label_model.setText(QCoreApplication.translate("ClassifierTile", u"Model Text", None))
        self.label_result.setText(QCoreApplication.translate("ClassifierTile", u"92.4%", None))
    # retranslateUi

