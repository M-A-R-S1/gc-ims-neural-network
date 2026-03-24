import sys
from config import *
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtGui import QIcon, QPalette, QColor
from ProjectWindow import Ui_ProjectWindow

class MainWindow(QtWidgets.QMainWindow, Ui_ProjectWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # create fade animations for the buttons.
        """
        self.button_hover_animation(button=self.button_create,
                                    start_color=QtGui.QColor(BUTTON_BACKGROUND_COLOR),
                                    end_color=QtGui.QColor(BUTTON_BACKGROUND_HOVER_COLOR),
                                    dashed=True)

        self.button_hover_animation(button=self.button_open,
                                    start_color=QtGui.QColor(BUTTON_BACKGROUND_COLOR),
                                    end_color=QtGui.QColor(BUTTON_BACKGROUND_HOVER_COLOR),
                                    dashed=True)

        self.button_hover_animation(button=self.button_cancle,
                                    start_color=QtGui.QColor(BUTTON_BACKGROUND_COLOR),
                                    end_color=QtGui.QColor(BUTTON_BACKGROUND_HOVER_COLOR),
                                    dashed=False)

        self.button_hover_animation(button=self.button_create_2,
                                    start_color=QtGui.QColor(BUTTON_BACKGROUND_COLOR),
                                    end_color=QtGui.QColor(BUTTON_BACKGROUND_HOVER_COLOR),
                                    dashed=False)
        """

        # Get the active color palette
        palette_active = self.dataset_button.palette()
        palette_active.setColor(QPalette.WindowText, QColor(ACTIVE_COLOR))
        # Get the deactivated color palette
        palette_deactivated = self.dataset_button.palette()
        palette_deactivated.setColor(QPalette.WindowText, QColor(DEACTIVATED_COLOR))
        # Get the normal color palette
        palette_normal = self.dataset_button.palette()
        palette_normal.setColor(QPalette.WindowText, QColor(NORMAL_COLOR))

        # Set the dataset as active.
        self.dataset_button.setIcon(QIcon("ui/_pics/icons/dataset_orange.png"))
        self.dataset_label.setPalette(palette_active)
        # Set the remaining buttons as inactive.
        self.preprocessing_button.setEnabled(False)
        self.preprocessing_button.setIcon(QIcon("ui/_pics/icons/preprocessing_grey.png"))
        self.preprocessing_label.setPalette(palette_deactivated)
        self.peak_explorer_button.setEnabled(False)
        self.peak_explorer_button.setIcon(QIcon("ui/_pics/icons/peak_explorer_grey.png"))
        self.peak_explorer_label.setPalette(palette_deactivated)
        self.consensus_button.setEnabled(False)
        self.consensus_button.setIcon(QIcon("ui/_pics/icons/consensus_peak_grey.png"))
        self.consensus_label.setPalette(palette_deactivated)
        self.classifier_button.setEnabled(False)
        self.classifier_button.setIcon(QIcon("ui/_pics/icons/classifier_grey.png"))
        self.classifier_label.setPalette(palette_deactivated)


    def button_hover_animation(self,
                               button: QtWidgets.QPushButton,
                               start_color: QtGui.QColor,
                               end_color: QtGui.QColor,
                               dashed: bool) -> None:
        """
        Defines the hover animation for the create and load buttons. This animation changes the background color over
        the duration of some milliseconds to create a fade effect. This is done according to the values saved in the
        global variables BUTTON_BACKGROUND_COLOR and BUTTON_BACKGROUND_HOVER_COLOR.

        :param button: the button widget for which the animation will be shown
        :param start_color: the start background color [base background]
        :param end_color: the end background color [hover background]
        :param dashed: If True the border of the button is dashed.

        :return: None
        """

        # Defining the animation.
        animation = QtCore.QVariantAnimation(button)
        animation.setDuration(250)
        animation.setStartValue(start_color)
        animation.setEndValue(end_color)

        def update_stylesheet_dashed(color: QtGui.QColor) -> None:
            """
            Updates the stylesheet of the button while the animation is running.

            :param color: The current color in the animation.

            :return: None.
            """

            # Set the button stylesheet.
            button.setStyleSheet(f"""
                                    QPushButton {{
                                        border: 1.5px dashed {button.palette().buttonText().color().name()};
                                        background-color: {color.name()}; 
                                        color: {button.palette().buttonText().color().name()};
                                        border-radius: 10px;
                                    }}
                                """)

        def update_stylesheet_solid(color: QtGui.QColor) -> None:
            """
            Updates the stylesheet of the button while the animation is running.

            :param color: The current color in the animation.

            :return: None.
            """

            # Set the button stylesheet.
            button.setStyleSheet(f"""
                                    QPushButton {{
                                        border: 1px solid {button.palette().buttonText().color().name()};
                                        background-color: {color.name()}; 
                                        color: {button.palette().buttonText().color().name()};
                                        border-radius: 10px;
                                    }}
                                """)

        # Connects the animation to the update function.
        if dashed:
            animation.valueChanged.connect(update_stylesheet_dashed)
        else:
            animation.valueChanged.connect(update_stylesheet_solid)
        # Connects the animation to the button.
        button.background_animation = animation

        # React to mouse enter and leave events for the button.
        button.enterEvent = lambda e: self.run_animation(button, True)
        button.leaveEvent = lambda e: self.run_animation(button, False)

    def run_animation(self,
                      button: QtWidgets.QPushButton,
                      hover: bool) -> None:
        """
        Runs the animation with the specified direction, if the mouse goes in or out or a button.

        :param button: The button for which the animation runs.
        :param hover: Is the mouse currently hovering over the button?

        :return: None
        """

        # Check which animation to play.
        if hover:
            button.background_animation.setDirection(QtCore.QAbstractAnimation.Direction.Forward)
        else:
            button.background_animation.setDirection(QtCore.QAbstractAnimation.Direction.Backward)

        # Start the animation.
        button.background_animation.start()


# Create an application instance!
app = QtWidgets.QApplication(sys.argv)

# Create a window and show it.
window = MainWindow()
window.show()

# Start the App.
app.exec()