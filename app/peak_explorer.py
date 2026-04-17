from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QSize, Qt, QTimer, QLocale, Signal
from PeakExplorerWidget import Ui_PeakExplorerWidget
from dialogs import CustomMessageDialog, CustomYesNoDialog, CustomProgressDialog, CustomTwoChoiceDialog
from project_manager import *
from preprocessing import DatasetSubEntry, DatasetMainEntry, PlottingCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib import pyplot as plt
from collections import defaultdict
from skimage.morphology import max_tree, h_maxima, area_opening
from skimage.measure import label, regionprops
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import pandas as pd
import shutil
import ims

class PeakExplorerPage(QtWidgets.QWidget, Ui_PeakExplorerWidget):
    def __init__(self, project_path: str, project_manager: ProjectManager):
        super().__init__()
        self.setupUi(self)

        # Project save path
        self.project_path = Path(project_path)
        # The project manager
        self.project_manager = project_manager
        # Currently selected spectrum.
        self.current_selected_spectrum = None
        self.selected_spectrum_name = None
        self.selected_label_name = None
        self.current_selected_peak = None
        # Saves labels and spectra in a dictionary.
        self.dataset_storage = {}
        # Path to the peak Excel file.
        self.peaks_excel_path = self.project_path.parent / "peaks.xlsx"

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

        # Canvas plot element.
        self.canvas = PlottingCanvas(self, width=5, height=4, dpi=50)
        # Initialize the plot canvas.
        self.init_plot_canvas()
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


    def showEvent(self, event) -> None:
        """
        This function is called every time the user enters this page and checks if the peak Exel file exists.
        If the file does not exist, a peak detection dialog is prompted to the user.
        :param event: The page display event.
        =============================================================================
        :return: None
        """

        super().showEvent(event)

        if not self.peaks_excel_path.exists():
            QtCore.QTimer.singleShot(100, self.show_peak_detection_dialog)
        else:
            self.overlay.hide()



    def show_peak_detection_dialog(self) -> None:
        """
        This function is called when the peak Excel file does not exist. It creates a dialog where the user is
        prompted to start the peak detection process. If the user declines he will be redirected to the preprocessing page.
        =============================================================================
        :return: None.
        """

        dialog = CustomYesNoDialog(
            title="Peak calculation",
            message="In order to use the peak explorer you need to start the peak detection process first. Do you "
                    " want to detect the peaks of this dataset?",
            type="warning",
            parent=self
        )

        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.start_peak_detection()
        else:
            main_window = self.window()

            if hasattr(main_window, 'sb_preprocessing_button'):
                main_window.sb_preprocessing_button.click()
            else:
                print("Error: Sidebar button 'Preprocessing' not found.")


    def start_peak_detection(self):

        # Open the progress dialog which informs the user about the current state of the preprocessing.
        self.detection_progress_dialog = CustomProgressDialog("Peak detection...")
        # Reset the start time.
        self.detection_progress_dialog.start_time = None
        self.detection_progress_dialog.show()

        # Create a thread and worker for the progress dialog.
        self.thread = QtCore.QThread()
        self.worker = PeakDetectionWorker(path=self.project_path,
                                          dataset=self.dataset_storage)

        self.worker.moveToThread(self.thread)

        # Connect some signals to the worker and thread.
        self.thread.started.connect(self.worker.run)
        self.worker.progress_update.connect(self.detection_progress_dialog.update_progress)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.detection_progress_dialog.accept)
        self.worker.finished.connect(self.check_peaks)
        self.detection_progress_dialog.button_no.clicked.connect(self.worker.stop, type=QtCore.Qt.DirectConnection)
        self.thread.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # Start the thread.
        self.thread.start()


    def check_peaks(self) -> None:
        if not self.peaks_excel_path.exists():
            main_window = self.window()

            if hasattr(main_window, 'sb_preprocessing_button'):
                main_window.sb_preprocessing_button.click()
            else:
                print("Error: Sidebar button 'Preprocessing' not found.")
        else:
            self.overlay.hide()


    def load_data(self):
        """
        This function is called every time the user enters this page. It reloads all label and spectra of the dataset,
        recreates the widgets of the scroll area.
        =============================================================================
        :return: None
        """

        self.current_selected_spectrum = None
        self.label_preview.setText("Spectrum preview")

        # Clear the dataset storage and load the new one.
        self.dataset_storage.clear()
        self.dataset_storage.update(self.project_manager.get_dataset())
        # Clear the canvas.
        self.clear_canvas()

        # Remove all widgets from the scroll area to clear it.
        layout = self.scrollArea_dataset_Contents.layout()
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            widget = item.widget()

            # Check if the widget is an instance of the DatasetMainEntry or DatasetSubEntry, if so remove it from the
            # layout and delete it.
            if widget is not None and isinstance(widget, DatasetMainEntry) or isinstance(widget, DatasetSubEntry):
                layout.removeWidget(widget)
                widget.setParent(None)
                widget.deleteLater()

        # Now walk through all labels in the dataset storage and add all labels to the scroll area.
        for label_name in self.dataset_storage.keys():
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

        # Get all spectra paths for the current label.
        paths = self.dataset_storage[label_widget.label_name.text()]

        # Loop through all spectra and add them as a widget to the scroll area.
        for index, path in enumerate(paths):
            spectrum_widget = DatasetSubEntry(path, index, label_widget, 'peak_explorer')
            self.scrollArea_dataset_Contents.layout().insertWidget(self.scrollArea_dataset_Contents.layout().count() - 1, spectrum_widget)
            spectrum_widget.click_signal.connect(self.handle_spectrum_click)
            spectrum_widget.hide()

            if self.selected_spectrum_name == spectrum_widget.label_name.text():
                self.handle_spectrum_click(spectrum_widget)
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
        self.toolbar.setStyleSheet("background-color: #191919; color: white; border: none;")

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
        self.canvas.fig.tight_layout()

        self.canvas.draw()


