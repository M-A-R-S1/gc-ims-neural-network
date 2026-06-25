import sys
from misc.config import *
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtGui import QPalette, QColor, QFontDatabase
from ui.LauncherWindow import Ui_StartWidget
from app_project import ProjectWindow
from misc.utils import get_resource_path
import multiprocessing
from pathlib import Path
import re
import json

class MainWindow(QtWidgets.QMainWindow, Ui_StartWidget):
    # Signal definitions.
    open_project_signal = QtCore.Signal(Path)

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # create fade animations for the buttons.
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

        # Connect the buttons and input fields
        self.button_create.clicked.connect(self.create_project_page)
        self.button_cancle.clicked.connect(self.create_home_page)
        self.button_location.clicked.connect(self.select_project_location)
        self.lineEdit_project_name.textChanged.connect(self.validate_project_inputs)
        self.button_create_2.clicked.connect(self.create_project)
        self.button_open.clicked.connect(self.open_project)


    def open_project(self) -> None:
        """
        This function is called when the "open" button is clicked.
        This function opens a file dialog where the user has to select a project for the loading process.

        :return: None.
        """

        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self,
                                                            "Open Project File",
                                                            "",
                                                            "GC-IMS Project Files (*.gcimsp)")

        if file_path:
            project_file = Path(file_path)

            if project_file.exists():
                self.open_project_signal.emit(project_file)
                self.close()


    def select_project_location(self) -> None:
        """
        This function is called if the user wants to select a location for the project.
        A File dialog will prompt the user to select a folder for the project.

        :return: None
        """

        start_directory = ""
        if self.project_path is not None:
            start_directory = str(self.project_path)

        # Start the file dialog for folder selection.
        folder = QtWidgets.QFileDialog.getExistingDirectory(self,
                                                            "Choose a directory for your project",
                                                            start_directory)
        # Was a folder selected?
        if folder:
            self.project_path = Path(folder)
            self.label_location.setText(str(Path(folder)))
            # Check if the "create" button can be pressed.
            self.validate_project_inputs()


    def create_project(self) -> None:
        """
        This function is called if the "create" button is clicked. This will create a new project at the
        project path with the project name and creates a .gcimsp file.

        :return: None.
        """

        # Strip the name of whitespace characters.
        project_name = self.lineEdit_project_name.text().strip()
        # Get the project folder and name and set the project file.
        project_folder = self.project_path / project_name
        project_file = project_folder / f"{project_name}.gcimsp"

        # Try to create the project ...
        try:
            # Create the project folder.
            project_folder.mkdir(parents=True, exist_ok=False)

            # Create the content for the .gcimsp file and create the file.
            content = {
                "version": "1.0",
            }

            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=4)

            # Change to the project main window
            self.open_project_signal.emit(project_file)
            self.close()

        # Error handling here!
        # Error if the project already exists [Same name].
        except FileExistsError:
            QtWidgets.QMessageBox.critical(self, "Error", "Folder with this name already exists!")
         # Error if the user has not the needed permissions to create a project.
        except PermissionError:
            QtWidgets.QMessageBox.critical(self,
                                      "Permission Denied",
                                      "You do not have permission to write in this directory. Please choose a different location.")
        # Error for other stuff...
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Systemerror", f"Error: {str(e)}")


    def validate_project_inputs(self) -> None:
        """
        This function is continuously called while the user is trying to create a new project.
        This function checks if all conditions are met in order to create a new project. This includes:
         - Valid project name
         - Valid project location

        :return: None.
        """

        project_name = self.lineEdit_project_name.text().strip()

        # Invalid character definition [Regex].
        invalid_chars = r'[\\/:*?"<>|+#]'
        # Check the project name for invalid characters.
        contains_invalid = re.search(invalid_chars, project_name)

        # Name and folder valid?
        is_name_valid = len(project_name) > 0 and not contains_invalid
        is_path_selected = self.project_path is not None

        # Invalid characters found in the project name -> Display error message!
        if contains_invalid:
            self.label_error_name.show()
            self.label_error_name.setText("Error: Invalid characters detected: \\ / : * ? \" < > | + #")
            self.lineEdit_project_name.setStyleSheet(f"""
                                                        QLineEdit {{
                                                            border: 1px solid #ff4c4c;
                                                            background-color: #232323; 
                                                            color: #ebebeb;
                                                            border-radius: 10px;
                                                           padding-left: 10px;
                                                        }}
                                                    """)

        # No invalid characters found in the project name.
        else:
            self.label_error_name.hide()
            self.lineEdit_project_name.setStyleSheet(f"""
                                                        QLineEdit {{
                                                            border: 1px solid #ff9000;
                                                            background-color: #232323; 
                                                            color: #9e9e9e;
                                                            border-radius: 10px;
                                                           padding-left: 10px;
                                                        }}
                                                    """)

        # All conditions are met and the project name is not equal to the placeholder.
        if is_name_valid and is_path_selected and project_name != "Project name ...":
            # Activate the "create" button and set the stylesheet.
            self.button_create_2.setEnabled(True)
            self.button_create_2.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
            self.button_create_2.setStyleSheet(f"""
                                                    QPushButton {{
                                                        border: 1px solid #00eaff;
                                                        background-color: #232323; 
                                                        color: #00eaff;
                                                        border-radius: 10px;
                                                    }}
                                                """)

        # Conditions are not met. The "create" button can't pre pressed.
        else:
            # Deactivate the "create" button and change the stylesheet.
            self.button_create_2.setCursor(QtCore.Qt.CursorShape.ForbiddenCursor)
            self.button_create_2.setEnabled(False)
            self.button_create_2.setStyleSheet(f"""
                                                    QPushButton {{
                                                        border: 1px solid #9e9e9e;
                                                        background-color: #232323; 
                                                        color: #9e9e9e;
                                                        border-radius: 10px;
                                                    }}
                                                """)

    def create_project_page(self) -> None:
        """
        Prepares and shows the "Create project" page if the "create" button on the home screen is clicked.

        :return: None
        """
        # reset page field and variables to default.
        self.lineEdit_project_name.clear()
        self.lineEdit_project_name.setPlaceholderText("Project name ...")
        self.project_path = None
        self.label_location.setText("Project location ...")
        self.validate_project_inputs()
        # Change to the "create project" page by changing the index of the stacked widget.
        self.stackedWidget.setCurrentIndex(1)


    def create_home_page(self) -> None:
        """
        Prepares and shows the home page if the "cancel" button on the "create project" page is clicked.

        :return: None
        """
        # Switch to the "home" page by changing the index of the stacked widget.
        self.stackedWidget.setCurrentIndex(0)


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


