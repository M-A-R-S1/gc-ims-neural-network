from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QSize, Qt, QTimer, QLocale, Signal
from PeakExplorerWidget import Ui_PeakExplorerWidget
from dialogs import CustomMessageDialog, CustomYesNoDialog, CustomProgressDialog, CustomTwoChoiceDialog
from project_manager import *
from preprocessing import DatasetSubEntry, DatasetMainEntry, PlottingCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib import pyplot as plt
from collections import defaultdict
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
            # self.start_peak_detection()
            pass
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
        self.worker.finished.connect(self.check_processed_spectra)
        self.detection_progress_dialog.button_no.clicked.connect(self.worker.stop, type=QtCore.Qt.DirectConnection)
        self.thread.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # Start the thread.
        self.thread.start()


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
            spectrum = DatasetSubEntry(path, index, label_widget, 'peak_explorer')
            self.scrollArea_dataset_Contents.layout().insertWidget(self.scrollArea_dataset_Contents.layout().count() - 1, spectrum)
            spectrum.click_signal.connect(self.handle_spectrum_click)
            spectrum.hide()

            if self.selected_spectrum_name == spectrum.label_name.text():
                self.handle_spectrum_click(spectrum)
                self.label_preview.setText(f"{self.selected_label_name} - {self.selected_spectrum_name}")


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
        self.label_preview.setText(f"{self.selected_label_name} - {self.selected_spectrum_name}")


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
        hdf5_path = self.project_path.parent / "dataset" / self.selected_label_name / Path(spectrum_widget.spectrum_path).stem
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
        used_dataset = defaultdict(list)
        spectra_to_process = 0

        # Loop through the dataset.
        for label, spectra_paths in self.dataset.items():
            for spectrum_path in spectra_paths:
                # Get the spectrum name.
                spec_name = Path(spectrum_path).stem
                # Set the folder where the processed spectrum will be saved.
                target_folder = self.project_path / "dataset" / label / spec_name
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
                    if label not in used_dataset:
                        used_dataset[label] = []

                    # Add the spectrum to the used dataset.
                    used_dataset[label].append(spectrum_path)
                    spectra_to_process += 1


        # Send the finished signal.
        self.finished.emit()
