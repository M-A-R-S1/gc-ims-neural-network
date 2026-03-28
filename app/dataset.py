from __future__ import annotations
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtCore import QSize, Qt
from DatasetWidget import Ui_DatasetWidget
from DatasetLabelEntry import Ui_DatasetLabelEntry
from DatasetSpectrumEntry import Ui_DatasetSpectrumEntry
from dialogs import CreateLabelDialog, CustomMessageDialog, CustomYesNoDialog, RenameLabelDialog
from pathlib import Path
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib import pyplot as plt
import ims
import json


class DatasetPage(QtWidgets.QWidget, Ui_DatasetWidget):
    def __init__(self, project_path: str) -> None   :
        super().__init__()
        self.setupUi(self)

        # Project save path
        self.project_path = Path(project_path)
        # Defining the layout.
        self.scrollArea_labels_Contents.layout().setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.scrollArea_labels_Contents.layout().setSpacing(5)
        self.scrollArea_spectra_Contents.layout().setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.scrollArea_spectra_Contents.layout().setSpacing(5)
        # Connect the "add label" button.
        self.button_add_label.clicked.connect(self.add_label_dialog)
        # The selected label.
        self.current_selected_label = None
        self.current_selected_spectrum = None
        # Connect the "add spectra" button.
        self.button_add_spectra.clicked.connect(self.add_spectra_dialog)
        # Saves labels and spectra in a dictionary.
        self.dataset_storage = {}
        # Setup the plot area.
        self.setup_plot()

        # load dataset from project.
        self.load_dataset()


    def add_label_dialog(self) -> None:
        """
        This function is called if the "Add label" button is pressed and shows a label dialog.
        In this dialog the user can enter a label name for the addition to the label list.
        This label is added to the label list if the label name is not emtpy and not a duplicate.
        =============================================================================
        :return: None.
        """

        # Create the dialog window.
        dialog = CreateLabelDialog(self)

        # Show the dialog window and wait for the user response. If the user wants to add a label proceed here.
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            name = data['name']

            # Check if the label is a new label and if the name is not empty.
            if name:
                if not self.duplication_check(name):
                    # The new label is not a duplicate, add the label!
                    self.add_label(name)
                else:
                    CustomMessageDialog.show_error("Error - Duplication", "Label already exists, please choose another name")
            else:
                CustomMessageDialog.show_error("Error - Empty", "Empty label name! Please choose a name for your label.")


    def duplication_check(self,
                          name: str,
                          exclude_widget=None) -> bool:
        """
        This function takes in the name of a new label or the name of a renamed label and checks if there is already
        a label with this name present. If so this label is considered a duplication and is not added as a new label!
        =============================================================================
        :param name: The name of the new/renamed label.
        :param exclude_widget: The widget of the renamed label.
        =============================================================================
        :return: Boolean value for the duplication check [True = duplicate | False = No duplicate]
        """

        # Walks through all labels and checks if the new label name is unique
        for i in range(self.scrollArea_labels_Contents.layout().count()):
            # Get the widget of the label.
            widget = self.scrollArea_labels_Contents.layout().itemAt(i).widget()

            # Check if the widget is of the correct type "DatasetLabelEntry" and if the widget should be excluded.
            if isinstance(widget, DatasetLabelEntry) and widget is not exclude_widget:
                # If the new label name matches on of the labels return true.
                if widget.label_name.text() == name:
                    return True

        # No duplications found.
        return False


    def add_label(self,
                        name: str) -> None:
        """
        This function is called when a new label is about to be added. The label is connected so a series of signals
        [Delete | Rename] and is finally added as a widget to the label scroll area and to the dataset storage dictionary.
        =============================================================================
        :param name: The name of the label.
        =============================================================================
        :return: None.
        """

        # Create a new instance of the "DatasetLabelEntry" class.
        label = DatasetLabelEntry(name)
        # Connect to the delete and rename signals.
        label.delete_signal.connect(self.delete_label_dialog)
        label.rename_signal.connect(self.rename_label_dialog)
        # Connect the label click to a handling function.
        label.clicked.connect(self.handle_label_click)
        # Insert the new label into the label scroll area as a widget.
        self.scrollArea_labels_Contents.layout().insertWidget(self.scrollArea_labels_Contents.layout().count() - 1, label)
        # Update the label counter.
        self.update_label_count()

        # Check if the label is already saved in the dataset storage directory. If not add it.
        if name not in self.dataset_storage:
            self.dataset_storage[name] = []
            self.save_dataset()

        # Count the number of spectra which are associated for the current label and update the spectra counter.
        label.spectra_counter.setText(f"{len(self.dataset_storage[name])}x")


    def handle_label_click(self,
                           label_widget: DatasetLabelEntry) -> None:
        """
        This function is handling the "label clicked" event. If a label widget is clicked inside the label scroll area
        this function is called. The label is now registered as the "currently selected" label.

        This will change the following things:
            1. The selected label widget is highlighted in the label scroll area.
            2. The header of the spectra scroll area is set to the name of the selected label.
            3. The spectra scroll area list is cleared and filled with all spectra which are associated with the new
               selected label.
        =============================================================================
        :param label_widget: The label widget which was clicked in the label scroll area.
        =============================================================================
        :return: None.
        """

        # Clear the spectra scroll area from all widgets.
        self.clear_spectra_list()
        self.current_selected_spectrum = None

        # Find out which label is currently selected and deactivate it.
        if self.current_selected_label:
            self.current_selected_label.set_active(False)

        # Set the clicked label as the "currently selected label".
        self.current_selected_label = label_widget
        self.current_selected_label.set_active(True)

        # Get the name of the label and set this name to the header of the spectra scroll area.
        label_name = label_widget.label_name.text()
        self.spectra_container_header.setText(label_name)

        # Refresh the spectra scroll area to show the spectra associated with the new selected label.
        self.update_spectra_list()


    def delete_label_dialog(self,
                            label_widget: DatasetLabelEntry) -> None:
        """
        This function is called when a label delete icon was pressed. A "label delete" dialog will be displayed to the
        user. If the user decides to delete the label, the label is removed from the label scroll area and the dataset
        storage. The Spectrum scroll area is cleared, if the deleted label was the currently selected label.
        =============================================================================
        :param label_widget: The label widget of which the delete button was pressed.
        =============================================================================
        :return: None.
        """
        
        # Get the name of the label.
        label_name = label_widget.label_name.text()
        # Define a Yes/No Dialog for the deletion.
        dialog = CustomYesNoDialog(title="Delete label",
                                   message=f"Are you sure you want to delete the '{label_name}' label?",
                                   type="warning",
                                   parent=self)

        # The user wants to delete the label.
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            # If the label was the currently selected label, the spectra scroll area has to be cleared.
            if label_widget == self.current_selected_label:
                self.spectra_container_header.setText("No label selected")
                self.current_selected_label = None
                self.current_selected_spectrum = None
                # TODO ... Clear the spectrum preview here.

            # Delete the label widget, remove it from the label scroll area and update the label counter.
            label_widget.deleteLater()
            self.scrollArea_labels_Contents.layout().removeWidget(label_widget)
            self.update_label_count()
            # Remove the label from the data storage dictionary and refresh the spectra scroll area.
            del self.dataset_storage[label_name]
            self.update_spectra_list()
            # Save the adjusted dataset storage.
            self.save_dataset()


    def rename_label_dialog(self,
                            label_widget: DatasetLabelEntry) -> None:
        """
        This function is called when the user clicked on the renaming button of a label inside the label scroll area.
        This function shows a rename dialog for the user to input a new label name.
        This new label name is then checked for duplication. If it is not a duplicate the label is renamed.
        =============================================================================
        :param label_widget: The label widget of which the rename button was clicked in the label scroll area.
        =============================================================================
        :return: None.
        """

        # Create the label rename dialog.
        dialog = RenameLabelDialog(label_widget.label_name.text(), self)

        # The user chooses to rename the label.
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            # get the new label name from the dialog data.
            new_label_name = dialog.get_data()['name']

            # If the old and the new label name are the same skip renaming.
            if new_label_name == label_widget.label_name.text():
                return

            # If the new label name is a duplicate [label name already exits in list] skip renaming and rollback.
            if self.duplication_check(new_label_name, exclude_widget=label_widget):
                CustomMessageDialog.show_error("Error - Duplication",
                                               "Label already exists, please choose another name")
                label_widget.label_name.setText(label_widget.old_label_name)
                return

            # Exchange the label name in the dataset storage and display the new label name.
            self.dataset_storage[new_label_name] = self.dataset_storage.pop(label_widget.old_label_name)
            label_widget.label_name.setText(new_label_name)
            label_widget.old_label_name = new_label_name

            # If the renamed label is the currently selected label, then change also the header of the spectra scroll area.
            if label_widget == self.current_selected_label:
                self.spectra_container_header.setText(new_label_name)

            # Save the adjusted dataset storage.
            self.save_dataset()


    def update_label_count(self) -> None:
        """
        This function counts the number of label widgets inside the label scroll area and updates this information
        in the viewspace.
        =============================================================================
        :return: None.
        """

        # Initialize the counter to 0.
        count = 0

        # Walk through all label widgets inside the label scroll area and increase the counter for each label widget.
        for i in range(self.scrollArea_labels_Contents.layout().count()):
            label_widget = self.scrollArea_labels_Contents.layout().itemAt(i).widget()
            if isinstance(label_widget, DatasetLabelEntry):
                count += 1

        # Set the counter.
        self.label_labelcounter.setText(f"{count} labels")


    def add_spectra_dialog(self) -> None:
        """
        This function opens a file dialog for spectra to choose when the "add spectra" button was pressed by the user.
        =============================================================================
        :return: None
        """

        # Show an error dialog if the user wants to add a spectrum without choosing a label first.
        if not self.current_selected_label:
            CustomMessageDialog.show_error(title="Error - no label selected!",
                                           message="You can't add a spectrum unless you select a label first!" ,
                                           parent=self)
            return

        # Open a file dialog and collect paths to .mea files.
        file_paths, _ = QtWidgets.QFileDialog.getOpenFileNames(self,
                                                               caption="Select GC-IMS spectra",
                                                               dir="",
                                                               filter="GC-IMS File (*.mea)")
        # Forward the paths for handling.
        if file_paths:
            self.add_spectra(paths=file_paths)


    def add_spectra(self,
                    paths: list[str]) -> None:
        """
        This function accepts a list of spectra paths and saves them in the dataset storage dictionary.
        =============================================================================
        :param paths: list of spectra paths.
        =============================================================================
        :return: None.
        """

        # Walk through all paths and add them to the dataset storage dictionary.
        for path in paths:
            # Check if the path is already part of the dictionary, if so skip it.
            if path not in self.dataset_storage[self.current_selected_label.label_name.text()]:
                self.dataset_storage[self.current_selected_label.label_name.text()].append(path)

        # Save the adjusted dataset storage.
        self.save_dataset()
        # 2. UI aktualisieren (Liste neu zeichnen)
        self.update_spectra_list()


    def update_spectra_list(self) -> None:
        """
        This function updates the spectra scroll area and shows all spectra which are connected to the currently
        selected label. It also connects delete and click signals to the spectra widgets.
        =============================================================================
        :return: None
        """

        # Get the spectra scroll area layout.
        spectra_layout = self.scrollArea_spectra_Contents.layout()
        # Clear the spectra list.
        self.clear_spectra_list()

        # If a label is selected look for all spectra which are connected to this label and add them to the spectra scroll area.
        if self.current_selected_label is not None:
            # Get all spectra paths of the current label from the dataset storage dictionary.
            paths = self.dataset_storage[self.current_selected_label.label_name.text()]
            # Sort the paths.
            paths.sort()

            # Walk through all paths from the current label and set up the spectra widgets.
            for path in paths:
                # Create a new spectra widget element.
                spectra_widget = DatasetSpectrumEntry(path, spectra_layout.count() + 1)
                # Connect the widget to a delete and click signal.
                spectra_widget.delete_signal.connect(self.delete_spectrum)
                spectra_widget.clicked.connect(self.plot_spectrum)
                # Insert the widget to the spectra scroll area.
                spectra_layout.insertWidget(spectra_layout.count(), spectra_widget)

            # Update the spectra counter inside the label scroll area and the counter beneath the spectra scroll area.
            self.current_selected_label.spectra_counter.setText(f"{len(self.dataset_storage[self.current_selected_label.label_name.text()])}x")
            self.label_spectracounter.setText(f"{len(self.dataset_storage[self.current_selected_label.label_name.text()])} spectra")
        # If there is currently no label selected set the spectra counter to the default value.
        else :
            self.label_spectracounter.setText("0 spectra")


    def clear_spectra_list(self) -> None:
        """
        This function removes all spectra widgets from the spectra scroll area.
        =============================================================================
        :return: None.
        """

        # Get the spectra scroll area layout
        spectra_layout = self.scrollArea_spectra_Contents.layout()
        # Remove all widgets from the spectra scroll area.
        while spectra_layout.count() > 0:
            item = spectra_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


    def delete_spectrum(self,
                        spectrum_widget: DatasetSpectrumEntry):
        """
        This function shows a delete dialog when the delete button of a spectrum is pressed.
        If the user chooses to delete the spectrum, it is removed from the spectra scroll area and the dataset storage
        dictionary.
        =============================================================================
        :param spectrum_widget: The widget of the spectrum to be deleted.
        =============================================================================
        :return: None
        """

        # Get the name of the spectrum which is about to be deleted.
        spectrum_name = spectrum_widget.spectrum_name.text()
        # Crop the name by removing the first part, which is a number followed by a hyphen. -> "1 -"
        cropped_name = spectrum_name.split(" - ", 1)[1] if " - " in spectrum_name else spectrum_name

        # Create a Yes/No dialog for the user to make sure that he really wants to delete the spectrum.
        delete_dialog = CustomYesNoDialog(title="Delete spectrum",
                                          message=f"Do you really want to remove this spectrum?\n\n {cropped_name}",
                                          type="warning",
                                          parent=self)

        # The user really wants to delete to spectrum.
        if delete_dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            # Delete the spectrum widget and remove it from the spectra scroll area.
            spectrum_widget.deleteLater()
            self.scrollArea_spectra_Contents.layout().removeWidget(spectrum_widget)
            # Wait for 10 milliseconds and then call the renumber_spectra function to adjust the spectra numbering in the spectra scroll area.
            QtCore.QTimer.singleShot(10, self.renumber_spectra)
            # Remove the spectrum also from the dataset storage directory.
            self.dataset_storage[self.current_selected_label.label_name.text()].remove(spectrum_widget.spectrum_path)
            # Update the displayed spectra list and save the dataset storage.
            self.update_spectra_list()
            self.save_dataset()


    def renumber_spectra(self) -> None:
        """
        This function walks through all spectra widgets of the spectra scroll area and adds numbers to their name according
        to their index in the scroll area. This function is called when one of the spectra was deleted and ensures the
        correct ordering.
        =============================================================================
        :return: None.
        """

        # Get the spectra layout.
        spectra_layout = self.scrollArea_spectra_Contents.layout()
        # The counter which is used for the numbering process.
        counter = 1

        # One iteration for each spectrum widget.
        for index in range(spectra_layout.count()):
            # Get the spectrum widget of the current index.
            spectrum_widget = spectra_layout.itemAt(index).widget()

            # Check if the widget is an instance of the DatasetSpectrumEntry class.
            if isinstance(spectrum_widget, DatasetSpectrumEntry):
                # Get the name of the spectrum, crop it and add the number of the current index to it.
                spectrum_name = spectrum_widget.spectrum_name.text()
                cropped_name = spectrum_name.split(" - ", 1)[1]
                spectrum_widget.spectrum_name.setText(f"{counter} - {cropped_name}")
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
                self.add_label(label_name)

            # 3. Die Benutzeroberfläche (UI) aktualisieren
            self.update_spectra_list()
        except Exception as e:
            print(f"Dataset loading error: {e}")


    def setup_plot(self):

        self.preview_image.setStyleSheet("background-color: #191919; border: none;")
        self.canvas = MplCanvas(self, width=5, height=4, dpi=50)
        self.canvas.fig.set_facecolor('#191919')
        self.canvas.axes.set_facecolor('#191919')

        plt.rcParams.update({
            'font.size': 14,  # Standardgröße für alles
            'axes.titlesize': 26,  # Größe des Titels
            'axes.labelsize': 20,  # Größe der Achsenbeschriftungen (X/Y Label)
            'xtick.labelsize': 16,  # Größe der Zahlen an den Achsen
            'ytick.labelsize': 16
        })

        # Optional: Den Rahmen der Axes (Spines) ebenfalls verstecken oder färben
        for spine in self.canvas.axes.spines.values():
            spine.set_edgecolor('#191919')  # Ein dezentes Grau für den Rahmen

        # 2. Layout für dein QWidget erstellen (falls noch keins da ist)
        layout = QtWidgets.QVBoxLayout(self.preview_image)
        layout.addWidget(self.canvas)

        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.setStyleSheet("background-color: #191919; color: white; border: none;")
        toolbar_actions = self.toolbar.actions()

        for action in toolbar_actions:
            if any(word in action.text() for word in ["Subplots", "Back", "Forward", "Customize"]):
                self.toolbar.removeAction(action)

        self.toolbar.setIconSize(QSize(36,36))
        # 2. Die Höhe der Toolbar fixieren
        self.toolbar.setFixedHeight(50)

        for button in self.toolbar.findChildren(QtWidgets.QToolButton):
            button.setCursor(Qt.CursorShape.PointingHandCursor)

        #self.toolbar.hide()
        layout.addWidget(self.toolbar)

        self.canvas.axes.set_xticks([])
        self.canvas.axes.set_yticks([])
        self.canvas.draw()


    def plot_spectrum(self, spectrum_widget):

        if self.current_selected_spectrum:
            self.current_selected_spectrum.set_active(False)

        self.current_selected_spectrum = spectrum_widget
        self.current_selected_spectrum.set_active(True)

        plt.style.use('dark_background')

        # 1. Daten laden
        spec = ims.Spectrum.read_mea(spectrum_widget.spectrum_path)
        spec.riprel()

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

        self.canvas.fig.subplots_adjust(left=0.069, bottom=0.058, right=0.094, top=0.995)
        self.toolbar.show()

        # 5. Layout anpassen und neu zeichnen
        self.canvas.fig.tight_layout()
        self.canvas.draw()


