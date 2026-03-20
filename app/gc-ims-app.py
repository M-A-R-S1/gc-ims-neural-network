import sys
from config import *
from PySide6 import QtWidgets, QtCore, QtGui
from StartUpWindow import Ui_StartUpWindow


class MainWindow(QtWidgets.QMainWindow, Ui_StartUpWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # create a fade animation for the create button.
        self.button_hover_animation(button=self.button_create,
                                    start_color=QtGui.QColor(BUTTON_BACKGROUND_COLOR),
                                    end_color=QtGui.QColor(BUTTON_BACKGROUND_HOVER_COLOR))

        # create a fade animation for the open button.
        self.button_hover_animation(button=self.button_open,
                                    start_color=QtGui.QColor(BUTTON_BACKGROUND_COLOR),
                                    end_color=QtGui.QColor(BUTTON_BACKGROUND_HOVER_COLOR))

    def button_hover_animation(self,
                               button: QtWidgets.QPushButton,
                               start_color: QtGui.QColor,
                               end_color: QtGui.QColor) -> None:
        """
        Defines the hover animation for the create and load buttons. This animation changes the background color over
        the duration of some milliseconds to create a fade effect. This is done according to the values saved in the
        global variables BUTTON_BACKGROUND_COLOR and BUTTON_BACKGROUND_HOVER_COLOR.

        :param button: the button widget for which the animation will be shown
        :param start_color: the start background color [base background]
        :param end_color: the end background color [hover background]

        :return: None
        """

        # Defining the animation.
        animation = QtCore.QVariantAnimation(button)
        animation.setDuration(250)
        animation.setStartValue(start_color)
        animation.setEndValue(end_color)

        def update_stylesheet(color: QtGui.QColor) -> None:
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

        # Connects the animation to the update function.
        animation.valueChanged.connect(update_stylesheet)
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
# turns of the minimize and maximize buttons.
window.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowCloseButtonHint)
window.show()

# Start the App.
app.exec()