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
    QPushButton, QSizePolicy, QSpacerItem, QStackedWidget,
    QVBoxLayout, QWidget)
import resources_rc

class Ui_ProjectWindow(object):
    def setupUi(self, ProjectWindow):
        if not ProjectWindow.objectName():
            ProjectWindow.setObjectName(u"ProjectWindow")
        ProjectWindow.resize(1599, 944)
        ProjectWindow.setMinimumSize(QSize(1400, 820))
        icon = QIcon()
        icon.addFile(u":/ui/_pics/logo_small.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        ProjectWindow.setWindowIcon(icon)
        self.centralwidget = QWidget(ProjectWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.Sidebar_container = QWidget(self.centralwidget)
        self.Sidebar_container.setObjectName(u"Sidebar_container")
        self.Sidebar_container.setMinimumSize(QSize(80, 820))
        self.Sidebar_container.setMaximumSize(QSize(80, 16777215))
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
        self.Sidebar_top.setMinimumSize(QSize(80, 780))
        self.Sidebar_top.setMaximumSize(QSize(80, 780))
        self.Sidebar_top.setStyleSheet(u"")
        self.verticalLayout_10 = QVBoxLayout(self.Sidebar_top)
        self.verticalLayout_10.setSpacing(6)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.verticalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.sb_dataset_container = QWidget(self.Sidebar_top)
        self.sb_dataset_container.setObjectName(u"sb_dataset_container")
        self.sb_dataset_container.setMinimumSize(QSize(0, 0))
        self.sb_dataset_container.setMaximumSize(QSize(16777215, 90))
        self.sb_dataset_container.setStyleSheet(u"")
        self.verticalLayout = QVBoxLayout(self.sb_dataset_container)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(-1, -1, -1, 5)
        self.sb_dataset_button = QPushButton(self.sb_dataset_container)
        self.sb_dataset_button.setObjectName(u"sb_dataset_button")
        self.sb_dataset_button.setMinimumSize(QSize(0, 60))
        self.sb_dataset_button.setMaximumSize(QSize(16777215, 70))
        self.sb_dataset_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.sb_dataset_button.setStyleSheet(u"QPushButton {\n"
"    background-color: transparent;\n"
"    border: none;\n"
"}")
        icon1 = QIcon()
        icon1.addFile(u":/ui/_pics/icons/dataset_white.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.sb_dataset_button.setIcon(icon1)
        self.sb_dataset_button.setIconSize(QSize(60, 60))

        self.verticalLayout.addWidget(self.sb_dataset_button)

        self.sb_dataset_label = QLabel(self.sb_dataset_container)
        self.sb_dataset_label.setObjectName(u"sb_dataset_label")
        self.sb_dataset_label.setMaximumSize(QSize(16777215, 16777215))
        font = QFont()
        font.setFamilies([u"Lato"])
        font.setPointSize(10)
        self.sb_dataset_label.setFont(font)
        self.sb_dataset_label.setStyleSheet(u"color: #ebebeb;")
        self.sb_dataset_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sb_dataset_label.setWordWrap(True)

        self.verticalLayout.addWidget(self.sb_dataset_label)


        self.verticalLayout_10.addWidget(self.sb_dataset_container)

        self.sb_preprocessing_container = QWidget(self.Sidebar_top)
        self.sb_preprocessing_container.setObjectName(u"sb_preprocessing_container")
        self.sb_preprocessing_container.setStyleSheet(u"")
        self.verticalLayout_2 = QVBoxLayout(self.sb_preprocessing_container)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.sb_preprocessing_button = QPushButton(self.sb_preprocessing_container)
        self.sb_preprocessing_button.setObjectName(u"sb_preprocessing_button")
        self.sb_preprocessing_button.setEnabled(True)
        self.sb_preprocessing_button.setMaximumSize(QSize(16777215, 70))
        self.sb_preprocessing_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.sb_preprocessing_button.setStyleSheet(u"QPushButton {\n"
"    background-color: transparent;\n"
"    border: none;\n"
"    border-top: 2px solid #666666;\n"
"	padding-top: 20px;\n"
"}\n"
"")
        icon2 = QIcon()
        icon2.addFile(u":/ui/_pics/icons/preprocessing_white.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.sb_preprocessing_button.setIcon(icon2)
        self.sb_preprocessing_button.setIconSize(QSize(60, 60))

        self.verticalLayout_2.addWidget(self.sb_preprocessing_button)

        self.sb_preprocessing_label = QLabel(self.sb_preprocessing_container)
        self.sb_preprocessing_label.setObjectName(u"sb_preprocessing_label")
        self.sb_preprocessing_label.setFont(font)
        self.sb_preprocessing_label.setStyleSheet(u"color: #ebebeb;")
        self.sb_preprocessing_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sb_preprocessing_label.setWordWrap(True)

        self.verticalLayout_2.addWidget(self.sb_preprocessing_label)


        self.verticalLayout_10.addWidget(self.sb_preprocessing_container)

        self.sb_peak_explorer_container = QWidget(self.Sidebar_top)
        self.sb_peak_explorer_container.setObjectName(u"sb_peak_explorer_container")
        self.sb_peak_explorer_container.setStyleSheet(u"")
        self.verticalLayout_3 = QVBoxLayout(self.sb_peak_explorer_container)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.sb_peak_explorer_button = QPushButton(self.sb_peak_explorer_container)
        self.sb_peak_explorer_button.setObjectName(u"sb_peak_explorer_button")
        self.sb_peak_explorer_button.setMaximumSize(QSize(16777215, 70))
        self.sb_peak_explorer_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.sb_peak_explorer_button.setStyleSheet(u"QPushButton {\n"
"    background-color: transparent;\n"
"    border: none;\n"
"    border-top: 2px solid #666666;\n"
"	padding-top: 20px;\n"
"}")
        icon3 = QIcon()
        icon3.addFile(u":/ui/_pics/icons/peak_explorer_white.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.sb_peak_explorer_button.setIcon(icon3)
        self.sb_peak_explorer_button.setIconSize(QSize(60, 60))

        self.verticalLayout_3.addWidget(self.sb_peak_explorer_button)

        self.sb_peak_explorer_label = QLabel(self.sb_peak_explorer_container)
        self.sb_peak_explorer_label.setObjectName(u"sb_peak_explorer_label")
        self.sb_peak_explorer_label.setFont(font)
        self.sb_peak_explorer_label.setStyleSheet(u"color: #ebebeb;")
        self.sb_peak_explorer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sb_peak_explorer_label.setWordWrap(True)

        self.verticalLayout_3.addWidget(self.sb_peak_explorer_label)


        self.verticalLayout_10.addWidget(self.sb_peak_explorer_container)

        self.sb_consensus_container = QWidget(self.Sidebar_top)
        self.sb_consensus_container.setObjectName(u"sb_consensus_container")
        self.sb_consensus_container.setStyleSheet(u"")
        self.verticalLayout_4 = QVBoxLayout(self.sb_consensus_container)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.sb_consensus_button = QPushButton(self.sb_consensus_container)
        self.sb_consensus_button.setObjectName(u"sb_consensus_button")
        self.sb_consensus_button.setMaximumSize(QSize(16777215, 70))
        self.sb_consensus_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.sb_consensus_button.setStyleSheet(u"QPushButton {\n"
"    background-color: transparent;\n"
"    border: none;\n"
"    border-top: 2px solid #666666;\n"
"	padding-top: 20px;\n"
"}")
        icon4 = QIcon()
        icon4.addFile(u":/ui/_pics/icons/consensus_peak_white.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.sb_consensus_button.setIcon(icon4)
        self.sb_consensus_button.setIconSize(QSize(60, 60))

        self.verticalLayout_4.addWidget(self.sb_consensus_button)

        self.sb_consensus_label = QLabel(self.sb_consensus_container)
        self.sb_consensus_label.setObjectName(u"sb_consensus_label")
        self.sb_consensus_label.setFont(font)
        self.sb_consensus_label.setStyleSheet(u"color: #ebebeb;")
        self.sb_consensus_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sb_consensus_label.setWordWrap(True)

        self.verticalLayout_4.addWidget(self.sb_consensus_label)


        self.verticalLayout_10.addWidget(self.sb_consensus_container)

        self.sb_model_container = QWidget(self.Sidebar_top)
        self.sb_model_container.setObjectName(u"sb_model_container")
        self.sb_model_container.setStyleSheet(u"")
        self.verticalLayout_9 = QVBoxLayout(self.sb_model_container)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.sb_model_button = QPushButton(self.sb_model_container)
        self.sb_model_button.setObjectName(u"sb_model_button")
        self.sb_model_button.setMaximumSize(QSize(16777215, 70))
        self.sb_model_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.sb_model_button.setStyleSheet(u"QPushButton {\n"
"    background-color: transparent;\n"
"    border: none;\n"
"    border-top: 2px solid #666666;\n"
"	padding-top: 20px;\n"
"}")
        icon5 = QIcon()
        icon5.addFile(u":/ui/_pics/icons/neural_network_white.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.sb_model_button.setIcon(icon5)
        self.sb_model_button.setIconSize(QSize(60, 60))

        self.verticalLayout_9.addWidget(self.sb_model_button)

        self.sb_model_label = QLabel(self.sb_model_container)
        self.sb_model_label.setObjectName(u"sb_model_label")
        self.sb_model_label.setFont(font)
        self.sb_model_label.setStyleSheet(u"color: #ebebeb;")
        self.sb_model_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sb_model_label.setWordWrap(True)

        self.verticalLayout_9.addWidget(self.sb_model_label)


        self.verticalLayout_10.addWidget(self.sb_model_container)

        self.sb_classifier_container = QWidget(self.Sidebar_top)
        self.sb_classifier_container.setObjectName(u"sb_classifier_container")
        self.sb_classifier_container.setStyleSheet(u"")
        self.verticalLayout_5 = QVBoxLayout(self.sb_classifier_container)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.sb_classifier_button = QPushButton(self.sb_classifier_container)
        self.sb_classifier_button.setObjectName(u"sb_classifier_button")
        self.sb_classifier_button.setMaximumSize(QSize(16777215, 70))
        self.sb_classifier_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.sb_classifier_button.setStyleSheet(u"QPushButton {\n"
"    background-color: transparent;\n"
"    border: none;\n"
"    border-top: 2px solid #666666;\n"
"	padding-top: 20px;\n"
"}")
        icon6 = QIcon()
        icon6.addFile(u":/ui/_pics/icons/classifier_white.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.sb_classifier_button.setIcon(icon6)
        self.sb_classifier_button.setIconSize(QSize(60, 60))

        self.verticalLayout_5.addWidget(self.sb_classifier_button)

        self.sb_classifier_label = QLabel(self.sb_classifier_container)
        self.sb_classifier_label.setObjectName(u"sb_classifier_label")
        self.sb_classifier_label.setFont(font)
        self.sb_classifier_label.setStyleSheet(u"color: #ebebeb;")
        self.sb_classifier_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sb_classifier_label.setWordWrap(True)

        self.verticalLayout_5.addWidget(self.sb_classifier_label)


        self.verticalLayout_10.addWidget(self.sb_classifier_container)


        self.verticalLayout_7.addWidget(self.Sidebar_top)

        self.verticalSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_7.addItem(self.verticalSpacer)

        self.Sidebar_bottom = QWidget(self.Sidebar_container)
        self.Sidebar_bottom.setObjectName(u"Sidebar_bottom")
        self.Sidebar_bottom.setEnabled(True)
        sizePolicy.setHeightForWidth(self.Sidebar_bottom.sizePolicy().hasHeightForWidth())
        self.Sidebar_bottom.setSizePolicy(sizePolicy)
        self.Sidebar_bottom.setMinimumSize(QSize(80, 100))
        self.Sidebar_bottom.setMaximumSize(QSize(80, 100))
        self.Sidebar_bottom.setStyleSheet(u"")
        self.verticalLayout_8 = QVBoxLayout(self.Sidebar_bottom)
        self.verticalLayout_8.setSpacing(0)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.sb_settings_container = QWidget(self.Sidebar_bottom)
        self.sb_settings_container.setObjectName(u"sb_settings_container")
        self.sb_settings_container.setEnabled(True)
        self.sb_settings_container.setStyleSheet(u"")
        self.verticalLayout_6 = QVBoxLayout(self.sb_settings_container)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(9, 0, -1, 9)
        self.sb_settings_button = QPushButton(self.sb_settings_container)
        self.sb_settings_button.setObjectName(u"sb_settings_button")
        self.sb_settings_button.setMaximumSize(QSize(16777215, 70))
        self.sb_settings_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.sb_settings_button.setStyleSheet(u"QPushButton {\n"
"    background-color: transparent;\n"
"    border: none;\n"
"    border-top: 2px solid #666666;\n"
"	padding-top: 20px;\n"
"}")
        icon7 = QIcon()
        icon7.addFile(u":/ui/_pics/icons/settings_white.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.sb_settings_button.setIcon(icon7)
        self.sb_settings_button.setIconSize(QSize(60, 60))

        self.verticalLayout_6.addWidget(self.sb_settings_button)

        self.sb_settings_label = QLabel(self.sb_settings_container)
        self.sb_settings_label.setObjectName(u"sb_settings_label")
        self.sb_settings_label.setFont(font)
        self.sb_settings_label.setStyleSheet(u"color: #ebebeb;")
        self.sb_settings_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sb_settings_label.setWordWrap(True)

        self.verticalLayout_6.addWidget(self.sb_settings_label)


        self.verticalLayout_8.addWidget(self.sb_settings_container)


        self.verticalLayout_7.addWidget(self.Sidebar_bottom)


        self.horizontalLayout.addWidget(self.Sidebar_container)

        self.Main_container = QStackedWidget(self.centralwidget)
        self.Main_container.setObjectName(u"Main_container")
        self.Main_container.setStyleSheet(u"background-color: #1d1d1d;")
        self.dataset_container = QWidget()
        self.dataset_container.setObjectName(u"dataset_container")
        self.Main_container.addWidget(self.dataset_container)

        self.horizontalLayout.addWidget(self.Main_container)

        ProjectWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(ProjectWindow)

        QMetaObject.connectSlotsByName(ProjectWindow)
    # setupUi

    def retranslateUi(self, ProjectWindow):
        ProjectWindow.setWindowTitle(QCoreApplication.translate("ProjectWindow", u"MainWindow", None))
        self.sb_dataset_button.setText("")
        self.sb_dataset_label.setText(QCoreApplication.translate("ProjectWindow", u"Dataset", None))
        self.sb_preprocessing_button.setText("")
        self.sb_preprocessing_label.setText(QCoreApplication.translate("ProjectWindow", u"Pre-processing", None))
        self.sb_peak_explorer_button.setText("")
        self.sb_peak_explorer_label.setText(QCoreApplication.translate("ProjectWindow", u"Peak Explorer", None))
        self.sb_consensus_button.setText("")
        self.sb_consensus_label.setText(QCoreApplication.translate("ProjectWindow", u"Consensus Peaks", None))
        self.sb_model_button.setText("")
        self.sb_model_label.setText(QCoreApplication.translate("ProjectWindow", u"Model", None))
        self.sb_classifier_button.setText("")
        self.sb_classifier_label.setText(QCoreApplication.translate("ProjectWindow", u"Classifier", None))
        self.sb_settings_button.setText("")
        self.sb_settings_label.setText(QCoreApplication.translate("ProjectWindow", u"Settings", None))
    # retranslateUi

