from __future__ import annotations
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtGui import QFont
from ClassifierWidget import Ui_ClassifierWidget
from ClassifierTile import Ui_ClassifierTile
from dialogs import CustomYesNoDialog, CustomProgressDialog, RenameLabelDialog, CustomMessageDialog
import sqlite3
from pathlib import Path
import torch
import model
import plot
import re
import shutil
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report


class ClassifierPage(QtWidgets.QWidget, Ui_ClassifierWidget):
    def __init__(self, project_path: Path):
        super().__init__()
        self.setupUi(self)

        # Project save path.
        self.project_path = Path(project_path)
        # Database path.
        self.db_path = self.project_path.parent / "database" / "project_database.db"
        self.current_selected_classifier_id = None

        # ScrollArea-Layout oben ausrichten, damit Elemente nicht mittig schweben
        self.scrollArea_classifier_Contents.layout().setAlignment(QtCore.Qt.AlignTop)

        # Initiale Daten laden
        self.load_classifiers_to_ui()

        # Connect the button
        self.pushButton_new_classification.clicked.connect(self.show_new_classifier_dialog)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_confusion_matrix_image()


    def load_classifiers_to_ui(self):
        """
        Lädt alle Classifier aus der Datenbank und baut die Tiles auf.
        """
        layout = self.scrollArea_classifier_Contents.layout()

        # 1. Altes Layout bereinigen (Wichtig, falls die Liste neu geladen wird)
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # 2. Datenbankverbindung und Query
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # SQL: Wir holen uns den Classifier und joinen die Tabellen, um den
        # is_summary=1 Wert (das Gesamtergebnis) direkt abzugreifen.
        query = """
                SELECT c.id,
                       c.name,
                       c.consensus_count,
                       cv.f1_score
                FROM classifier c
                         LEFT JOIN classifier_result cr ON c.id = cr.classifier_id AND cr.consensus_id IS NULL
                         LEFT JOIN classifier_value cv ON cr.id = cv.classifier_result_id AND cv.label = 'weighted avg'
                ORDER BY c.id ASC
                """
        cursor.execute(query)
        classifiers = cursor.fetchall()
        conn.close()

        # 3. Tiles erstellen und dem Layout hinzufügen
        for c_id, name, count, accuracy in classifiers:
            # Hier nutzen wir unsere Custom-Klasse von oben
            tile = ClassifierTileWidget(
                classifier_id=c_id,
                name=name,
                peak_count=count if count else 0,
                accuracy=accuracy
            )

            # Signale mit Funktionen in dieser Klasse verbinden
            tile.delete_clicked.connect(self.on_delete_classifier)
            tile.rename_clicked.connect(self.on_rename_classifier)
            tile.tile_clicked.connect(self.on_open_results)

            # Ab ins UI-Layout
            layout.addWidget(tile)


    def on_delete_classifier(self,
                             classification_widget: ClassifierTileWidget) -> None:

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


    def on_open_results(self, classifier_id: int):

        self.current_selected_classifier_id = classifier_id

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


    def show_new_classifier_dialog(self) -> None:
        """
        This function is called when the user wants to create a new classification. It creates a dialog where the user is
        prompted to start the classification process.
        =============================================================================
        :return: None.
        """

        # Create a custom yes/no dialog for the user where he can start the classification process.
        dialog = CustomYesNoDialog(
            title="Start new classification",
            message="You are about to start a new classification process. Check the activity of all desired consensus peaks in the "
                    "consensus peak tab, select a name and choose a classification model.",
            type="warning",
            parent=self
        )

        # If the user accepted the dialog, call the start_new_classification method.
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.start_new_classification()


    def start_new_classification(self) -> None:
        """
        This function is called when the user accepted the "start new classification" prompt.
        A Thread is created and started on which the random forest classification is executed.
        =============================================================================
        :return: None
        """

        # Open the progress dialog which informs the user about the current state of the preprocessing.
        self.classification_progress_dialog = CustomProgressDialog(title="Classification in progress...", header="Classifying...",)
        # Reset the start time.
        self.classification_progress_dialog.start_time = None
        self.classification_progress_dialog.show()

        # Create a thread and worker for the progress dialog.
        self.thread = QtCore.QThread()
        self.worker = ClassificationWorker(path=self.project_path)
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

        # Start the thread.
        self.thread.start()


