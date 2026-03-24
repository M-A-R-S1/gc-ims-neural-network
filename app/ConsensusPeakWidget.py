# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ConsensusPeakWidget.ui'
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

class Ui_ConsensusPeakWidget(object):
    def setupUi(self, ConsensusPeakWidget):
        if not ConsensusPeakWidget.objectName():
            ConsensusPeakWidget.setObjectName(u"ConsensusPeakWidget")
        ConsensusPeakWidget.resize(643, 473)
        self.label = QLabel(ConsensusPeakWidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(20, 20, 151, 16))

        self.retranslateUi(ConsensusPeakWidget)

        QMetaObject.connectSlotsByName(ConsensusPeakWidget)
    # setupUi

    def retranslateUi(self, ConsensusPeakWidget):
        ConsensusPeakWidget.setWindowTitle(QCoreApplication.translate("ConsensusPeakWidget", u"Form", None))
        self.label.setText(QCoreApplication.translate("ConsensusPeakWidget", u"Consensus Peaks", None))
    # retranslateUi

