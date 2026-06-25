from __future__ import annotations
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtCore import QSize, Qt
from ui.dataset_ui.DatasetWidget import Ui_DatasetWidget
from ui.dataset_ui.DatasetLabelEntry import Ui_DatasetLabelEntry
from ui.dataset_ui.DatasetSpectrumEntry import Ui_DatasetSpectrumEntry
from dialogs import CreateLabelDialog, CustomMessageDialog, CustomYesNoDialog, RenameLabelDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib import pyplot as plt
from pathlib import Path
import sqlite3
import shutil
import ims

class DatasetPage(QtWidgets.QWidget, Ui_DatasetWidget):
    # Signal definition.
    system_state_changed = QtCore.Signal()

    def __init__(self, project_path: str) -> None   :
        super().__init__()
        self.setupUi(self)

        # Project save path
        self.project_path = Path(project_path)
        # Currently selected label and spectrum.
        self.current_selected_label = None
        self.current_selected_spectrum = None
        self.current_selected_spectrum_path = None
        # The path to the database file.
        self.db_path = self.project_path.parent / "database" / "project_database.db"

        # Defining the scroll area layouts.
        self.scrollArea_labels_Contents.layout().setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.scrollArea_labels_Contents.layout().setSpacing(5)
        self.scrollArea_spectra_Contents.layout().setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.scrollArea_spectra_Contents.layout().setSpacing(5)

        # Button connections.
        self.button_add_label.clicked.connect(self.add_label_dialog)
        # Connect the "add spectra" button.
        self.button_add_spectra.clicked.connect(self.add_spectra_dialog)

        # Canvas plot element.
        self.canvas = PlottingCanvas(self, width=5, height=4, dpi=50)
        # Initialize the plot canvas.
        self.init_plot_canvas()
        # load dataset from database.
        self.load_data()


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
        [Delete | Rename] and is finally added as a widget to the label scroll area and to the database.
        =============================================================================
        :param name: The name of the label.
        =============================================================================
        :return: None.
        """

        # Add the new label to the database.
        conn = sqlite3.connect(self.db_path)
        conn.execute("INSERT OR IGNORE INTO labels (name) VALUES (?)", (name,))
        conn.commit()

        # Create a new instance of the "DatasetLabelEntry" class.
        label = DatasetLabelEntry(name)
        # Connect to the delete/rename/click signals.
        label.delete_signal.connect(self.delete_label_dialog)
        label.rename_signal.connect(self.rename_label_dialog)
        label.click_signal.connect(self.handle_label_click)
        # Insert the new label into the label scroll area as a widget.
        self.scrollArea_labels_Contents.layout().insertWidget(self.scrollArea_labels_Contents.layout().count() - 1, label)
        # Update the label counter.
        self.update_label_count()

        # If this is the first label to be added select it automatically.
        if self.scrollArea_labels_Contents.layout().count() == 2:
            self.current_selected_label = label
            self.handle_label_click(label)

        # Count the number of spectra which are associated for the current label and update the spectra counter.
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM labels WHERE name = ?", (name,))
        result = cursor.fetchone()
        label_id = result[0]
        cursor.execute("SELECT COUNT(*) FROM spectra WHERE label_id = ?", (label_id,))
        spectra_count = cursor.fetchone()[0]
        conn.close()

        label.spectra_counter.setText(f"{spectra_count}x")


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

            # Try to delete the label folder from the "dataset" folder.
            try:
                label_folder = self.project_path.parent / "dataset" / label_name
                if label_folder.exists() and label_folder.is_dir():
                    shutil.rmtree(label_folder)
            except Exception as e:
                print(f"Error while deleting: {e}")

            # If the label was the currently selected label, the spectra scroll area has to be cleared.
            if label_widget == self.current_selected_label:
                self.spectra_container_header.setText("No label selected")
                self.current_selected_label = None
                self.current_selected_spectrum = None
                self.current_selected_spectrum_path = None
                self.clear_canvas()

            # Delete the label widget, remove it from the label scroll area and update the label counter.
            label_widget.deleteLater()
            self.scrollArea_labels_Contents.layout().removeWidget(label_widget)
            self.update_label_count()

            # Remove the label from the labels tabel in the database and remove all spectra entries which are connected
            # to this label.
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM labels WHERE name = ?", (label_name,))
            result = cursor.fetchone()
            label_id = result[0]
            cursor.execute("DELETE FROM labels WHERE id = ?", (label_id,))

            # Check if there are still any spectra left.
            cursor.execute("SELECT COUNT(*) FROM spectra")
            spectra_count = cursor.fetchone()[0]

            if spectra_count == 0:
                cursor.execute("UPDATE system_state SET has_spectra = 0, is_preprocessed = 0, has_peaks = 0, has_consensus_peaks = 0 WHERE id = 1")
            else:
                cursor.execute("UPDATE system_state SET consensus_peaks_changed = 1 WHERE id = 1")

            conn.commit()
            conn.close()

            self.system_state_changed.emit()
            self.update_spectra_list()



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

            # Try to rename the label folder in the dataset folder.
            try:
                base_path = self.project_path.parent / "dataset"
                old_folder = base_path / label_widget.old_label_name
                new_folder = base_path / new_label_name

                # Nur umbenennen, wenn der alte Ordner überhaupt existiert
                if old_folder.exists() and old_folder.is_dir():
                    if not new_folder.exists():
                        old_folder.rename(new_folder)
                    else:
                        print("Error - new label folder already exists!")

            except Exception as e:
                print(f"Error while renaming: {e}")

            # Exchange the label name in the database.
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM labels WHERE name = ?", (label_widget.old_label_name,))
            result = cursor.fetchone()
            label_id = result[0]
            cursor.execute("UPDATE labels SET name = ? WHERE id = ?", (new_label_name, label_id))
            conn.commit()
            conn.close()

            # Display the new label name.
            label_widget.label_name.setText(new_label_name)
            label_widget.old_label_name = new_label_name

            # If the renamed label is the currently selected label, then change also the header of the spectra scroll area.
            if label_widget == self.current_selected_label:
                self.spectra_container_header.setText(new_label_name)


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

        # Dialog box - Does the user want to open .mea files or a folder.
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle("Add Spectra")
        msg_box.setText("Do you want to select individual files or an entire folder?")
        btn_files = msg_box.addButton("Files", QtWidgets.QMessageBox.ActionRole)
        btn_folder = msg_box.addButton("Folder", QtWidgets.QMessageBox.ActionRole)
        btn_cancel = msg_box.addButton("Cancel", QtWidgets.QMessageBox.RejectRole)

        msg_box.exec()
        mea_files = []

        # Open .mea files directly.
        if msg_box.clickedButton() == btn_files:
            paths, _ = QtWidgets.QFileDialog.getOpenFileNames(self,
                                                              caption="Select GC-IMS spectra files",
                                                              dir="",
                                                              filter="GC-IMS File (*.mea)")
            mea_files = paths

        # Open folders.
        elif msg_box.clickedButton() == btn_folder:
            dir_path = QtWidgets.QFileDialog.getExistingDirectory(self,
                                                                  caption="Select GC-IMS spectra folder",
                                                                  dir="")
            if dir_path:
                folder_path = Path(dir_path)

                # Look for .mea files in the selected folder (and subfolders).
                mea_files = [str(p) for p in folder_path.rglob("*.mea")]

                # Folder without .mea files was selected.
                if not mea_files:
                    CustomMessageDialog.show_error(title="No Spectra found",
                                                   message="Could not find any .mea files in the selected directory.",
                                                   parent=self)
                    return

        if mea_files:
            self.add_spectra(paths=mea_files)


    def add_spectra(self,
                    paths: list[str]) -> None:
        """
        This function accepts a list of spectra paths and saves them in the dataset storage dictionary.
        =============================================================================
        :param paths: list of spectra paths.
        =============================================================================
        :return: None.
        """

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM labels WHERE name = ?", (str(self.current_selected_label.label_name.text()),))
        result = cursor.fetchone()
        label_id = result[0]

        cursor.execute("SELECT path FROM spectra WHERE label_id = ?", (label_id,))
        existing_paths = {row[0] for row in cursor.fetchall()}
        spectra_to_insert = []

        for path in paths:
            path_str = str(path)

            if path_str in existing_paths:
                continue

            p = Path(path)
            spectrum_name = str(p.name)
            spectra_to_insert.append((label_id, spectrum_name, str(path)))

        # 3. Batch-Insert in die Datenbank
        if spectra_to_insert:
            cursor.executemany("INSERT INTO spectra (label_id, name, path) VALUES (?, ?, ?)", spectra_to_insert)


        # Update the System state
        cursor.execute("UPDATE system_state SET has_spectra = 1, is_preprocessed = 0, has_peaks = 0, has_consensus_peaks = 0 WHERE id = 1")
        conn.commit()
        conn.close()

        # Send the state changed signal for the sidebar.
        self.system_state_changed.emit()
        # Update the spectra scroll area.
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
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM labels WHERE name = ?", (str(self.current_selected_label.label_name.text()),))
            result = cursor.fetchone()
            label_id = result[0]
            cursor.execute("SELECT path FROM spectra WHERE label_id = ?", (label_id,))
            paths = cursor.fetchall()

            # Walk through all paths from the current label and set up the spectra widgets.
            for row in paths:
                # Get the first element from the SQL result tuple.
                path = row[0]
                # Create a new spectra widget element.
                spectra_widget = DatasetSpectrumEntry(path, spectra_layout.count() + 1)
                # Connect the widget to a delete and click signal.
                spectra_widget.delete_signal.connect(self.delete_spectrum)
                spectra_widget.click_signal.connect(self.plot_spectrum)
                # Insert the widget to the spectra scroll area.
                spectra_layout.insertWidget(spectra_layout.count(), spectra_widget)

                if path == self.current_selected_spectrum_path:
                    spectra_widget.set_active(True)
                    self.current_selected_spectrum = spectra_widget

            # Update the spectra counter inside the label scroll area and the counter beneath the spectra scroll area.
            self.current_selected_label.spectra_counter.setText(f"{len(paths)}x")
            self.label_spectracounter.setText(f"{len(paths)} spectra")

            conn.commit()
            conn.close()
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

            # Try to delete the spectrum folder from the "dataset" folder.
            try:
                label = self.current_selected_label.label_name.text()
                mea_path = Path(spectrum_widget.spectrum_path)
                processed_folder = self.project_path.parent / "dataset" / label / mea_path.stem

                if processed_folder.exists() and processed_folder.is_dir():
                    shutil.rmtree(processed_folder)
            except Exception as e:
                print(f"Error while deleting: {e}")

            # This spectrum is currently selected. This is why the canvas has to be cleared after deletion.
            if self.current_selected_spectrum == spectrum_widget:
                self.clear_canvas()
                self.current_selected_spectrum = None
                self.current_selected_spectrum_path = None

            # Delete the spectrum widget and remove it from the spectra scroll area.
            spectrum_widget.deleteLater()
            self.scrollArea_spectra_Contents.layout().removeWidget(spectrum_widget)
            # Wait for 10 milliseconds and then call the renumber_spectra function to adjust the spectra numbering in the spectra scroll area.
            QtCore.QTimer.singleShot(10, self.renumber_spectra)

            # Remove the spectrum from the database.
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM spectra WHERE path = ?", (spectrum_widget.spectrum_path,))
            result = cursor.fetchone()
            spectrum_id = result[0]
            cursor.execute("DELETE FROM spectra WHERE id = ?", (spectrum_id,))

            # Check if there are still any spectra left.
            cursor.execute("SELECT COUNT(*) FROM spectra")
            spectra_count = cursor.fetchone()[0]

            if spectra_count == 0:
                cursor.execute("UPDATE system_state SET has_spectra = 0, is_preprocessed = 0, has_peaks = 0, has_consensus_peaks = 0 WHERE id = 1")
            else:
                cursor.execute("UPDATE system_state SET consensus_peaks_changed = 1 WHERE id = 1")

            conn.commit()
            conn.close()

            self.system_state_changed.emit()
            self.update_spectra_list()


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


    def load_data(self) -> None:
        """
        This function loads all labels and spectra paths from the database and saves them in dataframes.
        It will also call the add_label function to create all label widgets, as well as the update_spectra_list
        method to create all spectra widgets for the scroll area.
        =============================================================================
        :return: None.
        """

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM labels", )
        label_names = cursor.fetchall()

        # Walk through all labels in the database, get the names and add them as labels.
        for row in label_names:
            # Get the first element from the SQL result tuple.
            label_name = row[0]
            self.add_label(label_name)

        # Handle the spectra widgets in another method.
        self.update_spectra_list()


    def init_plot_canvas(self) -> None:
        """
        This function initializes the plot canvas and setups the basic settings like background colors, font sizes ect.
        =============================================================================
        :return: None.
        """

        # Set the figure and exes background colors of the plot canvas.
        self.canvas.fig.set_facecolor('#191919')
        self.canvas.axes.set_facecolor('#191919')

        # Font size definitions for the plot.
        plt.rcParams.update({
            'font.size': 14,
            'axes.titlesize': 26,
            'axes.labelsize': 20,
            'xtick.labelsize': 16,
            'ytick.labelsize': 16
        })

        # Set the color for the spines [axes boarder].
        for spine in self.canvas.axes.spines.values():
            spine.set_edgecolor('#191919')

        # Create a vertical layout widget for the canvas.
        canvas_layout = QtWidgets.QVBoxLayout(self.preview_image)
        canvas_layout.addWidget(self.canvas)

        # Create a toolbar at the bottom of the canvas and set the style.
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.setStyleSheet("""
                            QToolButton {
                                background-color: transparent;
                                border: 1px solid transparent;
                                border-radius: 4px;
                                margin: 2px;
                                padding: 2px;
                            }
                            QToolButton:hover {
                                background-color: #3d3d3d;
                                border: 1px solid #555555;
                            }
                            QToolButton:checked {
                                background-color: #af6300; 
                                border: 1px solid #ffffff;
                            }
                        """)

        # Remove some of the toolbar buttons which are not needed.
        toolbar_actions = self.toolbar.actions()
        for action in toolbar_actions:
            if any(word in action.text() for word in ["Subplots", "Back", "Forward", "Customize"]):
                self.toolbar.removeAction(action)
        # Set the toolbar icons size and resize the toolbar height.
        self.toolbar.setIconSize(QSize(36,36))
        self.toolbar.setFixedHeight(50)

        # Change the toolbar button hover mouse icon.
        for button in self.toolbar.findChildren(QtWidgets.QToolButton):
            button.setCursor(Qt.CursorShape.PointingHandCursor)

        # Hide the toolbar during the setup and add the toolbar to the canvas.
        self.toolbar.hide()
        canvas_layout.addWidget(self.toolbar)

        # remove the ticks from the axis [only during the setup].
        self.canvas.axes.set_xticks([])
        self.canvas.axes.set_yticks([])
        # Draw the canvas.
        self.canvas.draw()


    def plot_spectrum(self,
                      spectrum_widget: DatasetSpectrumEntry) -> None:
        """
        This function loads the .mea file of one spectrum and plots it to the canvas.
        =============================================================================
        :param spectrum_widget: Widget of the currently selected spectrum in the spectra scroll area.
        =============================================================================
        :return: None
        """

        # Deselect the last selected spectrum and remove the highlight effect from the spectra scroll area.
        if self.current_selected_spectrum:
            self.current_selected_spectrum.set_active(False)

        # Set the highlight to the currently clicked spectrum.
        self.current_selected_spectrum = spectrum_widget
        self.current_selected_spectrum.set_active(True)
        self.current_selected_spectrum_path = spectrum_widget.spectrum_path

        # Set a dark background for the plot.
        plt.style.use('dark_background')

        # Load the spectrum from the .mea file and adjust the drift time coordinates in relation to the RIP.
        spectrum = ims.Spectrum.read_mea(spectrum_widget.spectrum_path)
        spectrum.riprel()

        # Clear the axes and set their colors.
        self.canvas.fig.patch.set_facecolor('#191919')
        self.canvas.axes.clear()
        self.canvas.axes.set_facecolor('#191919')

        # Draw the spectrum to the canvas.
        self.canvas.axes.imshow(
            spectrum.values,
            origin="lower",
            aspect="auto",
            cmap="RdBu_r",
            vmin=30,
            vmax=400,
            extent=(
                min(spectrum.drift_time),
                max(spectrum.drift_time),
                min(spectrum.ret_time),
                max(spectrum.ret_time),
            ),
        )

        # Set the axis labels.
        self.canvas.axes.set_xlabel("Drift Time [ms]", labelpad=15)
        self.canvas.axes.set_ylabel("Retention Time [s]", labelpad=15)
        # Adjust the visual spacing of the canvas.
        self.canvas.fig.subplots_adjust(left=0.069, bottom=0.058, right=0.094, top=0.995)
        # Show the toolbar.
        self.toolbar.show()

        # Apply a tight layout and draw the canvas.
        self.canvas.fig.tight_layout()
        self.canvas.draw()


    def clear_canvas(self) -> None:
        """
        This function is called when a label or spectrum is deleted which is currently displayed on the canvas.
        This will reset the canvas to its default empty state.
        =============================================================================
        :return: None
        """

        self.toolbar.hide()
        self.canvas.axes.clear()
        self.canvas.axes.set_xticks([])
        self.canvas.axes.set_yticks([])
        self.canvas.draw()


class DatasetLabelEntry(QtWidgets.QLabel, Ui_DatasetLabelEntry):
    # Signal definitions
    delete_signal = QtCore.Signal(object)
    rename_signal = QtCore.Signal(object)
    click_signal = QtCore.Signal(object)

    def __init__(self,
                 label_name: str,
                 count: int = 0) -> None:

        super().__init__()
        self.setupUi(self)

        # Set label and spectra counter text.
        self.label_name.setText(label_name.strip())
        self.spectra_counter.setText(f"{count}x")
        # Save the current label name [important for renaming].
        self.old_label_name = label_name.strip()

        # Connect buttons and emit signals if clicked.
        self.button_labelDelete.clicked.connect(lambda: self.delete_signal.emit(self))
        self.button_labelRename.clicked.connect(lambda: self.rename_signal.emit(self))

        # Hover effects for buttons.
        self.button_labelRename.enterEvent = lambda e: self.button_hover_effect(self.button_labelRename, 'edit_orange', True)
        self.button_labelRename.leaveEvent = lambda e: self.button_hover_effect(self.button_labelRename, 'edit_grey', False)
        self.button_labelDelete.enterEvent = lambda e: self.button_hover_effect(self.button_labelDelete, 'delete_magenta',True)
        self.button_labelDelete.leaveEvent = lambda e: self.button_hover_effect(self.button_labelDelete, 'delete_grey',False)


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


    def mousePressEvent(self,
                        event: QtGui.QMouseEvent) -> None:
        """
        This function overrides the mousePressEvent function and emits the "click_signal". This signal is fetched
        by the dataset page and takes care of highlighting the label widget and connects this label to the spectra
        scroll area to display spectra of this label.
        =============================================================================
        :param event: Mouse event object.
        =============================================================================
        :return: None.
        """

        # Check if the label widget is clicked with the left mouse button and emits the click signal.
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.click_signal.emit(self)


    def set_active(self,
                   active: bool) -> None:
        """
        This function is called when a label widget is clicked and changes the label stylesheet to highlight the currently
        selected label in the label scroll area.
        =============================================================================
        :param active: True if a label widget is selected, False if a label widget is deselected.
        =============================================================================
        :return: None.
        """

        # Sets the label stylesheet depending on the state [active = currently selected | not active = not selected]
        if active:
            self.label_name.setStyleSheet("border: None; color: #ff9000; background-color: transparent; font-weight: bold;")
            self.spectra_counter.setStyleSheet("border: None; color: #ff9000; background-color: transparent; font-weight: bold;")
        else:
            self.label_name.setStyleSheet("border: None; color: #ebebeb; background-color: transparent; font-weight: light;")
            self.spectra_counter.setStyleSheet("border: None; color: #ebebeb; background-color: transparent; font-weight: light;")


class DatasetSpectrumEntry(QtWidgets.QWidget, Ui_DatasetSpectrumEntry):
    # Signal definitions
    delete_signal = QtCore.Signal(object)
    click_signal = QtCore.Signal(object)

    def __init__(self, path:str, number: int):
        super().__init__()
        self.setupUi(self)

        # Make the background styleable [sometimes needed if a widget is not complex enough].
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)

        # Set some basic variables and texts.
        self.spectrum_path = path
        self.spectrum_name.setText(f"{number} - {Path(self.spectrum_path).parent.name}/{Path(self.spectrum_path).stem}")
        # Hover effects for buttons.
        self.button_spectrumDelete.enterEvent = lambda e: self.button_spectrumDelete.setIcon(QtGui.QIcon(r':/ui/_pics/icons/delete_magenta.png'))
        self.button_spectrumDelete.leaveEvent = lambda e: self.button_spectrumDelete.setIcon(QtGui.QIcon(r':/ui/_pics/icons/delete_grey.png'))

        # Connect the delete button
        self.button_spectrumDelete.clicked.connect(lambda: self.delete_signal.emit(self))


    def mousePressEvent(self,
                        event: QtGui.QMouseEvent) -> None:
        """
        This function overrides the mousePressEvent function and emits the "click_signal". This signal is fetched
        by the dataset page and takes care of highlighting the spectra widget and displays the selected spectrum in
        the plot canvas.
        =============================================================================
        :param event: Mouse event object.
        =============================================================================
        :return: None.
        """

        # Check if the spectra widget is clicked with the left mouse button and emits the click signal.
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.click_signal.emit(self)


    def set_active(self,
                   active: bool) -> None:
        """
        This function is called when a spectra widget is clicked and changes the spectra stylesheet to highlight the currently
        selected spectrum in the spectra scroll area.
        =============================================================================
        :param active: True if a spectrum widget is selected, False if a spectrum widget is deselected.
        =============================================================================
        :return: None.
        """

        # Sets the spectrum stylesheet depending on the state [active = currently selected | not active = not selected]
        if active:
            self.spectrum_name.setStyleSheet("border: None; color: #ff9000; background-color: transparent; font-weight: bold;")
        else:
            self.spectrum_name.setStyleSheet("border: None; color: #ebebeb; background-color: transparent; font-weight: light;")


class PlottingCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=50):
        # Basic settings for the plot canvas.
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.fig.tight_layout()
        super().__init__(self.fig)