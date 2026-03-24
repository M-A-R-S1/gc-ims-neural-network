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
from PySide6.QtWidgets import (QApplication, QLabel, QSizePolicy, QWidget)

class Ui_ClassifierWidget(object):
    def setupUi(self, ClassifierWidget):
        if not ClassifierWidget.objectName():
            ClassifierWidget.setObjectName(u"ClassifierWidget")
        ClassifierWidget.resize(733, 583)
        self.label = QLabel(ClassifierWidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(20, 10, 111, 16))

        self.retranslateUi(ClassifierWidget)

        QMetaObject.connectSlotsByName(ClassifierWidget)
    # setupUi

    def retranslateUi(self, ClassifierWidget):
        ClassifierWidget.setWindowTitle(QCoreApplication.translate("ClassifierWidget", u"Form", None))
        self.label.setText(QCoreApplication.translate("ClassifierWidget", u"Classifier", None))
    # retranslateUi

