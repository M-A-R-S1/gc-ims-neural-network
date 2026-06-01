from PySide6 import QtWidgets, QtCore
from ui.ClassifierWidget import Ui_ClassifierWidget
from ui.ClassifierTile import Ui_ClassifierTile
from dialogs import CustomYesNoDialog, CustomProgressDialog
import sqlite3
from pathlib import Path
import torch
import model
import re
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

        # ScrollArea-Layout oben ausrichten, damit Elemente nicht mittig schweben
        self.scrollArea_classifier_Contents.layout().setAlignment(QtCore.Qt.AlignTop)

        # Initiale Daten laden
        self.load_classifiers_to_ui()

        # Connect the button
        self.pushButton_new_classification.clicked.connect(self.show_new_classifier_dialog)


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
                SELECT c.id, \
                       c.name, \
                       c.consensus_count, \
                       cv.f1_score -- (oder precision/accuracy, je nachdem was dein Hauptwert ist)
                FROM classifier c
                         LEFT JOIN classifier_result cr ON c.id = cr.classifier_id
                         LEFT JOIN classifier_value cv ON cr.id = cv.classifier_result_id
                WHERE cv.is_summary = 1 \
                   OR cv.is_summary IS NULL
                ORDER BY c.id DESC \
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

    # --- SLOTS (Reaktionen auf die Tile-Klicks) ---

    def on_delete_classifier(self, classifier_id: int):
        # Hier später: QMessageBox "Wirklich löschen?"
        print(f"Lösche Classifier mit ID: {classifier_id}")

        # Dank "ON DELETE CASCADE" in deinem SQL musst du nur in der
        # Tabelle 'classifier' löschen, SQLite löscht die Results/Values automatisch mit!
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM classifier WHERE id = ?", (classifier_id,))
        conn.commit()
        conn.close()

        # UI aktualisieren
        self.load_classifiers_to_ui()

    def on_rename_classifier(self, classifier_id: int, old_name: str):
        # Hier später: QInputDialog öffnen
        print(f"Benenne Classifier um: {old_name} (ID: {classifier_id})")

    def on_open_results(self, classifier_id: int):
        # Hier später: Deinen QDialog öffnen!
        print(f"Öffne Detail-Ansicht für Classifier ID: {classifier_id}")


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
        A Thread is created and started on which multiple pools are started to process the random forest classification.
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
        #start_random_forest(model=vae_model, device=device)






        # Connect to the database.
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Select all spectra paths, their associated label names and label ids for all spectra where the peak detection
        # process was not performed on.
        query = """
                SELECT spectra.path, labels.name, labels.id, spectra.id FROM spectra 
                JOIN labels ON spectra.label_id = labels.id 
                WHERE spectra.peaks_done = 0
                """
        cursor.execute(query)
        spectra_todo_list = cursor.fetchall()

        # Get the total number of spectra where the peak detection has to be performed.
        total_spectra = len(spectra_todo_list)
        if total_spectra == 0:
            conn.close()
            self.finished.emit()
            return

        # Get the number of available CPUs.
        num_cores = mp.cpu_count()
        # List where the peaks are saved to.
        peak_data_all = []
        # Number spectra where peaks have been calculated-
        processed_count = 0

        # Create a partial fixed function call, where the project_path and the peak_radis is set.
        worker_function = partial(peak_detection,
                                  project_path=self.project_path,
                                  peak_radius=5)

        # Start as many pools as possible [Depends on the number of CPU cores available].
        with mp.Pool(processes=num_cores) as pool:
            for result in pool.imap_unordered(worker_function, spectra_todo_list):
                # Check if the user stopped the peak detection.
                if self.worker_stopped:
                    pool.terminate()
                    pool.join()
                    break

                # Peak detection on one pool is done with results.
                if result:
                    spectrum_path, peaks = result

                    # If there are peaks append them to the peak_data_all list.
                    if peaks:
                        peak_data_all.extend(peaks)

                    # Update the database entry of this spectrum and commit the changes.
                    cursor.execute("UPDATE spectra SET peaks_done = 1 WHERE path = ?", (spectrum_path,))
                    conn.commit()

                # Update the counter and send an update signal for the progress bar widget.
                processed_count += 1
                self.progress_update.emit(processed_count, total_spectra)

        if peak_data_all:
            # Convert the peak data to a pandas dataframe and commit the peaks to the database.
            dataframe = pd.DataFrame(peak_data_all)
            dataframe.to_sql('peaks', conn, if_exists='append', index=False)
            conn.commit()
            print(f"Erfolgreich {len(dataframe)} Peaks in die Datenbank gespeichert.")

        conn.close()
        self.finished.emit()


