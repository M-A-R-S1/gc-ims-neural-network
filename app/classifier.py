from __future__ import annotations
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtGui import QFont
from ui.classifier_ui.ClassifierWidget import Ui_ClassifierWidget
from ui.classifier_ui.ClassifierTile import Ui_ClassifierTile
from dialogs import CustomYesNoDialog, CustomProgressDialog, RenameLabelDialog, CustomMessageDialog
from misc.utils import get_resource_path
import sqlite3
from pathlib import Path
import torch
import misc.vae_model
import misc.plot
import re
import shutil
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from collections import Counter
import joblib
import ims


class ClassifierPage(QtWidgets.QWidget, Ui_ClassifierWidget):
    def __init__(self, project_path: Path):
        super().__init__()
        self.setupUi(self)

        # Project save path.
        self.project_path = Path(project_path)
        # Database path.
        self.db_path = self.project_path.parent / "database" / "project_database.db"
        # Current selected tile and id.
        self.current_selected_classifier_id = None
        self.current_selected_tile = None
        # Number of active consesus peaks.
        self.active_consensus_peaks = 0

        # Aligning the classifier scroll area content to the top.
        self.scrollArea_classifier_Contents.layout().setAlignment(QtCore.Qt.AlignTop)

        # Load initial data.
        self.load_classifiers_to_ui()
        self.load_models_to_dropdown()

        # Connect the buttons.
        self.pushButton_new_classification.clicked.connect(self.show_new_classifier_dialog)
        self.pushButton_load_single_spectrum.clicked.connect(self.on_load_single_spectrum_clicked)


    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_confusion_matrix_image()


    def showEvent(self, event) -> None:
        """
        This function is called every time the user enters this page.
        It checks the number of active consensus peaks and reloads all classifications and VAE models.
        =============================================================================
        :param event: The page display event.
        =============================================================================
        :return: None
        """

        super().showEvent(event)
        # Check how many active consensus peaks are there.
        self.active_consensus_peaks = self.get_active_consensus_peaks_count()
        self.label_consesus_peak_counter.setText(f"This classification uses {self.active_consensus_peaks} consensus peaks.")
        # Reload the classification list.
        self.load_classifiers_to_ui()
        self.load_models_to_dropdown()


    def get_active_consensus_peaks_count(self) -> int:
        """
        This function is called each time the user enters the classifier page.
        It connects to the database and fetches the number of active consensus peaks.

        :return: Number of active consensus peaks.
        """

        # Connect to the database and get the number of active consensus peaks.
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        query = "SELECT COUNT(*) FROM consensus_peaks WHERE is_active = 1"
        cursor.execute(query)
        active_peaks_count = cursor.fetchone()[0]
        conn.close()

        return active_peaks_count

    def load_classifiers_to_ui(self) -> None:
        """

        :return: None
        """

        # Get the layout of the classifier scroll area.
        layout = self.scrollArea_classifier_Contents.layout()
        # Reset the selected classifier id and the selected tile.
        self.current_selected_classifier_id = None
        self.current_selected_tile = None

        # 1. Remove everything from the classifier scroll area.
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Connect to the database and fetch some classification data.
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        query = """
                SELECT c.id,
                       c.name,
                       c.model,
                       cv.f1_score
                FROM classifier c
                         LEFT JOIN classifier_result cr ON c.id = cr.classifier_id AND cr.consensus_id IS NULL
                         LEFT JOIN classifier_value cv ON cr.id = cv.classifier_result_id AND cv.label = 'weighted avg'
                ORDER BY c.id ASC
                """
        cursor.execute(query)
        classifiers = cursor.fetchall()
        conn.close()

        # Create a tile for each classification and add this tile to the classifier scroll area.
        for c_id, name, model, accuracy in classifiers:

            tile = ClassifierTileWidget(classifier_id=c_id,
                                        name=name,
                                        model_name=model,
                                        accuracy=accuracy)

            # Connect the tile with some signals.
            tile.delete_clicked.connect(self.on_delete_classifier)
            tile.rename_clicked.connect(self.on_rename_classifier)
            tile.tile_clicked.connect(self.on_open_results)

            layout.addWidget(tile)


    def on_delete_classifier(self,
                             classification_widget: ClassifierTileWidget) -> None:
        """
        This is function is called when the user clicked on the "delete" button of a classification tile in the scroll area.
        The user is prompted with a dialog where he needs to verify that the wants to delete the classification.
        If the user chooses to delete, the classification is removed from the database and the folder with the saved confusion matrix
        and random forest model is deleted from the drive.

        :param classification_widget: The classification widget which should be deleted.

        :return:  None
        """

        # Get the name of the classification.
        classification_name = classification_widget.label_name.text()
        # Get the ID of this classification.
        classification_id = classification_widget.classifier_id
        # Define a Yes/No Dialog for the deletion.
        dialog = CustomYesNoDialog(title="Delete classification results",
                                   message=f"Are you sure you want to delete the classification results for '{classification_name}'?",
                                   type="warning",
                                   parent=self)

        # The user wants to delete the classification.
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:

            # Try to delete from the "classification" folder.
            try:
                classification_folder = self.project_path.parent / "classification" / f"{classification_id}"
                if classification_folder.exists() and classification_folder.is_dir():
                    shutil.rmtree(classification_folder)
            except Exception as e:
                print(f"Error while deleting: {e}")

            # Delete the database entry.
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute("DELETE FROM classifier WHERE id = ?", (classification_id,))
            conn.commit()
            conn.close()

            # Reload the classification list.
            self.load_classifiers_to_ui()



    def on_rename_classifier(self,
                             classification_widget: ClassifierTileWidget) -> None:

        # Create the rename dialog.
        dialog = RenameLabelDialog(classification_widget.label_name.text(), self)

        # The user chooses to rename the label.
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            # get the new label name from the dialog data.
            new_classification_name = dialog.get_data()['name']

            # If the old and the new name are the same skip renaming.
            if new_classification_name == classification_widget.label_name.text():
                return

            # If the new label name is a duplicate [name already exits in list] skip renaming and rollback.
            if self.duplication_check(new_classification_name, exclude_widget=classification_widget):
                CustomMessageDialog.show_error("Error - Duplication",
                                               "Classification name already exists, please choose another name")
                classification_widget.label_name.setText(classification_widget.old_label_name)
                return

            # Exchange the classification name in the database.
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM classifier WHERE name = ?", (classification_widget.old_label_name,))
            result = cursor.fetchone()
            classifier_id = result[0]
            cursor.execute("UPDATE classifier SET name = ? WHERE id = ?", (new_classification_name, classifier_id))
            conn.commit()
            conn.close()

            # Display the new name.
            classification_widget.label_name.setText(new_classification_name)
            classification_widget.old_label_name = new_classification_name

    def duplication_check(self,
                          name: str,
                          exclude_widget=None) -> bool:
        """
        This function takes in the name of a classification and checks if there is already
        a classification with this name present. If so this classification is considered a duplication and is not added or renamed!
        =============================================================================
        :param name: The name of the classification.
        :param exclude_widget: The widget of the classification.
        =============================================================================
        :return: Boolean value for the duplication check [True = duplicate | False = No duplicate]
        """

        # Walks through all classifications and check if the name is unique
        for i in range(self.scrollArea_classifier_Contents.layout().count()):
            # Get the widget of the classification.
            widget = self.scrollArea_classifier_Contents.layout().itemAt(i).widget()

            # Check if the widget is of the correct type "ClassifierTileWidget" and if the widget should be excluded.
            if isinstance(widget, ClassifierTileWidget) and widget is not exclude_widget:
                # If the new name matches on of the existing names return true.
                if widget.label_name.text() == name:
                    return True

        # No duplications found.
        return False


    def on_open_results(self, tile_widget: ClassifierTileWidget):

        classifier_id = tile_widget.classifier_id
        self.current_selected_classifier_id = classifier_id

        # Deselect the last selected tile and remove the highlight effect from the scroll area.
        if self.current_selected_tile:
            self.current_selected_tile.set_selected(False)

        # Set the highlight to the currently clicked tile.
        self.current_selected_tile = tile_widget
        self.current_selected_tile.set_selected(True)

        # 1. DATEN AUS DER DATENBANK HOLEN
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Wir holen nur die Werte für das "Combined" Ergebnis (consensus_id IS NULL)
        query = """
                SELECT cv.label, cv.precision, cv.recall, cv.f1_score, cv.support, cv.is_summary
                FROM classifier_value cv
                         JOIN classifier_result cr ON cv.classifier_result_id = cr.id
                WHERE cr.classifier_id = ? \
                  AND cr.consensus_id IS NULL
                ORDER BY cv.is_summary ASC, cv.label ASC
                """
        cursor.execute(query, (classifier_id,))
        results = cursor.fetchall()
        conn.close()

        if not results:
            print("Keine Detaildaten in der Datenbank gefunden!")
            return

        # 2. DIE TABELLE (QTableWidget) FÜLLEN
        table = self.tableWidget_results
        table.clearContents()
        table.setRowCount(len(results))
        table.setColumnCount(5)

        # Spaltenüberschriften setzen
        table.setHorizontalHeaderLabels(["Label", "Precision", "Recall", "F1-Score", "Support"])
        table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        table.verticalHeader().setVisible(False)

        table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                font-family: 'Lato';
                font-size: 16px;
                font-weight: bold;
                background-color: #232323;
                color: #ebebeb;
                border: None;
                border-bottom: 1px solid #ff9000;
            }
        """)

        header = table.horizontalHeader()
        font = QFont("Lato", 16, QFont.Bold)
        header.setFont(font)

        for row_idx, row_data in enumerate(results):
            label, precision, recall, f1, support, is_summary = row_data

            row_values = [
                str(label),
                f"{precision*100:.1f} %",
                f"{recall*100:.1f} %",
                f"{f1*100:.1f} %",
                f"{str(support)}x"
            ]

            for col_idx, value in enumerate(row_values):
                item = QtWidgets.QTableWidgetItem(value)
                item.setTextAlignment(QtCore.Qt.AlignCenter)

                if is_summary == 1:
                    item.setBackground(QtGui.QColor("#232323"))

                table.setItem(row_idx, col_idx, item)

            # 3. DAS BILD DER CONFUSION MATRIX LADEN
            plot_widget = self.widget_confusion_matrix

            # Falls das Widget noch kein Layout hat, geben wir ihm eins
            if plot_widget.layout() is None:
                layout = QtWidgets.QVBoxLayout()
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(0)
                plot_widget.setLayout(layout)
            else:
                # Alten Inhalt (altes Bild) restlos löschen
                while plot_widget.layout().count():
                    child = plot_widget.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

            # Leeres Label erstellen und ins Layout setzen
            image_label = QtWidgets.QLabel()
            image_label.setAlignment(QtCore.Qt.AlignCenter)
            image_label.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
            plot_widget.layout().addWidget(image_label)

            # --- FIX 1: Verhindern, dass die Tabelle den gesamten Platz frisst ---
            plot_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            plot_widget.setMinimumHeight(300)  # Mindesthöhe erzwingen!

            # --- FIX 2: Qt einen Wimpernschlag (10ms) Zeit geben, um das Layout zu berechnen ---
            QtCore.QTimer.singleShot(10, self.update_confusion_matrix_image)


    def update_confusion_matrix_image(self):
        """
        Liest das aktuelle Bild ein und skaliert es live auf die
        aktuelle Größe des Containers.
        """
        if not hasattr(self, "current_selected_classifier_id") or self.current_selected_classifier_id is None:
            return

        plot_widget = self.widget_confusion_matrix

        # Das Label finden
        image_label = None
        if plot_widget.layout():
            for i in range(plot_widget.layout().count()):
                widget = plot_widget.layout().itemAt(i).widget()
                if isinstance(widget, QtWidgets.QLabel):
                    image_label = widget
                    break

        if not image_label:
            return

        size = plot_widget.size()

        if size.width() <= 0 or size.height() <= 0:
            return

        # Pfad zum Bild bauen
        img_path = self.project_path.parent / "classification" / f"{self.current_selected_classifier_id}" / "total" / "confusion_matrix.png"

        if img_path.exists():
            pixmap = QtGui.QPixmap(str(img_path))

            # Bild auf die jetzige echte Größe skalieren
            pixmap_scaled = pixmap.scaled(
                size,
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            )
            image_label.setPixmap(pixmap_scaled)
        else:
            image_label.setText(f"Bild nicht gefunden:\n{img_path.name}")
            image_label.setStyleSheet("color: #ff4444; font-weight: bold;")


    def load_models_to_dropdown(self):
        # Pfad zum models-Ordner (passe diesen ggf. an deine Ordnerstruktur an)
        models_dir = get_resource_path("models")

        if not models_dir.exists():
            print(f"Warnung: Models-Ordner nicht gefunden unter {models_dir}")
            return

        self.comboBox_model.clear()

        # Geht alle .pt Dateien im Ordner durch
        for file_path in models_dir.glob("*.pt"):
            original_filename = file_path.name
            display_name = file_path.stem
            self.comboBox_model.addItem(display_name)


    def show_new_classifier_dialog(self) -> None:
        """
        This function is called when the user wants to create a new classification. It creates a dialog where the user is
        prompted to start the classification process.
        =============================================================================
        :return: None.
        """

        classification_name = self.lineEdit_name.text().strip()
        classification_name = re.sub(r'[^a-zA-Z0-9\s_-]', '', classification_name).strip()
        model_name = self.comboBox_model.currentText()

        # 2. Sicherheits-Check: Hat der Nutzer alles ausgefüllt?
        if not classification_name:
            CustomMessageDialog.show_error("Error - Empty", "Empty classification name! Please choose a name for the classification.")
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM classifier WHERE name = ?", (classification_name,))
        name_exists = cursor.fetchone()[0] > 0
        conn.close()

        if name_exists:
            CustomMessageDialog.show_error("Error - Duplication","Classification name already exists, please choose another name")
            return

        if not model_name:
            CustomMessageDialog.show_error("Error - Empty model", "Please select a model which the classification process should work with.")
            return

        # Create a custom yes/no dialog for the user where he can start the classification process.
        dialog = CustomYesNoDialog(
            title="Start new classification",
            message=f"Do you want to start the classification?\n\n"
                    f"Name: {classification_name}\n"
                    f"Model: {model_name}\n"
                    f"Consensus Peaks: {self.active_consensus_peaks}",
            type="warning",
            parent=self
        )

        # If the user accepted the dialog, call the start_new_classification method.
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.start_new_classification(name=classification_name,
                                          model=model_name)


    def start_new_classification(self,
                                 name: str,
                                 model: str) -> None:
        """
        This function is called when the user accepted the "start new classification" prompt.
        A Thread is created and started on which the random forest classification is executed.
        =============================================================================
        :return: None
        """

        # Open the progress dialog which informs the user about the current state of the preprocessing.
        self.classification_progress_dialog = CustomProgressDialog(title="Classification in progress...",
                                                                   header="Classifying...",)
        # Reset the start time.
        self.classification_progress_dialog.start_time = None
        self.classification_progress_dialog.show()

        # Create a thread and worker for the progress dialog.
        self.thread = QtCore.QThread()
        self.worker = ClassificationWorker(path=self.project_path,
                                           classification_name=name,
                                           model_filename=model)
        self.worker.moveToThread(self.thread)
        self.worker.moveToThread(self.thread)

        # Connect some signals to the worker and thread.
        self.thread.started.connect(self.worker.run)
        self.worker.progress_update.connect(self.classification_progress_dialog.update_progress)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.classification_progress_dialog.accept)
        self.worker.finished.connect(self.load_classifiers_to_ui)
        self.classification_progress_dialog.button_no.clicked.connect(self.worker.stop, type=QtCore.Qt.DirectConnection)
        self.thread.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.lineEdit_name.clear()
        # Start the thread.
        self.thread.start()


    def on_load_single_spectrum_clicked(self):
        """Öffnet den File-Dialog und startet die Klassifikation."""

        # 1. Prüfen, ob der Nutzer links überhaupt ein Modell ausgewählt hat
        if not self.current_selected_classifier_id:
            CustomMessageDialog.show_error("Missing Selection",
                                           "Please select a classification to classify.")
            return

        # 2. File-Dialog öffnen, um die .mea Datei zu finden
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select GC-IMS Spectrum",
            str(self.project_path.parent),  # Start-Ordner
            "Spectrum Files (*.mea);;All Files (*)"
        )

        if not file_path:
            return  # User hat auf "Abbrechen" geklickt

        # 3. Klassifikation starten (in try-except für sichere Fehlerbehandlung)
        try:
            self.process_and_classify_spectrum(Path(file_path))
        except Exception as e:
            print(e)
            CustomMessageDialog.show_error("Classification Error", f"Ein Fehler ist aufgetreten:\n{e}")



    def process_and_classify_spectrum(self, spectrum_path: Path):
        """Führt Preprocessing, Feature-Extraktion und Vorhersage durch."""

        window_size = 5
        peak_window_dimension = 4 * window_size + 1

        # A. PREPROCESSING
        spec = ims.Spectrum.read_mea(str(spectrum_path)).binning()
        spectrum = spec.copy()
        spectrum.riprel()
        spectrum.sub_first_rows(50)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT drift_start_cut, drift_end_cut, retention_start_cut, retention_end_cut FROM settings WHERE id = 1")
        settings_data = cursor.fetchone()
        d_start, d_stop, r_start, r_stop = settings_data

        spectrum.cut_dt(start=float(d_start), stop=float(d_stop))
        spectrum.cut_rt(start=float(r_start), stop=float(r_stop))
        spectrum.savgol(window_length=10, polyorder=4)
        spectrum.values[spectrum.values < 0] = 0.0

        # 1. Spectrum normalization.
        # Keep the non normalized values for later use.
        values_non_normalized = spectrum.values.copy()
        # Normalize the spectrum [0-1].
        spectrum.normalization()

        padded_values = np.pad(
            spectrum.values,
            pad_width=window_size,
            mode='constant',
            constant_values=0
        )

        padded_values_non_normalized = np.pad(
            values_non_normalized,
            pad_width=window_size,
            mode='constant',
            constant_values=0
        )

        # B. DATEN FÜR DIESEN CLASSIFIER HOLEN
        # 1. Classifier Infos holen (Um Namen für RF und VAE zu wissen)
        cursor.execute("SELECT name, model FROM classifier WHERE id = ?", (self.current_selected_classifier_id,))
        classifier_data = cursor.fetchone()
        classification_name = classifier_data[0]
        vae_model_name = classifier_data[1]

        # 2. Eingefrorene Peaks holen
        cursor.execute("SELECT ret_time, drift_time, min_intensity FROM cl_consensus_peaks WHERE classifier_id = ?",
                       (self.current_selected_classifier_id,))
        frozen_peaks = cursor.fetchall()
        conn.close()

        # C. VAE MODELL LADEN
        model_dir = get_resource_path("models")
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        vae = misc.vae_model.VariationalAutoencoderCNN(input_layers=1, hidden_layers=64, latent_dimension=16).to(device)
        vae.load_model(model_dir=model_dir, file_name=f"{vae_model_name}.pt", device=device)
        vae.eval()

        # Hier sammeln wir alle 16 Latent-Werte von JEDEM Peak aneinandergereiht
        latent_features = []

        with torch.inference_mode():
            for ret_time, drift_time, min_intensity in frozen_peaks:
                # 1. Finde die Indizes im Numpy Array, die den physikalischen Zeiten am nächsten liegen
                ret_idx = np.abs(spectrum.ret_time - ret_time).argmin()
                drift_idx = np.abs(spectrum.drift_time - drift_time).argmin()

                # Calculate the min and max coordinates for the padded peak window.
                start_ret_idx = ret_idx - window_size
                end_ret_idx = ret_idx + 3 * window_size + 1
                start_drift_idx = drift_idx - window_size
                end_drift_idx = drift_idx + 3 * window_size + 1

                # Set the adjusted peak window (One with normalized and one with non normalized intensity values)
                peak_window_intensities = padded_values[start_ret_idx:end_ret_idx, start_drift_idx:end_drift_idx]
                peak_window_intensities_non_normalized = padded_values_non_normalized[start_ret_idx:end_ret_idx, start_drift_idx:end_drift_idx]

                if np.max(peak_window_intensities_non_normalized) >= min_intensity:
                    min_intensity = peak_window_intensities.min()
                    max_intensity = peak_window_intensities.max()
                    if max_intensity - min_intensity == 0:
                        npy_file_normalized = np.zeros_like(peak_window_intensities)
                    else:
                        npy_file_normalized = (peak_window_intensities - min_intensity) / (max_intensity - min_intensity)

                    # 4. In Tensor umwandeln
                    peak_tensor = torch.from_numpy(npy_file_normalized).float().view(1, 1, peak_window_dimension, peak_window_dimension).to(device)

                    # 5. Durch das VAE schicken und nur den Latent Space (mean) nehmen
                    reconstruction, mean, log_variance = vae(peak_tensor)

                    # 6. Flach klopfen und an die Feature-Liste anhängen
                    #latent_features.extend(mean.cpu().numpy().flatten())
                    combined_feature = np.hstack((mean.cpu().numpy().flatten(), log_variance.cpu().numpy().flatten(), [ret_time, drift_time]))
                    latent_features.append(combined_feature)


        # E. VORHERSAGE MIT RANDOM FOREST
        # Lade den Forest von der Festplatte
        rf_file = self.project_path.parent / "classification" / f"{self.current_selected_classifier_id}" / f"{classification_name}.joblib"
        if not rf_file.exists():
            CustomMessageDialog.show_error("Error", "Random Forest Modell wurde nicht auf der Festplatte gefunden.")
            return

        rf_classifier = joblib.load(rf_file)

        # Aus der Liste von Arrays ein 2D-Array machen (Zeilen = Peaks, Spalten = 34 Features)
        # latent_features hat die Form: [ [34 Werte], [34 Werte], ... ]
        X_input = np.array(latent_features)

        peak_predictions = rf_classifier.predict(X_input)
        vote_result = Counter(peak_predictions)
        prediction, vote_count = vote_result.most_common(1)[0]

        # Die prozentuale Sicherheit basierend auf der Einstimmigkeit der Peaks
        total_peaks = len(peak_predictions)
        max_prob = (vote_count / total_peaks) * 100

        # F. ERGEBNIS ANZEIGEN
        CustomMessageDialog.show_info(
            "Classification Result",
            f"The given spectrum was predicted as.\n\nLabel: '{prediction}'\nAccuracy: {max_prob:.1f}%"
        )


class ClassificationWorker(QtCore.QObject):
    # Signal definitions.
    finished = QtCore.Signal()
    progress_update = QtCore.Signal(int, int)

    def __init__(self, path: Path,
                 classification_name: str,
                 model_filename: str):

        super().__init__()
        self.project_path = path.parent
        self.db_path = self.project_path / "database" / "project_database.db"
        self.worker_stopped = False
        self.classification_name = classification_name
        self.model_filename = model_filename


    @QtCore.Slot()
    def stop(self):
        self.worker_stopped = True

    def check_stopped(self) -> bool:
        return self.worker_stopped

    def run(self) -> None:
        """
        This function overrides the run function of a thread worker and starts the classification process.
        It starts a distinct number of pools [one for each CPU core], collects the classification results
        from all consensus peaks and saves them at the end into the database.
        =============================================================================
        :return: None.
        """

        # Device agnostic code.
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # Initialize the model.
        model = misc.vae_model.VariationalAutoencoderCNN(input_layers=1,
                                                         hidden_layers=64,
                                                         latent_dimension=16).to(device)

        # Load the model state dict.
        model_dir = get_resource_path("models")
        model.load_model(model_dir=model_dir, file_name=self.model_filename, device=device)
        # Start the random forest algorithm.
        self.start_random_forest(model=model,
                                 model_name=self.model_filename,
                                 device=device,
                                 db_path=self.db_path,
                                 project_path=self.project_path,
                                 classification_name=self.classification_name,
                                 check_stopped_callback=self.check_stopped)

        self.finished.emit()


    def start_random_forest(self,
                            model: torch.nn.Module,
                            model_name: str,
                            device: torch.device,
                            db_path: Path,
                            project_path: Path,
                            classification_name: str,
                            check_stopped_callback=None) -> None:

        """
        This function prepares and executes the random forest algorithm.
        1. All .npy files from the consensus peaks are located and loaded via Database.
        2. The latent mean vector from the autoencoder is calculated.
        3. Split into train and test datasets.
        4. A random forest classifier is trained and tested.
        5. The results are plotted, saved as Excel, and written to the DB.
        """

        # 1. Daten aus der DB laden (inklusive ret_time und drift_time!)
        conn = sqlite3.connect(db_path)
        query = """
                SELECT DISTINCT cp.id  AS consensus_id,
                                cp.ret_time,
                                cp.drift_time,
                                s.id   AS spectrum_id,
                                l.name AS label_name,
                                s.name AS spectrum_name
                FROM consensus_peaks cp
                         JOIN peaks p ON p.consensus_id = cp.id
                         JOIN spectra s ON p.spectrum_id = s.id
                         JOIN labels l ON s.label_id = l.id
                WHERE cp.is_active = 1
                  AND p.is_active = 1
                """
        df = pd.read_sql_query(query, conn)

        if df.empty:
            print("Keine aktiven Peaks für die Klassifizierung gefunden!")
            conn.close()
            return

        # 2. Den Pfad blind und mit 100%iger Sicherheit zusammenbauen
        def build_abs_path(row):
            c_id = int(row['consensus_id'])
            dimension = 4 * 5 + 1
            clean_spec_name = row['spectrum_name'].replace('.mea', '')
            filename = f"CID_{c_id}_PW_{row['label_name']}_{clean_spec_name}_{dimension}x{dimension}.npy"
            full_path = project_path / "dataset" / row['label_name'] / clean_spec_name / "consensus_peaks" / filename
            return full_path

        df['abs_npy_path'] = df.apply(build_abs_path, axis=1)

        # 3. Sicherheitscheck: Existiert die Datei wirklich?
        df['file_exists'] = df['abs_npy_path'].apply(lambda p: p.exists())
        df = df[df['file_exists'] == True]

        # ---------------------------------------------------------
        # NEU: Haupt-Eintrag für den Classifier in der DB erstellen
        # ---------------------------------------------------------
        cursor = conn.cursor()
        cursor.execute("INSERT INTO classifier (name, model) VALUES (?,?)", (classification_name, model_name))
        classifier_id = cursor.lastrowid
        conn.commit()

        # Switch into evaluation mode.
        model.eval()

        rf_features = []
        labels = []

        for _, row in df.iterrows():
            path = row['abs_npy_path']
            label = row['label_name']
            rt_val = row['ret_time']
            dt_val = row['drift_time']

            if check_stopped_callback and check_stopped_callback():
                print("Klassifizierung vor Gesamt-Klassifizierung abgebrochen!")
                conn.close()
                return

            peak_window = np.load(path)
            peak_window_dimension = 4 * 5 + 1

            min_intensity = peak_window.min()
            max_intensity = peak_window.max()
            if max_intensity - min_intensity == 0:
                npy_file_normalized = np.zeros_like(peak_window)
            else:
                npy_file_normalized = (peak_window - min_intensity) / (max_intensity - min_intensity)

            peak_window_tensor = torch.from_numpy(npy_file_normalized).float().view(1, 1, peak_window_dimension,
                                                                                    peak_window_dimension).to(device)

            with torch.inference_mode():
                reconstruction, mean, log_variance = model(peak_window_tensor)

            # Combine the latent vector with the retention and drifttime.
            combined_feature = np.hstack(
                (mean.cpu().numpy().flatten(), log_variance.cpu().numpy().flatten(), [rt_val, dt_val]))

            rf_features.append(combined_feature)
            labels.append(label)

        train_feature, test_feature, train_label, test_label = train_test_split(rf_features, labels, test_size=0.2)
        rf_model = RandomForestClassifier(n_estimators=1000, class_weight='balanced')
        rf_model.fit(train_feature, train_label)

        label_predictions = rf_model.predict(test_feature)
        results_dict = classification_report(test_label, label_predictions, output_dict=True, zero_division=0)
        results_dataframe = pd.DataFrame(results_dict).transpose()

        # --- 1. RANDOM FOREST MODELL SPEICHERN ---
        # Erstelle einen Ordner "rf_models", falls er nicht existiert
        rf_dir = project_path / "classification" / f"{classifier_id}"
        if not rf_dir.exists():
            rf_dir.mkdir(parents=True, exist_ok=True)

        # Generiere einen Dateinamen und speichere das Modell
        rf_filename = f"{classification_name}.joblib"
        rf_filepath = rf_dir / rf_filename
        joblib.dump(rf_model, rf_filepath)

        # --- DB SPEICHERN (Kombiniertes Ergebnis) ---
        # consensus_id = NULL bedeutet "Ergebnis über alle Peaks"
        cursor.execute("INSERT INTO classifier_result (classifier_id, consensus_id) VALUES (?, NULL)", (classifier_id,))
        current_result_id = cursor.lastrowid

        # Hole dir alle aktuell aktiven Consensus Peaks (die du fürs Training genutzt hast)
        cursor.execute("SELECT id, ret_time, drift_time, min_intensity FROM consensus_peaks WHERE is_active = 1")
        active_peaks = cursor.fetchall()

        # Speichere jeden dieser Peaks in der neuen Tabelle, gebunden an die classifier_id
        for peak in active_peaks:
            original_id = peak[0]
            ret_time = peak[1]
            drift_time = peak[2]
            min_intensity = peak[3]

            cursor.execute("""
                           INSERT INTO cl_consensus_peaks (classifier_id, original_id, ret_time, drift_time, min_intensity)
                           VALUES (?, ?, ?, ?, ?)
                           """, (classifier_id, original_id, ret_time, drift_time, min_intensity))

        for key, metrics in results_dict.items():
            if key == 'accuracy': continue
            is_summary = 1 if key in ['macro avg', 'weighted avg'] else 0
            cursor.execute("""
                           INSERT INTO classifier_value (classifier_result_id, label, is_summary, precision, recall, f1_score, support)
                           VALUES (?, ?, ?, ?, ?, ?, ?)
                           """,
                           (current_result_id, key, is_summary, metrics['precision'], metrics['recall'], metrics['f1-score'], metrics['support']))
        conn.commit()
        conn.close()
        # --------------------------------------------

        filedir = project_path / "classification" / f"{classifier_id}" / "total"
        if not filedir.exists():
            filedir.mkdir(parents=True, exist_ok=True)

        results_dataframe.to_excel(filedir / "classification_results.xlsx", index=True)
        misc.plot.random_forest_confusion_matrix(model=rf_model, test_feature=test_feature, test_label=test_label,output_dir=filedir)


class ClassifierTileWidget(QtWidgets.QWidget, Ui_ClassifierTile):
    # Signal definitions.
    delete_clicked = QtCore.Signal(object)
    rename_clicked = QtCore.Signal(object)
    tile_clicked = QtCore.Signal(object)

    def __init__(self, classifier_id: int, name: str, model_name: str, accuracy: float):
        super().__init__()
        self.setupUi(self)
        self.classifier_id = classifier_id

        # Make the background styleable [sometimes needed if a widget is not complex enough].
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)

        # 1. Texte in der UI setzen
        self.label_name.setText(name.strip())
        self.old_label_name = name.strip()
        self.label_model.setText(model_name)

        # Genauigkeit formatieren (z.B. 95.4%)
        if accuracy is not None:
            self.label_result.setText(f"{accuracy * 100:.1f}%")
        else:
            self.label_result.setText("N/A")

        # 2. Buttons mit den Signalen verknüpfen
        self.button_labelDelete.clicked.connect(self.emit_delete)
        self.button_labelRename.clicked.connect(self.emit_rename)

        # Hover effects for buttons.
        self.button_labelRename.enterEvent = lambda e: self.button_hover_effect(self.button_labelRename, 'edit_orange', True)
        self.button_labelRename.leaveEvent = lambda e: self.button_hover_effect(self.button_labelRename, 'edit_grey', False)
        self.button_labelDelete.enterEvent = lambda e: self.button_hover_effect(self.button_labelDelete, 'delete_magenta', True)
        self.button_labelDelete.leaveEvent = lambda e: self.button_hover_effect(self.button_labelDelete, 'delete_grey', False)


    def set_selected(self, is_selected: bool) -> None:
        if is_selected:
            self.label_name.setStyleSheet("border: None; color: #ff9000; background-color: transparent; font-weight: bold;")
            self.label_model.setStyleSheet("border: None; color: #ff9000; background-color: transparent; font-weight: bold;")
            self.label_result.setStyleSheet("border: None; color: #ff9000; background-color: transparent; font-weight: bold;")
        else:
            self.label_name.setStyleSheet("border: None; color: #ebebeb; background-color: transparent; font-weight: light;")
            self.label_model.setStyleSheet("border: None; color: #ebebeb; background-color: transparent; font-weight: light;")
            self.label_result.setStyleSheet("border: None; color: #ebebeb; background-color: transparent; font-weight: light;")


    def button_hover_effect(self,
                            button: QtWidgets.QPushButton,
                            icon_name: str,
                            hover: bool) -> None:
        """
        This function takes in a PushButton widget and changes the button icon depending on whether the mouse of the user
        is hovering over the button or not and creates a button hover effect.
        =============================================================================
        :param button: The button widget where the mouse is hovering over.
        :param icon_name: The name of the button icon to display.
        :param hover: Boolean value for the hovering mouse [True - Mouse is hovering | False - Mouse is not hovering]
        =============================================================================
        :return: None.
        """

        # If the mouse is hovering over the button show this button picture.
        if hover:
            button.setIcon(QtGui.QIcon(f':/ui/_pics/icons/{icon_name}.png'))
        else:
            button.setIcon(QtGui.QIcon(f':/ui/_pics/icons/{icon_name}.png'))


    def emit_delete(self):
        self.delete_clicked.emit(self)


    def emit_rename(self):
        self.rename_clicked.emit(self)


    # 3. Klick auf das gesamte Tile abfangen (für das Detail-Fenster später)
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.tile_clicked.emit(self)
        super().mousePressEvent(event)