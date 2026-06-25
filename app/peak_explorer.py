from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtWidgets import QGraphicsOpacityEffect
from PySide6.QtCore import QSize, Qt, Signal, QTimer
from ui.peak_explorer_ui.PeakExplorerWidget import Ui_PeakExplorerWidget
from dialogs import CustomYesNoDialog, CustomProgressDialog, CustomMessageDialog
from preprocessing import DatasetSubEntry, DatasetMainEntry, PlottingCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib import pyplot as plt
from matplotlib import cm
from skimage.morphology import max_tree, h_maxima, area_opening
from skimage.measure import label, regionprops
from pathlib import Path
import multiprocessing as mp
from functools import partial
import numpy as np
import pandas as pd
import shutil
import sqlite3
import ims

class PeakExplorerPage(QtWidgets.QWidget, Ui_PeakExplorerWidget):
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
        self.peak_widgets = {}
        self.selected_peak_id = None
        # Path to the database.
        self.db_path = self.project_path.parent / "database" / "project_database.db"
        # Show peak marker on the canvas? [True or False].
        self.show_peak_marker = True
        # Connect the button to the toggle methode.
        self.pushButton_toggle_peak_marker.clicked.connect(self.toggle_peak_markers)

        # Background overlay -> This overlay blocks the view to the peak explorer while the peak detection process is running.
        self.overlay = QtWidgets.QWidget(self)
        self.overlay.setStyleSheet("background-color: #1d1d1d;")

        # Defining the scroll area layouts.
        self.scrollArea_dataset_Contents.layout().setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.scrollArea_dataset_Contents.layout().setSpacing(5)
        self.scrollArea_dataset.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scrollArea_peak_Contents.layout().setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.scrollArea_peak_Contents.layout().setSpacing(5)
        self.scrollArea_peak.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scrollArea_peak_Contents.layout().setSpacing(10)

        # Signale für die Filter-ComboBoxen verbinden
        self.comboBox_sort_peaks.currentTextChanged.connect(self.sort_peaks_in_layout)
        self.comboBox_sort_direction.currentTextChanged.connect(self.sort_peaks_in_layout)

        # Export button connection.
        self.pushButton_export.clicked.connect(self.export_peaks_to_excel)

        # Timer for window resizing.
        self.resize_timer = QTimer()
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.finished_resizing)

        # Canvas plot element.
        self.canvas = PlottingCanvas(self, width=5, height=4, dpi=50)
        # Initialize the plot canvas.
        self.init_plot_canvas()
        # Connect pick events to the peaks from the canvas.
        self.canvas.mpl_connect('pick_event', self.on_canvas_pick)
        self.canvas.mpl_connect('motion_notify_event', self.on_canvas_hover)
        # Saves the plotted canvas and it's markers.
        self.canvas_spectrum = None
        self.canvas_peak_marker_base = None
        self.canvas_peak_marker_fill = None
        # load dataset from project.
        self.load_data()


    def resizeEvent(self, event) -> None:
        """
        This function overrides the resizeEvent method and resizes the overlay widget always to the size of the main window.
        =============================================================================
        :param event: The resizing event.
        =============================================================================
        :return: None.
        """

        super().resizeEvent(event)
        self.overlay.resize(self.size())
        # Start a timer, which will eventually call the finished_resizing method.
        self.resize_timer.start(250)


    def finished_resizing(self):
        """
        This function redraws the canvas after the user finished resizing the mainwindow.
        =============================================================================
        :return: None.
        """

        if self.current_selected_spectrum:
            self.plot_spectrum(self.current_selected_spectrum)


    def showEvent(self, event) -> None:
        """
        This function is called every time the user enters this page and checks if all spectra have peaks inside the database.
        If peaks are missing a peak detection dialog is prompted to the user.
        =============================================================================
        :param event: The page display event.
        =============================================================================
        :return: None
        """

        super().showEvent(event)
        # Check if the peak detection was performed on all spectra.
        self.check_spectra_without_peaks()


    def export_peaks_to_excel(self) -> None:

        # 1. Speicherort vom User abfragen
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            caption="Export Peaks to Excel",
            dir="",
            filter="Excel Files (*.xlsx);;All Files (*)"
        )

        # Wenn der User auf "Abbrechen" geklickt hat
        if not file_path:
            return

        # Sicherstellen, dass die Datei auf .xlsx endet
        if not file_path.endswith('.xlsx'):
            file_path += '.xlsx'

        # 2. Verbindung zur Datenbank herstellen und Daten abfragen
        conn = sqlite3.connect(self.db_path)
        query = """
                SELECT l.name       AS "Label",
                       REPLACE(s.name, '.mea', '') AS "Spectrum",
                       p.ret_time   AS "Retention time",
                       p.drift_time AS "Drift time",
                       p.intensity  AS "Intensity",
                       p.consensus_id AS "Consensus peak ID"
                FROM peaks p
                         JOIN spectra s ON p.spectrum_id = s.id
                         JOIN labels l ON p.label_id = l.id
                WHERE p.is_active = 1
                ORDER BY l.name, s.name, p.intensity DESC
                """

        try:
            # 3. Pandas liest die SQL-Abfrage direkt in einen DataFrame
            df = pd.read_sql_query(query, conn)

            # Prüfen, ob überhaupt Daten vorhanden sind
            if df.empty:
                CustomMessageDialog.show_info(
                    "Export Empty",
                    "There are not peaks to export."
                )
                return

            # 4. DataFrame als Excel exportieren (ohne den DataFrame-Index)
            df.to_excel(file_path, index=False, engine='openpyxl')

            # Erfolgsmeldung anzeigen
            CustomMessageDialog.show_info(
                "Export Successful",
                f"Peaks successfully exported to:\n{file_path}"
            )

        except Exception as e:
            CustomMessageDialog.show_error(
                "Export Error",
                f"Error while exporting:\n{str(e)}"
            )
        finally:
            conn.close()


    def show_peak_detection_dialog(self) -> None:
        """
        This function is called when the peak Excel file does not exist. It creates a dialog where the user is
        prompted to start the peak detection process. If the user declines he will be redirected to the preprocessing page.
        =============================================================================
        :return: None.
        """

        # Create a custom yes/no dialog for the user where he can start the peak detection process.
        dialog = CustomYesNoDialog(
            title="Peak calculation",
            message="In order to use the peak explorer you need to start the peak detection process first. Do you "
                    " want to detect the peaks of this dataset?",
            type="warning",
            parent=self
        )

        # If the user accepted the dialog, call the start_peak_detection method.
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.start_peak_detection()
        else:
            main_window = self.window()
            # The user declined the peak detection -> Redirect to the preprocessing page.
            if hasattr(main_window, 'sb_preprocessing_button'):
                main_window.sb_preprocessing_button.click()
            else:
                print("Error: Sidebar button 'Preprocessing' not found.")


    def start_peak_detection(self) -> None:
        """
        This function is called when the user accepted the "start peak detection" prompt to detect peaks.
        A Thread is created and started on which multiple pools are started to detect the peaks of the spectra.
        =============================================================================
        :return: None
        """

        # Open the progress dialog which informs the user about the current state of the preprocessing.
        self.detection_progress_dialog = CustomProgressDialog(title="Peak detection...", header="Detecting peaks...",)
        # Reset the start time.
        self.detection_progress_dialog.start_time = None
        self.detection_progress_dialog.show()

        # Create a thread and worker for the progress dialog.
        self.thread = QtCore.QThread()
        self.worker = PeakDetectionWorker(path=self.project_path)
        self.worker.moveToThread(self.thread)

        # Connect some signals to the worker and thread.
        self.thread.started.connect(self.worker.run)
        self.worker.progress_update.connect(self.detection_progress_dialog.update_progress)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.detection_progress_dialog.accept)
        self.worker.finished.connect(self.check_spectra_without_peaks)
        self.detection_progress_dialog.button_no.clicked.connect(self.worker.stop, type=QtCore.Qt.DirectConnection)
        self.thread.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # Start the thread.
        self.thread.start()


    def check_spectra_without_peaks(self) -> None:
        """
        This function checks if all spectra inside the database are flagged with peaks_done = 1.
        If the peak detection was not performed on a spectrum this flag is set to 0 and the
        peak detection dialog is shown to the user.
        =============================================================================
        :return: None.
        """

        # Connect to the database and get the number of spectra where the peak detection process was not performed.
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM spectra WHERE peaks_done = 0")
        spectra_without_peaks = cursor.fetchone()[0]

        # If there are spectra without peaks prompt the user with the "peak detection dialog".
        if spectra_without_peaks > 0:
            QtCore.QTimer.singleShot(100, self.show_peak_detection_dialog)
            # Update the system state.
            cursor.execute("UPDATE system_state SET has_peaks = 0 WHERE id = 1")
            conn.commit()
            self.system_state_changed.emit()

        else:
            self.overlay.hide()
            # Update the system state.
            cursor.execute("UPDATE system_state SET has_peaks = 1 WHERE id = 1")
            conn.commit()
            self.system_state_changed.emit()

        conn.close()


    def load_data(self):
        """
        This function is called every time the user enters this page. It reloads all label and spectra of the dataset,
        recreates the widgets of the scroll area.
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

            self.scrollArea_dataset_Contents.layout().insertWidget(
                self.scrollArea_dataset_Contents.layout().count() - 1, spectrum)
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


    def handle_spectrum_click(self,
                              spectrum_widget: DatasetSubEntry) -> None:
        """
        This function is called when a spectrum in the scroll area is clicked. It displays the selected spectrum to the
        canvas and shows all peaks of this spectrum in the peak scroll area.
        =============================================================================
        :param spectrum_widget: The widget of the clicked spectrum.
        =============================================================================
        :return: None.
        """

        # Clear the peak widgets dictionary.
        self.clear_canvas()
        self.clear_peak_markers()

        # Clear the old layout before the new peaks are added to the scroll area.
        self.clear_layout(self.scrollArea_peak_Contents.layout())

        # Connect to the database and get all peaks from the selected spectrum.
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        query = "SELECT id, npy_file, ret_time, drift_time FROM peaks WHERE spectrum_id = ? ORDER BY drift_time"
        cursor.execute(query, (spectrum_widget.spectrum_id,))
        peaks = cursor.fetchall()
        conn.close()

        # The number of columns inside the scroll area.
        max_columns = 5

        # Loop through all peaks.
        for index, (peak_id, npy_path, retention_time, drift_time) in enumerate(peaks):
            # Calculate the position of the peak widget inside the peak scroll area.
            row = index // max_columns
            column = index % max_columns
            # The path to the peak .npy file.
            absolute_npy_path = Path(self.project_path).parent / "dataset" / npy_path
            # Create the peak widget tile and add it to the scroll area.
            peak_tile = PeakTileWidget(peak_id=peak_id,
                                       npy_path=absolute_npy_path,
                                       retention_time=retention_time,
                                       drift_time=drift_time,
                                       db_path=self.db_path)

            # Connect the peak tile widget handler.
            peak_tile.peakActivityChanged.connect(self.set_peak_activity)
            # Add the peak to the dictionary.
            self.peak_widgets[peak_id] = peak_tile
            # Add a mouse click event listener to the peak tile.
            peak_tile.mousePressEvent = lambda event, peak_id=peak_id: self.on_peak_tile_clicked(peak_id)
            # Add the peak widget to the scroll area.
            self.scrollArea_peak_Contents.layout().addWidget(peak_tile, row, column)

        self.scrollArea_peak_Contents.layout().setRowStretch(self.scrollArea_peak_Contents.layout().rowCount(), 1)
        self.scrollArea_peak_Contents.layout().setColumnStretch(max_columns, 1)

        self.sort_peaks_in_layout()

        # Plot the clicked spectrum to the canvas.
        self.plot_spectrum(spectrum_widget)
        self.canvas.draw()
        self.selected_spectrum_name = spectrum_widget.label_name.text()
        self.label_preview.setText(f"{spectrum_widget.parent.label_name.text()} - {self.selected_spectrum_name}")


    def set_peak_activity(self,
                          peak_id: int,
                          is_active: bool) -> None:
        """
        This function is called when the user changes the visibility of a peak. If a peak is set to "inactive" or "invisible"
        the peak is no longer considered an important peak and will be ignored in later steps. The peak status is here
        updated to the database and the canvas is redrawn.
        =============================================================================
        :param peak_id: The id of the peak.
        :param is_active: The new activity status of the peak.
        =============================================================================
        :return: None.
        """

        # Connect to the database and update the peak activity.
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE peaks SET is_active = ? WHERE id = ?", (is_active, peak_id))
        conn.commit()

        # Save the current zoom status [limits].
        old_xlim = self.canvas.axes.get_xlim()
        old_ylim = self.canvas.axes.get_ylim()
        # Plot the spectrum.
        self.draw_peak_markers(self.current_selected_spectrum)
        # Apply the saved zoom status.
        self.canvas.axes.set_xlim(old_xlim)
        self.canvas.axes.set_ylim(old_ylim)
        # Draw the canvas.
        self.canvas.draw()
        #self.canvas.blit(self.canvas.axes.bbox)


    def clear_layout(self, layout) -> None:
        """
        This function clears the content of the peak scroll area.
        =============================================================================
        :param layout: The layout of the peak scroll area.
        =============================================================================
        :return: None
        """

        # If there is a layout then remove all of its items [Peak tile widgets].
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())


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


    def plot_spectrum(self,
                      spectrum_widget: DatasetSubEntry) -> None:
        """
        This function loads the .mea file of one spectrum and plots it to the canvas.
        Additionally, all detected peaks are marked on the canvas.
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

        # Path to the hdf5 file.
        hdf5_path = self.project_path.parent / "dataset" / spectrum_widget.parent.label_name.text() / Path(spectrum_widget.spectrum_path).stem
        hdf5_file = hdf5_path / f"{Path(spectrum_widget.spectrum_path).stem}.hdf5"
        # Load the spectrum from the .hdf5 file.
        spectrum = ims.Spectrum.read_hdf5(hdf5_file)

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
        self.canvas_spectrum = self.canvas.copy_from_bbox(self.canvas.axes.bbox)
        self.canvas.fig.tight_layout()
        self.draw_peak_markers(spectrum_widget)


    def draw_peak_markers(self, spectrum_widget: DatasetSubEntry) -> None:
        # Connect to the database and get all peak retention- and drifttimes of the current spectrum.
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, ret_time, drift_time, is_active FROM peaks WHERE spectrum_id = ?",
                       (spectrum_widget.spectrum_id,))
        peak_times = cursor.fetchall()
        conn.close()

        # Load the canvas from the cache and remove the peak markings.
        self.canvas_peak_marker_base = None
        self.canvas_peak_marker_fill = None

        # If there are peaks mark them on the plot canvas.
        if peak_times and self.show_peak_marker:
            # Extract peak information.
            peak_ids = [p[0] for p in peak_times]
            retention_time = [p[1] for p in peak_times]
            drift_time = [p[2] for p in peak_times]
            is_active = [p[3] for p in peak_times]

            # Color list for the peak markers, depending on the activity status and their selection.
            colors = []
            for peak_id, activity in zip(peak_ids, is_active):
                if peak_id == self.selected_peak_id:
                    colors.append('#ff9000')
                else:
                    colors.append('#00eaff' if activity == 1 else '#da05ab')

            # Falls die Scatter-Objekte noch nicht existieren, erstellen wir sie
            self.canvas_peak_marker_base = self.canvas.axes.scatter(drift_time, retention_time, marker='o', s=150,
                                                                    color='black', linewidths=2.0)
            self.canvas_peak_marker_fill = self.canvas.axes.scatter(drift_time, retention_time, marker='o', s=75,
                                                                    color=colors, linewidths=1.0, picker=True)

            # Save the ids for the pick event.
            self.canvas_peak_marker_fill.peak_ids = peak_ids
            # 3. Nur die Scatter-Objekte neu rendern
            self.canvas.axes.draw_artist(self.canvas_peak_marker_base)
            self.canvas.axes.draw_artist(self.canvas_peak_marker_fill)


    def clear_peak_markers(self):
        self.peak_widgets.clear()

        if hasattr(self, 'canvas_peak_marker_base') and self.canvas_peak_marker_base is not None:
            self.canvas_peak_marker_base.remove()
            self.canvas_peak_marker_base = None

        if hasattr(self, 'canvas_peak_marker_fill') and self.canvas_peak_marker_fill is not None:
            self.canvas_peak_marker_fill.remove()
            self.canvas_peak_marker_fill = None
        self.canvas_spectrum = None
        self.canvas.draw()


    def toggle_peak_markers(self) -> None:
        """
        This function is called when the 'Hide/Show peak markers' button is pressed and handels the change of view of
        the canvas. It either shows or hides the peak markers.
        =============================================================================
        :return: None.
        """

        if self.show_peak_marker:
            self.show_peak_marker = False
            self.pushButton_toggle_peak_marker.setText("Show peak markers")
        else:
            self.show_peak_marker = True
            self.pushButton_toggle_peak_marker.setText("Hide peak markers")

        if self.current_selected_spectrum is not None:
            # Save the current zoom status [limits].
            old_xlim = self.canvas.axes.get_xlim()
            old_ylim = self.canvas.axes.get_ylim()
            # Update the markers
            self.plot_spectrum(self.current_selected_spectrum)
            # Apply the saved zoom status.
            self.canvas.axes.set_xlim(old_xlim)
            self.canvas.axes.set_ylim(old_ylim)
            # Draw the canvas.
            self.canvas.draw()


    def on_peak_tile_clicked(self,
                             peak_id: int) -> None:
        """
        This function is called when the user clicked on one of the peak tiles in the peak scroll area.
        The clicked tile is highlighted.
        =============================================================================
        :param peak_id: The ID of the peak tile.
        =============================================================================
        :return: None.
        """

        # Remove the highlight from the peak widget tile.
        if self.selected_peak_id in self.peak_widgets:
            self.peak_widgets[self.selected_peak_id].set_selected(False)
            self.peak_widgets[self.selected_peak_id].change_tile_style()

        # Highlight the clicked peak tile in the scroll area.
        self.selected_peak_id = peak_id
        if peak_id in self.peak_widgets:
            self.peak_widgets[peak_id].set_selected(True)
            self.peak_widgets[peak_id].change_tile_style()
            self.scrollArea_peak.ensureWidgetVisible(self.peak_widgets[peak_id])

        # Maintain the zoom status of the canvas.
        xlim, ylim = self.canvas.axes.get_xlim(), self.canvas.axes.get_ylim()
        self.draw_peak_markers(self.current_selected_spectrum)
        self.canvas.axes.set_xlim(xlim)
        self.canvas.axes.set_ylim(ylim)
        self.canvas.draw()


    def on_canvas_pick(self, event) -> None:
        """
        This function is called when the user clicks on one of the peak markings in the canvas.
        The marked peak is highlighted on the canvas and in the peak scroll area.
        =============================================================================
        :param event: The click event.
        =============================================================================
        :return: None
        """

        if event.artist == self.canvas_peak_marker_fill:
            idx = event.ind[0]
            peak_id = event.artist.peak_ids[idx]
            # Call the on tile clicked method.
            self.on_peak_tile_clicked(peak_id)


    def on_canvas_hover(self, event) -> None:
        """
        This function is called when the user hovers over one of the peak markings in the canvas.
        The mouse icon is changed to the pointing hand cursor if the user currently not in the 'zoom' or 'pan' mode.
        =============================================================================
        :param event: The hover event.
        =============================================================================
        :return: None
        """

        # Are there reals peaks?
        if hasattr(self, 'canvas_peak_marker_fill') and self.canvas_peak_marker_fill is not None:
            # Get data of the current mouse location.
            cont, _ = self.canvas_peak_marker_fill.contains(event)

            # is the mouse hovering over a 'canvas_peak_marker_fill' element? [This is a peak marking].
            if cont and self.toolbar.mode != 'zoom rect' and self.toolbar.mode != 'pan/zoom':
                self.canvas.setCursor(QtCore.Qt.PointingHandCursor)
            else:
                # If the mouse is not hovering over a peak use the default style, according to the current mode.
                if self.toolbar.mode == 'zoom rect':
                    self.canvas.setCursor(QtCore.Qt.CrossCursor)
                elif self.toolbar.mode == 'pan/zoom':
                    self.canvas.setCursor(QtCore.Qt.SizeAllCursor)
                else:
                    self.canvas.setCursor(QtCore.Qt.ArrowCursor)


    def sort_peaks_in_layout(self) -> None:
        """
        Nimmt alle Peak-Tiles aus dem Layout, sortiert sie in-memory basierend
        auf den beiden ComboBoxen (Kriterium & Richtung) und fügt sie wieder ein.
        """
        layout = self.scrollArea_peak_Contents.layout()

        # 1. Nur die echten Peak-Tiles aus dem Layout sammeln
        tiles = []
        for i in range(layout.count()):
            item = layout.itemAt(i)
            widget = item.widget()

            # Wir prüfen mit hasattr, ob das Widget unsere Parameter hat.
            # So ignorieren wir erfolgreich Spacer oder unsichtbare Qt-Platzhalter!
            if widget is not None and hasattr(widget, 'retention_time'):
                tiles.append(widget)

        if not tiles:
            return

        # 2. Aktuelles Kriterium und Richtung auslesen
        sort_criterion = self.comboBox_sort_peaks.currentText()
        sort_direction = self.comboBox_sort_direction.currentText()

        # DESC bedeutet absteigend (reverse=True)
        is_reverse = (sort_direction == "DESC")

        # 3. Sortieren anhand der Attribute
        if sort_criterion == "Retention time":
            tiles.sort(key=lambda t: t.retention_time, reverse=is_reverse)
        elif sort_criterion == "Drift time":
            tiles.sort(key=lambda t: t.drift_time, reverse=is_reverse)
        elif sort_criterion == "Active":
            tiles.sort(key=lambda t: t.is_active, reverse=is_reverse)

        # 4. Widgets aus dem Grid-Layout lösen (ohne sie zu löschen)
        for tile in tiles:
            layout.removeWidget(tile)

        # 5. Widgets in der neuen Reihenfolge wieder ins Gitter einfügen
        max_columns = 5
        for row_index, tile in enumerate(tiles):
            row = row_index // max_columns
            column = row_index % max_columns
            layout.addWidget(tile, row, column)


