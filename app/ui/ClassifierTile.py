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

class Ui_ClassifierTile(object):
    def setupUi(self, ClassifierTile):
        if not ClassifierTile.objectName():
            ClassifierTile.setObjectName(u"ClassifierTile")
        ClassifierTile.resize(964, 50)
        ClassifierTile.setMinimumSize(QSize(0, 50))
        ClassifierTile.setMaximumSize(QSize(16777215, 50))
        ClassifierTile.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        ClassifierTile.setStyleSheet(u"QWidget {\n"
"	background-color: #2e2e2e;\n"
"	border-bottom: 1px solid #666666;\n"
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
        icon.addFile(u"dataset_ui/ui/_pics/icons/delete_grey.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
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
        icon1.addFile(u"dataset_ui/ui/_pics/icons/edit_grey.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.button_labelRename.setIcon(icon1)
        self.button_labelRename.setIconSize(QSize(30, 30))

        self.horizontalLayout.addWidget(self.button_labelRename)

        self.label_name = QLabel(ClassifierTile)
        self.label_name.setObjectName(u"label_name")
        font = QFont()
        font.setFamilies([u"Lato"])
        font.setPointSize(15)
        font.setWeight(QFont.Light)
        self.label_name.setFont(font)
        self.label_name.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.label_name.setStyleSheet(u"border: None;\n"
"color: #ebebeb;\n"
"background-color: transparent;")

        self.horizontalLayout.addWidget(self.label_name)

        self.consensus_peak_counter = QLabel(ClassifierTile)
        self.consensus_peak_counter.setObjectName(u"consensus_peak_counter")
        self.consensus_peak_counter.setMaximumSize(QSize(120, 16777215))
        self.consensus_peak_counter.setFont(font)
        self.consensus_peak_counter.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.consensus_peak_counter.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.consensus_peak_counter.setStyleSheet(u"border: None;\n"
"color: #ebebeb;\n"
"background-color: transparent;")
        self.consensus_peak_counter.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout.addWidget(self.consensus_peak_counter)

        self.label_result = QLabel(ClassifierTile)
        self.label_result.setObjectName(u"label_result")
        self.label_result.setMaximumSize(QSize(120, 16777215))
        font1 = QFont()
        font1.setFamilies([u"Lato"])
        font1.setPointSize(15)
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
        self.label_name.setText(QCoreApplication.translate("ClassifierTile", u"TextLabel", None))
        self.consensus_peak_counter.setText(QCoreApplication.translate("ClassifierTile", u"0x", None))
        self.label_result.setText(QCoreApplication.translate("ClassifierTile", u"92.4%", None))
    # retranslateUi

