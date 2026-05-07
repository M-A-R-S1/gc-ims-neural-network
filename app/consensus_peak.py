from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtWidgets import QGraphicsOpacityEffect
from PySide6.QtCore import QSize, Qt, Signal, QTimer
from ConsensusPeakWidget import Ui_ConsensusPeakWidget
from dialogs import CustomYesNoDialog, CustomProgressDialog
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

class ConsensusPeakPage(QtWidgets.QWidget, Ui_ConsensusPeakWidget):
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
        #self.canvas.mpl_connect('pick_event', self.on_canvas_pick)
        #self.canvas.mpl_connect('motion_notify_event', self.on_canvas_hover)
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
        This function is called every time the user enters this page and checks if all peaks are connected to a consensus peak inside the database.
        If peaks are not connected a consensus peak detection dialog is prompted to the user.
        =============================================================================
        :param event: The page display event.
        =============================================================================
        :return: None
        """

        super().showEvent(event)
        # Check if all peaks are connected to a consensus peak.
        self.check_speaks_for_consensus()


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
            message="Some of the peaks are not associated with a consensus peak. You need to start the consensus peak calculation process first. Do you "
                    " want to calculate the consensus peaks?",
            type="warning",
            parent=self
        )

        # If the user accepted the dialog, call the start_peak_detection method.
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.start_consensus_peak_calculation()
            # TODO ... Methode gibt es noch nicht.
        else:
            main_window = self.window()
            # The user declined the calculation -> Redirect to the peaks page.
            if hasattr(main_window, 'sb_peak_explorer_button'):
                main_window.sb_peak_explorer_button.click()
            else:
                print("Error: Sidebar button 'Peak Explorer' not found.")



    def check_speaks_for_consensus(self) -> None:
        """
        This function checks if all peaks inside the database are associated with a consensus peak id.
        If peaks are missing this id the consensus peak detection dialog is shown to the user.
        =============================================================================
        :return: None.
        """

        # Connect to the database and get the number of peaks where the consensus id is NULL.
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM peaks WHERE consensus_id IS NULL")
        peaks_without_consensus = cursor.fetchone()[0]

        # If there are peaks without a consensus id show the user the "consensus peak calculation dialog".
        if peaks_without_consensus > 0:
            QtCore.QTimer.singleShot(100, self.show_consensus_peak_calc_dialog)
        else:
            self.overlay.hide()

        conn.close()


    def load_data(self):
        """
        This function is called every time the user enters this page. It reloads all label and spectra of the dataset
        and recreates the widgets of the scroll area.
        =============================================================================
        :return: None
        """

        self.current_selected_spectrum = None
        self.label_preview.setText("Spectrum preview")

        # Clear the canvas.
        self.clear_canvas()

        # Connect to the database.
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM labels", )
        labels_data = cursor.fetchall()

        # TODO ...
        # Load consensus peak data from the database


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


class ConsensusPeakTileWidget(QtWidgets.QFrame):
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

        # Image paths for the activity icons.
        self.icon_active = QtGui.QIcon("ui/_pics/icons/eye_open.png")
        self.icon_inactive = QtGui.QIcon("ui/_pics/icons/eye_closed.png")

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
        self.activity_button.move(58, 50)
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