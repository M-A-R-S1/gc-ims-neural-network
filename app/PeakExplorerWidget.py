# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'PeakExplorerWidget.ui'
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

class Ui_PeakExplorerWidget(object):
    def setupUi(self, PeakExplorerWidget):
        if not PeakExplorerWidget.objectName():
            PeakExplorerWidget.setObjectName(u"PeakExplorerWidget")
        PeakExplorerWidget.resize(748, 559)
        self.label = QLabel(PeakExplorerWidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(20, 20, 111, 16))

        self.retranslateUi(PeakExplorerWidget)

        QMetaObject.connectSlotsByName(PeakExplorerWidget)
    # setupUi

    def retranslateUi(self, PeakExplorerWidget):
        PeakExplorerWidget.setWindowTitle(QCoreApplication.translate("PeakExplorerWidget", u"Form", None))
        self.label.setText(QCoreApplication.translate("PeakExplorerWidget", u"Peak Explorer", None))
    # retranslateUi

