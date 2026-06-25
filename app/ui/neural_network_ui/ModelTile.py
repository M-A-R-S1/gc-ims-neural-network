# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ModelTile.ui'
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

class Ui_ModelTile(object):
    def setupUi(self, ModelTile):
        if not ModelTile.objectName():
            ModelTile.setObjectName(u"ModelTile")
        ModelTile.resize(475, 50)
        ModelTile.setMinimumSize(QSize(0, 50))
        ModelTile.setMaximumSize(QSize(16777215, 50))
        ModelTile.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        ModelTile.setStyleSheet(u"QWidget {\n"
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
        self.horizontalLayout = QHBoxLayout(ModelTile)
        self.horizontalLayout.setSpacing(15)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.button_delete = QPushButton(ModelTile)
        self.button_delete.setObjectName(u"button_delete")
        self.button_delete.setMaximumSize(QSize(30, 16777215))
        self.button_delete.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.button_delete.setStyleSheet(u"QPushButton {\n"
"    background-color: transparent;\n"
"    border: none;\n"
"}")
        icon = QIcon()
        icon.addFile(u":/ui/_pics/icons/delete_grey.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.button_delete.setIcon(icon)
        self.button_delete.setIconSize(QSize(30, 30))

        self.horizontalLayout.addWidget(self.button_delete)

        self.button_rename = QPushButton(ModelTile)
        self.button_rename.setObjectName(u"button_rename")
        self.button_rename.setMaximumSize(QSize(30, 16777215))
        self.button_rename.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.button_rename.setStyleSheet(u"QPushButton {\n"
"    background-color: transparent;\n"
"    border: none;\n"
"	background-image: url(\"ui/_pics/icons/classifier_grey.png\");\n"
"}")
        icon1 = QIcon()
        icon1.addFile(u":/ui/_pics/icons/edit_grey.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.button_rename.setIcon(icon1)
        self.button_rename.setIconSize(QSize(30, 30))

        self.horizontalLayout.addWidget(self.button_rename)

        self.label_name = QLabel(ModelTile)
        self.label_name.setObjectName(u"label_name")
        font = QFont()
        font.setFamilies([u"Lato"])
        font.setPointSize(13)
        font.setWeight(QFont.Light)
        self.label_name.setFont(font)
        self.label_name.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.label_name.setStyleSheet(u"border: None;\n"
"color: #ebebeb;\n"
"background-color: transparent;")

        self.horizontalLayout.addWidget(self.label_name)


        self.retranslateUi(ModelTile)

        QMetaObject.connectSlotsByName(ModelTile)
    # setupUi

    def retranslateUi(self, ModelTile):
        ModelTile.setWindowTitle(QCoreApplication.translate("ModelTile", u"Form", None))
        self.button_delete.setText("")
        self.button_rename.setText("")
        self.label_name.setText(QCoreApplication.translate("ModelTile", u"TextLabel", None))
    # retranslateUi