class DatasetLabelEntry(QtWidgets.QLabel, Ui_DatasetLabelEntry):
    # Delete signal for the label.
    delete_signal = QtCore.Signal(object)
    # Rename signal.
    rename_signal = QtCore.Signal(object)
    # Label was clicked signal.
    clicked = QtCore.Signal(object)

    def __init__(self,
                 label_name: str,
                 count: int = 0) -> None:

        super().__init__()
        self.setupUi(self)

        # Set the label values.
        self.label_name.setText(label_name.strip())
        self.spectra_counter.setText(f"{count}x")
        self.old_label_name = label_name.strip()

        # Connect the delete button.
        self.button_labelDelete.clicked.connect(lambda: self.delete_signal.emit(self))
        # Connect the rename button.
        self.button_labelRename.clicked.connect(lambda: self.rename_signal.emit(self))
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


    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.clicked.emit(self)


    def set_active(self, active: bool) -> None:
        if active:
            self.label_name.setStyleSheet("border: None; color: #ff9000; background-color: transparent; font-weight: bold;")
            self.spectra_counter.setStyleSheet("border: None; color: #ff9000; background-color: transparent; font-weight: bold;")
        else:
            self.label_name.setStyleSheet("border: None; color: #ebebeb; background-color: transparent; font-weight: light;")
            self.spectra_counter.setStyleSheet("border: None; color: #ebebeb; background-color: transparent; font-weight: light;")


