from __future__ import annotations
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtGui import QDoubleValidator
from PySide6.QtCore import QSize, Qt, QTimer, QLocale, Signal
from dialogs import CreateLabelDialog, CustomMessageDialog, CustomYesNoDialog, RenameLabelDialog
from PreprocessingWidget import Ui_PreprocessingWidget
from DatasetSubEntry import Ui_DatasetSubEntry
from DatasetMainEntry import Ui_DatasetMainEntry
from pathlib import Path
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib import pyplot as plt
from project_manager import *
import ims
import json


class PreprocessingPage(QtWidgets.QWidget, Ui_PreprocessingWidget):
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
        # Saves labels and spectra in a dictionary.
        self.dataset_storage = {}

        # Defining the scroll area layouts.
        self.scrollArea_dataset_Contents.layout().setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.scrollArea_dataset_Contents.layout().setSpacing(5)
        self.scrollArea_dataset.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        retention_validator = QDoubleValidator(0, 1200, 0)
        retention_validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        self.lineEdit_retention_start_cut.setValidator(retention_validator)
        self.lineEdit_retention_end_cut.setValidator(retention_validator)

        drift_validator = QDoubleValidator(0.0, 3.0, 3)
        drift_validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        drift_validator.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        self.lineEdit_drift_start_cut.setValidator(drift_validator)
        self.lineEdit_drift_end_cut.setValidator(drift_validator)

        self.cut_timer = QTimer()
        self.cut_timer.setSingleShot(True)
        self.cut_timer.timeout.connect(self.update_cut_lines)

        self.lineEdit_retention_start_cut.textChanged.connect(lambda: self.cut_timer.start(500))
        self.lineEdit_retention_end_cut.textChanged.connect(lambda: self.cut_timer.start(500))
        self.lineEdit_drift_start_cut.textChanged.connect(lambda: self.cut_timer.start(500))
        self.lineEdit_drift_end_cut.textChanged.connect(lambda: self.cut_timer.start(500))

        self.canvas_fullscreen = True
        self.pushButton_toggle_canvas_area.clicked.connect(self.handle_canvas_toggle)

        # Canvas plot element.
        self.canvas = PlottingCanvas(self, width=5, height=4, dpi=50)
        # Initialize the plot canvas.
        self.init_plot_canvas()

        # load dataset from project.
        self.load_data()


    def load_dataset(self) -> None:
        """
        This function is called the first time the dataset page is loaded. This function reads all previously saved
        labels and spectra and loads them into the dataset storage. Each label is then created as a widget for the
        label scroll area.
        =============================================================================
        :return: None.
        """
        try:
            # load all label and spectra data from the project .gcimsp file.
            with open(self.project_path, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)

            # clear the dataset storage and override it with the loaded labels and spectra.
            self.dataset_storage.clear()
            self.dataset_storage.update(loaded_data)

            # Walk through all labels in the dataset storage and add them as label widgets to the label scroll area.
            for label_name in self.dataset_storage.keys():
                self.add_label(label_name)

        except Exception as e:
            # Display an error dialog - Something went wrong while loading the data.
            CustomMessageDialog.show_error("Error - Loading", "Something went wrong while loading the dataset!", self)
            print(f"Dataset loading error: {e}")


    def save_data(self):
        region_of_interest = { "rt_start": self.lineEdit_retention_start_cut.text() or 0,
                                "rt_end": self.lineEdit_retention_end_cut.text() or 0,
                                "dt_start": self.lineEdit_drift_start_cut.text() or 0,
                                "dt_end": self.lineEdit_drift_end_cut.text() or 0}

        self.project_manager.save_preprocessing(region_of_interest)


    def load_data(self):
        """Setzt die UI-Werte aus dem geladenen Dictionary."""

        self.current_selected_spectrum = None

        # 1. Den aktuellen Speicher leeren
        self.dataset_storage.clear()
        # 2. Mit den neuen Daten füllen
        self.dataset_storage.update(self.project_manager.get_dataset())
        # Clear the canvas.
        self.clear_canvas()

        # Remove all widgets.
        layout = self.scrollArea_dataset_Contents.layout()
        # Remove all widgets from the spectra scroll area.
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            widget = item.widget()

            # Prüfen, ob ein Widget existiert UND ob es die richtige Klasse ist
            if widget is not None and isinstance(widget, DatasetMainEntry) or isinstance(widget, DatasetSubEntry):
                layout.removeWidget(widget)  # Aus dem Layout nehmen
                widget.setParent(None)  # Sofort vom Parent trennen
                widget.deleteLater()  # Speicher freigeben

        # Walk through all labels in the dataset storage and add them as label widgets to the label scroll area.
        for label_name in self.dataset_storage.keys():
            self.add_label(label_name)

        cutting_data = self.project_manager.get_preprocessing()
        self.lineEdit_retention_start_cut.setText(str(cutting_data.get("rt_start", "")))
        self.lineEdit_retention_end_cut.setText(str(cutting_data.get("rt_end", "")))
        self.lineEdit_drift_start_cut.setText(str(cutting_data.get("dt_start", "")))
        self.lineEdit_drift_end_cut.setText(str(cutting_data.get("dt_end", "")))


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

        paths = self.dataset_storage[label_widget.label_name.text()]

        for index, path in enumerate(paths):
            spectrum = DatasetSubEntry(path, index, label_widget)
            self.scrollArea_dataset_Contents.layout().insertWidget(self.scrollArea_dataset_Contents.layout().count() - 1, spectrum)
            spectrum.click_signal.connect(self.handle_spectrum_click)
            spectrum.hide()

            if self.selected_spectrum_name == spectrum.label_name.text():
                self.handle_spectrum_click(spectrum)




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

        if label_widget.extended:
            label_widget.extend_label(False)

            for index in range(self.scrollArea_dataset_Contents.layout().count()):
                item = self.scrollArea_dataset_Contents.layout().itemAt(index)
                widget = item.widget()
                if isinstance(widget, DatasetSubEntry):
                    if widget.parent == label_widget:
                        widget.hide()

            self.selected_label_name = None

        else:
            label_widget.extend_label(True)

            for index in range(self.scrollArea_dataset_Contents.layout().count()):
                item = self.scrollArea_dataset_Contents.layout().itemAt(index)
                widget = item.widget()
                if isinstance(widget, DatasetSubEntry):
                    if widget.parent == label_widget:
                        widget.show()

            self.selected_label_name = label_widget.label_name.text()




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
        #self.update_cut_lines()


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


    def update_cut_lines(self):
        # 1. Den Plot säubern (aber nur die Linien, nicht das ganze Bild, falls möglich)
        # Einfacher für den Anfang: Den Plot neu zeichnen oder vorhandene Linien entfernen
        for line in getattr(self, 'temp_cut_lines', []):
            line.remove()
        self.temp_cut_lines = []

        # 2. Werte aus den LineEdits holen (mit Fehlerbehandlung, falls leer)
        try:
            r_start = float(self.lineEdit_retention_start_cut.text() or 0)
            r_end = float(self.lineEdit_retention_end_cut.text() or 0)
            d_start = float(self.lineEdit_drift_start_cut.text() or 0)
            d_end = float(self.lineEdit_drift_end_cut.text() or 0)
        except ValueError:
            return  # Falls der User Buchstaben tippt

        # Save the values
        self.save_data()

        # 3. Linien zeichnen (z.B. in Rot und gestrichelt)
        ax = self.canvas.axes
        style = {'color': '#da05ab', 'linestyle': '--', 'linewidth': 3, 'alpha': 0.8}

        if r_start > 0:
            self.temp_cut_lines.append(ax.axhline(y=r_start, **style))
        if r_end > 0:
            self.temp_cut_lines.append(ax.axhline(y=r_end, **style))
        if d_start > 0:
            self.temp_cut_lines.append(ax.axvline(x=d_start, **style))
        if d_end > 0:
            self.temp_cut_lines.append(ax.axvline(x=d_end, **style))

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


        if not self.canvas_fullscreen:
            ax = self.canvas.axes
            ax.set_xlim(d_start, d_end)
            ax.set_ylim(r_start, r_end)

            # 4. Canvas aktualisieren
        self.canvas.draw()


    def handle_canvas_toggle(self):
        if self.canvas_fullscreen:
            self.canvas_fullscreen = False
            self.zoom_to_cut()
            self.pushButton_toggle_canvas_area.setText("Show full spectrum")
        else:
            self.canvas_fullscreen = True
            self.reset_zoom()
            self.pushButton_toggle_canvas_area.setText("Show cutted spectrum")


    def handle_spectrum_click(self, spectrum_widget: DatasetSubEntry):
        self.plot_spectrum(spectrum_widget)
        self.selected_spectrum_name = spectrum_widget.label_name.text()

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


    def zoom_to_cut(self):
        # 1. Werte aus den LineEdits holen
        # Wir nutzen 0 als Fallback, falls ein Feld leer ist
        d_start = float(self.lineEdit_drift_start_cut.text())
        d_end = float(self.lineEdit_drift_end_cut.text())
        r_start = float(self.lineEdit_retention_start_cut.text())
        r_end = float(self.lineEdit_retention_end_cut.text())

        # 2. Die Achsenbegrenzungen setzen
        ax = self.canvas.axes
        ax.set_xlim(d_start, d_end)
        ax.set_ylim(r_start, r_end)  # Beachte: Bei IMS oft r_end unten, r_start oben?
        # Matplotlib spiegelt das, falls nötig.

        # 3. Canvas aktualisieren
        self.update_cut_lines()


    def reset_zoom(self):
        ax = self.canvas.axes
        ax.autoscale(enable=True, axis='both', tight=True)
        self.update_cut_lines()


