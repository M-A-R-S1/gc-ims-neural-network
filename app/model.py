from __future__ import annotations
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtCore import QSize, Qt, QTimer
from ui.neural_network_ui.ModelWidget import Ui_ModelWidget
from ui.neural_network_ui.ModelTile import Ui_ModelTile
from ui.neural_network_ui.ModelReconTile import Ui_ModelReconTile
from dialogs import CustomYesNoDialog, CustomProgressDialog, RenameLabelDialog, CustomMessageDialog
import sqlite3
from pathlib import Path
from matplotlib import pyplot as plt
from matplotlib import cm
from preprocessing import PlottingCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from misc.utils import get_resource_path
import ims
import torch
import re
import misc.vae_model
import misc.dataloader
from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split
import numpy as np

class ModelPage(QtWidgets.QWidget, Ui_ModelWidget):
    def __init__(self, project_path: Path):
        super().__init__()
        self.setupUi(self)

        # Project save path.
        self.project_path = Path(project_path)
        # Database path.
        self.db_path = self.project_path.parent / "database" / "project_database.db"

        # Show peak marker on the canvas? [True or False].
        self.show_peak_marker = True
        # Connect the button to the toggle methode.
        self.pushButton_toggle_peak_marker.clicked.connect(self.toggle_peak_markers)
        self.consensus_peak_widgets = {}
        self.selected_consensus_peak_id = None
        self.selected_model_tile = None
        self.best_spectrum = None

        # ScrollArea-Layout oben ausrichten, damit Modelle nicht vertikal zentriert schweben
        if self.scrollArea_models_Contents.layout() is not None:
            self.scrollArea_models_Contents.layout().setAlignment(QtCore.Qt.AlignTop)

        # Initiale Modelle laden
        self.load_models_to_scrollarea()
        self.load_available_devices_to_combobox()
        self.update_peak_count_info()

        self.pushButton_train_model.clicked.connect(self.on_start_training_clicked)

        # Defining the scroll area layout.
        self.scrollArea_recon_Contents.layout().setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.scrollArea_recon_Contents.layout().setSpacing(5)
        self.scrollArea_recon.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scrollArea_recon_Contents.layout().setSpacing(10)

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
        self.clear_data()


    def resizeEvent(self, event) -> None:
        """
        This function overrides the resizeEvent method and resizes the overlay widget always to the size of the main window.
        =============================================================================
        :param event: The resizing event.
        =============================================================================
        :return: None.
        """

        super().resizeEvent(event)
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
        This function is called every time the user enters this page.
        =============================================================================
        :param event: The page display event.
        =============================================================================
        :return: None
        """

        super().showEvent(event)
        self.best_spectrum = self.get_spectrum_with_most_consensus_peaks()
        self.load_consensus_peaks()
        self.load_models_to_scrollarea()


    def clear_data(self):
        self.selected_consensus_peak_id = None
        self.consensus_peak_widgets = {}
        self.label_preview.setText("Spectrum preview")

        # Clear the canvas.
        self.clear_canvas()


    def load_consensus_peaks(self) -> None:
        """
        This function is called when this page is loaded.
        It displays all consensus peaks as widgets in the peak scroll area.
        =============================================================================
        :return: None.
        """

        # Clear the consensus peak widget dictionary.
        self.clear_canvas()
        self.clear_peak_markers()

        # Clear the old layout before the new peaks are added to the scroll area.
        self.clear_layout(self.scrollArea_recon_Contents.layout())

        # Connect to the database and get all peaks from the selected spectrum.
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        query = "SELECT id, ret_time, drift_time, min_intensity FROM consensus_peaks ORDER BY drift_time"
        cursor.execute(query)
        consensus_peaks_data = cursor.fetchall()
        conn.close()

        # The number of columns inside the scroll area.
        max_columns = 2
        index_skipped = 0

        # Loop through all peaks.
        for index, (consensus_id, retention_time, drift_time, min_intensity) in enumerate(consensus_peaks_data):
            # The path to the peak .npy file.
            absolute_npy_path = Path(self.project_path).parent / "dataset" / self.best_spectrum['label_name'] / self.best_spectrum['spectrum_name'] / "consensus_peaks"
            absolute_npy_file = absolute_npy_path / f"CID_{consensus_id}_PW_{self.best_spectrum['label_name']}_{self.best_spectrum['spectrum_name']}_21x21.npy"

            if absolute_npy_file.exists():
                # Calculate the position of the peak widget inside the peak scroll area.
                row = (index - index_skipped) // max_columns
                column = (index - index_skipped) % max_columns

                # Create the consensus peak widget tile and add it to the scroll area.
                consensus_peak_tile = ModelReconTile(db_path=self.db_path,
                                                     consensus_id=consensus_id,
                                                     retention_time=retention_time,
                                                     drift_time=drift_time,
                                                     npy_file=absolute_npy_file)

                # Add the consensus peak to the dictionary.
                self.consensus_peak_widgets[consensus_id] = consensus_peak_tile
                # Add a mouse click event listener to the peak tile.
                consensus_peak_tile.mousePressEvent = lambda event, peak_id=consensus_id: self.on_peak_tile_clicked(peak_id)
                # Add the peak widget to the scroll area.
                self.scrollArea_recon_Contents.layout().addWidget(consensus_peak_tile, row, column)
            else:
                index_skipped += 1

        self.scrollArea_recon_Contents.layout().setRowStretch(self.scrollArea_recon_Contents.layout().rowCount(), 1)
        self.scrollArea_recon_Contents.layout().setColumnStretch(max_columns, 1)

        # Plot the clicked spectrum to the canvas.
        self.plot_spectrum()
        self.canvas.draw()


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

        # Path to the hdf5 file.
        hdf5_path = self.project_path.parent / "dataset" / self.best_spectrum['label_name'] / self.best_spectrum['spectrum_name']
        hdf5_file = hdf5_path / f"{self.best_spectrum['spectrum_name']}.hdf5"
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

        filtered_peaks = [p for p in peak_times if p[0] in self.consensus_peak_widgets]

        # If there are peaks mark them on the plot canvas.
        if filtered_peaks and self.show_peak_marker:
            # Extract peak information.
            peak_ids = [p[0] for p in filtered_peaks]
            retention_time = [p[1] for p in filtered_peaks]
            drift_time = [p[2] for p in filtered_peaks]
            is_active = [p[3] for p in filtered_peaks]

            # Color list for the peak markers depending on their selection.
            colors = []
            for peak_id, activity in zip(peak_ids, is_active):
                if peak_id == self.selected_consensus_peak_id:
                    colors.append('#ff9000')
                else:
                    colors.append('#00eaff')

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
            self.pushButton_toggle_peak_marker.setText("Show markers")
        else:
            self.show_peak_marker = True
            self.pushButton_toggle_peak_marker.setText("Hide markers")

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
            self.scrollArea_recon.ensureWidgetVisible(self.consensus_peak_widgets[consensus_peak_id])

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
                       p.consensus_id,
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
            "consensus_id": result[1],
            "spectrum_name": result[2],
            "label_name": result[3],
            "count": result[4]
        }


    def load_models_to_scrollarea(self):
        """
        Liest alle .pt Dateien aus dem 'models' Ordner und fügt sie als
        Tiles in die ScrollArea ein.
        """

        models_dir = get_resource_path("models")
        layout = self.scrollArea_models_Contents.layout()
        self.selected_model_tile = None

        # Falls das Widget im Designer versehentlich noch kein Layout bekommen hat:
        if layout is None:
            layout = QtWidgets.QVBoxLayout(self.scrollArea_models_Contents)
            layout.setAlignment(QtCore.Qt.AlignTop)

        # 1. Alte Tiles löschen (wichtig, wenn man diese Methode später aktualisieren will)
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # 2. Prüfen ob Ordner existiert
        if not models_dir.exists():
            print(f"Warnung: Models-Ordner nicht gefunden unter {models_dir.resolve()}")
            return

        # 3. Alle .pt Dateien finden und als Tiles anlegen
        for file_path in models_dir.glob("*.pt"):
            file_name = file_path.stem

            # Tile instanziieren
            tile = ModelTileWidget(file_name)

            # Klick-Event mit der Methode unten verknüpfen
            tile.tile_clicked.connect(self.on_model_selected)
            tile.delete_clicked.connect(self.on_delete_model)
            tile.rename_clicked.connect(self.on_rename_model)

            # Ins Layout packen
            layout.addWidget(tile)

            if self.selected_model_tile is None:
                self.on_model_selected(tile)

    def on_model_selected(self,
                          tile_widget: ModelTileWidget) -> None:
        """
        Wird aufgerufen, sobald der User auf ein Modell in der linken Liste klickt.
        """

        # Deselect the last selected tile and remove the highlight effect from the scroll area.
        if self.selected_model_tile:
            self.selected_model_tile.set_selected(False)

        # Set the highlight to the currently clicked tile.
        self.selected_model_tile = tile_widget
        self.selected_model_tile.set_selected(True)

        # 1. Das PyTorch Modell instanziieren (Parameter ggf. an dein Training anpassen!)
        self.current_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.current_vae_model = misc.vae_model.VariationalAutoencoderCNN(
            input_layers=1,
            hidden_layers=64,
            latent_dimension=16
        ).to(self.current_device)

        model_dir = get_resource_path("models")
        # 2. Die Gewichte (.pt Datei) laden
        self.current_vae_model.load_model(model_dir=model_dir, file_name=f"{tile_widget.name}.pt", device=self.current_device)

        # 3. WICHTIG: Das Modell in den Evaluierungs-Modus setzen (deaktiviert Dropout etc.)
        self.current_vae_model.eval()

        # 4. Alle Bilder auf der rechten Seite aktualisieren
        self.update_all_reconstructions()


    def on_delete_model(self,
                        model_widget: ModelTileWidget) -> None:

        # Get the name of the model.
        model_name = model_widget.name
        # Define a Yes/No Dialog for the deletion.
        dialog = CustomYesNoDialog(title="Delete model",
                                   message=f"Are you sure you want to delete this model'{model_name}'?",
                                   type="warning",
                                   parent=self)

        # The user wants to delete the classification.
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:

            # Try to delete the model file from the "model" folder.
            try:
                model_file = get_resource_path("models") / f"{model_name}.pt"
                if model_file.exists():
                    model_file.unlink()
            except Exception as e:
                print(f"Error while deleting: {e}")

            # Reload the model list.
            self.load_models_to_scrollarea()


    def on_rename_model(self,
                        model_widget: ModelTileWidget) -> None:

        # Create the rename dialog.
        dialog = RenameLabelDialog(model_widget.label_name.text(), self)

        # The user chooses to rename the label.
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            # get the new label name from the dialog data.
            new_model_name = dialog.get_data()['name']

            # If the old and the new name are the same skip renaming.
            if new_model_name == model_widget.label_name.text():
                return

            # Duplikation check.
            new_file_path = get_resource_path("models") / f"{new_model_name}.pt"
            if new_file_path.exists():
                CustomMessageDialog.show_error("Error - Duplication",
                                               f"A model with the name '{new_model_name}' already exists. Please choose another name.")
                model_widget.label_name.setText(model_widget.old_label_name)
                return

            # Change the actual file name.
            old_model_name = model_widget.label_name.text()
            old_file_path = get_resource_path("models") / f"{old_model_name}.pt"
            if old_file_path.exists():
                old_file_path.rename(new_file_path)

            # Change the name for the model on all classifications which used this model.
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                           UPDATE classifier
                           SET model = ?
                           WHERE model = ?
                           """, (new_model_name, old_model_name))
            conn.commit()
            conn.close()

            # Display the new name.
            model_widget.label_name.setText(new_model_name)
            model_widget.old_label_name = new_model_name
            model_widget.name = new_model_name


    def numpy_to_qimage(self, peak_data: np.ndarray) -> QtGui.QImage:
        """
        Wandelt ein 2D-Numpy Array in ein eingefärbtes QImage um.
        """
        # Werte zwischen 0 und 255 normalisieren
        if peak_data.max() > peak_data.min():
            normalized_peak_data = (peak_data - peak_data.min()) / (peak_data.max() - peak_data.min()) * 255
        else:
            normalized_peak_data = peak_data * 0

        image_data = normalized_peak_data.astype(np.uint8)
        height, width = image_data.shape

        # Colormap anwenden (Nutze die moderne Methode von matplotlib)
        color_map = plt.colormaps.get_cmap('RdBu_r')

        # Bild erstellen
        q_image = QtGui.QImage(image_data.data, width, height, width, QtGui.QImage.Format_Indexed8)

        # Farbpalette anwenden
        qt_color_table = []
        for i in range(256):
            rgba = color_map(i)
            qt_color_table.append(QtGui.qRgb(
                int(rgba[0] * 255),
                int(rgba[1] * 255),
                int(rgba[2] * 255)
            ))
        q_image.setColorTable(qt_color_table)

        return q_image


    def update_all_reconstructions(self):
        """
        Geht durch alle angezeigten Consensus-Peaks auf der rechten Seite und generiert
        die Rekonstruktion mit dem aktuell ausgewählten VAE-Modell neu.
        """
        # Wenn noch kein Modell geklickt wurde, brechen wir ab
        if not hasattr(self, "current_vae_model") or self.current_vae_model is None:
            return

        # self.consensus_peak_widgets ist dein Dictionary, in dem du die rechten Tiles speicherst
        for peak_id, tile_widget in self.consensus_peak_widgets.items():

            # 1. Original-Numpy-Array laden
            npy_path = tile_widget.npy_file

            # Load the peak window from the path.
            peak_window = np.load(npy_path)
            peak_window_dimension = 4 * 5 + 1

            # Normalize the peak window.
            min_intensity = peak_window.min()
            max_intensity = peak_window.max()
            if max_intensity - min_intensity == 0:
                npy_file_normalized = np.zeros_like(peak_window)
            else:
                npy_file_normalized = (peak_window - min_intensity) / (max_intensity - min_intensity)

            # 2. Numpy-Array in PyTorch Tensor umwandeln
            peak_window_tensor = torch.from_numpy(npy_file_normalized).float().view(1, 1, peak_window_dimension, peak_window_dimension).to(self.current_device)

            # 3. Das Bild durch das Modell jagen (Ohne Gradienten -> spart Speicher & ist schneller)
            with torch.inference_mode():
                # Ein VAE gibt meist Rekonstruktion, Mean, Log-Variance zurück.
                # Wir brauchen nur die Rekonstruktion (Index 0).
                reconstruction, mean, log_var = self.current_vae_model(peak_window_tensor)

            # 4. Den Tensor wieder zurück in ein reines Numpy Array (2D) verwandeln
            recon_data = reconstruction.squeeze().cpu().numpy()

            # 5. Unseren Helfer von oben nutzen, um das QImage zu generieren
            q_image = self.numpy_to_qimage(recon_data)
            pixmap = QtGui.QPixmap.fromImage(q_image)

            # 6. Dem rechten Label (peak_window_recon) das Bild zuweisen!
            # Achte darauf, dass das Bild auch schön skaliert wird, falls das Label eine feste Größe hat.
            pixmap_scaled = pixmap.scaled(
                tile_widget.peak_window_recon.size(),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            )
            tile_widget.peak_window_recon.setPixmap(pixmap_scaled)


    def update_peak_count_info(self):
        """Liest die Anzahl der verfügbaren Peaks aus und aktualisiert das UI-Label."""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM peaks")
        total_peaks = cursor.fetchone()[0]
        conn.close()

        if total_peaks > 0:
            self.label_model_info.setText(
                f"This model will be trained on {total_peaks} peaks.")


    def load_available_devices_to_combobox(self):

        # Clear the combobox entries.
        self.comboBox_device.clear()
        # Add CPU option which is always there.
        self.comboBox_device.addItem("CPU", "cpu")

        # 2. Check and add Cuda devices.
        if torch.cuda.is_available():
            num_gpus = torch.cuda.device_count()
            for i in range(num_gpus):
                gpu_name = torch.cuda.get_device_name(i)
                display_text = f"{gpu_name}"
                internal_data = f"cuda:{i}"
                self.comboBox_device.addItem(display_text, internal_data)

        # Check for Apple MPS devices
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            self.comboBox_device.addItem("Apple Silicon GPU", "mps")

        # By default, preselect the strongest device [option 2, which is the first found GPU device].
        if self.comboBox_device.count() > 1:
            self.comboBox_device.setCurrentIndex(1)


    def on_start_training_clicked(self):
        # 1. Namen validieren und bereinigen
        raw_name = self.lineEdit_name.text().strip()
        model_name = re.sub(r'[^a-zA-Z0-9\s_-]', '', raw_name).strip()

        if not model_name:
            CustomMessageDialog.show_error("Input Error", "Please input a valid model name!")
            return

        # 2. Duplikat Check: Gibt es das Modell schon im Ordner "models"?
        new_file_path = get_resource_path("models") / f"{model_name}.pt"
        if new_file_path.exists():
            CustomMessageDialog.show_error("Duplication Error",
                                           f"A model with the name '{model_name}' already exists. Please choose another name.")
            return

        # 3. Werte aus den Dropdowns auslesen
        epochs = int(self.comboBox_epochs.currentText())
        device_str = self.comboBox_device.currentData()

        # 4. Den Custom Progress Dialog vorbereiten und anzeigen
        self.training_progress_dialog = CustomProgressDialog(title="Training in progress",
                                                             header="Training new model")
        self.training_progress_dialog.show()

        # 5. Den QThread und den neuen Worker aufsetzen
        self.thread = QtCore.QThread()
        self.worker = TrainingWorker(
            project_path=self.project_path,
            db_path=self.db_path,
            model_name=model_name,
            epochs=epochs,
            device_str=device_str
        )
        self.worker.moveToThread(self.thread)

        # 6. Alle Signale sauber verknüpfen
        self.thread.started.connect(self.worker.run)
        # Leitet den Fortschritt (1/50 Epochen) an den Dialog weiter
        self.worker.progress_update.connect(self.training_progress_dialog.update_progress)
        # Zeigt eventuelle PyTorch/Numpy Fehler direkt als Popup-Message in der GUI an
        self.worker.error_occurred.connect(
            lambda msg: CustomMessageDialog.show_error("Training Error", f"Something went wrong:\n{msg}"))

        # Thread aufräumen, wenn beendet
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # Lade-Dialog schließen und UI (ScrollArea links) neu laden
        self.worker.finished.connect(self.training_progress_dialog.accept)
        self.worker.finished.connect(self.load_models_to_scrollarea)

        # Den "Abbrechen"-Button im Ladefenster mit dem Worker verknüpfen
        self.training_progress_dialog.button_no.clicked.connect(self.worker.stop)

        # 7. Textfeld leeren und Trainingsthread starten!
        self.lineEdit_name.clear()
        self.thread.start()


