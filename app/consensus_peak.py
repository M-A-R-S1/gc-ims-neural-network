from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtWidgets import QGraphicsOpacityEffect
from PySide6.QtCore import QSize, Qt, Signal, QTimer
from ui.consensus_peak_ui.ConsensusPeakWidget import Ui_ConsensusPeakWidget
from ui.consensus_peak_ui.ConsensusPeakTile import Ui_ConsensusPeakTile
from dialogs import CustomYesNoDialog, CustomProgressDialog
from preprocessing import PlottingCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib import pyplot as plt
from matplotlib import cm
from pathlib import Path
from collections import defaultdict
import numpy as np
import pandas as pd
import shutil
import networkx as nx
from scipy.spatial import KDTree
from sklearn.preprocessing import MinMaxScaler
import sqlite3
import ims

class ConsensusPeakPage(QtWidgets.QWidget, Ui_ConsensusPeakWidget):
    # Signal definition.
    system_state_changed = QtCore.Signal()

    def __init__(self, project_path: str):
        super().__init__()
        self.setupUi(self)

        # Project save path
        self.project_path = Path(project_path)
        # Path to the database.
        self.db_path = self.project_path.parent / "database" / "project_database.db"
        # Show peak marker on the canvas? [True or False].
        self.show_peak_marker = True
        # Connect the button to the toggle methode.
        self.pushButton_toggle_peak_marker.clicked.connect(self.toggle_peak_markers)
        self.consensus_peak_widgets = {}
        self.selected_consensus_peak_id = None

        # Background overlay -> This overlay blocks the view to the peak explorer while the consensus peak detection process is running.
        self.overlay = QtWidgets.QWidget(self)
        self.overlay.setStyleSheet("background-color: #1d1d1d;")

        # Defining the scroll area layout.
        self.scrollArea_peak_Contents.layout().setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.scrollArea_peak_Contents.layout().setSpacing(5)
        self.scrollArea_peak.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scrollArea_peak_Contents.layout().setSpacing(10)

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

        if self.consensus_peak_widgets:
            self.plot_spectrum()


    def showEvent(self, event) -> None:
        """
        This function is called every time the user enters this page and checks if all peaks are connected to a consensus peak inside the database.
        If peaks are not connected a consensus peak detection dialog is prompted to the user.
        =============================================================================
        :param event: The page display event.
        =============================================================================
        :return: None
        """

        super().showEvent(event)
        # Check if all peaks are connected to a consensus peak.
        self.check_peaks_for_consensus()


    def show_consensus_peak_calc_dialog(self) -> None:
        """
        This function is called when peaks are not associated with consensus peaks. It creates a dialog where the user is
        prompted to start the consensus peak calculation process. If the user declines he will be redirected to the peaks page.
        =============================================================================
        :return: None.
        """

        # Create a custom yes/no dialog for the user where he can start the consensus peak calculation process.
        dialog = CustomYesNoDialog(
            title="Consensus peak calculation",
            message="Some of the peaks are not associated with a consensus peak.\n\nDo you want to calculate the consensus peaks now?",
            type="warning",
            parent=self
        )

        # If the user accepted the dialog, call the start_peak_detection method.
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.start_consensus_peak_calculation()
        else:
            main_window = self.window()
            # The user declined the calculation -> Redirect to the peaks page.
            if hasattr(main_window, 'sb_peak_explorer_button'):
                main_window.sb_peak_explorer_button.click()
            else:
                print("Error: Sidebar button 'Peak Explorer' not found.")


    def start_consensus_peak_calculation(self) -> None:
        """
        This function is called when the user accepted the "start consensus peak calculation" prompt to calculate consensus peaks.
        A Thread is created and started on which the consensus peaks are calculated.
        =============================================================================
        :return: None
        """

        # Open the progress dialog which informs the user about the current state.
        self.consensus_progress_dialog = CustomProgressDialog(title="Consensus peak calculation...", header="Calculating consensus peaks...",)
        # Reset the start time.
        self.consensus_progress_dialog.start_time = None
        self.consensus_progress_dialog.show()

        # Create a thread and worker for the progress dialog.
        self.thread = QtCore.QThread()
        self.worker = ConsensusPeakCalculationWorker(path=self.project_path)
        self.worker.moveToThread(self.thread)

        # Connect some signals to the worker and thread.
        self.thread.started.connect(self.worker.run)
        self.worker.progress_update.connect(self.consensus_progress_dialog.update_progress)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.consensus_progress_dialog.accept)
        self.worker.finished.connect(self.update_system_state)
        self.worker.finished.connect(self.check_peaks_for_consensus)
        self.consensus_progress_dialog.button_no.clicked.connect(self.worker.stop, type=QtCore.Qt.DirectConnection)
        self.thread.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # Start the thread.
        self.thread.start()


    def update_system_state(self) -> None:
        # Connect to the database and get the number of peaks where the consensus id is NULL.
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE system_state SET has_consensus_peaks = 1, consensus_peaks_changed = 0 WHERE id = 1")
        conn.commit()
        conn.close()

        self.system_state_changed.emit()


    def check_peaks_for_consensus(self) -> None:
        """
        This function checks if all peaks inside the database are associated with a consensus peak id.
        If peaks are missing this id the consensus peak detection dialog is shown to the user.
        =============================================================================
        :return: None.
        """

        # Connect to the database and get the number of peaks where the consensus id is NULL.
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM peaks WHERE consensus_id IS NULL AND is_active = 1")
        peaks_without_consensus = cursor.fetchone()[0]

        cursor.execute("SELECT consensus_peaks_changed FROM system_state WHERE id = 1")
        state = cursor.fetchone()
        consensus_peaks_changed = bool(state[0])

        # If there are peaks without a consensus id show the user the "consensus peak calculation dialog".
        if consensus_peaks_changed or peaks_without_consensus > 0:
            QtCore.QTimer.singleShot(100, self.show_consensus_peak_calc_dialog)
        else:
            self.overlay.hide()
            self.load_consensus_peaks()

        conn.close()


    def load_data(self):
        """
        This function is called every time the user enters this page. It reloads all label and spectra of the dataset
        and recreates the widgets of the scroll area.
        =============================================================================
        :return: None
        """

        self.selected_consensus_peak_id = None
        self.consensus_peak_widgets = {}
        self.label_preview.setText("Spectrum preview")

        # Clear the canvas.
        self.clear_canvas()


    def load_consensus_peaks(self) -> None:
        """
        This function is called when this page is loaded or when the consensus peak detection is finished.
        It displays all consensus peaks as widgets in the peak scroll area.
        =============================================================================
        :return: None.
        """

        # Clear the consensus peak widget dictionary.
        self.clear_canvas()
        self.clear_peak_markers()

        # Clear the old layout before the new peaks are added to the scroll area.
        self.clear_layout(self.scrollArea_peak_Contents.layout())

        # Connect to the database and get all peaks from the selected spectrum.
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        query = "SELECT id, ret_time, drift_time, min_intensity, is_active FROM consensus_peaks ORDER BY drift_time"
        cursor.execute(query)
        consensus_peaks_data = cursor.fetchall()

        # Get the number of unique labels.
        label_count_query = "SELECT COUNT(DISTINCT name) FROM labels"
        cursor.execute(label_count_query)
        label_count = cursor.fetchone()[0]

        # Get the number of unique spectra.
        spectra_count_query = "SELECT COUNT(DISTINCT path) FROM spectra"
        cursor.execute(spectra_count_query)
        spectra_count = cursor.fetchone()[0]
        conn.close()

        # The number of columns inside the scroll area.
        max_columns = 3

        # Loop through all peaks.
        for index, (consensus_id, retention_time, drift_time, min_intensity, is_active) in enumerate(consensus_peaks_data):
            # Calculate the position of the peak widget inside the peak scroll area.
            row = index // max_columns
            column = index % max_columns
            # The path to the peak .npy file.
            absolute_npy_path = Path(self.project_path).parent / "dataset"
            # Create the consensus peak widget tile and add it to the scroll area.
            consensus_peak_tile = ConsensusPeakTile(db_path=self.db_path,
                                                    consensus_id=consensus_id,
                                                    retention_time=retention_time,
                                                    drift_time=drift_time,
                                                    unique_labels=label_count,
                                                    unique_spectra=spectra_count,
                                                    npy_path=absolute_npy_path,
                                                    is_active=is_active)

            # Connect the peak tile widget handler.
            consensus_peak_tile.consensusPeakActivityChanged.connect(self.set_consensus_peak_activity)
            # Add the consensus peak to the dictionary.
            self.consensus_peak_widgets[consensus_id] = consensus_peak_tile
            # Add a mouse click event listener to the peak tile.
            consensus_peak_tile.mousePressEvent = lambda event, peak_id=consensus_id: self.on_peak_tile_clicked(peak_id)
            # Add the peak widget to the scroll area.
            self.scrollArea_peak_Contents.layout().addWidget(consensus_peak_tile, row, column)

        self.scrollArea_peak_Contents.layout().setRowStretch(self.scrollArea_peak_Contents.layout().rowCount(), 1)
        self.scrollArea_peak_Contents.layout().setColumnStretch(max_columns, 1)

        # Plot the clicked spectrum to the canvas.
        self.plot_spectrum()
        self.canvas.draw()


    def set_consensus_peak_activity(self,
                                    consensus_id: int,
                                    is_active: bool) -> None:
        """
        This function is called when the user changes the visibility of a consensus peak. If a consensus peak is set to "inactive" or "invisible"
        the consensus peak is no longer considered an important consensus peak and will be ignored in later steps. The consensus peak status is here
        updated to the database and the canvas is redrawn.
        =============================================================================
        :param consensus_id: The id of the consensus peak.
        :param is_active: The new activity status of the peak.
        =============================================================================
        :return: None.
        """

        # Connect to the database and update the peak activity.
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE consensus_peaks SET is_active = ? WHERE id = ?", (is_active, consensus_id))
        conn.commit()

        # Save the current zoom status [limits].
        old_xlim = self.canvas.axes.get_xlim()
        old_ylim = self.canvas.axes.get_ylim()
        # Plot the spectrum.
        self.draw_peak_markers()
        # Apply the saved zoom status.
        self.canvas.axes.set_xlim(old_xlim)
        self.canvas.axes.set_ylim(old_ylim)
        # Draw the canvas.
        self.canvas.draw()
        self.canvas.blit(self.canvas.axes.bbox)


    def clear_layout(self, layout) -> None:
        """
        This function clears the content of a scroll area.
        =============================================================================
        :param layout: The layout of the scroll area.
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


    def plot_spectrum(self) -> None:
        """
        This function loads the .mea file of one spectrum and plots it to the canvas.
        Additionally, all detected peaks are marked on the canvas.
        =============================================================================
        :param spectrum_widget: Widget of the currently selected spectrum in the spectra scroll area.
        =============================================================================
        :return: None
        """

        # Set a dark background for the plot.
        plt.style.use('dark_background')

        best_spectrum = self.get_spectrum_with_most_consensus_peaks()

        # Path to the hdf5 file.
        hdf5_path = self.project_path.parent / "dataset" / best_spectrum['label_name'] / best_spectrum['spectrum_name']
        hdf5_file = hdf5_path / f"{best_spectrum['spectrum_name']}.hdf5"
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
        self.draw_peak_markers()


    def draw_peak_markers(self) -> None:
        # Connect to the database and get all consensus peak retention- and drifttimes of the current spectrum.
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, ret_time, drift_time, is_active FROM consensus_peaks")
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
                if peak_id == self.selected_consensus_peak_id:
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
        self.consensus_peak_widgets.clear()

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

        # Save the current zoom status [limits].
        old_xlim = self.canvas.axes.get_xlim()
        old_ylim = self.canvas.axes.get_ylim()
        # Update the markers
        self.plot_spectrum()
        # Apply the saved zoom status.
        self.canvas.axes.set_xlim(old_xlim)
        self.canvas.axes.set_ylim(old_ylim)
        # Draw the canvas.
        self.canvas.draw()


    def on_peak_tile_clicked(self,
                             consensus_peak_id: int) -> None:
        """
        This function is called when the user clicked on one of the peak tiles in the peak scroll area.
        The clicked tile is highlighted.
        =============================================================================
        :param consensus_peak_id: The ID of the peak tile.
        =============================================================================
        :return: None.
        """

        # Remove the highlight from the peak widget tile.
        if self.selected_consensus_peak_id in self.consensus_peak_widgets:
            self.consensus_peak_widgets[self.selected_consensus_peak_id].set_selected(False)
            self.consensus_peak_widgets[self.selected_consensus_peak_id].change_tile_style()

        # Highlight the clicked peak tile in the scroll area.
        self.selected_consensus_peak_id = consensus_peak_id
        if consensus_peak_id in self.consensus_peak_widgets:
            self.consensus_peak_widgets[consensus_peak_id].set_selected(True)
            self.consensus_peak_widgets[consensus_peak_id].change_tile_style()
            self.scrollArea_peak.ensureWidgetVisible(self.consensus_peak_widgets[consensus_peak_id])

        # Maintain the zoom status of the canvas.
        xlim, ylim = self.canvas.axes.get_xlim(), self.canvas.axes.get_ylim()
        self.draw_peak_markers()
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


    def get_spectrum_with_most_consensus_peaks(self) -> dict:

        # Connect to the database and get the spectrum id with the most consensus peaks.
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
                SELECT p.spectrum_id, 
                       REPLACE(s.name, '.mea', '')    AS spectrum_name,
                       l.name                         AS label_name,
                       COUNT(DISTINCT p.consensus_id) AS consensus_peak_count
                FROM peaks p
                         JOIN spectra s ON p.spectrum_id = s.id
                         JOIN labels l ON p.label_id = l.id
                WHERE p.consensus_id IS NOT NULL
                GROUP BY p.spectrum_id
                ORDER BY consensus_peak_count DESC
                LIMIT 1
                """

        cursor.execute(query)
        result = cursor.fetchone()
        conn.close()

        return {
            "spectrum_id": result[0],
            "spectrum_name": result[1],
            "label_name": result[2],
            "count": result[3]
        }