class DatasetMainEntry(QtWidgets.QLabel, Ui_DatasetMainEntry):
    # Signal definitions
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
            self.button_open_close.setIcon(QtGui.QIcon(f'ui/_pics/icons/chevron_down_white.png'))
            self.extended = True
            self.label_name.setStyleSheet("border: None; color: #ff9000; background-color: transparent; font-weight: bold;")
        else:
            self.button_open_close.setIcon(QtGui.QIcon(f'ui/_pics/icons/chevron_right_white.png'))
            self.extended = False
            self.label_name.setStyleSheet("border: None; color: #ebebeb; background-color: transparent; font-weight: light;")




class DatasetSubEntry(QtWidgets.QWidget, Ui_DatasetSubEntry):
    # Signal definitions
    click_signal = QtCore.Signal(object)

    def __init__(self, path: str, index: int, parent: DatasetMainEntry):
        super().__init__()
        self.setupUi(self)

        # Parent entry widget.
        self.parent = parent
        # Spectrum save path.
        self.spectrum_path = path
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
        :param active: True if a spectrum widget is selected, False if a sspectrum widget is deselected.
        =============================================================================
        :return: None.
        """

        # Sets the spectrum stylesheet depending on the state [active = currently selected | not active = not selected]
        if active:
            self.label_name.setStyleSheet("border: None; color: #ff9000; background-color: transparent; font-weight: bold;")
        else:
            self.label_name.setStyleSheet("border: None; color: #ebebeb; background-color: transparent; font-weight: light;")



class PlottingCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=50):
        # Basic settings for the plot canvas.
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.fig.tight_layout()
        super().__init__(self.fig)



class PreprocessingWorker(QtCore.QObject):
    # Signale für die Kommunikation mit der GUI
    progress_update = Signal(int, int, int)
    finished = Signal(tuple)  # Übergibt am Ende (preprocessed_data, spectra_paths)

    def __init__(self, input_dir, output_dir, drift_cut, retention_cut):
        super().__init__()
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.drift_cut = drift_cut
        self.retention_cut = retention_cut

    def run(self):
        # Hier rufst du einfach deine bestehende Funktion auf!
        # Tipp: Du könntest in deine 'start' Funktion ein Callback einbauen,
        # um echte Prozentwerte zu senden.

        try:
            # Deine Funktion (importiert aus deinem alten Skript)
            results = start(
                input_dir=self.input_dir,
                output_dir=self.output_dir,
                drift_cut=self.drift_cut,
                retention_cut=self.retention_cut
            )
            self.finished.emit(results)
        except Exception as e:
            print(f"Preprocessing error: {e}")
            self.finished.emit(([], []))