class ModelTileWidget(QtWidgets.QWidget, Ui_ModelTile):
    # Signal definitions.
    delete_clicked = QtCore.Signal(object)
    rename_clicked = QtCore.Signal(object)
    tile_clicked = QtCore.Signal(object)

    def __init__(self, name: str):
        super().__init__()
        self.setupUi(self)

        # 1. Texte in der UI setzen
        self.name = name
        self.label_name.setText(name)
        self.old_label_name = name

        # 2. Buttons mit den Signalen verknüpfen
        self.button_delete.clicked.connect(self.emit_delete)
        self.button_rename.clicked.connect(self.emit_rename)

        # Hover effects for buttons.
        self.button_rename.enterEvent = lambda e: self.button_hover_effect(self.button_rename, 'edit_orange', True)
        self.button_rename.leaveEvent = lambda e: self.button_hover_effect(self.button_rename, 'edit_grey', False)
        self.button_delete.enterEvent = lambda e: self.button_hover_effect(self.button_delete, 'delete_magenta', True)
        self.button_delete.leaveEvent = lambda e: self.button_hover_effect(self.button_delete, 'delete_grey', False)

        # Make the background styleable [sometimes needed if a widget is not complex enough].
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)


    def mousePressEvent(self, event):
        """Fängt Klicks auf das gesamte Tile ab."""
        if event.button() == QtCore.Qt.LeftButton:
            self.tile_clicked.emit(self)
        super().mousePressEvent(event)


    def set_selected(self, is_selected: bool) -> None:
        if is_selected:
            self.label_name.setStyleSheet(
                "border: None; color: #ff9000; background-color: transparent; font-weight: bold;")
        else:
            self.label_name.setStyleSheet(
                "border: None; color: #ebebeb; background-color: transparent; font-weight: light;")


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


    def emit_delete(self):
        self.delete_clicked.emit(self)


    def emit_rename(self):
        self.rename_clicked.emit(self)


