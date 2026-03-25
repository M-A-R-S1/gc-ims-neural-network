# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'DatasetLabelEntry.ui'
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
    QPushButton, QSizePolicy, QWidget)

class Ui_DatasetLabelEntry(object):
    def setupUi(self, DatasetLabelEntry):
        if not DatasetLabelEntry.objectName():
            DatasetLabelEntry.setObjectName(u"DatasetLabelEntry")
        DatasetLabelEntry.resize(462, 50)
        DatasetLabelEntry.setMinimumSize(QSize(0, 50))
        DatasetLabelEntry.setMaximumSize(QSize(16777215, 50))
        DatasetLabelEntry.setStyleSheet(u"QWidget {\n"
"background-color: #2e2e2e;\n"
"border-bottom: 1px solid #666666;\n"
"}")
        self.horizontalLayout = QHBoxLayout(DatasetLabelEntry)
        self.horizontalLayout.setSpacing(15)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.button_labelDelete = QPushButton(DatasetLabelEntry)
        self.button_labelDelete.setObjectName(u"button_labelDelete")
        self.button_labelDelete.setMaximumSize(QSize(30, 16777215))
        self.button_labelDelete.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.button_labelDelete.setStyleSheet(u"QPushButton {\n"
"    background-color: transparent;\n"
"    border: none;\n"
"}")
        icon = QIcon()
        icon.addFile(u"ui/_pics/icons/delete_grey.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.button_labelDelete.setIcon(icon)
        self.button_labelDelete.setIconSize(QSize(30, 30))

        self.horizontalLayout.addWidget(self.button_labelDelete)

        self.lineEdit_label = QLineEdit(DatasetLabelEntry)
        self.lineEdit_label.setObjectName(u"lineEdit_label")
        font = QFont()
        font.setFamilies([u"Lato"])
        font.setPointSize(15)
        font.setWeight(QFont.Light)
        self.lineEdit_label.setFont(font)
        self.lineEdit_label.setStyleSheet(u"border: None;")

        self.horizontalLayout.addWidget(self.lineEdit_label)

        self.label_counter = QLabel(DatasetLabelEntry)
        self.label_counter.setObjectName(u"label_counter")
        self.label_counter.setMaximumSize(QSize(60, 16777215))
        self.label_counter.setFont(font)
        self.label_counter.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.label_counter.setStyleSheet(u"border: None;")
        self.label_counter.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout.addWidget(self.label_counter)


        self.retranslateUi(DatasetLabelEntry)

        QMetaObject.connectSlotsByName(DatasetLabelEntry)
    # setupUi

    def retranslateUi(self, DatasetLabelEntry):
        DatasetLabelEntry.setWindowTitle(QCoreApplication.translate("DatasetLabelEntry", u"Form", None))
        self.button_labelDelete.setText("")
        self.lineEdit_label.setText(QCoreApplication.translate("DatasetLabelEntry", u"label name", None))
        self.label_counter.setText(QCoreApplication.translate("DatasetLabelEntry", u"0x", None))
    # retranslateUi