class PeakDetectionWorker(QtCore.QObject):
    # Signal definitions.
    finished = Signal()
    progress_update = Signal(int, int)

    def __init__(self, path: Path):

        super().__init__()
        self.project_path = path.parent
        self.db_path = self.project_path / "database" / "project_database.db"
        # Worker stopped signal [The user has canceled the preprocessing].
        self.worker_stopped = False


    @QtCore.Slot()
    def stop(self):
        self.worker_stopped = True


    def run(self) -> None:
        """
        This function overrides the run function of a thread worker and starts the peak detection process on all
        spectra without peaks. It starts a distinct number of pools [one for each CPU core], collects the detected peaks
        from all spectra and saves them at the end into the peak table of the database.
        =============================================================================
        :return: None.
        """

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


def peak_detection(spectrum_data: tuple[str, str, int, int],
                   project_path: Path,
                   peak_radius: int) -> tuple[Path, list]:
    """
    This function handles the peak detection for preprocessed gc-ims spectra in a series of steps.
    1. Normalization of the spectrum to values between 0 and 1.
    2. Create a component tree of the spectrum and detect hierarchy levels.
    3. Filter peaks from the component tree according to specific conditions [Area Opening, intensity threshold, tree hierarchy].
    4. Save the intensities of each detected peak and its surrounding (defined by peak_radius) as a .npy file.
    5. Return a list of dictionaries. One dictionary for each peak + surrounding with the following information.
        - 'label_id' -> The label/type of the used spectrum.
        - 'spectrum_id' -> Name of the spectrum.
        - 'ret_time' -> Retention time [s] of the peak.
        - 'drift_time' -> Drift time [ms] of the peak.
        - 'intensity' -> Intensity [not normalized] of peak + surrounding.
        - 'npy_file' -> Path to the saved npy file of this peak.
    =============================================================================
    :param spectrum_data: a tuple with spectrum data -> Path, associated label name, label id, spectrum id.
    :param project_path: The path to the current project.
    :param peak_radius: The radius around a detected peak within the intensities are saved.
    =============================================================================
    :return: List of dictionaries which contain peak + surrounding information.
    """

    spectrum_path, label_name, label_id, spectrum_id = spectrum_data
    spec_name = Path(spectrum_path).stem
    target_file = project_path / "dataset" / label_name / spec_name / f"{spec_name}.hdf5"
    spectrum = ims.Spectrum.read_hdf5(target_file)

    # 1. Spectrum normalization. ---------------------------------------------------------------------------------------
    # Keep the non normalized values for later use.
    values_non_normalized = spectrum.values.copy()
    # Normalize the spectrum [0-1].
    spectrum.normalization()
    # List of dictionaries which contain selected peak information. This list is returned at the end of this function.
    spectrum_peak_data = []

    try:
        # 2. Create a component tree. ----------------------------------------------------------------------------------
        parent, tree_traverser = max_tree(spectrum.values, connectivity=2)

        # 3. Filter peaks. ---------------------------------------------------------------------------------------------
        # Define the min. area threshold size in pixel. [Smaller value = finer peak detection]
        area_threshold = 5
        # Collapses nodes which are smaller than the area_threshold with their parents.
        filtered_local_maxima = area_opening(spectrum.values,
                                             area_threshold=area_threshold,
                                             connectivity=2,
                                             parent=parent,
                                             tree_traverser=tree_traverser)

        # What is the min. height differenz (normalized values) for nodes to be discriminated as different peaks?
        height_differenz = 0.02
        # Remove nodes which are to small compared to their node neighbors (node height differenz < height_differenz)
        peak_mask = h_maxima(filtered_local_maxima, h=height_differenz)
        # label the found nodes.
        label_mask = label(peak_mask, connectivity=2)
        # Create regions from the original spectrum values of the labeled nodes.
        regions = regionprops(label_mask, intensity_image=spectrum.values)
        # create a new empty array with the size of found regions (Each region = 1 peak).
        all_peak_coords = np.zeros((len(regions), 2), dtype=int)

        # Walk through all found regions, calculate the weighted center coordinates and save them as a peak.
        for region_idx, region in enumerate(regions):
            y, x = region.weighted_centroid
            all_peak_coords[region_idx] = [int(round(y)), int(round(x))]

        # Get all retention indices from the peak coordinates.
        ret_idx = all_peak_coords[:, 0]
        # Get all drift indices from the peak coordinates.
        drift_idx = all_peak_coords[:, 1]
        # List with normalized intensities which correlate to the coordinates of the "all_peak_coords" list.
        peak_intensities = spectrum.values[ret_idx, drift_idx]

        # Define the min. peak threshold intensity [non normalized value].
        peak_threshold = 64
        # How many intensity values are there in total?
        intensity_count_max = spectrum.values.shape[0] * spectrum.values.shape[1]
        # How many intensities values are over the peak_threshold?
        threshold_intensity_count = len(np.where(values_non_normalized >= peak_threshold)[0])
        # Calculate the % of intensity values which are below the peak_threshold.
        threshold_percentile = 100 - (threshold_intensity_count / intensity_count_max) * 100
        # Peak intensity detection threshold.
        intensity_threshold = np.percentile(spectrum.values, [threshold_percentile])

        # Are there peaks?
        # If so, select only peaks which are higher than the intensity threshold.
        if len(peak_intensities) > 0:
            intensity_mask = peak_intensities >= intensity_threshold
            # Use the mask on the peak coordinates.
            # Only Coordinates where the mask condition is satisfied are saved.
            peak_coords = all_peak_coords[intensity_mask]
        else:
            # No peaks. Create an empty numpy array.
            peak_coords = np.array([])

        if len(peak_coords) > 0:
            # Remove peaks which are located near the spectrum boarders.
            # list with all peak retention indices.
            peak_ret_idx_list = peak_coords[:, 0]
            # list with all peak drift indices.
            peak_drift_idx_list = peak_coords[:, 1]
            # Integer with the maximum retention and drift index.
            ret_idx_max, drift_idx_max = spectrum.values.shape

            # Create single mask conditions.
            mask_ret_min = peak_ret_idx_list >= peak_radius
            mask_ret_max = peak_ret_idx_list < (ret_idx_max - peak_radius)
            mask_drift_min = peak_drift_idx_list >= peak_radius
            mask_drift_max = peak_drift_idx_list < (drift_idx_max - peak_radius)
            # Combine all 4 masks to one mask condition. This mask will remove all peaks which are too close to the border.
            # This will create a list with tuples of the same length as the found peak list (peak_coords).
            # If all single mask conditions are met, true will be saved in this list. Otherwise, it will be set to False.
            final_validity_mask = (mask_ret_min &
                                   mask_ret_max &
                                   mask_drift_min &
                                   mask_drift_max)

            # Use the mask on the peak_coords list.
            # Only Coordinates where the mask is set to "True" are kept. The rest will be removed.
            peak_coords = peak_coords[final_validity_mask]

            # 4. Plot the detected peaks. ------------------------------------------------------------------------------
            # Reload the non normalized values.
            spectrum.values = values_non_normalized

            # 4. Extend peaks. Each peak will be saved ....
            # Copy the spectrum.values and add a padding of 0 around them.
            # Why? If a peak is detected near the spectrum boarder, this could lead to errors in the shape and or saved
            # intensities of the peak windows. The padding guarantees the correct shape and failsafe the intensities of
            # indices outside the spectrum boarder to 0.
            padded_values = np.pad(
                spectrum.values,
                pad_width=2 * peak_radius,
                mode='constant',
                constant_values=0
            )

            # Check if the peaks directory already exists - if so delete it and all old peaks.
            npy_save_dir = project_path / "dataset" / label_name / spectrum.name / "peaks"
            if npy_save_dir.exists():
                shutil.rmtree(npy_save_dir)

            # Walk through all peak coordinates.
            for ret_idx, drift_idx in peak_coords:
                start_ret_idx = ret_idx - peak_radius
                end_ret_idx = ret_idx + 5 * peak_radius + 1
                start_drift_idx = drift_idx - peak_radius
                end_drift_idx = drift_idx + 5 * peak_radius + 1
                peak_window_intensities = padded_values[start_ret_idx:end_ret_idx, start_drift_idx:end_drift_idx]
                peak_window = peak_window_intensities

                # Check if the peak window has the correct shape. This should always be the case!
                if peak_window_intensities.shape != (6 * peak_radius + 1, 6 * peak_radius + 1):
                    raise ValueError(f"\tPeak Window has the wrong shape: {peak_window_intensities.shape}. "
                                     f"Expected Shape: ({6 * peak_radius + 1}, {6 * peak_radius + 1})")

                # 5. Save peak information as .npy file ----------------------------------------------------------------
                npy_save_dir = project_path / "dataset" / label_name / spectrum.name / "peaks"
                if not npy_save_dir.exists():
                    npy_save_dir.mkdir(parents=True, exist_ok=True)

                npy_filename = npy_save_dir / f"PW_{spectrum.name}_RT{ret_idx}_DT{drift_idx}_{6 * peak_radius + 1}x{6 * peak_radius + 1}.npy"
                np.save(npy_filename, peak_window)

                npy_dictionary_file = Path(label_name) / spectrum.name / "peaks" / f"PW_{spectrum.name}_RT{ret_idx}_DT{drift_idx}_{6 * peak_radius + 1}x{6 * peak_radius + 1}.npy"

                # Dictionary with information about peaks.
                peak_data = {
                    'label_id': label_id,
                    'spectrum_id': spectrum_id,
                    'ret_time': float(spectrum.ret_time[ret_idx]),
                    'drift_time': float(spectrum.drift_time[drift_idx]),
                    'intensity': float(spectrum.values[ret_idx, drift_idx]),
                    'npy_file': str(npy_dictionary_file),
                }
                spectrum_peak_data.append(peak_data)

    except Exception as err:
        print(f"\tError on {spectrum.name} - Skipped: {err=}, {type(err)=}")
        return []

    return spectrum_path, spectrum_peak_data


