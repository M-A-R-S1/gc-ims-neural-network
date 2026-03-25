# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'PreprocessingWidget.ui'
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

class Ui_PreprocessingWidget(object):
    def setupUi(self, PreprocessingWidget):
        if not PreprocessingWidget.objectName():
            PreprocessingWidget.setObjectName(u"PreprocessingWidget")
        PreprocessingWidget.resize(764, 592)
        self.label = QLabel(PreprocessingWidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 10, 121, 16))

        self.retranslateUi(PreprocessingWidget)

        QMetaObject.connectSlotsByName(PreprocessingWidget)
    # setupUi

    def retranslateUi(self, PreprocessingWidget):
        PreprocessingWidget.setWindowTitle(QCoreApplication.translate("PreprocessingWidget", u"Form", None))
        self.label.setText(QCoreApplication.translate("PreprocessingWidget", u"Preprocessing", None))
    # retranslateUi