class PeakDetectionWorker(QtCore.QObject):
    # Signal definitions.
    finished = Signal()
    progress_update = Signal(int, int)

    def __init__(self,
                 path: Path,
                 dataset: dict):

        super().__init__()
        self.dataset = dataset
        self.project_path = path.parent
        # Worker stopped signal [The user has canceled the preprocessing].
        self.worker_stopped = False

    @QtCore.Slot()
    def stop(self):
        self.worker_stopped = True


    def run(self):
        # Create a new dataset list of labels and spectra which should be preprocessed.
        peak_data = []

        processed_spectra = 0
        # The total number of spectra of the dataset.
        total_spectra = sum(len(spectra) for spectra in self.dataset.values())

        # Loop through the dataset.
        for label, spectra_paths in self.dataset.items():
            for spectrum_path in spectra_paths:

                # Check during each loop if the user wants so cancel the processing.
                QtCore.QCoreApplication.processEvents()
                if self.worker_stopped:
                    self.finished.emit()
                    return

                # Get the spectrum name.
                spec_name = Path(spectrum_path).stem
                # Get the saved hdf5 file.
                target_folder = self.project_path / "dataset" / label / spec_name
                target_file = target_folder / f"{spec_name}.hdf5"
                # Save the spectrum from the hdf5 file.
                spectrum = ims.Spectrum.read_hdf5(target_file)

                # Start the peak detection process.
                peak_data.extend(self.peak_detection(spectrum=spectrum,
                                                     label_name=label,
                                                     peak_radius=5,
                                                     spectrum_path=spectrum_path))

                processed_spectra += 1
                self.progress_update.emit(processed_spectra, total_spectra)

        # Convert the peak_data list to a pandas dataframe.
        peak_dataframe = pd.DataFrame(peak_data)
        # Save peak data to Excel file.
        excel_file = self.project_path / "peaks.xlsx"
        print(excel_file)
        peak_dataframe.to_excel(excel_file, index=False)

        # Send the finished signal.
        self.finished.emit()

    def peak_detection(self,
                       spectrum: ims.Spectrum,
                       label_name: str,
                       peak_radius: int,
                       spectrum_path: Path) -> list[dict]:
        """
        This function handles the peak detection for preprocessed gc-ims spectra in a series of steps.
        1. Normalization of the spectrum to values between 0 and 1.
        2. Create a component tree of the spectrum and detect hierarchy levels.
        3. Filter peaks from the component tree according to specific conditions [Area Opening, intensity threshold, tree hierarchy].
        4. Create a plot with all selected peaks for each spectrum.
        5. Save the intensities of each detected peak and its surrounding (defined by peak_radius) as a .npy file.
        6. Return a list of dictionaries. One dictionary for each peak + surrounding with the following information.
            - 'label' -> The label/type of the used spectrum.
            - 'spectrum' -> Name of the spectrum.
            - 'ret_time' -> Retention time [s] of the peak.
            - 'drift_time' -> Drift time [ms] of the peak.
            - 'intensity' -> Intensity [not normalized] of peak + surrounding.
            - 'npy_file' -> Path to the saved npy file of this peak.

        :param spectrum: A single preprocessed gc-ims spectrum.
        :param peak_radius: Defines the radius around a detected peak within the intensities are saved.
        :param output_dir: Saving path for the plotting image.
        :param create_heatmaps: Specifies if heatmaps are created.
        :param create_npy: Specifies if npy files are created.

        :return: List of dictionaries which contain peak + surrounding information.
        """

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
                    npy_dir = Path(label_name) / spectrum.name / "peaks"
                    if not npy_dir.exists():
                        npy_dir.mkdir(parents=True, exist_ok=True)

                    npy_filename = npy_dir / f"PW_{spectrum.name}_RT{ret_idx}_DT{drift_idx}_{6 * peak_radius + 1}x{6 * peak_radius + 1}.npy"
                    np.save(npy_filename, peak_window)

                    # Dictionary with information about peaks.
                    peak_data = {
                        'label': label_name,
                        'spectrum': spectrum.name,
                        'ret_time': spectrum.ret_time[ret_idx],
                        'drift_time': spectrum.drift_time[drift_idx],
                        'intensity': spectrum.values[ret_idx, drift_idx],
                        'npy_file': npy_filename,
                    }
                    spectrum_peak_data.append(peak_data)

                # Notify that the peak detection on this spectrum is finished and print the number of peaks.
                print(f"\t- {len(peak_coords)} Peaks saved [{spectrum.name}]")

            else:
                # Notify that the peak detection on this spectrum is finished and print the number of peaks.
                print(f"\t- No Peaks saved [{spectrum.name}]")

        except Exception as err:
            print(f"\tError on {spectrum.name} - Skipped: {err=}, {type(err)=}")
            raise

        return spectrum_peak_data
