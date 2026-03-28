from PySide6 import QtWidgets, QtCore, QtGui
from DatasetWidget import Ui_DatasetWidget
import DatasetLabelEntry
from DatasetLabelEntry import Ui_DatasetLabelEntry
from DatasetSpectrumEntry import Ui_DatasetSpectrumEntry
from dialogs import CreateLabelDialog, CustomMessageDialog, CustomYesNoDialog, RenameLabelDialog
from pathlib import Path
import json
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import ims
from matplotlib import pyplot as plt


class DatasetPage(QtWidgets.QWidget, Ui_DatasetWidget):
    def __init__(self, project_path: str) -> None   :
        super().__init__()
        self.setupUi(self)

        # Project save path
        self.project_path = Path(project_path)
        # Defining the layout.
        self.scrollArea_labels_Contents.layout().setAlignment(QtCore.Qt.AlignTop)
        self.scrollArea_labels_Contents.layout().setSpacing(5)
        self.scrollArea_spectra_Contents.layout().setAlignment(QtCore.Qt.AlignTop)
        self.scrollArea_spectra_Contents.layout().setSpacing(5)
        # Connect the "add label" button.
        self.button_add_label.clicked.connect(self.open_label_file_dialog)
        # The selected label.
        self.current_selected_label = None
        # Connect the "add spectra" button.
        self.button_add_spectra.clicked.connect(self.open_spectra_file_dialog)
        # Saves labels and spectra in a dictionary.
        self.dataset_storage = {}
        # Setup the plot area.
        self.setup_plot()

        # load dataset from project.
        self.load_dataset()


    def open_label_file_dialog(self):
        dialog = CreateLabelDialog(self)

        if dialog.exec() == QtWidgets.QDialog.Accepted:
            data = dialog.get_data()
            name = data['name']

            if name:
                if not self.is_label_duplicate(name):
                    self.add_label_entry(name)
                else:
                    CustomMessageDialog.show_error("Error - Duplication", "Label already exists, please choose another name")
            else:
                CustomMessageDialog.show_error("Error - Empty", "Empty label name! Please choose a name for your label.")


    def is_label_duplicate(self, name: str, exclude_widget=None) -> bool:

        for i in range(self.scrollArea_labels_Contents.layout().count()):
            widget = self.scrollArea_labels_Contents.layout().itemAt(i).widget()

            if isinstance(widget, DatasetLabelEntry) and widget is not exclude_widget:
                if widget.label_name.text() == name:
                    return True

        return False


    def add_label_entry(self, name: str) -> None:
        label = DatasetLabelEntry(name)
        label.delete_requested.connect(self.confirm_delete)
        label.rename_requested.connect(self.confirm_rename)
        label.clicked.connect(self.handle_label_selection)
        self.scrollArea_labels_Contents.layout().insertWidget(self.scrollArea_labels_Contents.layout().count() - 1, label)
        self.update_label_count()

        if name not in self.dataset_storage:
            self.dataset_storage[name] = []
            self.save_dataset()

        label.label_counter.setText(f"{len(self.dataset_storage[name])}x")


    def handle_label_selection(self, selected_widget) -> None:
        self.clear_spectra_list()
        if self.current_selected_label:
            self.current_selected_label.set_active(False)

        self.current_selected_label = selected_widget
        self.current_selected_label.set_active(True)

        label_text = selected_widget.label_name.text()
        self.spectra_container_header.setText(label_text)

        self.refresh_spectra_display()


    def confirm_delete(self, label: DatasetLabelEntry) -> None:

        label_name = label.label_name.text()
        dialog = CustomYesNoDialog(title="Delete label",
                                   message=f"Are you sure you want to delete the '{label_name}' label?",
                                   type="warning",
                                   parent=self)


        if dialog.exec() == QtWidgets.QDialog.Accepted:
            if label == self.current_selected_label:
                self.spectra_container_header.setText("No label selected")
                self.current_selected_label = None

            label.deleteLater()
            self.scrollArea_labels_Contents.layout().removeWidget(label)
            self.update_label_count()
            del self.dataset_storage[label_name]
            self.refresh_spectra_display()
            self.save_dataset()


    def confirm_rename(self, label: DatasetLabelEntry, name: str) -> None:

        if self.is_label_duplicate(name, exclude_widget=label):
            CustomMessageDialog.show_error("Error - Duplication", "Label already exists, please choose another name")
            label.use_old_label_name()
            return

        self.dataset_storage[name] = self.dataset_storage.pop(label.old_label_name)

        label.label_name.setText(name)
        label.old_label_name = name

        if label == self.current_selected_label:
            self.spectra_container_header.setText(name)

        self.save_dataset()


    def update_label_count(self) -> None:
        count = 0

        for i in range(self.scrollArea_labels_Contents.layout().count()):
            widget = self.scrollArea_labels_Contents.layout().itemAt(i).widget()
            if isinstance(widget, DatasetLabelEntry):
                count += 1

        self.label_labelcounter.setText(f"{count} labels")


    def open_spectra_file_dialog(self):
        if not self.current_selected_label:
            CustomMessageDialog.show_error("Error - no label selected!", "You can't add a spectrum unless you select a label first!" , self)
            return

        file_paths, _ = QtWidgets.QFileDialog.getOpenFileNames(self,
                                                               "Select GC-IMS spectra",
                                                               "",
                                                               "GC-IMS File (*.mea)")

        if file_paths:
            self.add_spectra_to_list(file_paths)


    def add_spectra_to_list(self, file_paths):
        for file in file_paths:
            # Optional: Dubletten-Check
            if file not in self.dataset_storage[self.current_selected_label.label_name.text()]:
                self.dataset_storage[self.current_selected_label.label_name.text()].append(file)

        self.save_dataset()
        # 2. UI aktualisieren (Liste neu zeichnen)
        self.refresh_spectra_display()


    def refresh_spectra_display(self):
        # 1. Alle alten Widgets löschen
        layout = self.scrollArea_spectra_Contents.layout()
        while layout.count() >= 1:
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


        if self.current_selected_label is not None:
            # 2. Neue Widgets aus dem Speicher erstellen
            paths = self.dataset_storage[self.current_selected_label.label_name.text()]
            # Hier sortieren wir für die Anzeige
            paths.sort(key=lambda x: x)

            for i, path in enumerate(paths, 1):
                new_entry = DatasetSpectrumEntry(path, layout.count() + 1)
                new_entry.delete_requested.connect(self.remove_spectrum)
                new_entry.clicked.connect(self.plot_spectrum)
                layout.insertWidget(layout.count(), new_entry)

            self.current_selected_label.label_counter.setText(f"{len(self.dataset_storage[self.current_selected_label.label_name.text()])}x")
            self.label_spectracounter.setText(f"{len(self.dataset_storage[self.current_selected_label.label_name.text()])} spectra")
        else :
            self.label_spectracounter.setText("0 spectra")


    def clear_spectra_list(self):
        layout = self.scrollArea_spectra_Contents.layout()
        while layout.count() > 0:
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()


    def remove_spectrum(self, spectrum_widget):
        full_text = spectrum_widget.spectrum_name.text()
        display_name = full_text.split(" - ", 1)[1] if " - " in full_text else full_text

        dialog = CustomYesNoDialog(title="Delete spectrum",
                                   message=f"Do you really want to remove this spectrum?\n\n {display_name}",
                                   type="warning",
                                   parent=self)

        if dialog.exec() == QtWidgets.QDialog.Accepted:
            spectrum_widget.deleteLater()
            self.scrollArea_spectra_Contents.layout().removeWidget(spectrum_widget)
            QtCore.QTimer.singleShot(10, self.renumber_spectra)
            self.dataset_storage[self.current_selected_label.label_name.text()].remove(spectrum_widget.spectrum_path)
            self.refresh_spectra_display()
            self.save_dataset()

    def renumber_spectra(self):
        layout = self.scrollArea_spectra_Contents.layout()
        counter = 1

        for i in range(layout.count()):
            item = layout.itemAt(i)
            widget = item.widget()

            if isinstance(widget, DatasetSpectrumEntry):
                current_text = widget.spectrum_name.text()
                if " - " in current_text:
                    pure_name = current_text.split(" - ", 1)[1]
                    widget.spectrum_name.setText(f"{counter} - {pure_name}")
                    counter += 1

    def save_dataset(self):
        export_data = {
            label: [str(p) for p in paths] for label, paths in self.dataset_storage.items()
        }

        try:
            with open(self.project_path, 'w', encoding='utf-8') as f: json.dump(export_data, f, indent=4)
        except Exception as e:
            CustomMessageDialog.show_error("Error - Saving", "Something went wrong while saving the dataset!", self)
            print(f"Fehler beim Speichern: {e}")


    def load_dataset(self):
        try:
            with open(self.project_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 1. Alten Speicher komplett leeren
            self.dataset_storage.clear()
            self.dataset_storage.update(data)

            for label_name in self.dataset_storage.keys():
                self.add_label_entry(label_name)

            # 3. Die Benutzeroberfläche (UI) aktualisieren
            self.refresh_spectra_display()
        except Exception as e:
            print(f"Dataset loading error: {e}")


    def setup_plot(self):

        self.preview_image.setStyleSheet("background-color: #191919; border: none;")
        self.canvas = MplCanvas(self, width=5, height=4, dpi=50)
        self.canvas.fig.set_facecolor('#191919')

        # 2. Layout für dein QWidget erstellen (falls noch keins da ist)
        layout = QtWidgets.QVBoxLayout(self.preview_image)
        layout.addWidget(self.canvas)

        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.setStyleSheet("background-color: #2b2b2b; color: white; border: none;")
        layout.addWidget(self.toolbar)

        self.canvas.axes.set_title("Empty preview")
        self.canvas.axes.set_xticks([])
        self.canvas.axes.set_yticks([])
        self.canvas.draw()


    def plot_spectrum(self, file_path):
        plt.style.use('dark_background')

        # 1. Daten laden
        spec = ims.Spectrum.read_mea(file_path)

        # 2. Bestehende Achsen leeren (verhindert das "Überlagern" von alten Plots)
        self.canvas.fig.patch.set_facecolor('#191919')
        self.canvas.axes.clear()
        self.canvas.axes.set_facecolor('#191919')

        plt.rcParams.update({
            'font.size': 14,  # Standardgröße für alles
            'axes.titlesize': 26,  # Größe des Titels
            'axes.labelsize': 20,  # Größe der Achsenbeschriftungen (X/Y Label)
            'xtick.labelsize': 16,  # Größe der Zahlen an den Achsen
            'ytick.labelsize': 16
        })

        # 3. Zeichnen (direkt auf self.canvas.axes)
        # Nutze spec.values und die berechneten Extents
        img = self.canvas.axes.imshow(
            spec.values,
            origin="lower",
            aspect="auto",
            cmap="RdBu_r",
            vmin=30,  # Hintergrundrauschen unterdrücken
            vmax=400,  # RIP-Peak deckeln für besseren Kontrast
            extent=(
                min(spec.drift_time),
                max(spec.drift_time),
                min(spec.ret_time),
                max(spec.ret_time),
            ),
        )

        # 4. Beschriftung (Nur über das axes-Objekt!)
        self.canvas.axes.set_xlabel("Drift Time [ms]", labelpad=15)
        self.canvas.axes.set_ylabel("Retention Time [s]", labelpad=15)
        self.canvas.axes.set_title(Path(file_path).stem)

        # 5. Layout anpassen und neu zeichnen
        self.canvas.fig.tight_layout()
        self.canvas.draw()


class DatasetLabelEntry(QtWidgets.QLabel, Ui_DatasetLabelEntry):
    # Delete signal for the label.
    delete_requested = QtCore.Signal(object)
    # Rename signal.
    rename_requested = QtCore.Signal(object, str)
    # Label was clicked signal.
    clicked = QtCore.Signal(object)

    def __init__(self,
                 label_name: str,
                 count: int = 0) -> None:

        super().__init__()
        self.setupUi(self)

        # Set the label values.
        self.label_name.setText(label_name.strip())
        self.label_counter.setText(f"{count}x")
        self.old_label_name = label_name.strip()

        # Connect the delete button.
        self.button_labelDelete.clicked.connect(lambda: self.delete_requested.emit(self))
        # Connect the label Edit line.
        self.button_labelRename.clicked.connect(self.rename_dialog)
        # Hover effects for the rename button.
        self.button_labelRename.enterEvent = lambda e: self.button_hover_effect(self.button_labelRename, 'edit_orange', True)
        self.button_labelRename.leaveEvent = lambda e: self.button_hover_effect(self.button_labelRename, 'edit_grey', False)
        # Hover effects for the delete button.
        self.button_labelDelete.enterEvent = lambda e: self.button_hover_effect(self.button_labelDelete, 'delete_magenta',True)
        self.button_labelDelete.leaveEvent = lambda e: self.button_hover_effect(self.button_labelDelete, 'delete_grey',False)


    def button_hover_effect(self,
                            button: QtWidgets.QPushButton,
                            icon_name: str,
                            hover: bool):

        if hover:
            button.setIcon(QtGui.QIcon(f'ui/_pics/icons/{icon_name}.png'))
        else:
            button.setIcon(QtGui.QIcon(f'ui/_pics/icons/{icon_name}.png'))

    def rename_dialog(self):
        dialog = RenameLabelDialog(self.label_name.text(), self)

        if dialog.exec() == QtWidgets.QDialog.Accepted:
            new_label_name = dialog.get_data()['name']

            if new_label_name == self.label_name.text():
                return

            self.rename_requested.emit(self, new_label_name)


    def use_old_label_name(self):
        self.label_name.setText(self.old_label_name)


    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit(self)


    def set_active(self, active: bool) -> None:
        if active:
            self.label_name.setStyleSheet("border: None; color: #ff9000; background-color: transparent; font-weight: bold;")
            self.label_counter.setStyleSheet("border: None; color: #ff9000; background-color: transparent; font-weight: bold;")
        else:
            self.label_name.setStyleSheet("border: None; color: #ebebeb; background-color: transparent; font-weight: light;")
            self.label_counter.setStyleSheet("border: None; color: #ebebeb; background-color: transparent; font-weight: light;")


class DatasetSpectrumEntry(QtWidgets.QWidget, Ui_DatasetSpectrumEntry):
    # Delete signal
    delete_requested = QtCore.Signal(object)
    # Click signal
    clicked = QtCore.Signal(str)

    def __init__(self, path:str, number: int):
        super().__init__()
        self.setupUi(self)

        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)

        self.spectrum_path = path
        self.spectrum_name.setText(f"{number} - {Path(self.spectrum_path).parent.name}/{Path(self.spectrum_path).stem}")
        self.button_spectrumDelete.enterEvent = lambda e: self.button_spectrumDelete.setIcon(QtGui.QIcon(r'ui/_pics/icons/delete_magenta.png'))
        self.button_spectrumDelete.leaveEvent = lambda e: self.button_spectrumDelete.setIcon(QtGui.QIcon(r'ui/_pics/icons/delete_grey.png'))

        # Connect the delete button
        self.button_spectrumDelete.clicked.connect(lambda: self.delete_requested.emit(self))

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit(self.spectrum_path)


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=50):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.fig.tight_layout()
        super().__init__(self.fig)