# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'DatasetWidget.ui'
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
from PySide6.QtWidgets import (QApplication, QLabel, QSizePolicy, QWidget)

class Ui_DatasetWidget(object):
    def setupUi(self, DatasetWidget):
        if not DatasetWidget.objectName():
            DatasetWidget.setObjectName(u"DatasetWidget")
        DatasetWidget.resize(873, 705)
        self.label = QLabel(DatasetWidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(20, 20, 49, 16))

        self.retranslateUi(DatasetWidget)

        QMetaObject.connectSlotsByName(DatasetWidget)
    # setupUi

    def retranslateUi(self, DatasetWidget):
        DatasetWidget.setWindowTitle(QCoreApplication.translate("DatasetWidget", u"Form", None))
        self.label.setText(QCoreApplication.translate("DatasetWidget", u"Dataset", None))
    # retranslateUi

