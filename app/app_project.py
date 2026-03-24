import sys
from config import *
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtGui import QIcon, QPalette, QColor
from ProjectWindow import Ui_ProjectWindow
from dataset import DatasetPage
from preprocessing import PreprocessingPage
from peak_explorer import PeakExplorerPage
from consensus_peak import ConsensusPeakPage
from classifier import ClassifierPage
from settings import SettingsPage

class ProjectWindow(QtWidgets.QMainWindow, Ui_ProjectWindow):
    def __init__(self, project_path):
        super().__init__()
        self.setupUi(self)

        # Set the current project path.
        self.current_project = project_path

        # Set the window titel name.
        if self.current_project:
            project_name = self.current_project.stem
            self.setWindowTitle(f"GC-IMS suite - {project_name}")
        else:
            self.setWindowTitle("GC-IMS suite - No Project Loaded")


        # All different pages.
        self.dataset_page = None
        self.preprocessing_page = None
        self.peak_explorer_page = None
        self.consensus_peak_page = None
        self.classifier_page = None
        self.settings_page = None
        self.current_page = {}

        # Sidebar color pallets.
        self.palette_active = None
        self.palette_deactivated = None
        self.palette_normal = None

        # Pages Setup.
        self.setup_pages()
        # Set the default page [Dataset].
        self.Main_container.setCurrentWidget(self.dataset_page)
        # Reference to the current page.
        self.current_page = self.Main_container.currentWidget()
        # Set the sidebar buttons.
        self.setup_sidebar_buttons()


    def setup_pages(self):
        # Dataset
        self.dataset_page = DatasetPage()
        self.Main_container.addWidget(self.dataset_page)
        # Preprocessing
        self.preprocessing_page = PreprocessingPage()
        self.Main_container.addWidget(self.preprocessing_page)
        # Peak Explorer
        self.peak_explorer_page = PeakExplorerPage()
        self.Main_container.addWidget(self.peak_explorer_page)
        # Consensus Peak
        self.consensus_peak_page = ConsensusPeakPage()
        self.Main_container.addWidget(self.consensus_peak_page)
        # Classifier
        self.classifier_page = ClassifierPage()
        self.Main_container.addWidget(self.classifier_page)
        # Settings
        self.settings_page = SettingsPage()
        self.Main_container.addWidget(self.settings_page)


    def setup_sidebar_buttons(self):
        # Get the active color palette
        self.palette_active = self.sb_dataset_button.palette()
        self.palette_active.setColor(QPalette.WindowText, QColor(ACTIVE_COLOR))
        # Get the deactivated color palette
        self.palette_deactivated = self.sb_dataset_button.palette()
        self.palette_deactivated.setColor(QPalette.WindowText, QColor(DEACTIVATED_COLOR))
        # Get the normal color palette
        self.palette_normal = self.sb_dataset_button.palette()
        self.palette_normal.setColor(QPalette.WindowText, QColor(NORMAL_COLOR))

        # Set the dataset as active.
        self.sb_dataset_button.setIcon(QIcon("ui/_pics/icons/dataset_orange.png"))
        self.sb_dataset_label.setPalette(self.palette_active)

        # Connect the buttons.
        self.sb_dataset_button.clicked.connect(lambda: self.change_page(self.dataset_page))
        self.sb_preprocessing_button.clicked.connect(lambda: self.change_page(self.preprocessing_page))
        self.sb_peak_explorer_button.clicked.connect(lambda: self.change_page(self.peak_explorer_page))
        self.sb_consensus_button.clicked.connect(lambda: self.change_page(self.consensus_peak_page))
        self.sb_classifier_button.clicked.connect(lambda: self.change_page(self.classifier_page))
        self.sb_settings_button.clicked.connect(lambda: self.change_page(self.settings_page))


    def change_page(self, page) -> None:
        # Set the dataset page as active.
        self.Main_container.setCurrentWidget(page)

        # Make the latest button and label on the sidebar white.
        if self.current_page == self.dataset_page:
            self.sb_dataset_button.setIcon(QIcon("ui/_pics/icons/dataset_white.png"))
            self.sb_dataset_label.setPalette(self.palette_normal)
        elif self.current_page == self.preprocessing_page:
            self.sb_preprocessing_button.setIcon(QIcon("ui/_pics/icons/preprocessing_white.png"))
            self.sb_preprocessing_label.setPalette(self.palette_normal)
        elif self.current_page == self.peak_explorer_page:
            self.sb_peak_explorer_button.setIcon(QIcon("ui/_pics/icons/peak_explorer_white.png"))
            self.sb_peak_explorer_label.setPalette(self.palette_normal)
        elif self.current_page == self.consensus_peak_page:
            self.sb_consensus_button.setIcon(QIcon("ui/_pics/icons/consensus_peak_white.png"))
            self.sb_consensus_label.setPalette(self.palette_normal)
        elif self.current_page == self.classifier_page:
            self.sb_classifier_button.setIcon(QIcon("ui/_pics/icons/classifier_white.png"))
            self.sb_classifier_label.setPalette(self.palette_normal)
        elif self.current_page == self.settings_page:
            self.sb_settings_button.setIcon(QIcon("ui/_pics/icons/settings_white.png"))
            self.sb_settings_label.setPalette(self.palette_normal)

        # Change the active color of the sidebar button/label
        if page == self.dataset_page:
            self.sb_dataset_button.setIcon(QIcon("ui/_pics/icons/dataset_orange.png"))
            self.sb_dataset_label.setPalette(self.palette_active)
        elif page == self.preprocessing_page:
            self.sb_preprocessing_button.setIcon(QIcon("ui/_pics/icons/preprocessing_orange.png"))
            self.sb_preprocessing_label.setPalette(self.palette_active)
        elif page == self.peak_explorer_page:
            self.sb_peak_explorer_button.setIcon(QIcon("ui/_pics/icons/peak_explorer_orange.png"))
            self.sb_peak_explorer_label.setPalette(self.palette_active)
        elif page == self.consensus_peak_page:
            self.sb_consensus_button.setIcon(QIcon("ui/_pics/icons/consensus_peak_orange.png"))
            self.sb_consensus_label.setPalette(self.palette_active)
        elif page == self.classifier_page:
            self.sb_classifier_button.setIcon(QIcon("ui/_pics/icons/classifier_orange.png"))
            self.sb_classifier_label.setPalette(self.palette_active)
        elif page == self.settings_page:
            self.sb_settings_button.setIcon(QIcon("ui/_pics/icons/settings_orange.png"))
            self.sb_settings_label.setPalette(self.palette_active)

        self.current_page = page


if __name__ == "__main__":
    # Create an application instance!
    app = QtWidgets.QApplication(sys.argv)

    # Create a window and show it.
    project_window = ProjectWindow("")
    project_window.show()

    # Start the App.
    sys.exit(app.exec())