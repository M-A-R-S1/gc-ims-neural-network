import sys
from config import *
from PySide6 import QtWidgets
from PySide6.QtGui import QIcon, QPalette, QColor
from ui.ProjectWindow import Ui_ProjectWindow
from dataset import DatasetPage
from preprocessing import PreprocessingPage
from peak_explorer import PeakExplorerPage
from consensus_peak import ConsensusPeakPage
from model import ModelPage
from classifier import ClassifierPage
from settings import SettingsPage
import sqlite3

class ProjectWindow(QtWidgets.QMainWindow, Ui_ProjectWindow):
    def __init__(self, project_path):
        super().__init__()
        self.setupUi(self)

        # Set the current project path.
        self.project_path = project_path

        # Set the window titel name.
        if self.project_path:
            project_name = self.project_path.stem
            self.setWindowTitle(f"GC-IMS suite - {project_name}")
        else:
            self.setWindowTitle("GC-IMS suite - No Project Loaded")

        # All different pages.
        self.dataset_page = None
        self.preprocessing_page = None
        self.peak_explorer_page = None
        self.consensus_peak_page = None
        self.model_page = None
        self.classifier_page = None
        self.settings_page = None
        self.current_page = {}

        # Sidebar color pallets.
        self.palette_active = None
        self.palette_deactivated = None
        self.palette_normal = None

        # Initialize the database.
        self.initialize_database()
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
        self.dataset_page = DatasetPage(self.project_path)
        self.Main_container.addWidget(self.dataset_page)
        # Preprocessing
        self.preprocessing_page = PreprocessingPage(self.project_path)
        self.Main_container.addWidget(self.preprocessing_page)
        # Peak Explorer
        self.peak_explorer_page = PeakExplorerPage(self.project_path)
        self.Main_container.addWidget(self.peak_explorer_page)
        # Consensus Peak
        self.consensus_peak_page = ConsensusPeakPage(self.project_path)
        self.Main_container.addWidget(self.consensus_peak_page)
        # Model
        self.model_page = ModelPage(self.project_path)
        self.Main_container.addWidget(self.model_page)
        # Classifier
        self.classifier_page = ClassifierPage(self.project_path)
        self.Main_container.addWidget(self.classifier_page)
        # Settings
        self.settings_page = SettingsPage()
        self.Main_container.addWidget(self.settings_page)


    def setup_sidebar_buttons(self):
        # Get the active color palette
        self.palette_active = self.sb_dataset_button.palette()
        self.palette_active.setColor(QPalette.ColorRole.WindowText, QColor(ACTIVE_COLOR))
        # Get the deactivated color palette
        self.palette_deactivated = self.sb_dataset_button.palette()
        self.palette_deactivated.setColor(QPalette.ColorRole.WindowText, QColor(DEACTIVATED_COLOR))
        # Get the normal color palette
        self.palette_normal = self.sb_dataset_button.palette()
        self.palette_normal.setColor(QPalette.ColorRole.WindowText, QColor(NORMAL_COLOR))

        # Set the dataset as active.
        self.sb_dataset_button.setIcon(QIcon("ui/_pics/icons/dataset_orange.png"))
        self.sb_dataset_label.setPalette(self.palette_active)

        # Connect the buttons.
        self.sb_dataset_button.clicked.connect(lambda: self.change_page(self.dataset_page))
        self.sb_preprocessing_button.clicked.connect(lambda: self.change_page(self.preprocessing_page))
        self.sb_peak_explorer_button.clicked.connect(lambda: self.change_page(self.peak_explorer_page))
        self.sb_consensus_button.clicked.connect(lambda: self.change_page(self.consensus_peak_page))
        self.sb_model_button.clicked.connect(lambda: self.change_page(self.model_page))
        self.sb_classifier_button.clicked.connect(lambda: self.change_page(self.classifier_page))
        self.sb_settings_button.clicked.connect(lambda: self.change_page(self.settings_page))


    def change_page(self, page) -> None:
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
        elif self.current_page == self.model_page:
            self.sb_model_button.setIcon(QIcon("ui/_pics/icons/neural_network_white.png"))
            self.sb_model_label.setPalette(self.palette_normal)
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
            self.preprocessing_page.load_data()
            self.preprocessing_page.check_processed_spectra()
        elif page == self.peak_explorer_page:
            self.sb_peak_explorer_button.setIcon(QIcon("ui/_pics/icons/peak_explorer_orange.png"))
            self.sb_peak_explorer_label.setPalette(self.palette_active)
            self.peak_explorer_page.load_data()
        elif page == self.consensus_peak_page:
            self.sb_consensus_button.setIcon(QIcon("ui/_pics/icons/consensus_peak_orange.png"))
            self.sb_consensus_label.setPalette(self.palette_active)
            self.consensus_peak_page.load_data()
        elif page == self.model_page:
            self.sb_model_button.setIcon(QIcon("ui/_pics/icons/neural_network_orange.png"))
            self.sb_model_label.setPalette(self.palette_active)
        elif page == self.classifier_page:
            self.sb_classifier_button.setIcon(QIcon("ui/_pics/icons/classifier_orange.png"))
            self.sb_classifier_label.setPalette(self.palette_active)
        elif page == self.settings_page:
            self.sb_settings_button.setIcon(QIcon("ui/_pics/icons/settings_orange.png"))
            self.sb_settings_label.setPalette(self.palette_active)

        # Set the dataset page as active.
        self.Main_container.setCurrentWidget(page)

        self.current_page = page


    def initialize_database(self) -> None:
        """
        This function initializes the database of this project where all the detected peaks and more is saved.
        =============================================================================
        :return: None.
        """

        # Path to the database.
        db_directory = self.project_path.parent / "database"
        # Create the database directory if it does not exist.
        if not db_directory.exists():
            db_directory.mkdir(parents=True, exist_ok=True)
        # Database full path.
        db_file = db_directory / "project_database.db"

        # Connect to the database.
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Creat the settings table.
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS settings
                       (
                           id INTEGER PRIMARY KEY CHECK (id = 1),
                           drift_start_cut REAL,
                           drift_end_cut REAL,
                           retention_start_cut INTEGER,
                           retention_end_cut INTEGER
                       )
                       ''')

        # Input the settings.
        cursor.execute("INSERT OR IGNORE INTO settings (id, drift_start_cut, drift_end_cut, retention_start_cut, retention_end_cut) VALUES (1, 0, 0, 0, 0)")
        conn.commit()

        # Creat the labels table.
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS labels
                       (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           name TEXT UNIQUE NOT NULL
                        )
                    ''')

        # Creat the spectra table.
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS spectra
                       (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           label_id INTEGER NOT NULL,
                           name TEXT NOT NULL,
                           path TEXT NOT NULL,
                           processing_done INTEGER DEFAULT 0,
                           peaks_done INTEGER DEFAULT 0,
                           intensity_max INTEGER DEFAULT NULL,
                           intensity_min INTEGER DEFAULT NULL,
                           FOREIGN KEY (label_id) REFERENCES labels (id) ON DELETE CASCADE
                       )
                       ''')

        # Create the peak table.
        cursor.execute('''
                            CREATE TABLE IF NOT EXISTS peaks (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                label_id INTEGER NOT NULL,
                                spectrum_id INTEGER NOT NULL,
                                consensus_id INTEGER DEFAULT NULL,
                                ret_time REAL,
                                drift_time REAL,
                                intensity REAL,
                                npy_file TEXT,
                                is_active INTEGER DEFAULT 1,
                                FOREIGN KEY (label_id) REFERENCES labels (id) ON DELETE CASCADE,
                                FOREIGN KEY (spectrum_id) REFERENCES spectra (id) ON DELETE CASCADE
                            )
                        ''')

        # Create the consensus peak table.
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS consensus_peaks
                       (
                           id               INTEGER PRIMARY KEY,
                           ret_time         REAL,
                           drift_time       REAL,
                           min_intensity    REAL,
                           is_active        INTEGER DEFAULT 1
                       )
                       ''')

        # Create the classifier table.
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS classifier
                       (
                           id                   INTEGER PRIMARY KEY,
                           name                 TEXT NOT NULL,
                           model                TEXT NOT NULL
                       )
                       ''')

        # Create the classifier result table.
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS classifier_result
                       (
                           id               INTEGER PRIMARY KEY,
                           classifier_id    INTEGER NOT NULL,
                           consensus_id     INTEGER DEFAULT NULL,
                           FOREIGN KEY (classifier_id) REFERENCES classifier (id) ON DELETE CASCADE
                       )
                       ''')

        # Create the classifier value table.
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS classifier_value
                       (
                           id                       INTEGER PRIMARY KEY,
                           classifier_result_id     INTEGER NOT NULL,
                           label                    TEXT,
                           is_summary               INTEGER DEFAULT 0,
                           precision                REAL,
                           recall                   REAL,
                           f1_score                 REAL,
                           support                  INTEGER,
                           FOREIGN KEY (classifier_result_id) REFERENCES classifier_result (id) ON DELETE CASCADE
                       )
                       ''')

        conn.commit()
        conn.close()


if __name__ == "__main__":
    # Create an application instance!
    app = QtWidgets.QApplication(sys.argv)

    # Create a window and show it.
    project_window = ProjectWindow("")
    project_window.showMaximized()

    # Start the App.
    sys.exit(app.exec())