def load_custom_fonts() -> None:
    """
    Loads the lato font from the asset directory.

    :return: None.
    """

    font_path = get_resource_path("assets/fonts")

    if not font_path.exists():
        print(f"Warning: Font directory not found at: {font_path}")
        return

    # Load and register all fonts from the path.
    for font_file in font_path.glob("*.ttf"):
        QFontDatabase.addApplicationFont(str(font_file))


def main():
    multiprocessing.freeze_support()

    # Create an application instance!
    app = QtWidgets.QApplication(sys.argv)

    # Set the standard text colors to white [Needed for linux and possibly other os].
    palette = app.palette()
    palette.setColor(QPalette.Text, QColor(235, 235, 235))
    palette.setColor(QPalette.WindowText, QColor(235, 235, 235))
    palette.setColor(QPalette.ButtonText, QColor(235, 235, 235))
    palette.setColor(QPalette.ColorRole.Button, QColor(45, 45, 45))
    palette.setColor(QPalette.ColorRole.Base, QColor(30, 30, 30))
    palette.setColor(QPalette.ColorRole.Window, QColor(45, 45, 45))
    # BrightText wird oft für Highlights auf dunklem Grund genutzt
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 255, 255))
    app.setPalette(palette)

    # Load the custom fonts of this app [Lato...]
    load_custom_fonts()

    if sys.platform == "win32":
        import ctypes
        myappid = 'RUB.gc_ims_suite.app.1_0'
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

    if sys.platform == "linux":
        app.setDesktopFileName("gc_ims_suite.desktop")

    # Create a window and show it.
    launcher = MainWindow()
    app.setWindowIcon(QtGui.QIcon(':/app_icon.ico'))
    # turns of the minimize and maximize buttons.
    launcher.setWindowFlags(QtCore.Qt.WindowType.CustomizeWindowHint | QtCore.Qt.WindowType.WindowCloseButtonHint)
    launcher.show()

    # Reference array for the project window.
    project_window_reference = []

    def launch_main_project(path: Path) -> None:
        """
        This function is called when a project is about to be loaded. The current launcher is closed and the
        main project window is loaded with the selected project.

        :param path: Path to the project folder.

        :return: None.
        """

        project_window = ProjectWindow(path)
        project_window_reference.append(project_window)
        project_window.showMaximized()
        project_window.raise_()
        project_window.activateWindow()

    # Connect the "open project" signal.
    launcher.open_project_signal.connect(launch_main_project)

    # Start the App.
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