def start_random_forest(model: torch.nn.Module,
                        device: torch.device) -> None:

    """
    This function prepares and executes the random forest algorithm.
    1. All .npy files from the consensus peaks are located and loaded.
    2. The latent mean vector from the autoencoder is calculated for each .npy file and appended by the
    retention and drifttime. Together this information is stored as a new vector.
    3. All these new vectors are split into train and test datasets.
    4. A random forest classifier is trained and tested with these vectors.
    5. The results are plotted and saved additionally as an Excel file.

    :param model: the trained Autoencoder model for the peak reconstruction.
    :param device: the device to run the model on.

    :return: None.
    """

    print("=======================================================")
    print("VI. RANDOM FOREST CLASSIFICATION")

    output_dir = Path(config.OUTPUT_DIR)
    # Get all consensus .npy files.
    npy_paths = list(output_dir.glob("*/npy/consensus peak/*/*.npy"))
    # Set with all consensus peak times.
    unique_consensus_peaks = set()

    # Find out how many spectra files are there.
    #folders = list(output_dir.glob("*/npy/consensus peak/*/"))
    # 2. Filtern, um sicherzugehen, dass es wirklich Verzeichnisse sind
    # (Optional, falls du sicher bist, dass dort keine Dateien liegen)
    spectra_count = len([f for f in list(output_dir.glob("*/npy/consensus peak/*/")) if f.is_dir()])
    # 3. Anzahl ermitteln


    # Collect all unique consensus peak times and save them in a set.
    for path in npy_paths:
        filename = path.stem
        consensus_peak = re.search(r'(RT[\d.]+_(DT[\d.]+))', filename)

        if consensus_peak:
            unique_consensus_peaks.add(consensus_peak.group(1))

    model.eval()


    # Walk through all consensus times and create a random forest for each individual consensus peak.
    for idx, consensus_peak in enumerate(unique_consensus_peaks):
        # List of all features and labels which will be used for the random forest algorithm.
        rf_features = []
        labels = []
        original_features = []
        reconstructions = []

        # Get the retention and drifttimes from the filename.
        # This code uses a regular expression. It looks for the pattern 'RT' followed by a number, followed by a dot.
        # Like RT125.154 -> By using group(1) the RT part is omitted and only "125.154" is selected.
        rt_val = float(re.search(r'RT([\d.]+)', consensus_peak).group(1))
        dt_val = float(re.search(r'DT([\d.]+)', consensus_peak).group(1))

        # Walk through all npy paths.
        for path in npy_paths:
            filename = path.stem

            if consensus_peak not in filename:
                continue

            parts = filename.split('_')

            # Get the label from the filename.
            label = parts[1]
            # Load the peak window from the path.
            peak_window = np.load(path)
            # Calculating the peak window size.
            peak_window_dimension = 4 * config.PEAK_RADIUS + 1

           # Normalize the peak window.
            min_intensity = peak_window.min()
            max_intensity = peak_window.max()
            if max_intensity - min_intensity == 0:
                npy_file_normalized = np.zeros_like(peak_window)
            else:
                npy_file_normalized = (peak_window - min_intensity) / (max_intensity - min_intensity)

            # Changing the peak window to a tensor and converting the tensor format.
            peak_window_tensor = torch.from_numpy(npy_file_normalized).float().view(1, 1, peak_window_dimension, peak_window_dimension).to(device)

            # Calculate the latent dimension vector for the current peak window.
            with torch.inference_mode():
                reconstruction, mean, log_variance = model(peak_window_tensor)

            # Combine the mean and variance vector.
            combined_feature = np.hstack((mean.cpu().numpy().flatten(),
                                          log_variance.cpu().numpy().flatten()))

            # Append the feature and labe to the list.
            original_features.append(peak_window_tensor)
            reconstructions.append(reconstruction)
            rf_features.append(combined_feature)
            labels.append(label)


        # Check if features and labels were found. If not, continue with the next consensus peak.
        if len(rf_features)*0.2 <= 4:
            print(f"Index: {idx + 1} - Skipping. Not enough peak windows: {len(rf_features)}x")
            continue

        # Split in Training und Test datasets.
        train_feature, test_feature, train_label, test_label = train_test_split(rf_features,
                                                                                labels,
                                                                                test_size=0.2,
                                                                                random_state=42)
        # Initialize the random forest algorithm.
        rf_model = RandomForestClassifier(n_estimators=1000,
                                          class_weight='balanced',
                                          random_state=42)

        # Start the random forest training.
        rf_model.fit(train_feature, train_label)
        # Get the random forest predictions.
        label_predictions = rf_model.predict(test_feature)
        # Save the results as a dictionary.
        results_dict = classification_report(test_label, label_predictions, output_dict=True)
        # Convert the dictionary to a pandas dataframe.
        results_dataframe = pd.DataFrame(results_dict).transpose()

        # Print the results to the console.
        print(f"Index: {idx + 1} - {(results_dict['accuracy'] * 100): .0f} % - RT{rt_val: .2f}_DT{dt_val: .2f} - {len(rf_features)}/{spectra_count}x")

        # Check and create the directory.
        filedir = Path(config.PLOT_DIR) / "random forest" / f"{(results_dict['accuracy']*100):.0f}% - RT{rt_val:.2f}_DT{dt_val:.2f} - {len(rf_features)}-{spectra_count}x"
        if not filedir.exists():
            filedir.mkdir(parents=True, exist_ok=True)
         # Save the dataframe as an Excel file.
        filename = filedir /"classification_results.xlsx"
        results_dataframe.to_excel(filename, index=True)

        # Plot the all used peak windows and their reconstructions as an overlay image.
        plot.plot_all_rf_peak_windows(labels=labels,
                                      features=original_features,
                                      feature_recons=reconstructions,
                                      plot_dir=filedir)

        # Plot the Importance graph.
        plot.random_forest_importance_plot(model=rf_model,
                                           output_dir=filedir,
                                           coordinates=False)
        # Plot the confusion matrix.
        plot.random_forest_confusion_matrix(model=rf_model,
                                            test_feature=test_feature,
                                            test_label=test_label,
                                            output_dir=filedir)
        # Plot the comparison boxplot.
        plot.random_forest_boxplot(features=rf_features,
                                   labels=labels,
                                   output_dir=filedir)

    print("Random Forest: All Individual peaks classified")



    # List of all features and labels which will be used for the random forest algorithm.
    rf_features = []
    labels = []

    # Walk through all consensus times and create a random forest for each all consensus peak together.
    for path in npy_paths:
        filename = path.stem

        parts = filename.split('_')

        # Get the label from the filename.
        label = parts[1]
        # Load the peak window from the path.
        peak_window = np.load(path)
        # Calculating the peak window size.
        peak_window_dimension = 4 * config.PEAK_RADIUS + 1

        # Normalize the peak window.
        min_intensity = peak_window.min()
        max_intensity = peak_window.max()
        if max_intensity - min_intensity == 0:
            npy_file_normalized = np.zeros_like(peak_window)
        else:
            npy_file_normalized = (peak_window - min_intensity) / (max_intensity - min_intensity)

        # Changing the peak window to a tensor and converting the tensor format.
        peak_window_tensor = torch.from_numpy(npy_file_normalized).float().view(1, 1, peak_window_dimension,
                                                                                peak_window_dimension).to(device)

        # Calculate the latent dimension vector for the current peak window.
        with torch.inference_mode():
            reconstruction, mean, log_variance = model(peak_window_tensor)

        rt_val = float(re.search(r'RT([\d.]+)', filename).group(1))
        dt_val = float(re.search(r'DT([\d.]+)', filename).group(1))

        # Combine the latent vector with the retention and drifttime.
        combined_feature = np.hstack((mean.cpu().numpy().flatten(), log_variance.cpu().numpy().flatten(), [rt_val, dt_val]))

        # Append the feature and labe to the list.
        rf_features.append(combined_feature)
        labels.append(label)


    # Split in Training und Test datasets.
    train_feature, test_feature, train_label, test_label = train_test_split(rf_features,
                                                                            labels,
                                                                            test_size=0.2,
                                                                            random_state=42)
    # Initialize the random forest algorithm.
    rf_model = RandomForestClassifier(n_estimators=1000,
                                      random_state=42)

    # Start the random forest training.
    rf_model.fit(train_feature, train_label)
    # Get the random forest predictions.
    label_predictions = rf_model.predict(test_feature)
    # Save the results as a dictionary.
    results_dict = classification_report(test_label, label_predictions, output_dict=True)
    # Convert the dictionary to a pandas dataframe.
    results_dataframe = pd.DataFrame(results_dict).transpose()

    # Print the results to the console.
    print(
        f"All Peak Results: {(results_dict['accuracy'] * 100): .0f}% - {results_dict['weighted avg']['support']}x")

    # Check and create the directory.
    filedir = Path(
        config.PLOT_DIR) / "random forest" / f"_ALL - {(results_dict['accuracy'] * 100):.0f}% - {results_dict['weighted avg']['support']}x"
    if not filedir.exists():
        filedir.mkdir(parents=True, exist_ok=True)
    # Save the dataframe as an Excel file.
    filename = filedir / "classification_results.xlsx"
    results_dataframe.to_excel(filename, index=True)

    # Plot the Importance graph.
    plot.random_forest_importance_plot(model=rf_model,
                                       output_dir=filedir,
                                       coordinates=True)
    # Plot the confusion matrix.
    plot.random_forest_confusion_matrix(model=rf_model,
                                        test_feature=test_feature,
                                        test_label=test_label,
                                        output_dir=filedir)
    # Plot the comparison boxplot.
    plot.random_forest_boxplot(features=rf_features,
                               labels=labels,
                               output_dir=filedir)

    print("Random Forest: Combined Peaks classified")


