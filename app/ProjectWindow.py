# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ProjectWindow.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QMainWindow,
    QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_ProjectWindow(object):
    def setupUi(self, ProjectWindow):
        if not ProjectWindow.objectName():
            ProjectWindow.setObjectName(u"ProjectWindow")
        ProjectWindow.resize(1400, 883)
        ProjectWindow.setMinimumSize(QSize(1400, 820))
        icon = QIcon()
        icon.addFile(u"ui/_pics/logo_small.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        ProjectWindow.setWindowIcon(icon)
        self.centralwidget = QWidget(ProjectWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.Sidebar_container = QWidget(self.centralwidget)
        self.Sidebar_container.setObjectName(u"Sidebar_container")
        self.Sidebar_container.setMinimumSize(QSize(130, 820))
        self.Sidebar_container.setMaximumSize(QSize(130, 16777215))
        self.Sidebar_container.setStyleSheet(u"background-color: #2f2f2f;")
        self.verticalLayout_7 = QVBoxLayout(self.Sidebar_container)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.Sidebar_top = QWidget(self.Sidebar_container)
        self.Sidebar_top.setObjectName(u"Sidebar_top")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Sidebar_top.sizePolicy().hasHeightForWidth())
        self.Sidebar_top.setSizePolicy(sizePolicy)
        self.Sidebar_top.setMinimumSize(QSize(130, 670))
        self.Sidebar_top.setMaximumSize(QSize(130, 670))
        self.Sidebar_top.setStyleSheet(u"")
        self.verticalLayout_9 = QVBoxLayout(self.Sidebar_top)
        self.verticalLayout_9.setSpacing(6)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.dataset_container = QWidget(self.Sidebar_top)
        self.dataset_container.setObjectName(u"dataset_container")
        self.dataset_container.setStyleSheet(u"")
        self.verticalLayout = QVBoxLayout(self.dataset_container)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(-1, -1, -1, 15)
        self.dataset_button = QPushButton(self.dataset_container)
        self.dataset_button.setObjectName(u"dataset_button")
        self.dataset_button.setMaximumSize(QSize(16777215, 90))
        self.dataset_button.setStyleSheet(u"border: 0px;")
        icon1 = QIcon()
        icon1.addFile(u"ui/_pics/icons/dataset_white.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.dataset_button.setIcon(icon1)
        self.dataset_button.setIconSize(QSize(80, 80))

        self.verticalLayout.addWidget(self.dataset_button)

        self.dataset_label = QLabel(self.dataset_container)
        self.dataset_label.setObjectName(u"dataset_label")
        font = QFont()
        font.setFamilies([u"Lato"])
        font.setPointSize(10)
        self.dataset_label.setFont(font)
        self.dataset_label.setStyleSheet(u"")
        self.dataset_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.dataset_label)


        self.verticalLayout_9.addWidget(self.dataset_container)

        self.preprocessing_container = QWidget(self.Sidebar_top)
        self.preprocessing_container.setObjectName(u"preprocessing_container")
        self.preprocessing_container.setStyleSheet(u"")
        self.verticalLayout_2 = QVBoxLayout(self.preprocessing_container)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.preprocessing_button = QPushButton(self.preprocessing_container)
        self.preprocessing_button.setObjectName(u"preprocessing_button")
        self.preprocessing_button.setMaximumSize(QSize(16777215, 90))
        self.preprocessing_button.setStyleSheet(u"border: 0px;\n"
"border-top: 2px solid #666666;\n"
"padding-top: 20px;")
        icon2 = QIcon()
        icon2.addFile(u"ui/_pics/icons/preprocessing_white.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.preprocessing_button.setIcon(icon2)
        self.preprocessing_button.setIconSize(QSize(80, 80))

        self.verticalLayout_2.addWidget(self.preprocessing_button)

        self.preprocessing_label = QLabel(self.preprocessing_container)
        self.preprocessing_label.setObjectName(u"preprocessing_label")
        self.preprocessing_label.setFont(font)
        self.preprocessing_label.setStyleSheet(u"")
        self.preprocessing_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_2.addWidget(self.preprocessing_label)


        self.verticalLayout_9.addWidget(self.preprocessing_container)

        self.peak_explorer_container = QWidget(self.Sidebar_top)
        self.peak_explorer_container.setObjectName(u"peak_explorer_container")
        self.peak_explorer_container.setStyleSheet(u"")
        self.verticalLayout_3 = QVBoxLayout(self.peak_explorer_container)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.peak_explorer_button = QPushButton(self.peak_explorer_container)
        self.peak_explorer_button.setObjectName(u"peak_explorer_button")
        self.peak_explorer_button.setMaximumSize(QSize(16777215, 90))
        self.peak_explorer_button.setStyleSheet(u"border: 0px;\n"
"border-top: 2px solid #666666;\n"
"padding-top: 20px;")
        icon3 = QIcon()
        icon3.addFile(u"ui/_pics/icons/peak_explorer_white.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.peak_explorer_button.setIcon(icon3)
        self.peak_explorer_button.setIconSize(QSize(80, 80))

        self.verticalLayout_3.addWidget(self.peak_explorer_button)

        self.peak_explorer_label = QLabel(self.peak_explorer_container)
        self.peak_explorer_label.setObjectName(u"peak_explorer_label")
        self.peak_explorer_label.setFont(font)
        self.peak_explorer_label.setStyleSheet(u"")
        self.peak_explorer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_3.addWidget(self.peak_explorer_label)


        self.verticalLayout_9.addWidget(self.peak_explorer_container)

        self.consensus_container = QWidget(self.Sidebar_top)
        self.consensus_container.setObjectName(u"consensus_container")
        self.consensus_container.setStyleSheet(u"")
        self.verticalLayout_4 = QVBoxLayout(self.consensus_container)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.consensus_button = QPushButton(self.consensus_container)
        self.consensus_button.setObjectName(u"consensus_button")
        self.consensus_button.setMaximumSize(QSize(16777215, 90))
        self.consensus_button.setStyleSheet(u"border: 0px;\n"
"border-top: 2px solid #666666;\n"
"padding-top: 20px;")
        icon4 = QIcon()
        icon4.addFile(u"ui/_pics/icons/consensus_peak_white.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.consensus_button.setIcon(icon4)
        self.consensus_button.setIconSize(QSize(80, 80))

        self.verticalLayout_4.addWidget(self.consensus_button)

        self.consensus_label = QLabel(self.consensus_container)
        self.consensus_label.setObjectName(u"consensus_label")
        self.consensus_label.setFont(font)
        self.consensus_label.setStyleSheet(u"")
        self.consensus_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_4.addWidget(self.consensus_label)


        self.verticalLayout_9.addWidget(self.consensus_container)

        self.classifier_container = QWidget(self.Sidebar_top)
        self.classifier_container.setObjectName(u"classifier_container")
        self.classifier_container.setStyleSheet(u"")
        self.verticalLayout_5 = QVBoxLayout(self.classifier_container)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.classifier_button = QPushButton(self.classifier_container)
        self.classifier_button.setObjectName(u"classifier_button")
        self.classifier_button.setMaximumSize(QSize(16777215, 90))
        self.classifier_button.setStyleSheet(u"border: 0px;\n"
"border-top: 2px solid #666666;\n"
"padding-top: 20px;")
        icon5 = QIcon()
        icon5.addFile(u"ui/_pics/icons/classifier_white.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.classifier_button.setIcon(icon5)
        self.classifier_button.setIconSize(QSize(80, 80))

        self.verticalLayout_5.addWidget(self.classifier_button)

        self.classifier_label = QLabel(self.classifier_container)
        self.classifier_label.setObjectName(u"classifier_label")
        self.classifier_label.setFont(font)
        self.classifier_label.setStyleSheet(u"")
        self.classifier_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_5.addWidget(self.classifier_label)


        self.verticalLayout_9.addWidget(self.classifier_container)


        self.verticalLayout_7.addWidget(self.Sidebar_top)

        self.verticalSpacer = QSpacerItem(20, 65, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_7.addItem(self.verticalSpacer)

        self.Sidebar_bottom = QWidget(self.Sidebar_container)
        self.Sidebar_bottom.setObjectName(u"Sidebar_bottom")
        sizePolicy.setHeightForWidth(self.Sidebar_bottom.sizePolicy().hasHeightForWidth())
        self.Sidebar_bottom.setSizePolicy(sizePolicy)
        self.Sidebar_bottom.setMinimumSize(QSize(130, 130))
        self.Sidebar_bottom.setMaximumSize(QSize(130, 130))
        self.Sidebar_bottom.setStyleSheet(u"")
        self.verticalLayout_8 = QVBoxLayout(self.Sidebar_bottom)
        self.verticalLayout_8.setSpacing(0)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.settings_container = QWidget(self.Sidebar_bottom)
        self.settings_container.setObjectName(u"settings_container")
        self.settings_container.setStyleSheet(u"")
        self.verticalLayout_6 = QVBoxLayout(self.settings_container)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(9, 0, -1, 9)
        self.settings_button = QPushButton(self.settings_container)
        self.settings_button.setObjectName(u"settings_button")
        self.settings_button.setMaximumSize(QSize(16777215, 90))
        self.settings_button.setStyleSheet(u"border: 0px;\n"
"border-top: 2px solid #666666;\n"
"padding-top: 20px;")
        icon6 = QIcon()
        icon6.addFile(u"ui/_pics/icons/settings_white.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.settings_button.setIcon(icon6)
        self.settings_button.setIconSize(QSize(80, 80))

        self.verticalLayout_6.addWidget(self.settings_button)

        self.settings_label = QLabel(self.settings_container)
        self.settings_label.setObjectName(u"settings_label")
        self.settings_label.setFont(font)
        self.settings_label.setStyleSheet(u"")
        self.settings_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_6.addWidget(self.settings_label)


        self.verticalLayout_8.addWidget(self.settings_container)


        self.verticalLayout_7.addWidget(self.Sidebar_bottom)


        self.horizontalLayout.addWidget(self.Sidebar_container)

        self.Main_container = QWidget(self.centralwidget)
        self.Main_container.setObjectName(u"Main_container")
        self.Main_container.setStyleSheet(u"background-color: #1d1d1d;")

        self.horizontalLayout.addWidget(self.Main_container)

        ProjectWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(ProjectWindow)

        QMetaObject.connectSlotsByName(ProjectWindow)
    # setupUi

    def retranslateUi(self, ProjectWindow):
        ProjectWindow.setWindowTitle(QCoreApplication.translate("ProjectWindow", u"MainWindow", None))
        self.dataset_button.setText("")
        self.dataset_label.setText(QCoreApplication.translate("ProjectWindow", u"Dataset", None))
        self.preprocessing_button.setText("")
        self.preprocessing_label.setText(QCoreApplication.translate("ProjectWindow", u"Preprocessing", None))
        self.peak_explorer_button.setText("")
        self.peak_explorer_label.setText(QCoreApplication.translate("ProjectWindow", u"Peak Explorer", None))
        self.consensus_button.setText("")
        self.consensus_label.setText(QCoreApplication.translate("ProjectWindow", u"Consensus Peaks", None))
        self.classifier_button.setText("")
        self.classifier_label.setText(QCoreApplication.translate("ProjectWindow", u"Classifier", None))
        self.settings_button.setText("")
        self.settings_label.setText(QCoreApplication.translate("ProjectWindow", u"Settings", None))
    # retranslateUi

