# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ModelReconTile.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QSizePolicy,
    QVBoxLayout, QWidget)
import resources_rc

class Ui_ModelReconTile(object):
    def setupUi(self, ModelReconTile):
        if not ModelReconTile.objectName():
            ModelReconTile.setObjectName(u"ModelReconTile")
        ModelReconTile.resize(240, 120)
        ModelReconTile.setMinimumSize(QSize(240, 120))
        ModelReconTile.setMaximumSize(QSize(448, 120))
        ModelReconTile.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        ModelReconTile.setStyleSheet(u"#ModelReconTile  {\n"
"	background-color: #1d1d1d;\n"
"	border: 1px solid #1d1d1d;\n"
"	border-radius: 5px;\n"
"}\n"
"\n"
"#ModelReconTile:hover {\n"
"	background-color: #555555;\n"
"	border: 1px solid #323232;\n"
"	border-radius: 5px;\n"
"}\n"
"")
        self.verticalLayout = QVBoxLayout(ModelReconTile)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.peak_window_container = QWidget(ModelReconTile)
        self.peak_window_container.setObjectName(u"peak_window_container")
        self.horizontalLayout = QHBoxLayout(self.peak_window_container)
        self.horizontalLayout.setSpacing(3)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.peak_window_original = QLabel(self.peak_window_container)
        self.peak_window_original.setObjectName(u"peak_window_original")
        self.peak_window_original.setMinimumSize(QSize(70, 70))
        self.peak_window_original.setMaximumSize(QSize(70, 70))
        self.peak_window_original.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout.addWidget(self.peak_window_original)

        self.arrow_left = QLabel(self.peak_window_container)
        self.arrow_left.setObjectName(u"arrow_left")
        self.arrow_left.setMinimumSize(QSize(50, 60))
        self.arrow_left.setMaximumSize(QSize(50, 50))
        self.arrow_left.setPixmap(QPixmap(u":/ui/_pics/icons/arrow_right.png"))
        self.arrow_left.setScaledContents(True)

        self.horizontalLayout.addWidget(self.arrow_left, 0, Qt.AlignmentFlag.AlignVCenter)

        self.peak_window_recon = QLabel(self.peak_window_container)
        self.peak_window_recon.setObjectName(u"peak_window_recon")
        self.peak_window_recon.setMinimumSize(QSize(70, 70))
        self.peak_window_recon.setMaximumSize(QSize(70, 70))
        self.peak_window_recon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout.addWidget(self.peak_window_recon)


        self.verticalLayout.addWidget(self.peak_window_container)

        self.position_label = QLabel(ModelReconTile)
        self.position_label.setObjectName(u"position_label")
        font = QFont()
        font.setFamilies([u"Lato"])
        font.setPointSize(10)
        font.setWeight(QFont.Light)
        self.position_label.setFont(font)
        self.position_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.position_label.setStyleSheet(u"border: None;\n"
"color: #ebebeb;\n"
"background-color: transparent;")
        self.position_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.position_label)


        self.retranslateUi(ModelReconTile)

        QMetaObject.connectSlotsByName(ModelReconTile)
    # setupUi

    def retranslateUi(self, ModelReconTile):
        ModelReconTile.setWindowTitle(QCoreApplication.translate("ModelReconTile", u"Form", None))
        self.peak_window_original.setText(QCoreApplication.translate("ModelReconTile", u"Original", None))
        self.arrow_left.setText("")
        self.peak_window_recon.setText(QCoreApplication.translate("ModelReconTile", u"Recon", None))
        self.position_label.setText(QCoreApplication.translate("ModelReconTile", u"RT; XX.X - DT: XXX.XX", None))
    # retranslateUi