class DatasetSpectrumEntry(QtWidgets.QWidget, Ui_DatasetSpectrumEntry):
    # Delete signal
    delete_signal = QtCore.Signal(object)
    # Click signal
    clicked = QtCore.Signal(object)

    def __init__(self, path:str, number: int):
        super().__init__()
        self.setupUi(self)

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)

        self.spectrum_path = path
        self.spectrum_name.setText(f"{number} - {Path(self.spectrum_path).parent.name}/{Path(self.spectrum_path).stem}")
        self.button_spectrumDelete.enterEvent = lambda e: self.button_spectrumDelete.setIcon(QtGui.QIcon(r'ui/_pics/icons/delete_magenta.png'))
        self.button_spectrumDelete.leaveEvent = lambda e: self.button_spectrumDelete.setIcon(QtGui.QIcon(r'ui/_pics/icons/delete_grey.png'))

        # Connect the delete button
        self.button_spectrumDelete.clicked.connect(lambda: self.delete_signal.emit(self))

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.clicked.emit(self)


    def set_active(self, active: bool) -> None:
        if active:
            self.spectrum_name.setStyleSheet("border: None; color: #ff9000; background-color: transparent; font-weight: bold;")
        else:
            self.spectrum_name.setStyleSheet("border: None; color: #ebebeb; background-color: transparent; font-weight: light;")


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=50):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.fig.tight_layout()
        super().__init__(self.fig)