class ModelReconTile(QtWidgets.QWidget, Ui_ModelReconTile):
    def __init__(self,
                 db_path: Path,
                 consensus_id: int,
                 retention_time: float,
                 drift_time: float,
                 npy_file: Path):

        super().__init__()
        self.setupUi(self)

        self.db_path = db_path
        self.consensus_id = consensus_id
        self.retention_time = retention_time
        self.drift_time = drift_time
        self.npy_file = None
        self.is_selected = False

        # Erlaube dem Custom QWidget, Hintergründe per Stylesheet zu zeichnen
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)

        # Image paths for the activity icons.
        self.icon_active = QtGui.QIcon(":/ui/_pics/icons/eye_open.png")
        self.icon_inactive = QtGui.QIcon(":/ui/_pics/icons/eye_closed.png")

        # Define the absolute path to the npy file.
        self.npy_file = npy_file
        # Set the image to the peak image label.
        self.set_peak_tile_image(self.npy_file)
        # Text area of the widget.
        self.position_label.setText(f"DT: {drift_time:.2f} | RT: {retention_time:.2f}")
        # Set hover mouse icon
        self.setCursor(QtCore.Qt.PointingHandCursor)


    def set_selected(self, is_selected: bool) -> None:
        self.is_selected = is_selected


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
                            #ModelReconTile {{
                                background-color: {background_color};
                                border: 1px solid {border_color};
                                border-radius: 5px;
                            }}
                            #ModelReconTile:hover {{
                                background-color: {background_color_hover};
                                border: 1px solid {border_color_hover};
                                border-radius: 5px;
                            }}
                        """)


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
        pixmap = QtGui.QPixmap.fromImage(q_image).scaled(70, 70, QtCore.Qt.KeepAspectRatio)
        self.peak_window_original.setPixmap(pixmap)
        self.peak_window_recon.setPixmap(pixmap)



class TrainingWorker(QtCore.QObject):
    # Signal definitions.
    finished = QtCore.Signal()
    progress_update = QtCore.Signal(int, int)  # (Aktuelle Epoche, Total Epochen)
    error_occurred = QtCore.Signal(str)

    def __init__(self,
                 project_path: Path,
                 db_path: Path,
                 model_name: str,
                 epochs: int,
                 device_str: str):

        super().__init__()
        self.project_path = project_path
        self.db_path = db_path
        self.model_name = model_name
        self.epochs = epochs
        self.device = torch.device(device_str)
        self.is_stopped = False

    def stop(self):
        """Wird aufgerufen, wenn der User im Ladefenster auf 'Abbrechen' klickt."""
        self.is_stopped = True

    def run(self):
        try:
            # 1. Daten laden (Pfade sammeln)
            dataset_dir = self.project_path.parent / "dataset"
            npy_paths = []

            # Connect to the database and get all peak .npy files.
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT npy_file FROM peaks")
            peak_rows = cursor.fetchall()

            for row in peak_rows:
                full_path = dataset_dir / Path(row[0])
                npy_paths.append(full_path)

            # Get all unique labels.
            cursor.execute("SELECT name FROM labels ORDER BY name")
            label_rows = cursor.fetchall()
            conn.close()

            class_dict = {row[0]: idx for idx, row in enumerate(label_rows)}

            # Train/Test Split
            train_paths, _ = train_test_split(npy_paths, test_size=0.20, shuffle=True)

            # 2. Dataset und Dataloader aufsetzen
            train_dataset = misc.dataloader.VaeDataset(npy_paths=train_paths, class_dict=class_dict, window_size=5)
            train_dataloader = DataLoader(train_dataset, batch_size=16, shuffle=True)

            # 3. Modell initialisieren
            model = misc.vae_model.VariationalAutoencoderCNN(input_layers=1,
                                                        hidden_layers=64,
                                                        latent_dimension=16).to(self.device)

            optimizer = torch.optim.Adam(model.parameters(), lr=0.00005)

            beta_warmup = int(self.epochs/5)
            target_beta = 1.0

            # 4. Der eigentliche Training-Loop
            for epoch in range(self.epochs):
                if self.is_stopped:
                    break  # User hat auf "Abbrechen" geklickt

                # Calculate the current beta value [Beta annealing].
                if epoch < beta_warmup:
                    current_beta = target_beta * (epoch / beta_warmup)
                else:
                    current_beta = target_beta

                model.train()

                for feature, label in train_dataloader:
                    # Put image and label on the device.
                    feature, label = feature.to(self.device), label.to(self.device)

                    # 1. Forward pass.
                    reconstruction, mean, log_variance = model(feature)
                    # 2. Calculate the loss.
                    total_loss, recon_loss, kld_loss = misc.vae_model.vae_loss(feature, reconstruction, mean, log_variance, current_beta)
                    # Divide the loss with the bach size.
                    normalized_loss = total_loss / feature.size(0)
                    # 3 Clear the gardient.
                    optimizer.zero_grad()
                    # 4. Backpropagation.
                    normalized_loss.backward()
                    # 5. Adjust parameters through gradient decent.
                    optimizer.step()

                # Nach jeder abgeschlossenen Epoche den Ladebalken updaten!
                self.progress_update.emit(epoch + 1, self.epochs)

            # 5. Modell speichern, falls das Training komplett durchlief
            if not self.is_stopped:
                model_dir = get_resource_path("models")
                model.save_model(model_dir=model_dir,
                                 file_name=f"{self.model_name}.pt")

        except Exception as e:
            # Falls irgendwas in PyTorch crasht, die GUI sauber mit dem Error benachrichtigen
            self.error_occurred.emit(str(e))

        finally:
            self.finished.emit()