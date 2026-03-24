import sys
from config import *
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtGui import QIcon, QPalette, QColor
from ProjectWindow import Ui_ProjectWindow

class ProjectWindow(QtWidgets.QMainWindow, Ui_ProjectWindow):
    def __init__(self, project_path):
        super().__init__()
        self.setupUi(self)
        self.current_project = project_path

        # Set the window titel name.
        if self.current_project:
            project_name = self.current_project.stem
            self.setWindowTitle(f"GC-IMS suite - {project_name}")
        else:
            self.setWindowTitle("GC-IMS suite - No Project Loaded")

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


if __name__ == "__main__":
    # Create an application instance!
    app = QtWidgets.QApplication(sys.argv)

    # Create a window and show it.
    project_window = ProjectWindow("")
    project_window.show()

    # Start the App.
    sys.exit(app.exec())