class PeakTileWidget(QtWidgets.QFrame):
    # Signal definition.
    peakActivityChanged = QtCore.Signal(int, bool)

    def __init__(self,
                 peak_id: int,
                 npy_path: Path,
                 retention_time: float,
                 drift_time: float,
                 db_path: Path,
                 parent=None) -> None:

        super().__init__(parent)
        self.peak_id = peak_id
        self.db_path = db_path
        self.retention_time = retention_time
        self.drift_time = drift_time
        self.is_selected = False

        # Connect to the database and get the activity status of this peak.
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT is_active FROM peaks WHERE id = ?", (peak_id,))
        peak_data = cursor.fetchone()

        # Set the peak activity.
        self.is_active = bool(peak_data[0]) if peak_data else False
        conn.close()

        # lower the opacity of the widget if the peak is inactive.
        self.opacity_effect = QGraphicsOpacityEffect()
        if not self.is_active:
            self.opacity_effect.setOpacity(0.3)
            self.setGraphicsEffect(self.opacity_effect)

        # Image paths for the activity icons.
        self.icon_active = QtGui.QIcon(":/ui/_pics/icons/eye_open.png")
        self.icon_inactive = QtGui.QIcon(":/ui/_pics/icons/eye_closed.png")

        # Set the size and the style for the peak tile widget.
        self.setFixedSize(90, 120)
        self.setStyleSheet("""
            PeakTileWidget {
                background-color: #2b2b2b;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
            }
            PeakTileWidget:hover {
                border: 1px solid #555555;
                background-color: #323232;
            }
        """)

        # Define the main layout of this widget and its margins.
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)

        # Create a label for the image
        self.image_label = QtWidgets.QLabel()
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        # Set the image to the label.
        self.set_peak_tile_image(npy_path)

        # Create a button which is placed on top of the peak image.
        self.activity_button = QtWidgets.QPushButton(self.image_label)
        self.activity_button.setFixedSize(20, 20)
        self.activity_button.move(57, 50)
        self.activity_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.activity_button.setStyleSheet("background: rgba(0,0,0,100); border: none;")
        # Set the correct peak button icon for the current peak activity.
        self.change_button_icon()
        # Connect the button.
        self.activity_button.clicked.connect(self.change_peak_activity_button)

        # Add the image label to the main layout.
        self.main_layout.addWidget(self.image_label)

        # Text area of the widget.
        info_text = f"DT: {drift_time:.2f}\nRT: {retention_time:.2f}"
        self.info_label = QtWidgets.QLabel(info_text)
        self.info_label.setStyleSheet("font-size: 12px; color: #aaaaaa;")
        self.info_label.setAlignment(QtCore.Qt.AlignCenter)
        self.main_layout.addWidget(self.info_label)

        # Set hover mouse icon
        self.setCursor(QtCore.Qt.PointingHandCursor)


    def set_selected(self, is_selected: bool) -> None:
        self.is_selected = is_selected

    def change_peak_activity_button(self) -> None:
        """
        This function is called when the user clicked on the peak activity button.
        The peak activity is adjusted, the button icon is changed and a signal is emitted which will update the
        peak activity in the database.
        =============================================================================
        :return: None.
        """

        # Change the peak activity and update the icon.
        self.is_active = not self.is_active
        self.change_button_icon()
        self.change_tile_style()
        # Emmit a signal which will update the peak entry in the database.
        self.peakActivityChanged.emit(self.peak_id, self.is_active)


    def change_button_icon(self) -> None:
        """
        This function changes the peak activity button icon.
        =============================================================================
        :return: None.
        """

        # Get the path to the correct icon.
        path = self.icon_active if self.is_active else self.icon_inactive
        # Replace the icon on the button.
        self.activity_button.setIcon(path)
        self.activity_button.setIconSize(QtCore.QSize(20, 20))


    def change_tile_style(self) -> None:
        """
        This function changed the style of a peak tile if it is currently selected or not.
        =============================================================================
        :return: None.
        """

        if self.is_selected:
            border_color = "#ff9000"
            border_color_hover = "#ff9000"
            background_color = "#1b1b1b"
            background_color_hover = "#323232"
        else:
            border_color = "#3d3d3d"
            border_color_hover = "#555555"
            background_color = "#2b2b2b"
            background_color_hover = "#323232"

        self.setStyleSheet(f"""
                            PeakTileWidget {{
                                background-color: {background_color};
                                border: 1px solid {border_color};
                                border-radius: 5px;
                            }}
                            PeakTileWidget:hover {{
                                background-color: {background_color_hover};
                                border: 1px solid {border_color_hover};
                                border-radius: 5px;
                            }}
                        """)

        self.opacity_effect = QGraphicsOpacityEffect()
        if self.is_active or self.is_selected:
            self.opacity_effect.setOpacity(1.0)
        else:
            self.opacity_effect.setOpacity(0.3)
        self.setGraphicsEffect(self.opacity_effect)


    def set_peak_tile_image(self,
                            npy_path: Path) -> None:
        """
        This function loads the .npy file of a peak, normalizes it between 0-255, applies a colormap and represents
        the peak as an image on the peak tile widget.
        =============================================================================
        :param npy_path: Path to the .npy peak file.
        =============================================================================
        :return: None.
        """

        try:
            # Load the peak .npy file and normalize the values.
            peak_data = np.load(npy_path)
            if peak_data.max() > peak_data.min():
                normalized_peak_data = (peak_data - peak_data.min()) / (peak_data.max() - peak_data.min()) * 255
            else:
                normalized_peak_data = peak_data * 0

            # change the dataformat and define a colormap.
            image_data = normalized_peak_data.astype(np.uint8)
            height, width = image_data.shape
            color_map = cm.get_cmap('RdBu_r', 256)

            # Create a greyscale QImage of the numpy array data.
            q_image = QtGui.QImage(image_data.data, width, height, width, QtGui.QImage.Format_Indexed8)

            # Convert into the right color format.
            qt_color_table = []
            for i in range(256):
                rgba = color_map(i)
                qt_color_table.append(QtGui.qRgb(
                    int(rgba[0] * 255),
                    int(rgba[1] * 255),
                    int(rgba[2] * 255)
                ))

            # Apply the color pallet to the image.
            q_image.setColorTable(qt_color_table)
            pixmap = QtGui.QPixmap.fromImage(q_image).scaled(80, 80, QtCore.Qt.KeepAspectRatio)
            self.image_label.setPixmap(pixmap)
        except:
            self.image_label.setText("N/A")