from __future__ import annotations
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtGui import QDoubleValidator
from PySide6.QtCore import QSize, Qt, QTimer, QLocale, Signal
from dialogs import CustomYesNoDialog, CustomProgressDialog, CustomTwoChoiceDialog
from ui.preprocessing_ui.PreprocessingWidget import Ui_PreprocessingWidget
from ui.preprocessing_ui.DatasetSubEntry import Ui_DatasetSubEntry
from ui.preprocessing_ui.DatasetMainEntry import Ui_DatasetMainEntry
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib import pyplot as plt
from collections import defaultdict
from pathlib import Path
import sqlite3
import shutil
import ims


class PreprocessingPage(QtWidgets.QWidget, Ui_PreprocessingWidget):
    # Signal definition.
    system_state_changed = QtCore.Signal()

    def __init__(self, project_path: str):
        super().__init__()
        self.setupUi(self)

        # Project save path
        self.project_path = Path(project_path)
        # Currently selected spectrum.
        self.current_selected_spectrum = None
        self.selected_spectrum_name = None
        self.selected_label_name = None
        # The path to the database file.
        self.db_path = self.project_path.parent / "database" / "project_database.db"

        # Defining the scroll area layouts.
        self.scrollArea_dataset_Contents.layout().setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.scrollArea_dataset_Contents.layout().setSpacing(5)
        self.scrollArea_dataset.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        # Validators for the retentiontime input fields.
        retention_validator = QDoubleValidator(0, 1200, 0)
        retention_validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        self.lineEdit_retention_start_cut.setValidator(retention_validator)
        self.lineEdit_retention_end_cut.setValidator(retention_validator)
        # Validators for the drifttime input fields.
        drift_validator = QDoubleValidator(0.0, 3.0, 3)
        drift_validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        drift_validator.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        self.lineEdit_drift_start_cut.setValidator(drift_validator)
        self.lineEdit_drift_end_cut.setValidator(drift_validator)
        # Defines a timer so that changes in the drift- and retentionttime fields are only checked every x milliseconds.
        self.cut_timer = QTimer()
        self.cut_timer.setSingleShot(True)
        self.cut_timer.timeout.connect(self.update_region_of_interest)
        self.lineEdit_retention_start_cut.textChanged.connect(lambda: self.cut_timer.start(500))
        self.lineEdit_retention_end_cut.textChanged.connect(lambda: self.cut_timer.start(500))
        self.lineEdit_drift_start_cut.textChanged.connect(lambda: self.cut_timer.start(500))
        self.lineEdit_drift_end_cut.textChanged.connect(lambda: self.cut_timer.start(500))
        self.lineEdit_drift_start_cut.textChanged.connect(self.check_comma)
        self.lineEdit_drift_end_cut.textChanged.connect(self.check_comma)
        self.lineEdit_retention_start_cut.textChanged.connect(self.check_comma)
        self.lineEdit_retention_end_cut.textChanged.connect(self.check_comma)

        # Toggle option of the plotting canvas -> Fullscreen vs region of interest.
        self.canvas_fullscreen = True
        self.pushButton_toggle_canvas_area.clicked.connect(self.toggle_canvas)
        # Canvas plot element.
        self.canvas = PlottingCanvas(self, width=5, height=4, dpi=50)
        # Initialize the plot canvas.
        self.init_plot_canvas()

        # Connect the button
        self.pushButton_start_processing.clicked.connect(self.start_preprocessing)
        # load dataset from the database.
        self.load_data()
        # Check if any spectra are already processed.
        self.check_processed_spectra()


    def showEvent(self, event) -> None:
        """
        This function is called every time the user enters this page.
        =============================================================================
        :param event: The page display event.
        =============================================================================
        :return: None
        """

        super().showEvent(event)
        self.load_data()
        self.check_processed_spectra()


    def save_data(self):
        """
        This function saves the state of the currently set region of interest.
        It is saved to the settings table in the database.
        =============================================================================
        :return: None.
        """

        region_of_interest = { "rt_start": self.lineEdit_retention_start_cut.text() or 0,
                                "rt_end": self.lineEdit_retention_end_cut.text() or 0,
                                "dt_start": self.lineEdit_drift_start_cut.text() or 0,
                                "dt_end": self.lineEdit_drift_end_cut.text() or 0}

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
                       UPDATE settings 
                       SET retention_start_cut = ?,
                           retention_end_cut   = ?,
                           drift_start_cut     = ?,
                           drift_end_cut       = ?
                       WHERE id = 1
                       ''', (region_of_interest['rt_start'],
                             region_of_interest['rt_end'],
                             region_of_interest['dt_start'],
                             region_of_interest['dt_end']))

        conn.commit()
        conn.close()


    def load_data(self):
        """
        This function is called every time the user enters this page. It reloads all label and spectra of the dataset,
        recreates the widgets of the scroll area and sets the region of interest values into the input fields.
        =============================================================================
        :return: None
        """

        self.current_selected_spectrum = None
        self.label_preview.setText("Spectrum preview")

        # Clear the canvas.
        self.clear_canvas()

        # Remove all widgets from the scroll area to clear it.
        layout = self.scrollArea_dataset_Contents.layout()
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            widget = item.widget()

            # Check if the widget is an instnace of the DatasetMainEntry or DatasetSubEntry, if so remove it from the
            # layout and delete it.
            if widget is not None and isinstance(widget, DatasetMainEntry) or isinstance(widget, DatasetSubEntry):
                layout.removeWidget(widget)
                widget.setParent(None)
                widget.deleteLater()

        # Connect to the database.
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM labels", )
        labels_data = cursor.fetchall()

        # Walk through all labels in the database, get the names and add them as labels.
        for row in labels_data:
            # Get the label name of the current row.
            label_name = row['name']
            self.add_label(label_name)

        # Load and set the region of interest values.
        cursor.execute("SELECT * FROM settings WHERE id = ?", (1,))
        roi_data = cursor.fetchone()

        self.lineEdit_retention_start_cut.setText(str(roi_data['retention_start_cut']))
        self.lineEdit_retention_end_cut.setText(str(roi_data['retention_end_cut']))
        self.lineEdit_drift_start_cut.setText(str(roi_data['drift_start_cut']))
        self.lineEdit_drift_end_cut.setText(str(roi_data['drift_end_cut']))


    def add_label(self,
                  name: str) -> None:
        """
        This function is called when a label is added as a widget to the scroll area and to the dataset storage dictionary.
        =============================================================================
        :param name: The name of the label.
        =============================================================================
        :return: None.
        """

        # Create a new instance of the "DatasetMainEntry" class.
        label = DatasetMainEntry(name)
        # Connect to the click signals.
        label.click_signal.connect(self.handle_label_click)
        # Insert the new label into the scroll area as a main widget.
        self.scrollArea_dataset_Contents.layout().insertWidget(self.scrollArea_dataset_Contents.layout().count() - 1, label)
        self.add_spectra(label)
        # Set this label as active.
        if self.selected_label_name == label.label_name.text():
            self.handle_label_click(label)


    def add_spectra(self,
                    label_widget: DatasetMainEntry) -> None:
        """
        This function is called when a label was added as a widget to the scroll area. The label is here extended
        by one sub widget for each spectrum associated with this label.
        =============================================================================
        :param label_widget: The last label which was added.
        =============================================================================
        :return: None.
        """

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM labels WHERE name = ?", (label_widget.label_name.text(),))
        result = cursor.fetchone()
        cursor.execute("SELECT id, path FROM spectra WHERE label_id = ?", (result['id'],))
        spectra_rows = cursor.fetchall()
        conn.close()

        # Loop through all spectra and add them as a widget to the scroll area.
        for index, row in enumerate(spectra_rows):
            path = row['path']

            spectrum = DatasetSubEntry(path=path,
                                       index=index,
                                       parent=label_widget,
                                       spectrum_id=row['id'],
                                       page='preprocessing')

            self.scrollArea_dataset_Contents.layout().insertWidget(self.scrollArea_dataset_Contents.layout().count() - 1, spectrum)
            spectrum.click_signal.connect(self.handle_spectrum_click)
            spectrum.hide()

            if self.selected_spectrum_name == spectrum.label_name.text():
                self.handle_spectrum_click(spectrum)
                self.label_preview.setText(f"{label_widget.label_name.text()} - {self.selected_spectrum_name}")


    def handle_label_click(self,
                           label_widget: DatasetMainEntry) -> None:
        """
        This function is handling the "label clicked" event. If a label widget is clicked inside the scroll area
        this function is called. The selected label widget is expanded or collapsed.
        =============================================================================
        :param label_widget: The label widget which was clicked in the scroll area.
        =============================================================================
        :return: None.
        """

        # Collapse the clicked widget.
        if label_widget.extended:
            label_widget.extend_label(False)

            # Loop through all spectra widgets of the clicked label and hide them in the scroll area.
            for index in range(self.scrollArea_dataset_Contents.layout().count()):
                item = self.scrollArea_dataset_Contents.layout().itemAt(index)
                spectrum_widget = item.widget()
                if isinstance(spectrum_widget, DatasetSubEntry):
                    if spectrum_widget.parent == label_widget:
                        spectrum_widget.hide()

            # Reset the selected label name variable.
            self.selected_label_name = None

        # Extend the clicked widget.
        else:
            label_widget.extend_label(True)

            # Loop through all spectra widget of the clickd label and show them in the scoll area.
            for index in range(self.scrollArea_dataset_Contents.layout().count()):
                item = self.scrollArea_dataset_Contents.layout().itemAt(index)
                spectrum_widget = item.widget()
                if isinstance(spectrum_widget, DatasetSubEntry):
                    if spectrum_widget.parent == label_widget:
                        spectrum_widget.show()

            self.selected_label_name = label_widget.label_name.text()


    def init_plot_canvas(self) -> None:
        """
        This function initializes the plot canvas and setups the basic settings like background colors, font sizes ect.
        =============================================================================
        :return: None.
        """

        # Set the figure and axes background colors of the plot canvas.
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
                      spectrum_widget: DatasetSubEntry) -> None:
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


    def update_region_of_interest(self) -> None:
        """
        This function updates the region of interest of the canvas. This function is called when the user entered
        a region of interest value for the drift- or retentiontime.
        Each value is displayed as a red dashed line on the canvas and highlights the currently set region of interest.
        Additionally, this function takes care of the toggle button underneath the canvas which lets the user switch
        between the fullscreen and cropped canvas.
        =============================================================================
        :return: None.
        """

        # Clear the canvas of all region of interest lines.
        for line in getattr(self, 'roi_lines', []):
            line.remove()
        self.roi_lines = []

        # Get the region of interest values from the input fields.
        r_start = float(self.lineEdit_retention_start_cut.text() or 0)
        r_end = float(self.lineEdit_retention_end_cut.text() or 0)
        d_start = float(self.lineEdit_drift_start_cut.text() or 0)
        d_end = float(self.lineEdit_drift_end_cut.text() or 0)

        # Save the values
        self.save_data()

        # Define red dashed lines of each region of interest value.
        ax = self.canvas.axes
        style = {'color': '#da05ab', 'linestyle': '--', 'linewidth': 3, 'alpha': 0.8}

        if r_start > 0:
            self.roi_lines.append(ax.axhline(y=r_start, **style))
        if r_end > 0:
            self.roi_lines.append(ax.axhline(y=r_end, **style))
        if d_start > 0:
            self.roi_lines.append(ax.axvline(x=d_start, **style))
        if d_end > 0:
            self.roi_lines.append(ax.axvline(x=d_end, **style))

        # Enable the toggle canvas button to switch between fullscreen and region of interest.
        if (r_start > 0 and r_end > 0 and d_start > 0 and d_end > 0) or not self.canvas_fullscreen:
            self.pushButton_toggle_canvas_area.setEnabled(True)
            self.pushButton_toggle_canvas_area.setStyleSheet(f"""
                                                                QPushButton {{
                                                                    border: 1px solid #ff9000;
                                                                    background-color: #232323; 
                                                                    color: #ff9000;
                                                                    border-radius: 10px;
                                                                }}
                                                                
                                                                QPushButton:hover {{
                                                                    background-color: #131313;
                                                                }}
                                                            """)

        else:
            self.pushButton_toggle_canvas_area.setEnabled(False)
            self.pushButton_toggle_canvas_area.setStyleSheet(f"""
                                                                QPushButton {{
                                                                    border: 1px solid #666666;
                                                                    background-color: #232323; 
                                                                    color: #666666;
                                                                    border-radius: 10px;
                                                                }}

                                                                QPushButton:hover {{
                                                                    background-color: #131313;
                                                                }}
                                                            """)

        # Show only the region of interest area.
        if not self.canvas_fullscreen:
            ax = self.canvas.axes
            ax.set_xlim(d_start, d_end)
            ax.set_ylim(r_start, r_end)

        self.canvas.draw()


    def check_comma(self) -> None:
        """
        This function checks if the user entered a ',' into the region of interest input fields and replaces
        the ',' with a '.'.
        =============================================================================
        :return: None.
        """

        input_field = self.sender()
        text = input_field.text()
        if "," in text:
            pos = input_field.cursorPosition()
            input_field.setText(text.replace(",", "."))
            input_field.setCursorPosition(pos)


    def toggle_canvas(self):
        """
        This function is called when the 'toggle canvas button' is pressed and handels the change of view of
        the canvas. Show fullscreen or show the cropped region.
        =============================================================================
        :return: None.
        """
        
        if self.canvas_fullscreen:
            self.canvas_fullscreen = False
            self.zoom_to_cut()
            self.pushButton_toggle_canvas_area.setText("Show full spectrum")
        else:
            self.canvas_fullscreen = True
            self.reset_zoom()
            self.pushButton_toggle_canvas_area.setText("Show cutted spectrum")


    def handle_spectrum_click(self,
                              spectrum_widget: DatasetSubEntry) -> None:
        """
        This function is called when a spectrum in the scroll area is clicked. It displays the selected spectrum to the
        canvas and shows either the fullscreen or the cropped region of interest.
        =============================================================================
        :param spectrum_widget: The widget of the clicked spectrum.
        =============================================================================
        :return: None.
        """

        # Plot the clicked spectrum to the canvas.
        self.plot_spectrum(spectrum_widget)
        self.selected_spectrum_name = spectrum_widget.label_name.text()
        self.label_preview.setText(f"{spectrum_widget.parent.label_name.text()} - {self.selected_spectrum_name}")

        # If in fullscreen mode show the complete canvas, otheriese show the cropped region of interest.
        if self.canvas_fullscreen:
            self.reset_zoom()
        else:
            d_start = float(self.lineEdit_drift_start_cut.text() or 0)
            d_end = float(self.lineEdit_drift_end_cut.text() or 0)
            r_start = float(self.lineEdit_retention_start_cut.text() or 0)
            r_end = float(self.lineEdit_retention_end_cut.text() or 0)

            if r_start > 0 and r_end > 0 and d_start > 0 and d_end > 0:
                self.zoom_to_cut()
            else:
                self.reset_zoom()


    def zoom_to_cut(self) -> None:
        """
        This function loads the region of interest values which are set by the user in the input fields and
        adjusts the axes of the canvas to these values [It zooms the canvas within the region of interest].
        =============================================================================
        :return: None.
        """

        # Get the region of interest values the user used in the input fields.
        d_start = float(self.lineEdit_drift_start_cut.text())
        d_end = float(self.lineEdit_drift_end_cut.text())
        r_start = float(self.lineEdit_retention_start_cut.text())
        r_end = float(self.lineEdit_retention_end_cut.text())

        # Set the axis limitations
        ax = self.canvas.axes
        ax.set_xlim(d_start, d_end)
        ax.set_ylim(r_start, r_end)

        # Update the canvas.
        self.update_region_of_interest()


    def reset_zoom(self) -> None:
        """
        This function removes the region of interest zoom and shows the fullscreen canvas.
        =============================================================================
        :return: None.
        """

        ax = self.canvas.axes
        ax.autoscale(enable=True, axis='both', tight=True)
        self.update_region_of_interest()


    def start_preprocessing(self) -> None:
        """
        This function starts the preprocessing of the spectra and is called upon clicking the "start preprocessing"
        button. This function creates a custom dialog on a thread and displays it to the user until all spectra have
        been processed.

        Before starting preprocessing this function looks if and how many spectra are already processed.
        The user may be prompted to choose between continuing or restarting the preprocessing.
        =============================================================================
        :return: None.
        """

        # Path where the dataset is saved.
        path = self.project_path.parent / "dataset"
        # Number of processed spectra.
        processed_spectra = 0

        # The total number of spectra of the dataset.
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM spectra",)
        total_spectra = cursor.fetchone()[0]
        conn.close()

        # Check if the dataset path exists. If so look for already processed spectra which are saved as .hdf5 files.
        if path.exists():
            # Find all hdf5 files in the dataset directory and all subdirectories.
            hdf5_files = list(path.rglob("*.hdf5"))
            processed_spectra += len(hdf5_files)

        # Normally all spectra a processed.
        process_all = True

        # Show a dialog to the user that there are already saved spectra files which were processed.
        # The user can choose between continuing with the remaining unsaved spectra or restart and process all spectra.
        if total_spectra > 0 and processed_spectra > 0 and total_spectra != processed_spectra:
            dialog = CustomTwoChoiceDialog(title="Which spectra do you want to process?",
                                           message="It looks like some of the spectra are already processed. Do you want to continue with"
                                                   " the remaining spectra, or do you want to restart and process all spectra?",
                                           type="warning",
                                           button_a_label="Continue",
                                           button_b_label="Restart",
                                           parent=self)

            # Get the dialog results.
            dialog_result = dialog.exec_()
            # Continue with remining spectra.
            if dialog_result == 1:
                process_all = False
            # Restart with all spectra.
            elif dialog_result == 2:
                process_all = True
            # The user canceled.
            else:
                return

        # Notify the user that all spectra have already been processed and ask if the user wants to process the spectra again.
        elif total_spectra > 0 and processed_spectra > 0 and total_spectra == processed_spectra:
            dialog = CustomYesNoDialog(title="Override processed spectra?",
                                       message="All spectare are already processed. Do you want to restart the preprocessing and override the processed spectra?",
                                       type="warning",
                                       parent=self)

            if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
                process_all = True
            else:
                return

        # Open the progress dialog which informs the user about the current state of the preprocessing.
        self.loading_dialog = CustomProgressDialog(title="Preprocessing...", header="Dataset preprocessing")
        # Reset the start time.
        self.loading_dialog.start_time = None
        self.loading_dialog.show()

        # Create a thread and worker for the progress dialog.
        self.thread = QtCore.QThread()
        self.worker = PreprocessingWorker(path=self.project_path,
                                          db_path=self.db_path,
                                          drift_cut=(self.lineEdit_drift_start_cut.text(), self.lineEdit_drift_end_cut.text()),
                                          retention_cut=(self.lineEdit_retention_start_cut.text(), self.lineEdit_retention_end_cut.text()),
                                          process_all=process_all)

        self.worker.moveToThread(self.thread)

        # Connect some signals to the worker and thread.
        self.thread.started.connect(self.worker.run)
        self.worker.progress_update.connect(self.loading_dialog.update_progress)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.loading_dialog.accept)
        self.worker.finished.connect(self.check_processed_spectra)
        self.loading_dialog.button_no.clicked.connect(self.worker.stop, type=QtCore.Qt.DirectConnection)
        self.thread.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # Start the thread.
        self.thread.start()


    def check_processed_spectra(self) -> None:
        """
        This function updates a label and notifies the user about the number of processed spectra.
        - It will either show the message "All spectra processed" if all spectra were successfully processed.
        - Or it will notify the user that some spectra aren't processed yet -> "x unprocessed spectra"
        =============================================================================
        :return: None.
        """

        # Set the path to the saved dataset files.
        path = self.project_path.parent / "dataset"
        processed_spectra = 0

        # Get the total number of spectra which are in the dataset.
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM spectra", )
        total_spectra = cursor.fetchone()[0]

        # Check if the dataset folder exists and if so check how many spectra are already processed.
        if path.exists():
            hdf5_files = list(path.rglob("*.hdf5"))
            processed_spectra += len(hdf5_files)

        # Dont show the user notification of non spectra are processed.
        if processed_spectra == 0:
            self.label_process_info.hide()
            # Update the system state.
            cursor.execute("UPDATE system_state SET is_preprocessed = 0 WHERE id = 1")
            conn.commit()
            self.system_state_changed.emit()

        # Show this info if all spectra are processed.
        elif processed_spectra == total_spectra:
            self.label_process_info.show()
            self.label_process_info.setText("All spectra processed")
            self.label_process_info.setStyleSheet(f"""
                                                        border: 1.5px dashed #00eaff;
                                                        background-color: #232323; 
                                                        color: #00eaff;
                                                        margin-bottom: 10px;
                                                """)
            # Update the system state.
            cursor.execute("UPDATE system_state SET is_preprocessed = 1 WHERE id = 1")
            conn.commit()
            self.system_state_changed.emit()

        # Show this info only when a subset of all spectra are processed.
        else:
            new_spectra_count = total_spectra - processed_spectra
            self.label_process_info.show()
            if new_spectra_count == 1:
                self.label_process_info.setText(f"{new_spectra_count} unprocessed spectrum")
            else:
                self.label_process_info.setText(f"{new_spectra_count} unprocessed spectra")
            self.label_process_info.setStyleSheet(f"""
                                                       border: 1.5px dashed #ff00c6;
                                                       background-color: #232323;
                                                       color: #ff00c6;
                                                       margin-bottom: 10px;
                                               """)

            # Update the system state.
            cursor.execute("UPDATE system_state SET is_preprocessed = 0, has_peaks = 0, has_consensus_peaks = 0 WHERE id = 1")
            conn.commit()
            self.system_state_changed.emit()

        conn.close()


class DatasetMainEntry(QtWidgets.QLabel, Ui_DatasetMainEntry):
    # Signal definitions.
    click_signal = QtCore.Signal(object)

    def __init__(self, label_name: str) -> None:
        super().__init__()
        self.setupUi(self)

        # Set label and spectra counter text.
        self.label_name.setText(label_name.strip())
        # Is the label collapsed? [True = Spectra are hidden | False = Spectra are displayed]
        self.extended = False
        # Enable event propagation for the button [The button itself has no effect and is now ignored when clicked].
        self.button_open_close.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)


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


    def extend_label(self,
                     extend: bool) -> None:
        """
        This function is called when a label widget is clicked and changes the label stylesheet to highlight the currently
        selected label in the label scroll area.
        =============================================================================
        :param extend: True if a label widget is selected, False if a label widget is deselected.
        =============================================================================
        :return: None.
        """

        if extend:
            self.button_open_close.setIcon(QtGui.QIcon(f':/ui/_pics/icons/chevron_down_white.png'))
            self.extended = True
            self.label_name.setStyleSheet("border: None; color: #ff9000; background-color: transparent; font-weight: bold;")
        else:
            self.button_open_close.setIcon(QtGui.QIcon(f':/ui/_pics/icons/chevron_right_white.png'))
            self.extended = False
            self.label_name.setStyleSheet("border: None; color: #ebebeb; background-color: transparent; font-weight: light;")




class DatasetSubEntry(QtWidgets.QWidget, Ui_DatasetSubEntry):
    # Signal definitions
    click_signal = QtCore.Signal(object)

    def __init__(self, path: str, index: int, parent: DatasetMainEntry, spectrum_id: int, page: str):
        super().__init__()
        self.setupUi(self)

        if page == 'preprocessing':
            # Hide the peak counter for the preprocessing page.
            self.label_peak_counter.hide()
        elif page == 'peak_explorer':
            # Show the peak counter for the peak explorer page.
            self.label_peak_counter.show()

        # The page where this widget belongs to.
        self.page = page
        # Parent entry widget.
        self.parent = parent
        # Spectrum save path.
        self.spectrum_path = path
        # Spectrum id in the database.
        self.spectrum_id = spectrum_id
        # Spectrum name.
        self.label_name.setText(f"{index+1} - {Path(self.spectrum_path).parent.name}/{Path(self.spectrum_path).stem}")
        # Make the background styleable [sometimes needed if a widget is not complex enough].
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)


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
            self.label_name.setStyleSheet("border: None; color: #ff9000; background-color: transparent; font-weight: bold;")
            if self.page == 'peak_explorer':
                self.label_peak_counter.setStyleSheet("border: None; color: #ff9000; background-color: transparent; font-weight: bold;")
        else:
            self.label_name.setStyleSheet("border: None; color: #ebebeb; background-color: transparent; font-weight: light;")
            if self.page == 'peak_explorer':
                self.label_peak_counter.setStyleSheet("border: None; color: #ebebeb; background-color: transparent; font-weight: light;")



class PlottingCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=50):
        # Basic settings for the plot canvas.
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.fig.tight_layout()
        super().__init__(self.fig)



class PreprocessingWorker(QtCore.QObject):
    # Signal definitions.
    finished = Signal()
    progress_update = Signal(int, int)

    def __init__(self,
                 path: Path,
                 db_path: Path,
                 drift_cut: tuple,
                 retention_cut: tuple,
                 process_all: bool):

        super().__init__()
        self.drift_cut = drift_cut
        self.retention_cut = retention_cut
        self.project_path = path.parent
        self.process_all = process_all
        self.db_path = db_path
        # Worker stopped signal [The user has canceled the preprocessing].
        self.worker_stopped = False

    @QtCore.Slot()
    def stop(self):
        self.worker_stopped = True

    def run(self):
        """
        this function overrides the run function and is called when the preprocessing thread has started.
        This function takes care of loading the spectra .mea files and processes them by the following:
        - Set the drifttime coordinate at the RIP to 0.
        - Removes background noise.
        - Cuts the spectrum to the region of interest.
        - Applies a smoothing filter [Savitzky-Golay].
        - Removes negative intensities.
        - Saves the spectrum as a hdf5 file.
        =============================================================================
        :return: None.
        """

        # Create a new dataset list of labels and spectra which should be preprocessed.
        used_dataset = defaultdict(list)
        spectra_to_process = 0

        # Connect to the database and get all labels.
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM labels",)
        label_data = cursor.fetchall()

        # Walk through all labels in the database.
        for label in label_data:
            cursor.execute("SELECT id, path, name FROM spectra WHERE label_id = ?", (label['id'],))
            spectra_paths = cursor.fetchall()

            for spectrum_path_data in spectra_paths:
                spectrum_path = spectrum_path_data['path']
                # Get the spectrum name.
                spec_name = Path(spectrum_path_data['name']).stem
                # Set the folder where the processed spectrum will be saved.
                target_folder = self.project_path / "dataset" / label['name'] / spec_name
                target_file = target_folder / f"{spec_name}.hdf5"

                # Add the spectrum to the used dataset list for processing.
                if self.process_all or not target_file.exists():
                    # Remove the already saved hdf5 file if the user wants to process this spectrum again.
                    if self.process_all and target_file.exists():
                        try:
                            shutil.rmtree(target_folder)
                        except Exception as e:
                            print(f"Error while deleting {target_file}: {e}")

                    # Add the label to the used dataset.
                    if label['name'] not in used_dataset:
                        used_dataset[label['name']] = []

                    # Add the spectrum to the used dataset.
                    used_dataset[label['name']].append(spectrum_path)
                    spectra_to_process += 1

        # The number of processed spectra during this preprocessing.
        processed_spectra_counter = 0

        # Looks like there are no spectra to work with ...
        if spectra_to_process == 0:
            self.finished.emit()
            return

        # Loop through all labels and spectra of the used dataset.
        for label, spectra_paths in used_dataset.items():
            for spectrum_path in spectra_paths:

                # Check during each loop if the user wants so cancel the processing.
                QtCore.QCoreApplication.processEvents()
                if self.worker_stopped:
                    self.finished.emit()
                    return

                # Load the ims spectrum and create a copy.
                spec = ims.Spectrum.read_mea(spectrum_path).binning()
                spectrum = spec.copy()
                # Set the drifttime coordinate of the RIP to 0.
                spectrum.riprel()
                # Background noise reduction by using the mean values of the first 50 rows.
                spectrum.sub_first_rows(50)
                # Get region of interest values for cutting.
                # TODO ... Maybe add a condition. What if NO region of interest is set?
                d_start = float(self.drift_cut[0])
                d_stop = float(self.drift_cut[1])
                r_start = float(self.retention_cut[0])
                r_stop = float(self.retention_cut[1])
                # Cut the spectrum.
                spectrum.cut_dt(start=d_start, stop=d_stop)
                spectrum.cut_rt(start=r_start, stop=r_stop)

                # Smooth the spectrum by the use of the Savitzky-Golay filter.
                spectrum.savgol(window_length=10, polyorder=4)
                # Remove all negative intensities and set them to 0.
                spectrum.values[spectrum.values < 0] = 0.0

                # Get the min and max intensity values.
                intensity_min = spectrum.values.min()
                intensity_max = spectrum.values.max()

                # Create the path where the spectrum should be saved and create the folders if necessary.
                save_path =  self.project_path / "dataset" / label / spectrum.name
                if not save_path.exists():
                    save_path.mkdir(parents=True, exist_ok=True)

                # Specify the file name and delete the old file (if an old file exists).
                spectrum_file = save_path / f"{spectrum.name}.hdf5"
                if spectrum_file.exists():
                    spectrum_file.unlink()

                # Save the processed spectrum, increase the counter and update the progress dialog.
                spectrum.to_hdf5(save_path)
                processed_spectra_counter += 1

                # Get the peaks directory and delete it.
                peak_dir = save_path / "peaks"
                if peak_dir.exists():
                    shutil.rmtree(peak_dir)

                # Get the consensus_peak directory and delete it.
                consensus_peak_dir = save_path / "consensus_peaks"
                if consensus_peak_dir.exists():
                    shutil.rmtree(consensus_peak_dir)

                cursor.execute("SELECT id FROM spectra WHERE path = ?", (str(spectrum_path),))
                spectra_data = cursor.fetchone()
                spectrum_id = spectra_data[0]
                # Delete peaks which are associated with this spectrum.
                cursor.execute("DELETE FROM peaks WHERE spectrum_id = ?", (spectrum_id,))
                # Reset all old consensus_ids
                cursor.execute("UPDATE peaks SET consensus_id = NULL")
                cursor.execute("DELETE FROM consensus_peaks")
                # Update the spectrum database entry.
                cursor.execute("UPDATE spectra SET processing_done = ?, peaks_done = ?, intensity_max = ?, intensity_min = ? "
                                    "WHERE path = ?", (1, 0, intensity_max, intensity_min, str(spectrum_path)))

                conn.commit()

                self.progress_update.emit(processed_spectra_counter, spectra_to_process)

        conn.close()
        # Send the finished signal.
        self.finished.emit()