class ClassifierTileWidget(QtWidgets.QWidget, Ui_ClassifierTile):
    # Eigene Signale definieren, die an die Hauptseite gesendet werden
    delete_clicked = QtCore.Signal(int)  # Übergibt die classifier_id
    rename_clicked = QtCore.Signal(int, str)  # Übergibt ID und aktuellen Namen
    tile_clicked = QtCore.Signal(int)  # Übergibt die ID, um Details zu öffnen

    def __init__(self, classifier_id: int, name: str, peak_count: int, accuracy: float):
        super().__init__()
        self.setupUi(self)

        self.classifier_id = classifier_id

        # 1. Texte in der UI setzen
        self.label_name.setText(name)
        self.consensus_peak_counter.setText(f"{peak_count}x")

        # Genauigkeit formatieren (z.B. 95.4%)
        if accuracy is not None:
            self.label_result.setText(f"{accuracy * 100:.1f}%")
        else:
            self.label_result.setText("N/A")

        # 2. Buttons mit den Signalen verknüpfen
        self.button_labelDelete.clicked.connect(self.emit_delete)
        self.button_labelRename.clicked.connect(self.emit_rename)

    def emit_delete(self):
        self.delete_clicked.emit(self.classifier_id)

    def emit_rename(self):
        self.rename_clicked.emit(self.classifier_id, self.label_name.text())

    # 3. Klick auf das gesamte Tile abfangen (für das Detail-Fenster später)
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.tile_clicked.emit(self.classifier_id)
        super().mousePressEvent(event)