class ClassificationWorker(QtCore.QObject):
    # Signal definitions.
    finished = QtCore.Signal()
    progress_update = QtCore.Signal(int, int)

    def __init__(self, path: Path):

        super().__init__()
        self.project_path = path.parent
        self.db_path = self.project_path / "database" / "project_database.db"
        self.worker_stopped = False


    @QtCore.Slot()
    def stop(self):
        self.worker_stopped = True

    def emit_progress(self, current_step: int, total_steps: int):
        self.progress_update.emit(current_step, total_steps)

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
        vae_model = model.VariationalAutoencoderCNN(input_layers=1,
                                                hidden_layers=64,
                                                latent_dimension=16).to(device)

        # Load the model state dict.
        vae_model.load_model(model_dir="models", file_name="GC-IMS-CNN-VAE-HONEY-RUB-E1500-DIM16.pt", device=device)
        # Start the random forest algorithm.
        self.start_random_forest(model=vae_model,
                                 device=device,
                                 db_path=self.db_path,
                                 project_path=self.project_path,
                                 classification_name="Test Name",
                                 progress_callback=self.emit_progress,
                                 check_stopped_callback=self.check_stopped)

        self.finished.emit()


    def start_random_forest(self,
                            model: torch.nn.Module,
                            device: torch.device,
                            db_path: Path,
                            project_path: Path,
                            classification_name: str,
                            progress_callback=None,
                            check_stopped_callback=None) -> None:

        """
        This function prepares and executes the random forest algorithm.
        1. All .npy files from the consensus peaks are located and loaded via Database.
        2. The latent mean vector from the autoencoder is calculated.
        3. Split into train and test datasets.
        4. A random forest classifier is trained and tested.
        5. The results are plotted, saved as Excel, and written to the DB.
        """

        print("=======================================================")
        print("VI. RANDOM FOREST CLASSIFICATION")

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

        spectra_count = df['spectrum_id'].nunique()
        unique_consensus_count = df['consensus_id'].nunique()

        total_steps = unique_consensus_count + 1

        # ---------------------------------------------------------
        # NEU: Haupt-Eintrag für den Classifier in der DB erstellen
        # ---------------------------------------------------------
        cursor = conn.cursor()
        cursor.execute("INSERT INTO classifier (name, consensus_count) VALUES (?, ?)",
                       (classification_name, unique_consensus_count))
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

        train_feature, test_feature, train_label, test_label = train_test_split(rf_features, labels, test_size=0.2,
                                                                                random_state=42)
        rf_model = RandomForestClassifier(n_estimators=1000, random_state=42)
        rf_model.fit(train_feature, train_label)

        label_predictions = rf_model.predict(test_feature)
        results_dict = classification_report(test_label, label_predictions, output_dict=True, zero_division=0)
        results_dataframe = pd.DataFrame(results_dict).transpose()

        print(
            f"All Peak Results: {(results_dict['accuracy'] * 100): .0f}% - {results_dict['weighted avg']['support']}x")

        # --- DB SPEICHERN (Kombiniertes Ergebnis) ---
        # consensus_id = NULL bedeutet "Ergebnis über alle Peaks"
        cursor.execute("INSERT INTO classifier_result (classifier_id, consensus_id) VALUES (?, NULL)", (classifier_id,))
        result_id = cursor.lastrowid

        for key, metrics in results_dict.items():
            if key == 'accuracy': continue
            is_summary = 1 if key in ['macro avg', 'weighted avg'] else 0
            cursor.execute("""
                           INSERT INTO classifier_value (classifier_result_id, label, is_summary, precision, recall, f1_score, support)
                           VALUES (?, ?, ?, ?, ?, ?, ?)
                           """,
                           (result_id, key, is_summary, metrics['precision'], metrics['recall'], metrics['f1-score'], metrics['support']))
        conn.commit()
        conn.close()
        # --------------------------------------------

        filedir = project_path / "classification" / f"{classifier_id}" / "total"
        if not filedir.exists(): filedir.mkdir(parents=True, exist_ok=True)
        results_dataframe.to_excel(filedir / "classification_results.xlsx", index=True)

        #plot.random_forest_importance_plot(model=rf_model, output_dir=filedir, coordinates=True)
        plot.random_forest_confusion_matrix(model=rf_model, test_feature=test_feature, test_label=test_label,output_dir=filedir)
        #plot.random_forest_boxplot(features=rf_features, labels=labels, output_dir=filedir)

        if progress_callback:
            progress_callback(total_steps, total_steps)

        print("Random Forest: Combined Peaks classified")


class ClassifierTileWidget(QtWidgets.QWidget, Ui_ClassifierTile):
    # Signal definitions.
    delete_clicked = QtCore.Signal(object)
    rename_clicked = QtCore.Signal(object)
    tile_clicked = QtCore.Signal(int)

    def __init__(self, classifier_id: int, name: str, peak_count: int, accuracy: float):
        super().__init__()
        self.setupUi(self)
        self.classifier_id = classifier_id

        # Make the background styleable [sometimes needed if a widget is not complex enough].
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)

        # 1. Texte in der UI setzen
        self.label_name.setText(name.strip())
        self.old_label_name = name.strip()
        self.consensus_peak_counter.setText(f"{peak_count}x")

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
            button.setIcon(QtGui.QIcon(f'ui/_pics/icons/{icon_name}.png'))
        else:
            button.setIcon(QtGui.QIcon(f'ui/_pics/icons/{icon_name}.png'))


    def emit_delete(self):
        self.delete_clicked.emit(self)


    def emit_rename(self):
        self.rename_clicked.emit(self)


    # 3. Klick auf das gesamte Tile abfangen (für das Detail-Fenster später)
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.tile_clicked.emit(self.classifier_id)
        super().mousePressEvent(event)