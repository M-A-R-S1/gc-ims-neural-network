# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MainWindow.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QLayout,
    QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_StartWidget(object):
    def setupUi(self, StartWidget):
        if not StartWidget.objectName():
            StartWidget.setObjectName(u"StartWidget")
        StartWidget.resize(1574, 1028)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(StartWidget.sizePolicy().hasHeightForWidth())
        StartWidget.setSizePolicy(sizePolicy)
        StartWidget.setMinimumSize(QSize(1500, 800))
        StartWidget.setMaximumSize(QSize(9999999, 999999))
        StartWidget.setBaseSize(QSize(0, 0))
        font = QFont()
        font.setKerning(True)
        StartWidget.setFont(font)
        StartWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        icon = QIcon()
        icon.addFile(u"ui/_pics/logo_small.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        StartWidget.setWindowIcon(icon)
        StartWidget.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        StartWidget.setAutoFillBackground(False)
        StartWidget.setStyleSheet(u"background-color: rgb(29, 29, 29)")
        StartWidget.setLocale(QLocale(QLocale.English, QLocale.Germany))
        self.horizontalLayout = QHBoxLayout(StartWidget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.Sidebar = QWidget(StartWidget)
        self.Sidebar.setObjectName(u"Sidebar")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.Sidebar.sizePolicy().hasHeightForWidth())
        self.Sidebar.setSizePolicy(sizePolicy1)
        self.Sidebar.setMinimumSize(QSize(130, 800))
        self.Sidebar.setMaximumSize(QSize(130, 16777215))
        self.Sidebar.setStyleSheet(u"background-color: #2f2f2f;")
        self.verticalLayout_7 = QVBoxLayout(self.Sidebar)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.Sidebar_top = QWidget(self.Sidebar)
        self.Sidebar_top.setObjectName(u"Sidebar_top")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.Sidebar_top.sizePolicy().hasHeightForWidth())
        self.Sidebar_top.setSizePolicy(sizePolicy2)
        self.Sidebar_top.setMinimumSize(QSize(130, 600))
        self.Sidebar_top.setMaximumSize(QSize(130, 600))
        self.Sidebar_top.setStyleSheet(u"background-color: #444400;")
        self.verticalLayout_9 = QVBoxLayout(self.Sidebar_top)
        self.verticalLayout_9.setSpacing(6)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.dataset_container = QWidget(self.Sidebar_top)
        self.dataset_container.setObjectName(u"dataset_container")
        self.dataset_container.setStyleSheet(u"background-color: #005544;")
        self.verticalLayout = QVBoxLayout(self.dataset_container)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.dataset_button = QPushButton(self.dataset_container)
        self.dataset_button.setObjectName(u"dataset_button")
        self.dataset_button.setMaximumSize(QSize(16777215, 70))
        self.dataset_button.setStyleSheet(u"border: 0px;")
        icon1 = QIcon()
        icon1.addFile(u"ui/_pics/icons/dataset_white.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.dataset_button.setIcon(icon1)
        self.dataset_button.setIconSize(QSize(80, 80))

        self.verticalLayout.addWidget(self.dataset_button)

        self.dataset_label = QLabel(self.dataset_container)
        self.dataset_label.setObjectName(u"dataset_label")
        font1 = QFont()
        font1.setFamilies([u"Lato"])
        font1.setPointSize(11)
        self.dataset_label.setFont(font1)
        self.dataset_label.setStyleSheet(u"")
        self.dataset_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.dataset_label)


        self.verticalLayout_9.addWidget(self.dataset_container)

        self.preprocessing_container = QWidget(self.Sidebar_top)
        self.preprocessing_container.setObjectName(u"preprocessing_container")
        self.preprocessing_container.setStyleSheet(u"background-color: #005544;")
        self.verticalLayout_2 = QVBoxLayout(self.preprocessing_container)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.preprocessing_button = QPushButton(self.preprocessing_container)
        self.preprocessing_button.setObjectName(u"preprocessing_button")
        self.preprocessing_button.setMaximumSize(QSize(16777215, 70))
        self.preprocessing_button.setStyleSheet(u"border: 0px;")
        icon2 = QIcon()
        icon2.addFile(u"ui/_pics/icons/preprocessing_white.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.preprocessing_button.setIcon(icon2)
        self.preprocessing_button.setIconSize(QSize(80, 80))

        self.verticalLayout_2.addWidget(self.preprocessing_button)

        self.preprocessing_label = QLabel(self.preprocessing_container)
        self.preprocessing_label.setObjectName(u"preprocessing_label")
        self.preprocessing_label.setFont(font1)
        self.preprocessing_label.setStyleSheet(u"")
        self.preprocessing_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_2.addWidget(self.preprocessing_label)


        self.verticalLayout_9.addWidget(self.preprocessing_container)

        self.peak_explorer_container = QWidget(self.Sidebar_top)
        self.peak_explorer_container.setObjectName(u"peak_explorer_container")
        self.peak_explorer_container.setStyleSheet(u"background-color: #005544;")
        self.verticalLayout_3 = QVBoxLayout(self.peak_explorer_container)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.peak_explorer_button = QPushButton(self.peak_explorer_container)
        self.peak_explorer_button.setObjectName(u"peak_explorer_button")
        self.peak_explorer_button.setMaximumSize(QSize(16777215, 70))
        self.peak_explorer_button.setStyleSheet(u"border: 0px;")
        icon3 = QIcon()
        icon3.addFile(u"ui/_pics/icons/peak_explorer_white.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.peak_explorer_button.setIcon(icon3)
        self.peak_explorer_button.setIconSize(QSize(80, 80))

        self.verticalLayout_3.addWidget(self.peak_explorer_button)

        self.peak_explorer_label = QLabel(self.peak_explorer_container)
        self.peak_explorer_label.setObjectName(u"peak_explorer_label")
        self.peak_explorer_label.setFont(font1)
        self.peak_explorer_label.setStyleSheet(u"")
        self.peak_explorer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_3.addWidget(self.peak_explorer_label)


        self.verticalLayout_9.addWidget(self.peak_explorer_container)

        self.consensus_container = QWidget(self.Sidebar_top)
        self.consensus_container.setObjectName(u"consensus_container")
        self.consensus_container.setStyleSheet(u"background-color: #005544;")
        self.verticalLayout_4 = QVBoxLayout(self.consensus_container)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.consensus_button = QPushButton(self.consensus_container)
        self.consensus_button.setObjectName(u"consensus_button")
        self.consensus_button.setMaximumSize(QSize(16777215, 70))
        self.consensus_button.setStyleSheet(u"border: 0px;")
        icon4 = QIcon()
        icon4.addFile(u"ui/_pics/icons/consensus_peak_white.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.consensus_button.setIcon(icon4)
        self.consensus_button.setIconSize(QSize(80, 80))

        self.verticalLayout_4.addWidget(self.consensus_button)

        self.consensus_label = QLabel(self.consensus_container)
        self.consensus_label.setObjectName(u"consensus_label")
        self.consensus_label.setFont(font1)
        self.consensus_label.setStyleSheet(u"")
        self.consensus_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_4.addWidget(self.consensus_label)


        self.verticalLayout_9.addWidget(self.consensus_container)

        self.classifier_container = QWidget(self.Sidebar_top)
        self.classifier_container.setObjectName(u"classifier_container")
        self.classifier_container.setStyleSheet(u"background-color: #005544;")
        self.verticalLayout_5 = QVBoxLayout(self.classifier_container)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.classifier_button = QPushButton(self.classifier_container)
        self.classifier_button.setObjectName(u"classifier_button")
        self.classifier_button.setMaximumSize(QSize(16777215, 70))
        self.classifier_button.setStyleSheet(u"border: 0px;")
        icon5 = QIcon()
        icon5.addFile(u"ui/_pics/icons/classifier_white.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.classifier_button.setIcon(icon5)
        self.classifier_button.setIconSize(QSize(80, 80))

        self.verticalLayout_5.addWidget(self.classifier_button)

        self.classifier_label = QLabel(self.classifier_container)
        self.classifier_label.setObjectName(u"classifier_label")
        self.classifier_label.setFont(font1)
        self.classifier_label.setStyleSheet(u"")
        self.classifier_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_5.addWidget(self.classifier_label)


        self.verticalLayout_9.addWidget(self.classifier_container)


        self.verticalLayout_7.addWidget(self.Sidebar_top, 0, Qt.AlignmentFlag.AlignTop)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_7.addItem(self.verticalSpacer)

        self.Sidebar_bottom = QWidget(self.Sidebar)
        self.Sidebar_bottom.setObjectName(u"Sidebar_bottom")
        sizePolicy2.setHeightForWidth(self.Sidebar_bottom.sizePolicy().hasHeightForWidth())
        self.Sidebar_bottom.setSizePolicy(sizePolicy2)
        self.Sidebar_bottom.setMinimumSize(QSize(130, 120))
        self.Sidebar_bottom.setMaximumSize(QSize(130, 120))
        self.Sidebar_bottom.setStyleSheet(u"background-color: #444400;")
        self.verticalLayout_8 = QVBoxLayout(self.Sidebar_bottom)
        self.verticalLayout_8.setSpacing(0)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.settings_container = QWidget(self.Sidebar_bottom)
        self.settings_container.setObjectName(u"settings_container")
        self.settings_container.setStyleSheet(u"background-color: #005544;")
        self.verticalLayout_6 = QVBoxLayout(self.settings_container)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.settings_button = QPushButton(self.settings_container)
        self.settings_button.setObjectName(u"settings_button")
        self.settings_button.setMaximumSize(QSize(16777215, 70))
        self.settings_button.setStyleSheet(u"border: 0px;")
        icon6 = QIcon()
        icon6.addFile(u"ui/_pics/icons/settings_white.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.settings_button.setIcon(icon6)
        self.settings_button.setIconSize(QSize(80, 80))

        self.verticalLayout_6.addWidget(self.settings_button)

        self.settings_label = QLabel(self.settings_container)
        self.settings_label.setObjectName(u"settings_label")
        self.settings_label.setFont(font1)
        self.settings_label.setStyleSheet(u"")
        self.settings_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_6.addWidget(self.settings_label)


        self.verticalLayout_8.addWidget(self.settings_container)


        self.verticalLayout_7.addWidget(self.Sidebar_bottom, 0, Qt.AlignmentFlag.AlignBottom)

        self.verticalLayout_7.setStretch(2, 1)

        self.horizontalLayout.addWidget(self.Sidebar)

        self.widget = QWidget(StartWidget)
        self.widget.setObjectName(u"widget")
        self.widget.setStyleSheet(u"background-color: #440000;")

        self.horizontalLayout.addWidget(self.widget)


        self.retranslateUi(StartWidget)

        QMetaObject.connectSlotsByName(StartWidget)
    # setupUi

    def retranslateUi(self, StartWidget):
        StartWidget.setWindowTitle(QCoreApplication.translate("StartWidget", u"GC-IMS suite", None))
        self.dataset_button.setText("")
        self.dataset_label.setText(QCoreApplication.translate("StartWidget", u"Dataset", None))
        self.preprocessing_button.setText("")
        self.preprocessing_label.setText(QCoreApplication.translate("StartWidget", u"Preprocessing", None))
        self.peak_explorer_button.setText("")
        self.peak_explorer_label.setText(QCoreApplication.translate("StartWidget", u"Peak Explorer", None))
        self.consensus_button.setText("")
        self.consensus_label.setText(QCoreApplication.translate("StartWidget", u"Consensus Peaks", None))
        self.classifier_button.setText("")
        self.classifier_label.setText(QCoreApplication.translate("StartWidget", u"Classifier", None))
        self.settings_button.setText("")
        self.settings_label.setText(QCoreApplication.translate("StartWidget", u"Settings", None))
    # retranslateUi