class ConsensusPeakTile(QtWidgets.QWidget, Ui_ConsensusPeakTile):
    # Signal definition.
    consensusPeakActivityChanged = QtCore.Signal(int, bool)

    def __init__(self,
                 db_path: Path,
                 consensus_id: int,
                 retention_time: float,
                 drift_time: float,
                 unique_labels: int,
                 unique_spectra: int,
                 npy_path: Path,
                 is_active: bool):

        super().__init__()
        self.setupUi(self)

        self.db_path = db_path
        self.consensus_id = consensus_id
        self.retention_time = retention_time
        self.drift_time = drift_time
        self.is_active = is_active
        self.is_selected = False

        # lower the opacity of the widget if the consensus peak is inactive.
        self.opacity_effect = QGraphicsOpacityEffect()
        if not is_active:
            self.opacity_effect.setOpacity(0.3)
            self.setGraphicsEffect(self.opacity_effect)

        # Erlaube dem Custom QWidget, Hintergründe per Stylesheet zu zeichnen
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)

        # Image paths for the activity icons.
        self.icon_active = QtGui.QIcon(":/ui/_pics/icons/eye_open.png")
        self.icon_inactive = QtGui.QIcon(":/ui/_pics/icons/eye_closed.png")

        # Define the main layout of this widget and its margins.
        #self.main_layout = QtWidgets.QVBoxLayout(self)
        #self.main_layout.setContentsMargins(5, 5, 5, 5)

        # Connect to the datase and get one of the peak npy files which is connected to this consensus peak.
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        npy_file_query = "SELECT npy_file FROM peaks WHERE consensus_id = ? LIMIT 1"
        cursor.execute(npy_file_query, (consensus_id,))
        npy_file_result = cursor.fetchone()
        conn.close()

        # Define the absolute path to the npy file.
        npy_file = npy_path / npy_file_result[0]

        # Set the image to the peak image label.
        self.set_peak_tile_image(npy_file)

        # Create a button which is placed on top of the peak image.
        self.activity_button = QtWidgets.QPushButton(self.peak_window)
        self.activity_button.setFixedSize(20, 20)
        self.activity_button.move(40, 40)
        self.activity_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.activity_button.setStyleSheet("background: rgba(0,0,0,100); border: none;")
        # Set the correct peak button icon for the current peak activity.
        self.change_button_icon()
        # Connect the button.
        self.activity_button.clicked.connect(self.change_peak_activity_button)

        # Connect to the database check to how many labels and spectra this consensus peak is connected too.
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        query = """
                SELECT COUNT(DISTINCT label_id)    AS unique_labels_count,
                       COUNT(DISTINCT spectrum_id) AS unique_spectra_count
                FROM peaks
                WHERE consensus_id = ?
                """

        cursor.execute(query, (consensus_id,))
        result = cursor.fetchone()
        labels_count, spectra_count = result
        conn.close()

        # Text area of the widget.
        self.label_count_label.setText(f"In labels: {labels_count} / {unique_labels}")
        self.spectra_count_label.setText(f"In spectra: {spectra_count} / {unique_spectra}")
        self.position_label.setText(f"DT: {drift_time:.2f} | RT: {retention_time:.2f}")

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
        # Emmit a signal which will update the consensus peak entry in the database.
        self.consensusPeakActivityChanged.emit(self.consensus_id, self.is_active)


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
            border_color = "#1d1d1d"
            border_color_hover = "#555555"
            background_color = "#1d1d1d"
            background_color_hover = "#323232"

        self.setStyleSheet(f"""
                            #ConsensusPeakTile {{
                                background-color: {background_color};
                                border: 1px solid {border_color};
                                border-radius: 5px;
                            }}
                            #ConsensusPeakTile:hover {{
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
        pixmap = QtGui.QPixmap.fromImage(q_image).scaled(60, 60, QtCore.Qt.KeepAspectRatio)
        self.peak_window.setPixmap(pixmap)


class ConsensusPeakCalculationWorker(QtCore.QObject):
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
        This function overrides the run function of a thread worker and starts the consensus peak calculation process.
        =============================================================================
        :return: None.
        """

        # Calculate connected components.
        graph = calculate_connected_components(db_path=self.db_path,
                                               max_node_distance=0.006,
                                               batch_size=20000)

        # Calculate consensus peaks.
        calculate_consensus_peaks(db_path=self.db_path,
                                  graph=graph)

        # Save consensus peak npy files
        create_consensus_peak_npy(project_path=self.project_path,
                                  db_path=self.db_path,
                                  peak_radius=5)

        self.finished.emit()


def calculate_connected_components(db_path: Path,
                                   max_node_distance: float,
                                   batch_size: int) -> nx.Graph:
    """
    Not yet described ... TODO

    :param db_path: Path to the database.
    :param max_node_distance: The max. distance between nodes for the connected components calculation.
    :param batch_size: Limits the number of nodes during computation [prevents ram overflow problems].

    :return: Unidirected graph of the connected components calculation.
    """

    # Connect to the database and get all relevant peak, label and spectra information.
    conn = sqlite3.connect(db_path)
    query = """
            SELECT p.id,
                   p.ret_time,
                   p.drift_time,
                   p.intensity,
                   p.npy_file,
                   l.name AS label,
                   s.name AS spectrum
            FROM peaks p
                     JOIN labels l ON p.label_id = l.id
                     JOIN spectra s ON p.spectrum_id = s.id
            WHERE p.is_active = 1
            """

    peak_dataframe = pd.read_sql_query(query, conn)

    # normalize the retention and drifttime
    scaler = MinMaxScaler()
    times_normalized = scaler.fit_transform(peak_dataframe[['ret_time', 'drift_time']].values)

    # Initialize a graph.
    graph = nx.Graph()
    unique_coords = {}

    # Wir iterieren durch das DataFrame und nutzen times_normalized für die Koordinate
    for idx in range(len(peak_dataframe)):
        node = tuple(times_normalized[idx])
        peak_data = peak_dataframe.iloc[idx]

        # Finde alle Peaks mit identischer Koordinate (Original-Logik)
        # Wir suchen im Original-DF nach gleichen Zeiten
        peak_count_df = peak_dataframe[(peak_dataframe['ret_time'] == peak_data['ret_time']) &
                                       (peak_dataframe['drift_time'] == peak_data['drift_time'])]

        # Metadaten extrahieren
        labels = peak_count_df['label'].to_list()
        npy_files = peak_count_df['npy_file'].to_list()
        db_ids = peak_count_df['id'].to_list()
        spectrum_names = peak_count_df['spectrum'].to_list()
        intensities = peak_count_df['intensity'].to_list()

        # Knoten hinzufügen (überschreibt existierende Knoten mit gleichen Koordinaten,
        # fügt aber durch die Listen-Logik oben alle Informationen zusammen)
        graph.add_node(node_for_adding=node,
                       labels=labels,
                       npy_files=npy_files,
                       db_ids=db_ids,
                       ret_time=peak_data['ret_time'],
                       drift_time=peak_data['drift_time'],
                       peak_count=len(peak_count_df),
                       spectrum_names=spectrum_names,
                       intensities=intensities)

    # 4. KDTree & Kanten (wie gehabt)
    tree = KDTree(times_normalized)
    # Number of nodes in the graph.
    node_count = graph.number_of_nodes()

    # Create edges between all nodes within a defined radius. Create batches of nodes and walk through them.
    # neighbor_nodes is a list with lists inside. The position of the list is the index of the node.
    # The inner list contains the positions of nodes which are considered the nodes neighbors.
    for start_node in range(0, node_count, batch_size):
        end_node = min(start_node + batch_size, node_count)
        sub_nodes = times_normalized[start_node:end_node]
        neighbor_nodes = tree.query_ball_point(sub_nodes, r=max_node_distance, p=2)

        for sub_node_idx, neighbors in enumerate(neighbor_nodes):
            global_idx = start_node + sub_node_idx
            node_1 = tuple(times_normalized[global_idx])
            for neighbor_idx in neighbors:
                node_2 = tuple(times_normalized[neighbor_idx])
                if not node_1 == node_2:
                    graph.add_edge(node_1, node_2)

    # 5. Connected Components & DB-Update Vorbereitung
    connected_components = list(nx.connected_components(graph))
    db_update_data = []

    for component_idx, component in enumerate(connected_components):
        for node in component:
            node_data = graph.nodes[node]
            for p_id in node_data['db_ids']:
                db_update_data.append((component_idx, p_id))

    # 6. Batch-Update in der DB
    cursor = conn.cursor()
    try:
        # Reset all old consensus_ids
        cursor.execute("UPDATE peaks SET consensus_id = NULL")
        cursor.execute("DELETE FROM consensus_peaks")
        cursor.executemany("UPDATE peaks SET consensus_id = ? WHERE id = ?", db_update_data)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database Error: {e}")
        conn.rollback()
    finally:
        conn.close()

    return graph


def calculate_consensus_peaks(db_path: Path,
                              graph: nx.Graph) -> None:
    """
    Not yet described ... TODO

    :param db_path: Path to the database.
    :param graph: Unidirected graph with all peaks as nodes.

    :return: List with consensus peak dictionaries [One dictionary per consensus peak].
    """

    # List of all connected components.
    components = list(nx.connected_components(graph))
    # List of dictionaries with consensus peak information (returned by this function).
    consensus_peaks = []

    # Walk through all components.
    for component_idx, component in enumerate(components):
        # Create a temporary dictionary which counts the occurrences of each label per component.
        temp_dictionary = defaultdict(int)
        total_peaks = 0

        # Create a peak dictionary and fill it with peak and label information.
        peak_dictionary = {}

        # Create lists with all retention and drift times for the current component.
        ret_times = []
        drift_times = []
        min_intensity = -1

        # Walk through each node.
        for node in component:
            # Get all labels of this node
            # If multiple labels are there, it means that this node consists of multiple peaks.
            node_data = graph.nodes[node]
            labels = node_data['labels']

            if min_intensity == -1 or min_intensity > min(node_data['intensities']):
                min_intensity = min(node_data['intensities'])

            # Each label represents one peak of this node. This loop makes sure that each peak of a node is
            # considered for the consensus peak calculation.
            for label in labels:
                ret_times.append(node_data['ret_time'])
                drift_times.append(node_data['drift_time'])
                temp_dictionary[label] += 1
                total_peaks += 1

        # TODO - Experimental
        # Skip a component, if it only consists of x peaks. This removes rare encountered peaks.
        if total_peaks <= 5:
            continue

        # Calculate the consensus peak retention and drift time.
        mean_ret_time = sum(ret_times) / len(ret_times)
        mean_drift_time = sum(drift_times) / len(drift_times)

        # Insert consensus peak information to the peak_dictionary.
        peak_dictionary["id"] = component_idx
        peak_dictionary["ret_time"] = mean_ret_time
        peak_dictionary["drift_time"] = mean_drift_time
        peak_dictionary["min_intensity"] = min_intensity

        # Append a dictionary to the list.
        consensus_peaks.append(peak_dictionary)

    consensus_peaks_dataframe = pd.DataFrame(consensus_peaks)

    # Connect to the database and save the consensus peaks.
    conn = sqlite3.connect(db_path)

    try:
        # 3. Dataframe in die SQL-Tabelle schreiben
        # Wir nutzen 'if_exists=append', da wir die Tabelle behalten, aber die Zeilen füllen wollen.
        # index=False verhindert, dass der Pandas-Index als eigene Spalte geladen wird.
        consensus_peaks_dataframe.to_sql("consensus_peaks", conn, if_exists="append", index=False)
        conn.commit()

    except Exception as e:
        print(f"Error while saving to the database: {e}")
        conn.rollback()
    finally:
        conn.close()


def create_consensus_peak_npy(project_path: Path,
                              db_path: Path,
                              peak_radius: int) -> None:

    # Connect to the database.
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Select all spectra paths, their associated label names and label ids for all spectra where the peak detection
    # process was not performed on.
    query = """
            SELECT spectra.path, labels.name, labels.id, spectra.id
            FROM spectra
                     JOIN labels ON spectra.label_id = labels.id
            """
    cursor.execute(query)
    spectra_dataset = cursor.fetchall()

    # Connect to the database and get all relevant peak, label and spectra information.
    query = "SELECT id, ret_time, drift_time, min_intensity, is_active FROM consensus_peaks"
    consensus_peaks_dataframe = pd.read_sql_query(query, conn)

    # Loop through all spectra of the dataset.
    for spectra in spectra_dataset:
        spectrum_path, label_name, label_id, spectrum_id = spectra
        spec_name = Path(spectrum_path).stem
        target_file = project_path / "dataset" / label_name / spec_name / f"{spec_name}.hdf5"
        # Load the spectrum
        spectrum = ims.Spectrum.read_hdf5(target_file)

        # 1. Spectrum normalization.
        # Keep the non normalized values for later use.
        values_non_normalized = spectrum.values.copy()
        # Normalize the spectrum [0-1].
        spectrum.normalization()

        padded_values = np.pad(
            spectrum.values,
            pad_width=peak_radius,
            mode='constant',
            constant_values=0
        )

        padded_values_non_normalized = np.pad(
            values_non_normalized,
            pad_width=peak_radius,
            mode='constant',
            constant_values=0
        )

        # Define the consensus_peaks folder.
        npy_dir = project_path / "dataset" / label_name / spec_name / "consensus_peaks"
        # Check if the directory exists, if so delete it with all it's content [clean up old stuff]
        if npy_dir.exists():
            shutil.rmtree(npy_dir)

        # Walk through all consensus peaks.
        for idx, consensus_peak in consensus_peaks_dataframe.iterrows():
            # Calculate the retention and drifttime indices from the actual times saved in the Excel file.
            ret_idx_original = np.abs(spectrum.ret_time - consensus_peak['ret_time']).argmin()
            drift_idx_original = np.abs(spectrum.drift_time - consensus_peak['drift_time']).argmin()

            # Calculate the min and max coordinates for the padded peak window.
            start_ret_idx = ret_idx_original - peak_radius
            end_ret_idx = ret_idx_original + 3 * peak_radius + 1
            start_drift_idx = drift_idx_original - peak_radius
            end_drift_idx = drift_idx_original + 3 * peak_radius + 1

            # Set the adjusted peak window (One with normalized and one with non normalized intensity values)
            peak_window_intensities = padded_values[start_ret_idx:end_ret_idx, start_drift_idx:end_drift_idx]
            peak_window_intensities_non_normalized = padded_values_non_normalized[start_ret_idx:end_ret_idx, start_drift_idx:end_drift_idx]

            if np.max(peak_window_intensities_non_normalized) >= consensus_peak['min_intensity']:
                # Create the directory if not already there.
                if not npy_dir.exists():
                    npy_dir.mkdir(parents=True, exist_ok=True)

                c_id = int(consensus_peak['id'])
                dimension = 4 * peak_radius + 1
                npy_filename = npy_dir / f"CID_{c_id}_PW_{label_name}_{spec_name}_{dimension}x{dimension}.npy"
                np.save(npy_filename, peak_window_intensities_non_normalized)

    conn.close()
