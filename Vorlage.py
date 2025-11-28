# Standardbibliothek
import os
import math
import uuid
import multiprocessing

# Datenanalyse
import numpy as np  # --> für die Verwendung von numerische Arrays
import pandas as pd  # --> Für die Verwendung von tabellarischen Daten
from scipy.ndimage import uniform_filter  # --> Für die Glättung von Daten und Bildern

# Datenvorverarbeitung
from sklearn.preprocessing import MinMaxScaler  # Skalierung auf einen festen Bereich zwischen 0 bis 1
from sklearn.model_selection import ParameterGrid, \
    train_test_split  # train/test: Trainings-/Testsets erzeugen;  ParameterGrid:Grid-Search für ML-Modelle
from sklearn.manifold import TSNE  # nichtlineare Dimensionsreduktion
from sklearn.decomposition import PCA  # lineare Dimensionsreduktion--> Daten auf Hauptkomponenten reduzieren

# Deep Learning
import torch  # --> Grundfunktionen für Deep Learning
import torch.nn as nn  # Neuronale Netzwerke definieren--> für Layers, Aktivierungsfunktionen, Verlustfunktionen
import torch.optim as optim  # Optimierer--> für Adam, SGD usw. für Training
from torch.utils.data import DataLoader, TensorDataset  # Datenpipeline-->  Batch-Laden für Training
from torchvision import transforms  # Bildtransformationen

# Bildverarbeitung
from PIL import Image, ImageDraw, ImageFont, ImageOps  # Pillow-Bibliothek--> Bilder laden, bearbeiten, zeichnen
import matplotlib.image as mpimg  # Bilder einlesen und bearbeiten
from skimage.morphology import (
    max_tree_local_maxima, max_tree, local_maxima,
    square, disk, footprint_from_sequence
)
# Strukturanalyse im Bild--> Filter,  lokale Maxima
from skimage.metrics import structural_similarity as ssim

# Visualisierung
import matplotlib.pyplot as plt  # Plot-Erstellung
import seaborn as sns  # statistische Plots--> Heatmaps
import matplotlib.colors as mcolors  # Farbskalen definieren
import matplotlib.cm as cm  # Farbskalen definieren
import matplotlib.patches as mpatches  # Formen im Plot
from matplotlib.offsetbox import OffsetImage, \
    AnnotationBbox  # Bilder im Plot platzieren-->Heatmaps in Scatterplot einbetten
from matplotlib.backends.backend_pdf import PdfPages  # PDF-Speicherung
from mpl_toolkits.axes_grid1.inset_locator import inset_axes  # Achseneinbettung

# Graphen & Netzwerke
import networkx as nx  # Netzwerke, Knotenanalyse

import ims  # Open-Source für die Verarbeitung von GC-IMS-Spektren

def preprocess_and_visualize_spectra(input_dir, output_plot_dir):
    # Daten einlesen:
    # ims.Dataset.read_mea: liest alle Messdateien in MEA-Format aus dem ordner in ein ims-Dateset-Objekt
    dataset = ims.Dataset.read_mea(input_dir)
    # Ausgabe: Name des Datensatzes und Anzahl der geladenen Spektren
    print(f"Dataset: {dataset.name}, {len(dataset.data)} Spectra")
    os.makedirs(output_plot_dir, exist_ok=True)
    # interp_riprel(): Interpoliert die Daten auf eine standasierte relative Driftzeitachse (RIP-Referenz)
    dataset.interp_riprel()

    # filtered_data: Liste für Spektren, die erfolgreich vorverarbeitet wurden
    filtered_data = []
    # Umbennenungstabelle für Rohdateinamen
    name_map = {
        "Citrus": "Citrushonig",
        "Lavendel": "Lavendelhonig",
        "Sonnenblume": "Sonnenblumenhonig",
        "Linde": "Lindenhonig",
        "Eukalyptus": "Eukalyptushonig",
        "Akazie": "Akazienhonig",
        "Buchweizen": "Buchweizenhonig",
        "Raps": "Rapshonig",
        "Kastanie": "Kastanienhonig"
    }
    # Schleife über alle geladenen Spektren
    # Leere Spektren werden übersprungen
    for i, sample in enumerate(dataset.data):
        if sample.values.size == 0:
            print(f"Warning: Spektrum {i + 1} ist leer --> Überspringe Vorverarbeitung.")
            continue

        spectrum_name = os.path.splitext(os.path.basename(sample.name))[0]

        # Name aufbereiten
        # Extrahiert den Basisnamen der Datei ohne Endung
        # Zerlegt den Namen in Teile
        teile = spectrum_name.split('_')
        if len(teile) >= 6:
            original_name = teile[2]
            zahl1 = teile[3]
            zahl2 = teile[5]

            name_kurz = name_map.get(original_name, original_name)
            clean_name = f"{name_kurz}_{zahl1}_{zahl2}"
        else:
            clean_name = spectrum_name

        # Rohspektrum visualisieren
        # Zeichnet das Rohspektrum.
        plt.figure(figsize=(10, 6))
        sample.plot()
        # Beschriftung der Achsen: Driftzeit, Retentionszeit.
        plt.title(f"{clean_name}_Rohspektrum")
        plt.xlabel("Driftzeit [ms]")
        plt.ylabel("Retentionszeit [s]")
        # Legt Colorbar-Beschriftung auf "Intensität".
        cbar = plt.gcf().axes[-1]
        cbar.set_ylabel("Intensität", fontsize=10)
        caption = ""
        plt.figtext(0.1, -0.03, caption, wrap=True, horizontalalignment='left', fontsize=9)
        # Speichert PNG-Datei im Ausgabeordner
        plt.savefig(os.path.join(output_plot_dir, f"{clean_name}_Rohspektrum.png"), dpi=300, bbox_inches='tight')
        plt.close()

        # Zuschnitt & Baseline-Korrektur
        # Zuschnitt auf einen relevanten Bereich der Driftzeit(dt)
        sample.cut_dt(start=1.02, stop=1.5)
        # Zuschnitt auf einen relevanten Bereich der Retentionszeit(rt)
        sample.cut_rt(start=200, stop=2500)
        sample.values_processed = np.copy(sample.values)
        # TODO -> Why creating a copy?

        # Baseline-Korrektur
        # Zeilenweise und spaltenweise wird ein niedriger Perzentilwert (5 %) als Basislinie subtrahiert

        percentile = 5
        # Baseline-Korrektur: Zeilenweise
        perc_vals_rows = np.percentile(sample.values_processed, percentile, axis=0, keepdims=True)
        baseline_rows = perc_vals_rows
        sample.values_processed -= baseline_rows

        # Baseline-Korrektur:Spaltenweise
        perc_vals_col = np.percentile(sample.values_processed, percentile, axis=1, keepdims=True)
        baseline_col = perc_vals_col
        sample.values_processed -= baseline_col
        # Negative Werte nach Subtraktion --> auf 0 setzen.
        sample.values_processed[sample.values_processed < 0] = 0
        sample.values = sample.values_processed
        # Glättung: uniform_filter mittelt lokal über ein Fenster von 10x10 Punkten, um Rauschen zu reduzieren
        sample.values_processed = uniform_filter(sample.values, size=(10, 10))
        """ TODO -> In der Arbeit steht "Am Ende der Vorverarbeitung wurde mittels des Uniform-Filters mit einem
        # 11×11-Fenster gefiltert" ... Hier im Code wird aber 10x10 verwendet. Die uniform_filter function arbeitet NICHT
        # mit einem 0-index. Also müsste es auf 11x11 geändert werden?
        """

        # Vorverarbeitetes Spektrum visualisieren
        # Zeichnet das vorverarbeitete Spektrum
        plt.figure(figsize=(10, 6))
        sample.plot()
        # Beschriftung der Achsen:relative Driftzeit, Retentionszeit.
        plt.title(f"{clean_name}_Vorverarbeitetes_Spektrum")
        plt.xlabel("Relative Driftzeit [ms]")
        plt.ylabel("Retentionszeit [s]")
        # Legt Colorbar-Beschriftung auf "Intensität".
        cbar = plt.gcf().axes[-1]  # Annahme: letzte Achse ist die Colorbar
        cbar.set_ylabel("Intensität", fontsize=10)
        caption = ""
        plt.figtext(0.5, -0.008, caption, wrap=True, horizontalalignment='center', fontsize=7)
        # Speichert PNG-Datei im Ausgabeordner
        plot_filename = os.path.join(output_plot_dir, f"{clean_name}_{i + 1}_Vorverarbeitet_MinBaseline.png")
        plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Vorverarbeitetes Spektrum gespeichert als {plot_filename}")

        filtered_data.append(sample)

        # Grid-Plot der ersten 18 Rohspektren
        # Erstellt Rasterdarstellung (n_rows x n_cols)
        n_spectra = min(18, len(filtered_data))
        n_cols = 6
        n_rows = math.ceil(n_spectra / n_cols)

        fig, axes = plt.subplots(n_rows, n_cols, figsize=(18, 3 * n_rows), sharex=True, sharey=True)
        axes = axes.flatten()
        # Zeigt jedes Spektrum in imshow mit Farbcodierung cmap="viridis"
        for idx in range(n_spectra):
            ax = axes[idx]
            sample = filtered_data[idx]
            ax.imshow(sample.values, aspect='auto', cmap='viridis')
            ax.set_title(f"{idx + 1}: {sample.name}", fontsize=8)
            ax.axis('off')

        # Leere Subplots ausblenden, falls weniger als 18 Spektren
        for idx in range(n_spectra, len(axes)):
            axes[idx].axis('off')

        plt.suptitle("Grid-Plot der ersten 18 Rohspektren", fontsize=16)
        plt.tight_layout(rect=[0, 0, 1, 0.95])

        grid_plot_path = os.path.join(output_plot_dir, "grid_plot_18_rohspektren.png")
        plt.savefig(grid_plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Grid-Plot mit 18 Rohspektren gespeichert unter: {grid_plot_path}")

    # Gibt alle erfolgreich vorverarbeiteten Spektren zurück
    return filtered_data


# Parameter:
# sample: ein einzelnes Spektrum-Objekt
# spectrum_index: Nummer des Spektrums
# window_size: halbe Fenstergröße für Peak-Ausschnit--> window_size=5=Fenster 11×11
# output_dir: Speicherort für Ergebnisse
# processed_spectra: Dictionary, um bereits verarbeitete Spektren zu markieren
# all_peaks_data: globale Peak-Daten für alle Spektren
# min_margin: Mindestabstand vom Rand, damit ein Peak-Fenster nicht aus dem Bild fällt
# classic_peaks_dir: Ordner bei dem die echten Peaks(nicht verschobenen Peaks) gespeichert werden.
def process_spectrum_parallel(sample, spectrum_index, window_size, output_dir, processed_spectra, all_peaks_data,
                              Zustand, min_margin=5):
    # copy: Sicherung der vorverarbeiteten Daten (original_values), damit die Peak-Findung nicht die echten Werte verändert.
    original_values = sample.values_processed.copy()

    # Min-Max-Normalisierung auf Wertebereich [0,1] für die Peak-Findung
    min_val = original_values.min()
    max_val = original_values.max()
    if max_val - min_val == 0:
        normalized_values = np.zeros_like(original_values)
    else:
        normalized_values = (original_values - min_val) / (max_val - min_val)
    # Setzen von sample.values auf die normalisierte Matrix für die Peak-Findung.
    sample.values = normalized_values

    # Überprüft, ob das Spektrum schon verarbeitet wurde.
    # Falls ja --> Abbruch
    # Falls nein --> Markieren als verarbeitet
    if sample.name in processed_spectra['data'] and processed_spectra['data'][sample.name]:
        print(f"Spektrum {sample.name} wurde bereits verarbeitet. Überspringe.")
        return []

    processed_spectra['data'][sample.name] = True
    print(f"Start der Verarbeitung von Spektrum {spectrum_index + 1}: {sample.name}...")

    spectrum_peak_data = []

    try:
        try:
            honey_type = sample.name.split('_')[2]
        except IndexError:
            honey_type = "Unknown"

        # Es macht lokale Maxima-Erkennung in einem Bild
        # sample.values: Das ist das Spektrum (Intensitäten über Retentionszeit und Driftzeit) als NumPy-Array
        # connectivity=2:auch diagonale Nachbarn zählen (8er-Nachbarschaft)
        # parent=-1:Parameter für Baumstruktur-Auswertung. -1 heißt, dass der gesamte Max-Tree ohne Einschränkungen auf einen bestimmten Teilbaum erstellt wird.
        # tree_traverser=None: Gibt an, dass der Standard-Traversierungsmodus für den Max-Tree genutzt wird
        local_maxima = max_tree_local_maxima(sample.values, connectivity=2, parent=-1, tree_traverser=None)
        # local_maxima.max(): gibt die höchste Hierarchie-Stufe im Bild
        # Multiplikation mit 0.95 setzt einen Schwellenwert bei 95 % der maximalen Hierarchiestufe
        # int()--> Abrunden auf Ganzzahlen--> Hierarchie-Stufen sind ganzzahlig
        relative_hierarchy_threshold = int(local_maxima.max() * 0.95)
        # Entfernt alle Pixel mit zu niedriger Hierarchie-Stufe

        high_hierarchy_peaks = np.column_stack(
            np.where(
                (local_maxima >= 0.5) &
                # (local_maxima <= relative_hierarchy_threshold):Entfernt Pixel, deren Hierarchie über der 95%-Schwelle liegt
                (local_maxima <= relative_hierarchy_threshold)
            )
        )

        # Peak-Intensitäten basierend auf den normalisierten Werten für Filterung
        # Intensitätswerte der Peaks extrahieren
        # high_hierarchy_peaks enthält Koordinaten (ret_index, drift_index) der zuvor gefundenen Kandidaten-Peaks
        # normalized_values ist dein Min-Max-normalisiertes Spektrum (Wertebereich [0,1])
        # Diese List Comprehension holt für jede Peak-Koordinate den entsprechenden Intensitätswert
        # peak_intensities_norm ist ein 1D-Array den normierten Peakintensitäten
        peak_intensities_norm = np.array(
            [normalized_values[ret_idx, drift_idx] for ret_idx, drift_idx in high_hierarchy_peaks])

        # Falls keine Kandidaten gefunden wurden, wird direkt ein leeres Array highest_hierarchy_peaks zurückgegeben.
        if len(peak_intensities_norm) > 0:
            # berechnet den Wert, der 95,5 % aller Peakintensitäten unterschreitet
            # Nur die obersten 4,5 % der Peaks (bezogen auf Intensität) werden behalten.
            intensity_threshold = np.percentile(peak_intensities_norm, 95.5)
            # zip: verbindet Koordinaten und Intensitäten zu Paaren
            # Behalte nur die Koordinaten, deren Intensität über der Schwelle liegt
            # filtered_peaks enthält nur die intensivsten Peaks
            filtered_peaks = [
                coord for coord, intensity in zip(high_hierarchy_peaks, peak_intensities_norm) if
                intensity >= intensity_threshold
            ]
            # Macht aus der Liste ein NumPy-Array
            highest_hierarchy_peaks = np.array(filtered_peaks)
        else:
            highest_hierarchy_peaks = np.array([])
        # Rand
        # ret_index >= min_margin--> Der Peak muss mindestens min_margin Punkte vom linken Rand (Retentionszeit) entfernt sein
        # ret_index < original_values.shape[0] - min_margin--> Der Peak muss mindestens min_margin Punkte vom rechten Rand entfernt sein
        # drift_index >= min_margin--> Der Peak muss mindestens min_margin Punkte vom unteren Rand (Driftzeit) entfernt sein
        # drift_index < original_values.shape[1] - min_margin--> Der Peak muss mindestens min_margin Punkte vom oberen Rand entfernt sein
        #
        valid_peaks = []
        for coord in highest_hierarchy_peaks:
            ret_index, drift_index = coord

            if (ret_index >= min_margin and ret_index < original_values.shape[0] - min_margin and
                    drift_index >= min_margin and drift_index < original_values.shape[1] - min_margin):
                valid_peaks.append(coord)
        # die alte Liste wird durch die validierten peaks ersetzt
        highest_hierarchy_peaks = np.array(valid_peaks)

        # Ab hier wieder Originalwerte verwenden für alle weiteren Schritte
        sample.values = original_values

        # Erweiterung um Nachbarschafts-Koordinaten
        # all_coords_to_process = []--> Liste, welche alle Koordinate enthält, die verarbeitet werden sollen
        all_coords_to_process = []
        # Iteration über jeden Peak aus der gefilterten Liste highest_hierarchy_peak
        for ret_index, drift_index in highest_hierarchy_peaks:
            # dx und dy sind Offsets in Retentions- bzw. Driftzeit-Richtung
            # range(-5, 6) bedeutet:Von -5 bis +5 -->Das sind 11 Werte pro Achse --> ergibt 11×11 = 121 Punkte pro Peak
            # new_ret = ret_index + dx; new_drift = drift_index + dy--> Berechnet die neue Koordinate relativ zum ursprünglichen Peak
            #
            for dx in range(-5, 6):
                for dy in range(-5, 6):
                    new_ret = ret_index + dx
                    new_drift = drift_index + dy
                    # Randprüfung--> Nur gültige Koordinaten werden gespeichert
                    if (min_margin <= new_ret < original_values.shape[0] - min_margin and
                            min_margin <= new_drift < original_values.shape[1] - min_margin):
                        all_coords_to_process.append((new_ret, new_drift))

        # Deduplikation
        # Falls sich zwei Peaks überlappen, dann überschneiden sich die Nachbarschaftsfenster
        # set()--> doppelte Koordinaten werden entfernt, um nicht zweimal das gleiche Fenster zu extrahieren.
        all_coords_to_process = list(set(all_coords_to_process))

        # Map für spezielle Umbenennungen
        name_map = {
            "Citrus": "Citrushonig",
            "Lavendel": "Lavendelhonig",
            "Sonnenblume": "Sonnenblumenhonig",
            "Linde": "Lindenhonig",
            "Eukalyptus": "Eukalyptushonig",
            "Akazie": "Akazienhonig",
            "Buchweizen": "Buchweizenhonig",
            "Raps": "Rapshonig",
            "Kastanie": "Kastanienhonig"

        }

        # Ursprünglichen Namen zerlegen
        teile = sample.name.split('_')

        # Absicherung, falls Format mal nicht stimmt
        if len(teile) >= 6:
            original_name = teile[2]
            zahl1 = teile[3]
            zahl2 = teile[5]

            #
            name_kurz = name_map.get(original_name, original_name)

            neuer_name = f"{name_kurz}_{zahl1}_{zahl2}"
        else:
            # Falls unerwartetes Format, einfach Originalname nehmen
            neuer_name = sample.name

        # Visualisierung
        # sample.plot() zeichnet das komplette 2D-Spektrum
        #
        plt.figure(figsize=(12, 8))
        sample.plot()

        # highest_hierarchy_peaks: enthält die Matrix-Indices (ret_index, drift_index) der Peak
        # sample.drift_time[drift_index]--> Umrechnung von Spaltenindex zu realer Driftzeit
        # sample.ret_time[ret_index]--> Umrechnung von Zeilenindex zu realer Retentionszeit.
        # r+', markersize=3--> rotes Kreuz '+' für die einzelnen Peaks
        # peak_ids.append()--> speichert die Peak-Koordinaten in einer Liste
        peak_ids = []
        for coord in highest_hierarchy_peaks:
            ret_index, drift_index = coord
            plt.plot(sample.drift_time[drift_index], sample.ret_time[ret_index], 'r+', markersize=3)
            peak_ids.append((sample.ret_time[ret_index], sample.drift_time[drift_index]))

        # X-Achse = Driftzeit; Y-Achse = Retentionszeit
        plt.title(f"Peak-Plot (Original): {neuer_name}")
        plt.xlabel("Relative Driftzeit [ms]")
        plt.ylabel("Retentionszeit [s]")

        # Farbskala = Intensität (Colorbar)
        cbar = plt.gcf().axes[-1]
        cbar.set_ylabel("Intensität", fontsize=10)
        # Fügt unterhalb des Plots eine Textzeile hinzu
        caption = ""
        plt.figtext(0.5, -0.05, caption, wrap=True, horizontalalignment='center', fontsize=7)
        # Speichert den Plot als PNG mit hoher Auflösung (300 dpi)
        # bbox_inches="tight"--> unnötige Ränder werden abgeschnitten
        peak_plot_filename = os.path.join(output_dir, f"peak_plot_{neuer_name}_peak_plot_vorverarbeitet.png")
        plt.savefig(peak_plot_filename, dpi=300, bbox_inches="tight")
        plt.close()
        print(f"Peak-Plot gespeichert unter: {peak_plot_filename}")

        # Verwendung der erweiterten Koordinate
        # all_coords_to_process--> kommt aus dem Schritt davor, wo um jeden Peak herum eine Nachbarschaft gebildet wurde
        # Jede coord ist ein Tupel(ret_index, drift_index)--> Indizes im 2D-Datenarray (original_values)
        # original_values: Roh-Intensitätsmatrix des Spektrums
        # peak_intensity: Intensität an genau dieser Koordinate
        # ret_time und drift_time: Physikalische Werte statt Array-Indizes
        # sample.ret_time[ret_index] --> Retentionszeit in Sekunden
        # sample.drift_time[drift_index] --> Driftzeit in Millisekunden
        # ret_index, drift_index = coord
        # peak_intensity = original_values[ret_index, drift_index]
        # ret_time = sample.ret_time[ret_index]
        # drift_time = sample.drift_time[drift_index]

        for coord in all_coords_to_process:
            ret_index, drift_index = coord
            peak_intensity = original_values[ret_index, drift_index]
            ret_time = sample.ret_time[ret_index]
            drift_time = sample.drift_time[drift_index]
            # Erzeugt 8-stellige eindeutige Kennung (aus einer UUID), damit Dateinamen nicht kollidieren.
            unique_id = uuid.uuid4().hex[:8]
            # extract_window--> externe Funktion, welches ein 11x11 Peakfenster aus dem GC-IMS ausschneidet
            # gibt eine Peakfenster mit einer Intensitätsmatrix wieder.
            peak_window, intensity = extract_window(
                sample, {"ret_time": ret_time, "drift_time": drift_time}, window_size, output_dir, Zustand, unique_id
            )

            # Gültigkeitsprüfung des Fensters
            # Ist das Fenster leer (size == 0) oder hat es nicht die erwartete Form--> überspringen, da der Peak am Rand liegen könnte oder fehlerhaft ist
            if peak_window.size == 0 or peak_window.shape != (2 * window_size + 1, 2 * window_size + 1):
                print(f"Ungültiges Fenster für Peak bei RT={ret_time}, DT={drift_time}. Überspringe.")
                continue

            # Speichert den Fensterausschnitt als NumPy-Datei
            # Dateiname enthält:sample.name (Probenname);Retentions- & Driftzeit (6 Nachkommastellen), unique_id; Fenstergröße 11x11
            window_filename = os.path.join(
                output_dir, f"{sample.name}_peak_window_RT_{ret_time:.6f}_DT_{drift_time:.6f}_{unique_id}_11x11.npy"
            )

            np.save(window_filename, peak_window)

            # Metadaten zu diesem Peak
            # Für jeden Peak wird ein Dictionary mit allen wichtigen Infos erstellt
            # honey_type: Probenklassifizierung (Honigsorte)
            # npy_file: Pfad zur gespeicherten NumPy-Datei
            # ret_time: Retentionszeit
            # drift_time: Driftzeit
            # intensity: Intensität

            peak_data = {
                'honey_type': honey_type,
                'ret_time': ret_time,
                'drift_time': drift_time,
                'intensity': peak_intensity,
                'npy_file': window_filename,
            }

            spectrum_peak_data.append(peak_data)

        # all_peaks_data ist ein globales Dictionary:
        # Schlüssel = Spektrumsname, Wert = Liste aller Peak-Koordinaten
        # Die Liste wird erweitert
        if sample.name not in all_peaks_data:
            all_peaks_data[sample.name] = []

        all_peaks_data[sample.name].extend(peak_ids)

        # Aus spectrum_peak_data wird ein Pandas-DataFrame
        # Export als Excel-Datei (.xlsx), Sheetname = "Peak Data".
        # Enthält alle Metadaten zum Spektrum.

        spectrum_df = pd.DataFrame(spectrum_peak_data)
        excel_filename = os.path.join(output_dir,
                                      f"{sample.name}_peak_data_highest_hierarchy_Mean-Average-Filter_baseline_mit_nachbarn.xlsx")
        with pd.ExcelWriter(excel_filename) as writer:
            spectrum_df.to_excel(writer, index=False, sheet_name='Peak Data')
        print(f"Peak-Daten für {sample.name} gespeichert in {excel_filename}")

        # Falls etwas im Loop schiefgeht --> Fehlermeldung mit Spektrumsnummer und Name

    except Exception as e:
        print(f"Fehler bei der Verarbeitung von Spektrum {spectrum_index + 1} ({sample.name}): {str(e)}")
    # Gibt spectrum_peak_data zurück --> Liste aller Peak-Infos dieses Spektrums.
    print(f"Spektrum {spectrum_index + 1} abgeschlossen: {sample.name}")
    return spectrum_peak_data

    # Funktion für die Extraktion der Peakfenster aus dem GC-IMS-Spektrum
    ##sample: ein einzelnes Spektrum-Objekt
    # peak --> Dictionary mit ret_time und drift_time des Peaks
    # window_size --> halbe Fenstergröße (5 --> Fenster = 11×11)
    # output_dir --> Speicherort für die Peakfenster
    # Zustand
    # unique_id --> 8-stellige eindeutige Kennung, damit Dateinamen unverwechselbar sind.


def extract_window(sample, peak, window_size, output_dir, Zustand, unique_id):
    # Extrahiert die Retentions- und Driftzeit-Werte des Peaks
    peak_ret_time = peak['ret_time']  # Originalwert der Retentionszeit
    peak_drift_time = peak['drift_time']  # Originalwert der Driftzeit

    # Zuordnung von Retentionszeit und Driftzeit zu Indizes (exakte Übereinstimmung)
    try:
        ret_index = np.where(sample.ret_time == peak_ret_time)[0][0]
        drift_index = np.where(sample.drift_time == peak_drift_time)[0][0]
    except IndexError:
        raise ValueError(f"Peak-Werte ({peak_ret_time}, {peak_drift_time}) passen nicht zu den Indizes!")

    # Extrahiert die Peakintensität direkt an den Originalwerten

    intensity = sample.values[ret_index, drift_index]

    # Bestimmt basierend auf Indizes die Fenstergrenzen
    # Start und Ende werden so gewählt, dass das Fenster window_size Pixel in jede Richtung geht
    start_ret_index = max(0, ret_index - window_size)
    end_ret_index = min(sample.values.shape[0], ret_index + window_size + 1)

    start_drift_index = max(0, drift_index - window_size)
    end_drift_index = min(sample.values.shape[1], drift_index + window_size + 1)

    # Extrahiert das Fenster basierend auf den Indizes
    peak_window = sample.values[start_ret_index:end_ret_index, start_drift_index:end_drift_index]

    # Zero Padding anwenden, falls notwendig
    # Berechnet, ob an einer Seite Pixel fehlen, also zu nah am Rand sind
    # falls ja--> fehlende Pixel werden mit 0 aufgefüllt
    pad_left_ret = max(0, window_size - ret_index)
    pad_right_ret = max(0, (ret_index + window_size + 1) - sample.values.shape[0])
    pad_left_drift = max(0, window_size - drift_index)
    pad_right_drift = max(0, (drift_index + window_size + 1) - sample.values.shape[1])

    if pad_left_ret > 0 or pad_right_ret > 0 or pad_left_drift > 0 or pad_right_drift > 0:
        peak_window = np.pad(
            peak_window,
            ((pad_left_ret, pad_right_ret), (pad_left_drift, pad_right_drift)),
            mode='constant',
            constant_values=0
        )

    # Sicherstellen, dass das Fenster die Zielgröße hat
    target_size = 2 * window_size + 1
    if peak_window.shape != (target_size, target_size):
        print(f"Warnung--> Fenstergröße ist {peak_window.shape}, aber {target_size} erwartet.")

    intensity = sample.values[ret_index, drift_index]

    # Erstellt Heatmap und speichern
    # Enthält:
    # Probenname (sample.name)
    # Retentionszeit und Driftzeit mit 6 Nachkommastellen
    # Die eindeutige ID (unique_id)
    # Die Fenstergröße (11x11)
    # Suffix _vorverarbeitet.png--> Hinweis, dass es aus vorverarbeiteten Daten stammt
    heatmap_filename = os.path.join(
        output_dir,
        f"{sample.name}_heatmap_RT_{peak_ret_time:.6f}_DT_{peak_drift_time:.6f}_{unique_id}_11x11_vorverarbeitet.png"
    )

    plt.figure(figsize=(10, 10))

    # Zeichne die Heatmap
    # verwendet Seaborn Heatmap
    # annot=True --> Zahlenwerte werden in jedes Feld geschrieben.
    # fmt=".2f" --> 2 Nachkommastellen.
    # cmap="viridis" --> Farbverlauf
    # linecolor='white' --> weiße Gitterlinien.
    # linewidths=0.5 --> dünne Linien
    sns.heatmap(
        peak_window,
        annot=True,
        fmt=".2f",
        cmap="viridis",
        cbar=True,
        linecolor='white',
        linewidths=0.5,
        annot_kws={"size": 5}
    )
    # Titel und Achsenbeschriftung
    plt.title(f"Peak Heatmap: {sample.name}")
    # X-Achsenbeschriftung
    plt.xlabel("Drift Time")
    # Y-Achsenbeschriftung
    plt.ylabel("Retention Time")
    # Text unter der Grafik
    fig_caption = ("")
    plt.figtext(0.445, 0.02, fig_caption, ha="center", va="center", fontsize=7)  # Unterhalb des Plots
    # Speichern der Heatmap
    plt.savefig(heatmap_filename, bbox_inches="tight")
    plt.close()
    print(f"Heatmap gespeichert unter: {heatmap_filename}")

    # Rückgabe
    # peak_window --> 2D-Array des ausgeschnittenen Fensters
    # intensity --> Original-Intensität am Peakzentrum
    return peak_window, intensity


# Grid-Plot für die Peak-Plots
# plot_dir --> Ordner, in dem die Peak-Plot-Bilder liegen
# output_filename --> Dateiname und Pfad, unter dem die Abbildung gespeichert wird
# cols --> Anzahl der Spalten im Grid
# title --> Überschrift für die Collage
# font_size --> Schriftgröße für den Titel
# scale_factor --> Faktor, um die einzelnen Plots zu vergrößern oder verkleinern
def combine_peak_plots_to_single_figure(plot_dir, output_filename, Zustand, cols=6, title="Peak-Plot-Übersicht",
                                        font_size=200, scale_factor=1.5):
    # Lade alle Plot-Dateien aus dem Verzeichnis
    # Sucht alle Dateien, die mit "peak_plot_vorverarbeitet.png" enden
    plot_files = [os.path.join(plot_dir, f) for f in os.listdir(plot_dir) if f.endswith("peak_plot_vorverarbeitet.png")]
    plot_files.sort()  # Sortiert die Dateien alphabetisch
    # Bricht ab, wenn keine passenden Dateien existieren
    if not plot_files:
        print(f"Keine Peak-Plots im Verzeichnis {plot_dir} gefunden.")
        return

    # Ladet die Bilder und berechne die Anordnung
    # Öffnet die Bilder mit PIL und speichert sie in einer Liste
    images = [Image.open(file) for file in plot_files]
    # Teilt die Anzahl Bilder durch die Anzahl Spalten, aufgerundet --> ergibt die Anzahl der Reihen
    rows = (len(images) + cols - 1) // cols

    # Bestimmt die Größe der Abbildung (mit Skalierungsfaktor)
    # max_width / max_height --> größte Breite/Höhe unter allen Bildern, mit scale_factor multipliziert.
    # fig_width / fig_height --> gesamte Bildbreite/-höhe ohne Titel.
    max_width = int(max(img.width for img in images) * scale_factor)
    max_height = int(max(img.height for img in images) * scale_factor)
    fig_width = cols * max_width
    fig_height = rows * max_height

    # Zusätzlicher Platz für die Überschrift
    # Platz für den Titel basierend auf Schriftgröße
    title_height = font_size + 70
    # Image.new--> erstellt ein leeres weißes Bild im RGB-Format
    combined_image = Image.new("RGB", (fig_width, fig_height + title_height), (255, 255, 255))

    # Fügt die einzelnen Plots in das Raster ein
    # Schleife über alle Bilder
    # col / row --> Rasterposition bestimmen
    # x_offset / y_offset --> Pixelposition in der Abbildung
    # resize --> Skaliert b jedes Bild auf die gewünschte größe
    # paste --> Fügt das Bild an der berchneten Position ein
    for idx, img in enumerate(images):
        col = idx % cols
        row = idx // cols
        x_offset = col * max_width
        y_offset = row * max_height + title_height  # Platz für den Titel berücksichtigen
        img_resized = img.resize((max_width, max_height))  # Größe der Bilder ändern
        combined_image.paste(img_resized, (x_offset, y_offset))

    # Füge den Titel hinzu
    # Versucht, Arial in der angegebenen Größe zu laden. Falls nicht verfügbar --> Standardschrift.
    draw = ImageDraw.Draw(combined_image)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)  # Schriftgröße festlegen
    except IOError:
        font = ImageFont.load_default()

    # Berechnet die Bounding Box und zentriert den Text
    # textbbox() --> berechnet die Box um den Text
    # text_x --> zentriert den Titel horizontal
    # text_y --> setzt den Titel vertikal im reservierten Bereich.
    text_bbox = draw.textbbox((0, 0), title, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_x = (fig_width - text_width) // 2
    text_y = (title_height - font_size) // 2
    # Schreibt den Titel in Schwarz oben auf die Abbildung
    draw.text((text_x, text_y), title, font=font, fill=(0, 0, 0))

    # Speichere die kombinierte Abbildung
    combined_image.save(output_filename)
    print(f"Kombinierte Abbildung mit Titel gespeichert unter: {output_filename}")


# output_plot_dir --> Ordner, in dem die vorverarbeiteten Spektren als PNG liegen
# cols --> Spaltenanzahl im Subplot-Raster
# title --> Gesamttitel der Abbildung
# font_size --> Schriftgröße des Titels
# scale_factor --> Ist hier übergeben, aber wird nicht im Code benutzt
# Hier wird Matplotlib für die Anordnung der Bilder benutzt
def plot_processed_spectra_in_subplots(output_plot_dir, cols=6, title="Übersicht: Vorverarbeitete Spektren",
                                       font_size=12, scale_factor=1.5):
    # Lädt alle gespeicherten .png-Bilder der vorverarbeiteten Spektren
    plot_files = [os.path.join(output_plot_dir, f) for f in os.listdir(output_plot_dir) if
                  f.endswith("_Vorverarbeitet_MinBaseline.png")]
    plot_files.sort()  # Sortiert die Dateien alphabetisch

    # Falls keine passenden Dateien gefunden werden --> Meldung ausgeben, Funktion beenden
    if not plot_files:
        print(f"Keine vorverarbeiteten Spektren im Verzeichnis {output_plot_dir} gefunden.")
        return

    # Berechnet die Anzahl der benötigten Zeilen und Spalten für Subplots
    rows = (len(plot_files) + cols - 1) // cols  # Anzahl der Reihen
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 4, rows * 4))  # Größe der gesamten Abbildung
    axes = axes.flatten()  # Flache die Achsen-Array für einfachen Zugriff

    # Ladet die Bilder und fügt sie in Subplots ein
    # Iteriert über alle Bilddateien:
    # Öffnet das Bild mit PIL
    # Holt die entsprechende Achse (ax)
    # Zeigt das Bild in der Achse mit imshow
    # Blendet die Achsenbeschriftungen aus (axis('off'))
    for i, plot_file in enumerate(plot_files):
        img = Image.open(plot_file)
        ax = axes[i]
        ax.imshow(img)
        ax.axis('off')  # blendet Achsen aus

    # Entfernt nicht benutzte Subplots
    for i in range(len(plot_files), len(axes)):
        axes[i].axis('off')

    # Titel hinzufügen
    fig.suptitle(title, fontsize=font_size)

    # Speichert die kombinierten Abbildung
    # tight_layout(rect=[0, 0, 1, 0.96]-->sorgt dafür, dass die Subplots nicht aneinander kleben, und reserviert Platz für den Titel
    output_filename = os.path.join(output_plot_dir, "Vorverarbeitete_Spektren_Subplots_mean_avarage_baseline.png")
    plt.tight_layout(rect=[0, 0, 1, 0.96])  # Platz für den Titel reservieren
    plt.savefig(output_filename, dpi=300)
    plt.close()  # Speicherplatz freigeben
    print(f"Subplots gespeichert als {output_filename}")


# verarbeitet mehrere Spektren parallel
# filtered_data --> Liste von „Samples“ oder Spektren, die verarbeitet werden sollen
# window_size --> Größe des Fensters um Peaks (für Peak-Extraktion)
# output_dir --> Ordner, um verarbeitete Daten zu speichern
# plot_dir --> Ordner für Heatmaps oder Peak-Plots
# Zustand
# min_margin --> Minimaler Abstand zum Rand
# classic_peaks_dir --> Ordner mit Referenz-Peaks für Vergleich oder Klassifizierung
def parallel_process_spectra(filtered_data, window_size, output_dir, plot_dir, Zustand, min_margin):
    # multiprocessing.Manager() erzeugt sichere, geteilte Objekte, die mehrere Prozesse gleichzeitig bearbeiten können
    # processed_spectra --> verschachteltes Dictionary, das Ergebnisse aus jedem Prozess sammelt
    # all_peak_data --> Dictionary für die Peak-Daten aller Samples
    #
    with multiprocessing.Manager() as manager:
        processed_spectra = manager.dict({'data': manager.dict()})
        # Verwende ein Dictionary statt einer Liste
        all_peak_data = manager.dict()
        # Pool starten und parallele Verarbeitung
        # multiprocessing.Pool()-->Startet eine Gruppe von Prozessen --> automatisch so viele wie CPU-Kerne
        # starmap()--> Ruft parallel die Funktion process_spectrum_parallel auf, mit mehreren Argumenten
        # jedes sample bekommt--> sample --> das Spektrum; i --> Index ; window_size --> für Peak-Fenster; plot_dir --> für Heatmaps/Plots; processed_spectra --> gemeinsam genutztes Dictionary;
        # all_peak_data --> gemeinsam genutztes Dictionary für Peak-Infos; Zustand, min_margin, classic_peaks_dir
        with multiprocessing.Pool() as pool:
            results = pool.starmap(process_spectrum_parallel, [
                (sample, i, window_size, plot_dir, processed_spectra, all_peak_data, Zustand, min_margin) for i, sample
                in enumerate(filtered_data)
            ])

        # Alle Peak-Daten zusammenführen
        all_peak_data_list = [item for sublist in results for item in sublist]

        # Erstellt eine DataFrame für die Peak-Daten
        all_peak_df = pd.DataFrame(all_peak_data_list)

        # Erstellt eine kombinierte Abbildung der Plots
        combined_plot_filename = os.path.join(plot_dir, "combined_peak_plots_vorverarbeitet_max_tree_local_maxima.png")
        combine_peak_plots_to_single_figure(plot_dir, combined_plot_filename, Zustand)

        return all_peak_df


# if __name__ == "__main__":
#
#     #input_dir --> Ordner mit den Rohdaten der Spektren.
#     #output_dir --> Ordner für die verarbeiteten Daten
#     #plot_dir --> Ordner für die erzeugten Heatmaps/Plots.
#     #s.makedirs(exist_ok=True)--> erstellt die Ordner, falls sie noch nicht existieren
#     input_dir = "./Honig_Daten/mini_format/mini"
#     output_dir = "./All_test"
#     plot_dir = "./All_test"

#     os.makedirs(output_dir, exist_ok=True)
#     os.makedirs(plot_dir, exist_ok=True)
#     # Liste für alle exakten Peaks

#     #window_size --> Größe des Fensters für Peak-Extraktion(halb Länge = 5--> Peakfenster=11x11)
#     #min_margin--> Mindestabstand zum Rand
#     window_size = 5
#     min_margin = 5
#     Zustand = "raw"  # Zustand der Daten, z.B. "raw" oder "processed"

#     # lädt und verarbeitet die Rohdaten
#     filtered_data = preprocess_and_visualize_spectra(input_dir, plot_dir)

#     # Nach der Vorverarbeitung: Visualisierung der vorverarbeiteten Spektren als Subplots
#     plot_processed_spectra_in_subplots(output_dir, cols=6, title="Übersicht: Vorverarbeitete Spektren")

#     try:
#         # Parallelverarbeitung der Spektren, inklusive Peak-Erkennung
#         all_peak_df = parallel_process_spectra(filtered_data, window_size, output_dir, plot_dir, Zustand, min_margin)
#     except Exception as e:
#         print(f"Fehler bei der Peak-Erkennung: {str(e)}")

#     # Speichert die kombinierten Peak-Daten als CSV
#     all_peak_df.to_csv(os.path.join(output_dir, "11x11_raw_all_peak_data_exact_nachbarn_weniger.csv"), index=False)
#     print("Alle Peak-Daten gespeichert.")

#     # Speichert die kombinierten Peak-Daten als Excel-Datei
#     all_peak_df.to_excel(os.path.join(output_dir, "11x11_raw_all_peak_data_exact_nachbarn_weniger.xlsx"), index=False)


####################Bildung der Konsensus-Peaks################################


# Die Funktion erzeugt ein Farbdreieck, welches die Mischunng von drei Farben für die entsprechenden Honigytypen visualisiert
# ax: Die Haupt-Achse, auf der das Farbdreieck eingefügt wird
# size: Größe des Farbdreiecks relativ zum Plot (z. B. 0.2 = 20% der Achse)
def add_color_triangle(ax, size):
    # Farbdreieck-Daten
    # resolution--> bestimmt, wie fein das Farbdreieck aufgelöst wird)
    resolution = 100
    # Farben definieren
    # Jede Honigsorte wird einer RGB-Farbe zugeordnet
    # Rot=Linde
    # Gelb=Lavendel
    # Blau= Eukalyptus
    # RGB-Werte sind als NumPy-Arrays
    colors = {
        "Linde": np.array([1.0, 0.0, 0.0]),  # Rot
        "Lavendel": np.array([1.0, 1.0, 0.0]),  # Gelb
        "Eukalyptus": np.array([0.0, 0.0, 1.0])  # Blau
    }
    img = np.ones((resolution, resolution, 3))
    # Farbmischung für jedes Pixel
    # i --> horizontale Achse, j --> vertikale Achse.
    for i in range(resolution):
        for j in range(resolution):
            linde = 1 - (i / (resolution - 1)) - (j / (resolution - 1))
            lavendel = i / (resolution - 1)
            eucalyptus = j / (resolution - 1)
            # Liegt das Pixel innerhalb des Farbdreiecks --> RGB-Wert berechnen: Lineare Mischung der drei Grundfarben.
            # Sonst --> Weiß--> So entsteht das klassische baryzentrische Farbdreieck
            if linde >= 0 and lavendel >= 0 and eucalyptus >= 0:
                color = (
                        linde * colors["Linde"] +
                        lavendel * colors["Lavendel"] +
                        eucalyptus * colors["Eukalyptus"]
                )
                img[j, i, :] = color
            else:
                img[j, i, :] = [1, 1, 1]

    # Inset-Achse erstellen
    # inset_axes legt eine kleine Achse innerhalb der Haupt-Achse an
    # extent=(0,1,0,1) legt die Koordinaten des Bildes fest.

    axins = inset_axes(ax, width=f"{size * 100}%", height=f"{size * 100}%", loc='upper right', borderpad=1)
    axins.imshow(img, origin='lower', extent=(0, 1, 0, 1))
    axins.plot([0, 1, 0, 0], [0, 0, 1, 0], color='black', lw=1)

    # Labels
    axins.text(-0.05, -0.05, "Linde", color=colors["Linde"], fontsize=5, ha='right', va='top')
    axins.text(1.05, -0.05, "Lavendel", color=colors["Lavendel"], fontsize=5, ha='left', va='top')
    axins.text(0.5, 1.05, "Eukalyptus", color=colors["Eukalyptus"], fontsize=5, ha='center', va='bottom')
    # Versteckt Achsenlinien und Tickmarks – nur das Farbdreieck ist sichtbar
    axins.axis('off')

    # mix_component_color mischt Farben basierend auf den Anteilen von drei Honigsorten: Linde, Lavendel und Eukalyptus


def mix_component_color(linden_count, lavender_count, eucalyptus_count):
    # Gesamtsumme berechnen
    # total ist die Summe aller Anteile.
    # Wenn nichts da ist (total == 0), wird Schwarz zurückgegeben (0, 0, 0).
    total = linden_count + lavender_count + eucalyptus_count
    if total == 0:
        return (0, 0, 0)  # Schwarz, wenn nichts vorhanden

    # Definierte RGB-Farben für jede Sorte
    colors = {
        "Linde": np.array([1.0, 0.0, 0.0]),  # Rot
        "Lavendel": np.array([1.0, 1.0, 0.0]),  # Gelb
        "Eukalyptus": np.array([0.0, 0.0, 1.0])  # Blau
    }

    # Anteile berechnen
    # Jeder Anteil wird durch Division durch die Gesamtsumme normalisiert
    linden_ratio = linden_count / total
    lavender_ratio = lavender_count / total
    eucalyptus_ratio = eucalyptus_count / total

    # Lineare Mischung
    # Es wird eine gewichtete Mischung berechnet--> Jede Farbe wird mit ihrem Anteil multipliziert, und die Ergebnisse werden addiert
    mixed_color = (
            linden_ratio * colors["Linde"] +
            lavender_ratio * colors["Lavendel"] +
            eucalyptus_ratio * colors["Eukalyptus"]
    )
    # Rückgabe--> mixed_color wird in ein Tuple umgewandelt
    return tuple(mixed_color)


# Paramter:
# count = aktuelle Menge dieser Honigsorte
# max_count = maximal mögliche Menge dieser Sorte
# honey_type = Name der Honigsorte
# Ziel: eine Farbe zurückgeben, deren Intensität vom Anteil abhängt
def color_single_type_2(count, max_count, honey_type):
    # Definiert die Colormaps für bekannte Honigtypen
    # Je nach Honigsorte wird eine Colormap von Matplotlib gewählt
    if honey_type == "Koriander":
        cmap = plt.cm.Reds
    elif honey_type == "Raps":
        cmap = plt.cm.YlOrBr
    elif honey_type == "Lavendel":
        cmap = plt.cm.Purples
    elif honey_type == "Linde":
        cmap = plt.cm.Greens
    elif honey_type == "Kleehonig":
        cmap = plt.cm.Blues
    else:
        cmap = plt.cm.Greys  # für unbekannte Honigsorten

    # Berechnet die Intensität auf Basis der Häufigkeit
    # Normalisiert den aktuellen Wert auf einen Bereich von 0 bis 1
    # 0 = hellste Farbe der Colormap, 1 = dunkelste/intensivste Farbe
    intensity = count / max_count
    return cmap(intensity)  # Rückgabe der entsprechenden Farbe basierend auf der Intensität


# Diese Funktion erzeugt Scatterplots der Peaks für verschiedene Honigsorten, getrennt nach Einzeltypen und Mischungen
# Paramter:
# avg_peaks: Liste von Peaks
# component_honey_counts: Zeigt die Anteile der einzelnen Honigsorten für jeden Peak
# output_dir: Verzeichnis, in dem die Plots gespeichert werden.
# filename_prefix: Präfix für die gespeicherten Dateien

def plot_peaks_by_honey_type(avg_peaks, component_honey_counts, output_dir, filename_prefix="peaks_by_honey_type"):
    # Maximalwert für Normalisierung
    # Berechnet die maximale Gesamtmenge aller Honigkomponenten, um die Farbintensität zu normalisieren.
    # Wird für color_single_type_2 verwendet
    max_count = max(
        [linden_count + lavender_count + eucalyptus_count for linden_count, lavender_count, eucalyptus_count in
         component_honey_counts])
    print(avg_peaks[:10])  # Zeigt die ersten 10 Peaks

    # Erstelle die Scatterplots für 100% Lindeanteil, 100% Lavendelanteil, 100% Eukalyptusanteil und Mischverhältnisse
    for honey_type in ['Linde', 'Lavendel', 'Eukalyptus', 'Mischung']:
        plt.figure(figsize=(8, 6), dpi=1200)
        plt.title(f"Scatterplot der Konsensus-Peaks für {honey_type}")
        plt.xlabel("Driftzeit")
        plt.ylabel("Retentionszeit")

        # Filtert die Peaks je nach Typ (100% Linde, 100% Lavendel, 100% Eukalyptus, Mischung)
        # Geht alle Peaks durch
        for peak, (linden_count, lavender_count, eucalyptus_count) in zip(avg_peaks, component_honey_counts):
            ret_time = peak["ret_time"]
            drift_time = peak["drift_time"]
            component_id = peak["component_id"]

            # Bedingungen für Linde; Lavendel; Eukalyptus und Mischung
            # honey_type == "Linde"--> Plot, welches Linde darstellen soll
            # lavender_count == 0 and eucalyptus_count == 0--> Sicherstellen, dass dieser Peak wirklich nur Linde enthält, also keine Anteile von Lavendel oder Eukalyptus
            # Farbe berechnen--> color = color_single_type_2(linden_count, max_count, "Linde")--> siehe Funktion "color_single_type_2"

            if honey_type == 'Linde' and lavender_count == 0 and eucalyptus_count == 0:  # Nur Linde
                color = color_single_type_2(linden_count, max_count, "Linde")
                plt.scatter(drift_time, ret_time, color=color, marker='o', s=40)
                plt.text(drift_time, ret_time,
                         f"{linden_count + lavender_count + eucalyptus_count}\nID: {component_id}", fontsize=5,
                         ha='center', va='center', color='black')

            # honey_type == "Lavendel"--> Plot, welches Lavendel darstellen soll

            elif honey_type == 'Lavendel' and linden_count == 0 and eucalyptus_count == 0:  # Nur Lavendel
                color = color_single_type_2(lavender_count, max_count, "Lavendel")
                plt.scatter(drift_time, ret_time, color=color, marker='o', s=20)
                plt.text(drift_time, ret_time,
                         f"{linden_count + lavender_count + eucalyptus_count}\nID: {component_id}", fontsize=5,
                         ha='center', va='center', color='black')

            # honey_type == "Eukalyptus"--> Plot, welches nur Eukalyptus darstellen soll

            elif honey_type == 'Eukalyptus' and linden_count == 0 and lavender_count == 0:  # Nur Eukalyptus
                color = color_single_type_2(eucalyptus_count, max_count, "Eukalyptus")
                plt.scatter(drift_time, ret_time, color=color, marker='o', s=20)
                plt.text(drift_time, ret_time,
                         f"{linden_count + lavender_count + eucalyptus_count}\nID: {component_id}", fontsize=5,
                         ha='center', va='center', color='black')

            # honey_type == 'Mischung'--> plot welches alle Mischungen darstellt
            # linden_count > 0 and lavender_count > 0 and eucalyptus_count > 0--> Diese Mischung muss von allen drei Honigsorten Anteile haben; Keine 2er-Kombination, sondern wirklich alle drei im SpieKeine 2er-Kombination, sondern wirklich alle drei im Spie

            elif honey_type == 'Mischung' and linden_count > 0 and lavender_count > 0 and eucalyptus_count > 0:  # Mischung
                color = mix_component_color(linden_count, lavender_count, eucalyptus_count)  # Mischfarbe
                # Falls component_id == 109, wird das Symbol ein Kreuz ('x'),sonst ein Kreis ('o')
                marker_style = 'x' if component_id == 109 else 'o'
                plt.scatter(drift_time, ret_time, color=color, marker=marker_style, s=30)

        # Abbildungsunterschrift für den Plot basierend auf dem Honigtyp
        if honey_type == 'Linde':
            caption = (""

                       )
        elif honey_type == 'Lavendel':
            caption = ("")
        elif honey_type == 'Eukalyptus':
            caption = (
                ""
            )
        else:  # Mischung
            caption = (
                ""
            )

        # Speichern der Plots für jedes Szenario
        plt.savefig(os.path.join(output_dir, f"{filename_prefix}_{honey_type}.png"), dpi=300, bbox_inches="tight")
        plt.close()

    # Scatterplot für alle Peaks zusammen--> erstellt ein einziges großes Scatterplot für alle Peaks und hängt zusätzlich eine Farblegende in Form eines Dreiecks dran
    #
    fig, ax1 = plt.subplots(figsize=(12, 6))  # Erstelle das Haupt-Scatterplot
    ax1.set_title("Scatterplot der Konsensus-Peaks für alle Honigarten")
    ax1.set_xlabel("Driftzeit")
    ax1.set_ylabel("Retentionszeit")
    # avg_peaks: Liste mit Peak-Daten
    # component_honey_counts: Liste mit den Anteilen (Linde, Lavendel, Eukalyptus) für denselben Peak.

    for peak, (linden_count, lavender_count, eucalyptus_count) in zip(avg_peaks, component_honey_counts):
        ret_time = peak["ret_time"]
        drift_time = peak["drift_time"]
        component_id = peak["component_id"]

        # Beispiel: Linde
        # Bedingungen für Linde; Lavendel; Eukalyptus und Mischung
        # honey_type == "Linde"--> Plot, welches Linde darstellen soll
        # lavender_count == 0 and eucalyptus_count == 0--> Sicherstellen, dass dieser Peak wirklich nur Linde enthält, also keine Anteile von Lavendel oder Eukalyptus
        # Farbe berechnen--> color = color_single_type_2(linden_count, max_count, "Linde")--> siehe Funktion "color_single_type_2"
        # mix_component_color wird aufgerufen, um aus den Anteilen eine Mischfarbe zu berechnen

        if linden_count == 0 and lavender_count == 0 and eucalyptus_count == 0:  # Nur Linde
            color = color_single_type_2(linden_count, max_count, "Linde")
        elif lavender_count == 0 and linden_count == 0 and eucalyptus_count == 0:  # Nur Lavendel
            color = color_single_type_2(lavender_count, max_count, "Lavendel")
        elif eucalyptus_count == 0 and linden_count == 0 and lavender_count == 0:  # Nur Eukalyptus
            color = color_single_type_2(eucalyptus_count, max_count, "Eukalyptus")
        else:  # Mischung
            color = mix_component_color(linden_count, lavender_count, eucalyptus_count)

        # Peak is Diagramm einfügen
        # x-Achse = drift_time
        # y-Achse = ret_time
        # color = vorher berechnete Farbe
        # marker='o' = Kreissymbol
        # s=30 = Punktgröße
        ax1.scatter(drift_time, ret_time, color=color, marker='o', s=30)

    # Positioniert das Farbdreieck für alle Peaks neben dem Hauptplot
    bbox = ax1.get_position()  # Holen der Bounding Box des Hauptplots
    ax_triangle = fig.add_axes([
        bbox.x1 + 0.30,  # Rechts daneben, mit etwas Abstand
        bbox.y0 + (bbox.height - 0.1) / 2,  # Vertikal mittig zum Hauptplot
        0.1,  # Breite des Farbdreiecks
        0.1 * (3 ** 0.5) / 2  # Höhe des Farbdreiecks so skalieren, dass es gleichseitig aussieht
    ])  # Hinzufügen des Farbdreiecks als separates Axes-Objekt

    ax_triangle.set_axis_off()
    # Dreieck mit Farben füllen
    # Achsen werden ausgeblendet (keine Skalen)
    # zeichnet ein Farbdreieck,
    # wobei jede Ecke eine reine Honigsorte darstellt (z.B. Linde, Lavendel, Eukalyptus).
    # Die Farben im Inneren sind Mischungen der drei.
    add_color_triangle(ax_triangle, size=3.0)  # Hinzufügen des Farbdreiecks

    # Speichern des Gesamtplots mit der Farbdreieck-Legende
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"{filename_prefix}_Alle.png"), dpi=300, bbox_inches="tight")
    plt.close()


# Funktion: baut einen Graphen aus den Peak-Daten und bildet Zusammenhangskomponenten
# all_peak_df --> DataFrame von Peaks
# output_dir --> Verzeichnis, wo Ergebnisse gespeichert werden
# threshold --> Maximaler Abstand zwischen Peaks (euklidische distanz)
# batch_size --> Wie viele Punkte pro Durchlauf geprüft werden, um Speicherprobleme zu vermeiden.
def calculate_connected_components(all_peak_df, output_dir, threshold=0.001, batch_size=50000):
    # Erstellt einen Graphen aus den Peaks und findet Zusammenhangskomponenten basierend auf der euklidischen Distanz.
    # Batchweise Kantenfindung mit cKDTree zur Vermeidung von Speicherproblemen.

    import networkx as nx
    import pandas as pd
    import numpy as np
    import os
    from sklearn.preprocessing import MinMaxScaler
    from scipy.spatial import cKDTree

    if threshold is None:
        threshold = 0.001  # Standardwert setzen, falls keiner übergeben wurde
    print(f"Verwendeter threshold: {threshold}")

    # Erstellt einen Graphen aus den Peaks und findet zusammenhängende Komponenten basierend auf der euklidischen Distanz.

    G = nx.Graph()
    # Falls eine Liste übergeben wird, in DataFrame umwandeln.
    if isinstance(all_peak_df, list):
        all_peak_df = pd.DataFrame(all_peak_df)

    print("Struktur von all_peak_df:")
    print(all_peak_df.head())

    # x- und y-Werte extrahieren
    ret_times = all_peak_df['ret_time'].tolist()
    drift_times = all_peak_df['drift_time'].tolist()

    # Skalierung
    # Kombiniert ret_time und drift_time in ein 2D-Array
    # Skaliert beide Achsen zwischen 0 bis 1
    scaler = MinMaxScaler()
    scaled_times = scaler.fit_transform(np.column_stack((ret_times, drift_times))).astype(np.float64)

    # Knoten in den Graph hinzufügen
    # Jeder Peaks wird als Knoten eingefügt
    # Knoten-ID: die skalierte Koordinate (scaled_ret_time, scaled_drift_time).
    # Knoten bekommen zusätzliche Informationen--> honey_type; npy_file und index
    for i in range(len(all_peak_df)):
        node = tuple(scaled_times[i])
        peak_data = all_peak_df.iloc[i]
        G.add_node(node, honey_type=peak_data['honey_type'], npy_file=peak_data['npy_file'], index=i)
    # Nachbarschaften finden
    # Erstellt einen cKDTree aus allen Punkten
    tree = cKDTree(scaled_times)
    n_points = len(scaled_times)

    # Batchweise Kanten hinzufügen
    # query_ball_point --> Findet alle Punkte innerhalb des Radius threshold (euklidische Distanz, p=2)
    # Fügt eine Kante zwischen node1 und jedem Nachbarn hinzu
    # Peaks, die nahe beieinander liegen, werden verbunden
    for start in range(0, n_points, batch_size):
        end = min(start + batch_size, n_points)
        sub_points = scaled_times[start:end]
        neighbors_list = tree.query_ball_point(sub_points, r=threshold, p=2)  # euklidische Distanz

        for i_sub, neighbors in enumerate(neighbors_list):
            i_global = start + i_sub
            node1 = tuple(scaled_times[i_global])
            for j in neighbors:
                if i_global != j:
                    node2 = tuple(scaled_times[j])
                    G.add_edge(node1, node2)

    # Sucht alle Zusammenhangskomponenten
    # Jede Komponente ist eine Menge von Knoten, die über Kanten verbunden sind
    components = list(nx.connected_components(G))
    # Erstellt ein Dictionary, das jedem Peak-Index seine component_id zuordnet.
    component_mapping = {}
    for component_id, component in enumerate(components):
        for node in component:
            index = G.nodes[node]['index']
            component_mapping[index] = component_id
    # Fügt die component_id in den ursprünglichen DataFrame ein.
    all_peak_df['component_id'] = all_peak_df.index.map(component_mapping)
    # Baut eine Liste mit allen Peaks + ihren Attributen
    # Verwendet skalierte Koordinaten (node[0], node[1]).
    detailed_components = []
    for component_id, component in enumerate(components):
        for node in component:
            peak_data = G.nodes[node]
            detailed_components.append({
                'ret_time': node[0],
                'drift_time': node[1],
                'honey_type': peak_data['honey_type'],
                'npy_file': peak_data['npy_file'],
                'index': peak_data['index'],
                'component_id': component_id
            })

    df_detailed_components = pd.DataFrame(detailed_components)
    df_detailed_components.to_excel(os.path.join(output_dir, "detailed_components.xlsx"), index=False)
    df_detailed_components.to_csv(os.path.join(output_dir, "detailed_components.csv"), index=False)

    print("Excel-Datei gespeichert.")

    # Rückgabe
    # G = der vollständige Graph (Knoten + Kanten + Attribute)
    # components = Liste aller verbundenen Punktmengen
    # all_peak_df = ursprünglicher DataFrame + component_id
    return G, components, all_peak_df

    # wird nach der Berechnung der Zusammenhangskomponenten verwendet, um zu zählen, welcher Honigtyp in welcher Komponente wie stark vertreten ist
    # components--> Liste der verbundenen Komponenten aus calculate_connected_components
    # all_peak_df--> Dataframe mit allen Peaks und deren Honigtyp
    # scaled_times--> 2D-Array der skalierten (ret_time, drift_time) Werte


def count_honey_type_proportions(components, all_peak_df, scaled_times):
    # component_honey_stats --> Wird am Ende das Ergebnis als Dictionary speichern.
    component_honey_stats = {}

    print("\n Anteile der Honigtypen pro Komponente")
    # Iteration über alle Komponenten
    # valid_nodes --> Zählt, wie viele Knoten tatsächlich erfolgreich ausgewertet wurden
    for i, component in enumerate(components):
        linden_count = 0
        lavender_count = 0
        eucalyptus_count = 0
        valid_nodes = 0
        # Iteration über Knoten in der Komponente
        for node in component:
            print(f"Node: {node} | Type of node: {type(node)}")
            # Knotenkoordinaten extrahieren
            # Falls Dict --> Werte aus Keys 'ret_time' und 'drift_time' ziehen.
            # Falls Tuple oder Liste --> Werte direkt nehmen
            # Falls Format unbekannt --> Überspringen
            # Falls Konvertierung in Float fehlschlägt --> Überspringen
            try:
                # Extrahiere ret_time und drift_time
                if isinstance(node, dict):
                    node_ret_time = float(node['ret_time'])
                    node_drift_time = float(node['drift_time'])
                elif isinstance(node, (tuple, list)) and len(node) == 2:
                    node_ret_time = float(node[0])
                    node_drift_time = float(node[1])
                else:
                    print(f"Ungültiger Knoten wird übersprungen: {node}")
                    continue
            except (KeyError, ValueError, TypeError) as e:
                print(f"Fehler beim Parsen von Knotenwerten: {node} – {e}")
                continue

            # Findet den Index des Peak-Points im Original-DataFrame
            # Berechnet den Index des am nächsten liegenden Punkts im skalierten Koordinatensystem:
            # Es wird die Summe der absoluten Differenzen benutzt, nicht die echte euklidische Distanz
            # Holt dann den honey_type aus all_peak_df
            index = np.argmin(
                np.abs(scaled_times[:, 0] - node_ret_time) +
                np.abs(scaled_times[:, 1] - node_drift_time)
            )
            honey_type = all_peak_df.iloc[index]['honey_type']

            # Zählt den Peak im passenden Honigtyp.
            # Erhöht die Anzahl gültiger Knoten

            if 'Linde' in honey_type:
                linden_count += 1
            elif 'Lavendel' in honey_type:
                lavender_count += 1
            elif 'Eukalyptus' in honey_type:
                eucalyptus_count += 1

            valid_nodes += 1

        # Berechnung der Anteile in Prozent
        linden_ratio = (linden_count / valid_nodes) * 100 if valid_nodes > 0 else 0
        lavender_ratio = (lavender_count / valid_nodes) * 100 if valid_nodes > 0 else 0
        eucalyptus_ratio = (eucalyptus_count / valid_nodes) * 100 if valid_nodes > 0 else 0

        # Ergebnisse speichern
        # Speichert absolute und relative Werte für jede Komponente
        # Komponente wird mit 1-basiertem Index (i+1) gespeichert

        component_honey_stats[i + 1] = {
            "Linde_Count": linden_count,
            "Lavendel_Count": lavender_count,
            "Eukalyptus_Count": eucalyptus_count,
            "Linde_%": round(linden_ratio, 2),
            "Lavendel_%": round(lavender_ratio, 2),
            "Eukalyptus_%": round(eucalyptus_ratio, 2),
            "Total_Peaks": valid_nodes
        }

        print(f"Komponente {i + 1}: "
              f"Linde: {linden_count} Peaks ({linden_ratio:.2f}%), "
              f"Lavendel: {lavender_count} Peaks ({lavender_ratio:.2f}%), "
              f"Eukalyptus: {eucalyptus_count} Peaks ({eucalyptus_ratio:.2f}%), "
              f"Gesamt: {valid_nodes} gültige Peaks")

    return component_honey_stats
    # Rückgabe-> eine Dictionary

    # Erstellung einer Netzwerkdarstellung der von calculate_connected_components() gefundenen Cluster
    # Paramter:
    # G --> NetworkX-Graph mit Peaks als Knoten.
    # components --> Liste der Mengen von Knoten, jede Menge = eine Connected Component
    # filename --> Dateiname


def plot_connected_components(G, components, output_dir, filename="connected_components.png"):
    colors = plt.cm.hsv(np.linspace(0, 1, len(components)))

    # Erstellt ein Dictionary, das jedem Knoten (node) eine Position zuweist
    # node[1] = Driftzeit
    # node[0] = Retentionszeit
    pos = {node: (node[1], node[0]) for node in G.nodes()}  # Driftzeit, Retentionszei t
    # Plot erstellen
    plt.figure(figsize=(8, 6))
    # X-Achse
    plt.xlabel("Driftzeit")
    # Y-Achse
    plt.ylabel("Retentionszeit")
    # Titel
    plt.title("Zusammenhängende Peak-Komponenten")

    print("\n Start des Plotten der Komponenten")

    # Zeichnen jeder Komponente
    # G.subgraph(node_tuples): Nimmt nur die Knoten dieser Komponente.
    # pos: gleiche Positionierung wie oben
    # node_size=10: Größe der Knoten
    # node_color & edge_color: Gleiche Farbe für Knoten und Kanten einer Komponente.
    # with_labels=False: Keine Beschriftungen

    for i, component in enumerate(components):
        node_tuples = list(component)  # Set von Knoten

        print(f"Verarbeite Komponente {i + 1} mit {len(node_tuples)} Knoten.")

        nx.draw_networkx(
            G.subgraph(node_tuples),
            pos,
            node_size=10,
            node_color=[colors[i]] * len(node_tuples),
            edge_color=[colors[i]] * len(node_tuples),
            with_labels=False
        )

    print("\n Plotten abgeschlossen. Speichern des Bildes.")
    # Speichern der Abbildung
    plt.savefig(os.path.join(output_dir, filename), dpi=300, bbox_inches="tight")
    print(f"Bild gespeichert unter: {os.path.join(output_dir, filename)}")
    plt.close()


# G: ein networkx.Graph
# komponente: eine Liste von Knoten, die zusammen eine Zusammenhangskomponente bilden
# output_dir: Ordner, in dem die Plots gespeichert werden
# filename: Dateiname für den Plot
def plot_einzene_komponente(G, komponente, output_dir, filename="komponente_drift_retention.png"):
    # Falls der Speicherordner nicht existiert, wird er angelegt
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Plot 1: Drift Time vs Retention Time
    pos = {node: (node[1], node[0]) for node in komponente}  # (x=Drift, y=Retention)
    plt.figure(figsize=(6, 5))
    plt.xlabel("Driftzeit")
    plt.ylabel("Retentionszeit")
    plt.title("Zusammenhangskomponente 109 (NetworkX)")

    # Erstellt einen subgraphen von G, der nur die Knoten aus komponente enthält.
    # Zeichnet einen subgraphen
    # blaue Punkte für Knoten
    # hellgraue Linien für kanten
    # keine Labels
    subgraph = G.subgraph(komponente)
    nx.draw_networkx(
        subgraph,
        pos,
        node_size=20,
        node_color="tab:blue",
        edge_color="lightgray",
        with_labels=False
    )
    # Speichert Plot 1 im angegebenen Pfad.
    pfad1 = os.path.join(output_dir, filename)
    plt.savefig(pfad1, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Plot 1 gespeichert unter: {pfad1}")


import pandas as pd
import os


def get_average_peaks(G, all_peak_df, detailed_components, output_dir, filename="scatter_peaks_with_components"):
    avg_peaks_with_attributes = []

    # Falls `all_peak_df` noch keinen Index hat, setzen wir ihn explizit
    if "index" in all_peak_df.columns:
        all_peak_df = all_peak_df.set_index("index")

    for i, component in enumerate(detailed_components):
        # Indizes der Peaks in dieser Komponente
        component_indices = [G.nodes[peak]["index"] for peak in component if peak in G.nodes]

        # Falls keine gültigen Indizes existieren, überspringen
        if not component_indices:
            continue

        # Hol alle Peaks dieser Komponente
        component_peaks = all_peak_df.loc[component_indices]

        # Durchschnittswerte berechnen
        avg_drift_time = component_peaks["drift_time"].mean()
        avg_ret_time = component_peaks["ret_time"].mean()

        avg_peaks_with_attributes.append({
            'ret_time': avg_ret_time,
            'drift_time': avg_drift_time,
            'honeyType': component_peaks["honey_type"].iloc[0],
            'npy_file': component_peaks["npy_file"].iloc[0],
            'component_id': i
        })

    # Speichern der Durchschnittspeaks in einer Excel-Datei
    avg_peaks_df = pd.DataFrame(avg_peaks_with_attributes)
    output_excel_path = os.path.join(output_dir, f"{filename}_average_peaks.xlsx")
    avg_peaks_df.to_excel(output_excel_path, index=False)

    return avg_peaks_with_attributes


def process_peaks_and_plot(all_peak_df, output_dir, threshold=0.001):
    # Sicherstellen, dass die notwendigen Spalten vorhanden sind
    required_columns = {'ret_time', 'drift_time', 'honey_type'}
    if not required_columns.issubset(all_peak_df.columns):
        raise ValueError(f"Fehlende Spalten in all_peak_df. Erwartet: {required_columns}")

    # Berechnet Zusammenhangskomponenten
    G, components, all_peak_df = calculate_connected_components(all_peak_df, output_dir, threshold, batch_size=20000)

    # # Skalierung der Retentions- und Driftzeiten für spätere Zuweisung
    scaler = MinMaxScaler()
    scaled_times = scaler.fit_transform(all_peak_df[['ret_time', 'drift_time']].values)

    # Berechnet die Honigtyp-Anteile pro Komponente
    honey_stats = count_honey_type_proportions(components, all_peak_df, scaled_times)

    # Plottet und speichert das Ergebnis der Zusammenhangskomponenten
    plot_connected_components(G, components, output_dir)
    komponente = components[109]  # oder eine andere Komponente

    plot_einzene_komponente(G, komponente, output_dir, filename="komponente_drift_retention.png")

    get_average_peaks(G, all_peak_df, components, output_dir, filename="scatter_peaks_with_components")

    # Berechnet die Durchschnittspunkte für jede Komponente
    avg_peaks = get_average_peaks(G, all_peak_df, components, output_dir, filename="scatter_peaks_with_components")

    # Extrahiert die Honiganteile für jede Komponente
    component_honey_counts = [(honey['Linde_Count'], honey['Lavendel_Count'], honey['Eukalyptus_Count']) for honey in
                              honey_stats.values()]

    # Plottet Durchschnittspunkte mit den gemischten Farben basierend auf den Honiganteilen
    plot_peaks_by_honey_type(avg_peaks, component_honey_counts, output_dir, filename_prefix="peaks_by_honey_type")


# excel_path --> Pfad zur Excel-Datei mit Peak-Daten
# output_dir --> Ausgabeordner für Plots
# threshold --> Maximaler Abstand zwischen zwei Peaks, damit sie als "verbunden" gelten.
# filter_honey_types --> Liste von Honigsorten, die behalten werden sollen


def process_peaks_from_excel(excel_path, output_dir=".", threshold=0.0002, filter_honey_types=None):
    # Überprüfen, ob die Datei existiert
    if not os.path.exists(excel_path):
        print(f"Datei nicht gefunden: {excel_path}")
        return

    # Excel-Datei laden
    all_peak_df = pd.read_excel(excel_path)
    print(f"Excel-Datei geladen: {excel_path} mit {len(all_peak_df)} Zeilen")

    # Nach bestimmten honey_type-Werten filtern
    if filter_honey_types:
        original_len = len(all_peak_df)
        all_peak_df = all_peak_df[all_peak_df['honey_type'].isin(filter_honey_types)].reset_index(drop=True)
        print(
            f"Gefiltert nach honey_type {filter_honey_types}: {len(all_peak_df)} Zeilen (von ursprünglich {original_len})")

    # Sicherstellen, dass alle nötigen Spalten vorhanden sind
    required_columns = {'ret_time', 'drift_time', 'honey_type'}
    if not required_columns.issubset(all_peak_df.columns):
        raise ValueError(f"Fehlende Spalten in all_peak_df. Erwartet: {required_columns}")

    # Zusammenhangskomponenten bilden
    process_peaks_and_plot(all_peak_df, output_dir, threshold)

    print("Alle Berechnungen und Plots wurden abgeschlossen.")
    return all_peak_df


process_peaks_from_excel(
    excel_path="./All_Test/11x11_raw_all_peak_data_exact_nachbarn_weniger.xlsx",
    output_dir="./All_Test/",
    threshold=0.002,
    filter_honey_types=["Lavendel", "Linde", "Eukalyptus"]
    # filter_honey_types=["Raps"]
)


# ######exakte_Peakextraktion#####


def preprocess_and_visualize_spectra_exact(input_dir, output_plot_dir):
    # Dateneinlesen:
    # ims.Dataset.read_mea: liest alle Messdateien in MEA-Format aus dem ordner in ein ims-Dateset-Objekt
    dataset = ims.Dataset.read_mea(input_dir)
    # Ausgabe: Name des Datensatzes und Anzahl der geladenen Spektren
    print(f"Dataset: {dataset.name}, {len(dataset.data)} Spectra")
    os.makedirs(output_plot_dir, exist_ok=True)
    # interp_riprel(): Interpoliert die Daten auf eine standasierte relative Driftzeitachse (RIP-Referenz)
    dataset.interp_riprel()

    # filtered_data: Liste für Spektren, die erfolgreich vorverarbeitet wurden
    filtered_data = []
    # Umbennenungstabelle für Rohdateinamen
    name_map = {
        "Citrus": "Citrushonig",
        "Lavendel": "Lavendelhonig",
        "Sonnenblume": "Sonnenblumenhonig",
        "Linde": "Lindenhonig",
        "Eukalyptus": "Eukalyptushonig",
        "Akazie": "Akazienhonig",
        "Buchweizen": "Buchweizenhonig",
        "Raps": "Rapshonig",
        "Kastanie": "Kastanienhonig"
    }
    # Schleife über alle geladenen Spektren
    # Leere Spektren werden übersprungen
    for i, sample in enumerate(dataset.data):
        if sample.values.size == 0:
            print(f"Warning: Spektrum {i + 1} ist leer --> Überspringe Vorverarbeitung.")
            continue

        spectrum_name = os.path.splitext(os.path.basename(sample.name))[0]

        # Name aufbereiten
        # Extrahiert den Basisnamen der Datei ohne Endung
        # Zerlegt den Namen in Teile

        teile = spectrum_name.split('_')
        if len(teile) >= 6:
            original_name = teile[2]
            zahl1 = teile[3]
            zahl2 = teile[5]

            name_kurz = name_map.get(original_name, original_name)
            clean_name = f"{name_kurz}_{zahl1}_{zahl2}"
        else:
            clean_name = spectrum_name

        # Rohspektrum visualisieren
        # Zeichnet das Rohspektrum
        plt.figure(figsize=(10, 6))
        sample.plot()
        # Beschriftung der Achsen: Driftzeit, Retentionszeit.
        plt.title(f"{clean_name}_Rohspektrum")
        plt.xlabel("Driftzeit [ms]")
        plt.ylabel("Retentionszeit [s]")
        # Legt Colorbar-Beschriftung auf "Intensität".
        cbar = plt.gcf().axes[-1]
        cbar.set_ylabel("Intensität", fontsize=10)
        caption = ""
        plt.figtext(0.1, -0.03, caption, wrap=True, horizontalalignment='left', fontsize=9)
        # Speichert PNG-Datei im Ausgabeordner
        plt.savefig(os.path.join(output_plot_dir, f"{clean_name}_Rohspektrum.png"), dpi=300, bbox_inches='tight')
        plt.close()

        # Zuschnitt & Baseline-Korrektur
        # Zuschnitt auf einen relevanten Bereich der Driftzeit(dt)
        sample.cut_dt(start=1.02, stop=1.9)
        # Zuschnitt auf einen relevanten Bereich der Retentionszeit(rt)
        sample.cut_rt(start=200, stop=2500)
        sample.values_processed = np.copy(sample.values)

        # Baseline-Korrektur
        # Zeilenweise und spaltenweise wird ein niedriger Perzentilwert (5 %) als Basislinie subtrahiert
        percentile = 5
        # Baseline-Korrektur: Zeilenweise
        perc_vals_rows = np.percentile(sample.values_processed, percentile, axis=0, keepdims=True)
        baseline_rows = perc_vals_rows
        sample.values_processed -= baseline_rows

        # Baseline-Korrektur:Spaltenweise
        perc_vals_col = np.percentile(sample.values_processed, percentile, axis=1, keepdims=True)
        baseline_col = perc_vals_col
        sample.values_processed -= baseline_col
        # Negative Werte nach Subtraktion --> auf 0 setzen.
        sample.values_processed[sample.values_processed < 0] = 0
        sample.values = sample.values_processed
        # Glättung: uniform_filter mittelt lokal über ein Fenster von 10x10 Punkten, um Rauschen zu reduzieren
        sample.values_processed = uniform_filter(sample.values, size=(10, 10))

        # Vorverarbeitetes Spektrum visualisieren
        # Zeichnet das Vorverarbeitete Rohspektrum
        plt.figure(figsize=(10, 6))
        sample.plot()
        # Beschriftung der Achsen:relative Driftzeit, Retentionszeit.
        plt.title(f"{clean_name}_Vorverarbeitetes_Spektrum")
        plt.xlabel("Relative Driftzeit [ms]")
        plt.ylabel("Retentionszeit [s]")
        # Legt Colorbar-Beschriftung auf "Intensität".
        cbar = plt.gcf().axes[-1]  # Annahme: letzte Achse ist die Colorbar
        cbar.set_ylabel("Intensität", fontsize=10)
        caption = ""
        plt.figtext(0.5, -0.008, caption, wrap=True, horizontalalignment='center', fontsize=7)
        # Speichert PNG-Datei im Ausgabeordner
        plot_filename = os.path.join(output_plot_dir, f"{clean_name}_{i + 1}_Vorverarbeitet_MinBaseline.png")
        plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Vorverarbeitetes Spektrum gespeichert als {plot_filename}")

        filtered_data.append(sample)

        # Erstellt Rasterdarstellung (n_rows x n_cols)
        n_spectra = min(18, len(filtered_data))
        n_cols = 6
        n_rows = math.ceil(n_spectra / n_cols)

        fig, axes = plt.subplots(n_rows, n_cols, figsize=(18, 3 * n_rows), sharex=True, sharey=True)
        axes = axes.flatten()
        # Zeigt jedes Spektrum in imshow mit Farbcodierung cmap="viridis"
        for idx in range(n_spectra):
            ax = axes[idx]
            sample = filtered_data[idx]
            ax.imshow(sample.values, aspect='auto', cmap='viridis')
            ax.set_title(f"{idx + 1}: {sample.name}", fontsize=8)
            ax.axis('off')

        # Leere Subplots ausblenden, falls weniger als 18 Spektren
        for idx in range(n_spectra, len(axes)):
            axes[idx].axis('off')

        plt.suptitle("Grid-Plot der ersten 18 Rohspektren", fontsize=16)
        plt.tight_layout(rect=[0, 0, 1, 0.95])

        grid_plot_path = os.path.join(output_plot_dir, "grid_plot_18_rohspektren.png")
        plt.savefig(grid_plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Grid-Plot mit 18 Rohspektren gespeichert unter: {grid_plot_path}")

    # Gibt alle erfolgreich vorverarbeiteten Spektren zurück
    return filtered_data


# Parameter:
# sample: ein einzelnes Spektrum-Objekt
# spectrum_index: Nummer des Spektrums
# window_size: halbe Fenstergröße für Peak-Ausschnit--> window_size=5=Fenster 11×11
# output_dir: Speicherort für Ergebnisse
# processed_spectra: Dictionary, um bereits verarbeitete Spektren zu markieren
# all_peaks_data: globale Peak-Daten für alle Spektren
# min_margin: Mindestabstand vom Rand
# all_exact_peaks_data


def process_spectrum_parallel_exact(sample, spectrum_index, window_size, output_dir, processed_spectra, all_peaks_data,
                                    Zustand, min_margin=5, all_exact_peaks_data=None):
    # es werden die vorverarbeiteten Spektren aus dem Validierungsdatensatz verwendet
    # hier wird nicht vorher normalisiert

    sample.values = sample.values_processed

    # Überprüft, ob das Spektrum schon verarbeitet wurde.
    # Falls ja --> Abbruch
    # Falls nein --> Markieren als verarbeitet
    if sample.name in processed_spectra['data'] and processed_spectra['data'][sample.name]:
        print(f"Spektrum {sample.name} wurde bereits verarbeitet. Überspringe.")
        return []

    processed_spectra['data'][sample.name] = True
    print(f"Start der Verarbeitung von Spektrum {spectrum_index + 1}: {sample.name}...")

    # Leere Listen, in denen später die detektierten Peaks und die exakten (vordefinierten) Peaks gespeichert werden.

    spectrum_peak_data = []
    exact_peak_data = []  # Hier speichern wir nur die exakten Peaks!

    # Extrahiert aus dem Dateinamen (sample.name) die Honigsorte
    # Falls der Name nicht dem erwarteten Format entspricht --> "Unknown"

    try:
        try:
            honey_type = sample.name.split('_')[2]
        except IndexError:
            honey_type = "Unknown"

        # Hier wird ein feste Koordinate aus dem GC-IMS-Spektrum definiert
        exact_coords = [
            (716.412666666667, 1.09538600785056),
        ]

        # Zuordnung der Indexposition
        # Die tatsächlichen Werte im Raster (sample.ret_time, sample.drift_time) werden auf die nächsten Indizes gemappt

        coord_indices = []
        for ret_t, drift_t in exact_coords:
            try:
                ret_index = np.argmin(np.abs(sample.ret_time - ret_t))
                drift_index = np.argmin(np.abs(sample.drift_time - drift_t))
                # Randprüfung--> Nur gültige Koordinaten werden gespeichert
                if (ret_index >= min_margin and ret_index < sample.values.shape[0] - min_margin and
                        drift_index >= min_margin and drift_index < sample.values.shape[1] - min_margin):
                    coord_indices.append((ret_index, drift_index))
            except Exception as e:
                print(f"Fehler bei der Zuordnung von ({ret_t}, {drift_t}): {e}")

        all_coords_to_process = []

        # Map für spezielle Umbenennungen
        name_map = {
            "Citrus": "Citrushonig",
            "Lavendel": "Lavendelhonig",
            "Sonnenblume": "Sonnenblumenhonig",
            "Linde": "Lindenhonig",
            "Eukalyptus": "Eukalyptushonig",
            "Akazie": "Akazienhonig",
            "Buchweizen": "Buchweizenhonig",
            "Raps": "Rapshonig",
            "Kastanie": "Kastanienhonig"

        }

        # Ursprünglichen Namen zerlegen
        teile = sample.name.split('_')

        # Absicherung, falls Format mal nicht stimmt
        if len(teile) >= 6:
            original_name = teile[2]
            zahl1 = teile[3]
            zahl2 = teile[5]

            # Name ersetzen
            name_kurz = name_map.get(original_name, original_name)

            neuer_name = f"{name_kurz}_{zahl1}_{zahl2}"
        else:
            # Falls unerwartetes Format, einfach Originalname nehmen
            neuer_name = sample.name

        # Plot erstellen
        plt.figure(figsize=(12, 8))
        sample.plot()

        for ret_index, drift_index in coord_indices:
            plt.plot(sample.drift_time[drift_index], sample.ret_time[ret_index], 'g+', markersize=10,
                     label='Exakter Peak')

        #  plt.legend()

        plt.title(f"Peak-Plot (Fest definierter Peak): {neuer_name}")
        plt.xlabel("Relative Driftzeit [ms]")
        plt.ylabel("Retentionszeit [s]")
        cbar = plt.gcf().axes[-1]  # Annahme: letzte Achse ist die Colorbar
        cbar.set_ylabel("Intensität", fontsize=10)

        caption = ("")
        plt.figtext(0.5, -0.05, caption, wrap=True, horizontalalignment='center', fontsize=7)

        peak_plot_filename = os.path.join(output_dir, f"peak_plot_{sample.name}_EXACT_plus_neighbors.png")
        plt.savefig(peak_plot_filename, dpi=300, bbox_inches="tight")
        plt.close()
        print(f"Peak-Plot gespeichert unter: {peak_plot_filename}")

        # Jetzt separat: Nur die exakten Koordinaten speichern
        for ret_index, drift_index in coord_indices:
            peak_intensity = sample.values_processed[ret_index, drift_index]
            ret_time = sample.ret_time[ret_index]
            drift_time = sample.drift_time[drift_index]
            unique_id = uuid.uuid4().hex[:8]
            peak_window, intensity = extract_window_exact(
                sample, {"ret_time": ret_time, "drift_time": drift_time}, window_size, output_dir, Zustand, unique_id
            )

            if peak_window.size == 0 or peak_window.shape != (2 * window_size + 1, 2 * window_size + 1):
                print(f"Ungültiges Fenster für exakten Peak bei RT={ret_time}, DT={drift_time}. Überspringe.")
                continue

            window_filename = os.path.join(
                output_dir, f"{sample.name}_peak_window_{ret_time:.2f}_{drift_time:.2f}_EXACT.npy"
            )
            np.save(window_filename, peak_window)

            exact_peak_data.append({
                'honey_type': honey_type,
                'ret_time': ret_time,
                'drift_time': drift_time,
                'intensity': peak_intensity,
                'npy_file': window_filename,
            })

            # Füget die exakten Peak-Daten in die globale Liste für alle Spektren ein
            if all_exact_peaks_data is not None:
                all_exact_peaks_data.append({
                    'honey_type': honey_type,
                    'ret_time': ret_time,
                    'drift_time': drift_time,
                    'intensity': peak_intensity,
                    'npy_file': window_filename,
                })

        # Speichern der großen Tabelle (exakt + Nachbarn)
        spectrum_df = pd.DataFrame(spectrum_peak_data)
        excel_filename_all = os.path.join(output_dir, f"{sample.name}_peak_data_EXACTplus.xlsx")
        with pd.ExcelWriter(excel_filename_all) as writer:
            spectrum_df.to_excel(writer, index=False, sheet_name='Peak Data')

        print(f"Peak-Daten (exakt + Nachbarn) gespeichert in {excel_filename_all}")

        # Speichern der exakten Tabelle (nur exact_coords)
        if exact_peak_data:
            exact_df = pd.DataFrame(exact_peak_data)
            excel_filename_exact = os.path.join(output_dir, f"{sample.name}_peak_data_EXACT_only.xlsx")
            with pd.ExcelWriter(excel_filename_exact) as writer:
                exact_df.to_excel(writer, index=False, sheet_name='Exact Peak Data')
            print(f"Nur exakte Peak-Daten gespeichert in {excel_filename_exact}")

    except Exception as e:
        print(f"Fehler bei der Verarbeitung von Spektrum {spectrum_index + 1} ({sample.name}): {str(e)}")

    print(f"Spektrum {spectrum_index + 1} abgeschlossen: {sample.name}")
    spectrum_peak_data.extend(exact_peak_data)
    return spectrum_peak_data


def extract_window_exact(sample, peak, window_size, output_dir, Zustand, unique_id):
    # Extrahiert die Retentions- und Driftzeit-Werte des Peaks
    peak_ret_time = peak['ret_time']  # Originalwert der Retentionszeit
    peak_drift_time = peak['drift_time']  # Originalwert der Driftzeit

    # Zuordnung von Retentionszeit und Driftzeit zu Indizes (exakte Übereinstimmung)
    try:
        ret_index = np.where(sample.ret_time == peak_ret_time)[0][0]
        drift_index = np.where(sample.drift_time == peak_drift_time)[0][0]
    except IndexError:
        raise ValueError(f"Peak-Werte ({peak_ret_time}, {peak_drift_time}) passen nicht zu den Indizes!")

    # Extrahiert die Peakintensität direkt an den Originalwerten
    # Greift auf den genauen Wert (Signalstärke) an dieser Koordinate zu
    intensity = sample.values[ret_index, drift_index]

    # Bestimmt basierend auf Indizes die Fenstergrenzen
    # Start und Ende werden so gewählt, dass das Fenster window_size Pixel in jede Richtung geht
    start_ret_index = max(0, ret_index - window_size)
    end_ret_index = min(sample.values.shape[0], ret_index + window_size + 1)

    start_drift_index = max(0, drift_index - window_size)
    end_drift_index = min(sample.values.shape[1], drift_index + window_size + 1)

    # Extrahiert das Fenster basierend auf den Indizes
    peak_window = sample.values[start_ret_index:end_ret_index, start_drift_index:end_drift_index]

    # Zero Padding anwenden, falls notwendig
    # Berechnet, ob an einer Seite Pixel fehlen, also zu nah am Rand sind
    # falls ja--> fehlende Pixel werden mit 0 aufgefüllt
    pad_left_ret = max(0, window_size - ret_index)
    pad_right_ret = max(0, (ret_index + window_size + 1) - sample.values.shape[0])
    pad_left_drift = max(0, window_size - drift_index)
    pad_right_drift = max(0, (drift_index + window_size + 1) - sample.values.shape[1])

    if pad_left_ret > 0 or pad_right_ret > 0 or pad_left_drift > 0 or pad_right_drift > 0:
        peak_window = np.pad(
            peak_window,
            ((pad_left_ret, pad_right_ret), (pad_left_drift, pad_right_drift)),
            mode='constant',
            constant_values=0
        )

    # Sicherstellen, dass das Fenster die Zielgröße hat
    target_size = 2 * window_size + 1
    if peak_window.shape != (target_size, target_size):
        print(f"Warnung: Fenstergröße ist {peak_window.shape}, aber {target_size} erwartet.")

    intensity = sample.values[ret_index, drift_index]

    # Erstelle Heatmap und speichern
    # Enthält:
    # Probenname (sample.name)
    # Retentionszeit und Driftzeit mit 6 Nachkommastellen
    # Die eindeutige ID (unique_id)
    # Die Fenstergröße (11x11)
    # Suffix _vorverarbeitet.png--> Hinweis, dass es aus vorverarbeiteten Daten stammt
    heatmap_filename = os.path.join(
        output_dir,
        f"{sample.name}_heatmap_RT_{peak_ret_time:.6f}_DT_{peak_drift_time:.6f}_{unique_id}_11x11_exact.png"
    )

    plt.figure(figsize=(10, 10))

    # Zeichnet die Heatmapy
    # verwendet Seaborn Heatmap
    # annot=True --> Zahlenwerte werden in jedes Feld geschrieben.
    # fmt=".2f" --> 2 Nachkommastellen.
    # cmap="viridis" --> Farbverlauf
    # linecolor='white' --> weiße Gitterlinien.
    # linewidths=0.5 --> dünne Linien
    sns.heatmap(
        peak_window,
        annot=True,
        fmt=".2f",
        cmap="viridis",
        cbar=True,
        linecolor='white',
        linewidths=0.5,
        annot_kws={"size": 5}
    )
    # Titel und Achsenbeschriftung
    plt.title(f"Peak Heatmap: {sample.name}")
    # X-Achsenbeschriftung
    plt.xlabel("Drift Time")
    # Y-Achsenbeschriftung
    plt.ylabel("Retention Time")
    # Text unter der Grafik(optional)
    fig_caption = ("")
    plt.figtext(0.445, 0.02, fig_caption, ha="center", va="center", fontsize=7)  # Unterhalb des Plots
    # Speichern der Heatmap
    plt.savefig(heatmap_filename, bbox_inches="tight")
    plt.close()
    print(f"Heatmap gespeichert unter: {heatmap_filename}")

    # Rückgabe
    # peak_window --> 2D-Array des ausgeschnittenen Fensters
    # intensity --> Original-Intensität am Peakzentrum
    return peak_window, intensity


# erstellt ein Grid-Plot
# Parameter
# plot_dir --> Ordner, in dem die einzelnen Peak-Plots liegen
# output_filename --> Pfad & Dateiname der kombinierten Abbildung
# Zustand --> wird hier gar nicht direkt benutzt, könnte für spätere Erweiterungen oder Logik gedacht sein.
# cols --> Anzahl der Spalten im Bildraster
# title --> Titel, der oben auf das große Bild geschrieben wird
# font_size --> Schriftgröße des Titels.
# scale_factor --> Skaliert die einzelnen Bilder hoch oder runter
def combine_peak_plots_to_single_figure_exact(plot_dir, output_filename, Zustand, cols=6, title="Peak-Plot-Übersicht",
                                              font_size=200, scale_factor=1.5):
    # Ladet alle Plot-Dateien aus dem Verzeichnis
    # Sucht alle Dateien in plot_dir, deren Name auf peak_plot_vorverarbeitet.png endet
    # Speichert vollständige Pfade in plot_files
    plot_files = [os.path.join(plot_dir, f) for f in os.listdir(plot_dir) if
                  f.endswith("Vorverarbeitet_MinBaseline.png")]
    plot_files.sort()  # Sortiere die Dateien alphabetisch

    if not plot_files:
        print(f"Keine Peak-Plots im Verzeichnis {plot_dir} gefunden.")
        return

    # Lädt jedes Bild mit Pillow
    # Berechnet, wie viele Zeilen gebraucht werden, um alle Bilder in cols Spalten darzustellen
    # (len(images) + cols - 1) // cols sorgt dafür, dass unvollständige letzte Reihen auch gezählt werden
    images = [Image.open(file) for file in plot_files]
    rows = (len(images) + cols - 1) // cols  # Anzahl der benötigten Reihen

    # Bestimmt die Größe der kombinierten Abbildung (mit Skalierungsfaktor)
    # Multipliziert mit scale_factor, um die Bilder zu vergrößern/verkleinern.
    # Multipliziert mit Anzahl Spalten/Zeilen, um die Gesamtgröße zu berechnen.
    max_width = int(max(img.width for img in images) * scale_factor)
    max_height = int(max(img.height for img in images) * scale_factor)
    fig_width = cols * max_width
    fig_height = rows * max_height

    # Zusätzlicher Platz für die Überschrift
    title_height = font_size + 70  # Platz für den Titel basierend auf Schriftgröße
    combined_image = Image.new("RGB", (fig_width, fig_height + title_height), (255, 255, 255))

    # Fügt die einzelnen Plots in das Raster ein
    # col & row bestimmen Position im Raster
    # x_offset & y_offset sind die Pixelpositionen, an denen das Bild eingefügt wird.
    # Bilder werden vorher auf gleiche Größe skaliert
    # Mit paste werden die Bilder eingefügt.
    for idx, img in enumerate(images):
        col = idx % cols
        row = idx // cols
        x_offset = col * max_width
        y_offset = row * max_height + title_height  # Platz für den Titel berücksichtigen
        img_resized = img.resize((max_width, max_height))  # Größe der Bilder ändern
        combined_image.paste(img_resized, (x_offset, y_offset))

    # Füge den Titel hinzu
    # ImageDraw erstellt einen Zeichenbereich auf dem großen Bild
    # versucht, Arial zu laden --> ansonsten auf Standardschrift, falls nicht verfügbar
    draw = ImageDraw.Draw(combined_image)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)  # Schriftgröße festlegen
    except IOError:
        font = ImageFont.load_default()

    # Berechnet die Bounding Box und zentriere den Text
    text_bbox = draw.textbbox((0, 0), title, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_x = (fig_width - text_width) // 2
    text_y = (title_height - font_size) // 2

    draw.text((text_x, text_y), title, font=font, fill=(0, 0, 0))

    # Speichert die kombinierte Abbildung
    combined_image.save(output_filename)
    print(f"Kombinierte Abbildung mit Titel gespeichert unter: {output_filename}")


# Parameter
# filtered_data --> Liste von vorbereiteten Spektren
# window_size --> Fenstergröße für die Peakfenster
# Output_dir--> Ordner für die Excel-Ausgaben
# plot_dir--> Ausgabe für die Peak-Plots
# min_marigin--> Abstand zum Rand
# Zustand
def parallel_process_spectra_exact(filtered_data, window_size, output_dir, plot_dir, Zustand, min_margin):
    import multiprocessing
    import os
    import pandas as pd
    # multiprocessing.Manager() erzeugt sichere, geteilte Objekte, die mehrere Prozesse gleichzeitig bearbeiten können
    # processed_spectra --> verschachteltes Dictionary, das Ergebnisse aus jedem Prozess sammelt
    # all_peak_data --> Dictionary für die Peak-Daten aller Samples
    #
    with multiprocessing.Manager() as manager:
        processed_spectra = manager.dict({'data': manager.dict()})
        # Verwendet ein Dictionary
        all_peak_data = manager.dict()

        # Liste für alle exakten Peakdaten
        all_exact_peaks_data = manager.list()
        # Pool starten und parallele Verarbeitung
        # multiprocessing.Pool()-->Startet eine Gruppe von Prozessen-->automatisch so viele wie CPU-Kerne
        # starmap()--> Ruft parallel die Funktion process_spectrum_parallel auf, mit mehreren Argumenten
        # jedes sample bekommt--> sample --> das Spektrum; i --> Index ; window_size --> für Peak-Fenster; plot_dir --> für Heatmaps/Plots; processed_spectra --> gemeinsam genutztes Dictionary;
        # all_peak_data --> gemeinsam genutztes Dictionary für Peak-Infos; Zustand, min_margin,all_exact_peak_data
        with multiprocessing.Pool() as pool:
            results = pool.starmap(process_spectrum_parallel_exact, [
                (sample, i, window_size, plot_dir, processed_spectra, all_peak_data, Zustand, min_margin,
                 all_exact_peaks_data)
                for i, sample in enumerate(filtered_data)
            ])

        # Alle Peak-Daten zusammenführen
        all_peak_data_list = [item for sublist in results for item in sublist]

        # DataFrame für die Peak-Daten (alle Peaks inkl. Nachbarn)
        all_peak_df = pd.DataFrame(all_peak_data_list)

        # DataFrame für nur exakte Peaks (alle Samples zusammen)
        all_exact_df = pd.DataFrame(list(all_exact_peaks_data))

        # Speichern in eine gemeinsame Excel-Datei
        all_exact_peaks_filename = os.path.join(output_dir, "all_exact_peaks_data.xlsx")
        with pd.ExcelWriter(all_exact_peaks_filename) as writer:
            all_exact_df.to_excel(writer, index=False, sheet_name='All Exact Peak Data')

        print(f" Alle exakten Peaks wurden gesammelt und gespeichert in {all_exact_peaks_filename}")

        # Erstellt kombinierte Abbildung der Plots
        combined_plot_filename = os.path.join(plot_dir, "combined_peak_plots_vorverarbeitet_max_tree_local_maxima.png")
        combine_peak_plots_to_single_figure_exact(plot_dir, combined_plot_filename, Zustand)

        return all_peak_df


# if __name__ == "__main__":
#     input_dir = "./Honig_Daten/mini_format/mini"
#     output_dir = "./Honig_Ergebnisse/All_Test_exact"
#     plot_dir = "./Honig_Ergebnisse/All_Test_exact"

#     os.makedirs(output_dir, exist_ok=True)
#     os.makedirs(plot_dir, exist_ok=True)
#     window_size = 5
#     min_margin = 5
#     Zustand ="raw"
#     #Daten laden
#     filtered_data = preprocess_and_visualize_spectra_exact(input_dir, plot_dir)
#     # Nach der Vorverarbeitung: Visualisierung der vorverarbeiteten Spektren als Subplots
#     # Funktion zur Visualisierung der vorverarbeiteten Spektren
#     plot_processed_spectra_in_subplots(output_dir, cols=6, title="Übersicht: Vorverarbeitete Spektren exakte Spektren")


#     try:
#         all_peak_df = parallel_process_spectra_exact(filtered_data, window_size, output_dir, plot_dir, Zustand, min_margin)
#     except Exception as e:
#         print(f"Fehler bei der Peak-Erkennung: {str(e)}")

#     # Speichert die kombinierten Peak-Daten
#     all_peak_df.to_csv(os.path.join(output_dir, "11x11_raw_all_peak_data_exact_nachbarn.csv"), index=False)
#     print("Alle Peak-Daten gespeichert.")

#     # Speichert die kombinierten Peak-Daten
#     all_peak_df.to_excel(os.path.join(output_dir, "11x11_raw_all_peak_data_exact_nachbarn.xlsx"), index=False)
#     print("Alle Peak-Daten gespeichert.")


#####Autoencoder#####

def random_sampling_tensor(data_tensor, sample_size=None):
    indices = torch.randperm(len(data_tensor))[:sample_size]
    return data_tensor[indices]


# # --- Einstellungen ---
# input_excel: Excel-Datei mit Pfaden zu .npy Dateien
# output_dir: Ordner, in dem Ergebnisse gespeichert werden
# plot_output_path: Speicherort für die PDF mit den Rekonstruktionen
# component_filter: nur bestimmte Komponenten filtern
# pochs, latent_dim, batch_size, lr: Standard Hyperparameter für das Training des VAE
# DEVICE: Automatische Auswahl zwischen GPU (cuda) oder CPU
input_excel = './All_test/11x11_raw_all_peak_data_exact_nachbarn_weniger.xlsx'
output_dir = "./All_test/"
plot_output_path = os.path.join(output_dir, "reconstructions_100.pdf")
component_filter = None  # z.B. 23 oder None
epochs = 300
latent_dim = 16
batch_size = 128
lr = 1e-3
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Device: {DEVICE}")

# Daten laden
# Excel wird als DataFrame geladen
# Filter auf bestimmte component_id
# Jede .npy Datei wird geladen – np.load(path) → Liste von Arrays.
df = pd.read_excel(input_excel)
if component_filter:
    df = df[df['component_id'] == component_filter]

peak_windows = [np.load(path) for path in df['npy_file']]
peak_windows = np.array(peak_windows)
original_shape = peak_windows.shape[1:]
#
print("Shape:", peak_windows[0].shape)
print(peak_windows[0])

from sklearn.preprocessing import normalize

peak_windows_normalized = []
# Normalisierung der Daten
# Werte in jedem Peak-Fenster auf [0,1] skalieren
for window in peak_windows:
    min_val = window.min()
    max_val = window.max()
    if max_val - min_val == 0:
        normalized = np.zeros_like(window)  # oder np.ones_like(window)
    else:
        normalized = (window - min_val) / (max_val - min_val)
    peak_windows_normalized.append(normalized)

peak_windows_normalized = np.array(peak_windows_normalized)
print(peak_windows_normalized.shape)
print(peak_windows_normalized[0])

# Flatten auf 2D (N, 121) für 11x11
# Für ein VAE werden die Fenster zu Vektoren „flach“ gemacht
# Ein 11x11-Fenster → Vektor mit 121 Dimensionen
# Danach in einen PyTorch Tensor konvertiert (float32)
peak_windows_flat = peak_windows_normalized.reshape(len(peak_windows_normalized), -1)
print(peak_windows_flat.shape)  # (N, 121)

# Dann in Tensor umwandeln
X_tensor = torch.tensor(peak_windows_flat, dtype=torch.float32)

sample_size = None
X_sampled = random_sampling_tensor(X_tensor, sample_size=sample_size)

# Train-Test-Split
# Daten werden in Training (80%) und Test (20%) aufgeteilt
# PyTorch TensorDataset
# DataLoader sorgt für Batch-Training und optionales Shuffling
#
X_train, X_test = train_test_split(X_sampled, test_size=0.2, random_state=67)

train_dataset = TensorDataset(X_train)
test_dataset = TensorDataset(X_test)

# shuffle=True nur für Training
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

# x_dim → Eingabegröße des VAE (flattened window)
x_dim = X_tensor.shape[1]
# hidden_dim → Größe des versteckten Layers in Encoder/Decoder
hidden_dim = 300


# --- 4. VAE definieren ---
# class Encoder(nn.Module):
#     def __init__(self, input_dim, hidden_dim, latent_dim):
#         super().__init__()
#         self.fc1 = nn.Linear(input_dim, hidden_dim)
#         self.fc2 = nn.Linear(hidden_dim, hidden_dim)
#         self.mean = nn.Linear(hidden_dim, latent_dim)
#         self.logvar = nn.Linear(hidden_dim, latent_dim)
#         self.relu = nn.LeakyReLU(0.2)

#     def forward(self, x):
#         h = self.relu(self.fc1(x))
#         h = self.relu(self.fc2(h))
#         return self.mean(h), self.logvar(h)

# class Decoder(nn.Module):
#     def __init__(self, latent_dim, hidden_dim, output_dim):
#         super().__init__()
#         self.fc1 = nn.Linear(latent_dim, hidden_dim)
#         self.fc2 = nn.Linear(hidden_dim, hidden_dim)
#         self.out = nn.Linear(hidden_dim, output_dim)
#         self.relu = nn.LeakyReLU(0.2)

#     def forward(self, z):
#         h = self.relu(self.fc1(z))
#         h = self.relu(self.fc2(h))
#         return torch.sigmoid(self.out(h))
#         #return self.out(h)


class Encoder(nn.Module):

    def __init__(self, input_dim, hidden_dim, latent_dim):
        super(Encoder, self).__init__()

        self.FC_input = nn.Linear(input_dim, 128)
        self.FC_input2 = nn.Linear(128, 128)
        self.FC_input4 = nn.Linear(128, 64)
        self.FC_input7 = nn.Linear(64, 32)
        self.FC_input9 = nn.Linear(32, 32)
        self.FC_input10 = nn.Linear(32, 16)
        self.FC_mean = nn.Linear(16, latent_dim)
        self.FC_var = nn.Linear(16, latent_dim)

        self.LeakyReLU = nn.LeakyReLU(0.2)

        self.training = True

    def forward(self, x):
        h_ = self.LeakyReLU(self.FC_input(x))
        h_ = self.LeakyReLU(self.FC_input4(h_))
        h_ = self.LeakyReLU(self.FC_input7(h_))
        h_ = self.LeakyReLU(self.FC_input9(h_))
        h_ = self.LeakyReLU(self.FC_input10(h_))
        mean = self.FC_mean(h_)
        log_var = self.FC_var(h_)
        return mean, log_var


class Decoder(nn.Module):
    def __init__(self, latent_dim, hidden_dim, output_dim):
        super(Decoder, self).__init__()

        self.FC_hidden1 = nn.Linear(latent_dim, 16)
        self.FC_hidden10 = nn.Linear(16, 32)
        self.FC_hidden2 = nn.Linear(32, 32)
        self.FC_hidden4 = nn.Linear(32, 64)
        self.FC_hidden7 = nn.Linear(64, 128)
        self.FC_hidden9 = nn.Linear(128, 128)
        self.FC_output = nn.Linear(128, output_dim)

        self.LeakyReLU = nn.LeakyReLU(0.2)

    def forward(self, z):
        h = self.LeakyReLU(self.FC_hidden1(z))
        h = self.LeakyReLU(self.FC_hidden10(h))
        h = self.LeakyReLU(self.FC_hidden2(h))
        h = self.LeakyReLU(self.FC_hidden4(h))
        h = self.LeakyReLU(self.FC_hidden7(h))
        h = self.LeakyReLU(self.FC_hidden9(h))
        x_hat = self.FC_output(h)
        return x_hat


class VAE(nn.Module):
    def __init__(self, encoder, decoder):
        super().__init__()
        self.encoder = encoder
        self.decoder = decoder

    def reparameterize(self, mu, logvar):
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std

    def forward(self, x):
        mu, logvar = self.encoder(x)
        z = self.reparameterize(mu, logvar)
        return self.decoder(z), mu, logvar


def vae_loss(x, x_hat, mu, logvar, beta=1.5):
    recon = nn.functional.mse_loss(x_hat, x, reduction='sum')
    kld = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
    return recon + beta * kld


# return total, recon, kld

# Encoder und Decoder werden mit den jeweiligen Dimensionen erzeugt.
# VAE kombiniert beide Module
# .to(DEVICE) schiebt das Modell auf GPU (falls verfügbar)
# Adam Optimizer mit Lernrate lr = 1e-3 für das Training
encoder = Encoder(x_dim, hidden_dim, latent_dim)
decoder = Decoder(latent_dim, hidden_dim, x_dim)
model = VAE(encoder, decoder).to(DEVICE)
optimizer = torch.optim.Adam(model.parameters(), lr=lr)

# Epoch: Ein kompletter Durchlauf über alle Trainingsdaten
# model.train() aktiviert den Trainingsmodus
# optimizer.zero_grad() löscht alte Gradienten
# model(x_batch) → Rekonstruktion + latente Parameter
# vae_loss() → Summe aus Rekonstruktionsfehler + KLD
# loss.backward() → Backpropagation
# optimizer.step() → Parameterupdate


for epoch in range(epochs):
    model.train()
    train_loss = 0
    for (x_batch,) in train_loader:
        x_batch = x_batch.to(DEVICE)
        optimizer.zero_grad()
        x_hat, mu, logvar = model(x_batch)
        loss = vae_loss(x_batch, x_hat, mu, logvar)
        loss.backward()
        optimizer.step()
        train_loss += loss.item()

    # test
    # model.eval() deaktiviert Dropout/BatchNorm
    # torch.no_grad() → keine Gradienten
    # Testverlust wird berechnet, um Überanpassung zu prüfen

    model.eval()
    test_loss = 0
    with torch.no_grad():
        for (x_batch,) in test_loader:
            x_batch = x_batch.to(DEVICE)
            x_hat, mu, logvar = model(x_batch)
            loss = vae_loss(x_batch, x_hat, mu, logvar)
            test_loss += loss.item()

    print(
        f"Epoch {epoch + 1}: Train Loss = {train_loss / len(train_dataset):.4f}, Test Loss = {test_loss / len(test_dataset):.4f}")

# Speichert nur Modellgewichte, nicht die ganze TrainingsumgebungSpeichert nur Modellgewichte, nicht die ganze Trainingsumgebung
minimal_model_path = os.path.join(output_dir, "vae_model_minimal.pt")
torch.save(model.state_dict(), minimal_model_path)
print(f"Minimal-Modell gespeichert unter: {minimal_model_path}")

# Rekonstruktion visualisieren
# Dann Evaluation ohne Gradienten
model.eval()
with torch.no_grad():
    recon, _, _ = model(X_tensor.to(DEVICE))
    recon_np = recon.cpu().numpy().reshape(-1, *original_shape)
    original_np = X_tensor.cpu().numpy().reshape(-1, *original_shape)

# Splitting in Batches verhindert GPU-Speicherüberlauf
# mu_list speichert latente Mittelwerte für PCA/Analyse
batch_size = 1000
recon_list = []
mu_list = []
model.eval()
with torch.no_grad():
    for i in range(0, X_tensor.size(0), batch_size):
        batch = X_tensor[i:i + batch_size].to(DEVICE)
        recon_batch, _, _ = model(batch)
        recon_list.append(recon_batch.cpu())
        mu_list.append(mu.cpu())
recon_np = torch.cat(recon_list, dim=0).numpy().reshape(-1, *original_shape)
original_np = X_tensor.cpu().numpy().reshape(-1, *original_shape)

#
mu_tensor = torch.cat(mu_list, dim=0)
mu_np = mu_tensor.numpy()
print("mu_np.shape:", mu_np.shape)

# Rekonstruktion als PDF speichern
# Erstellt PDF  Vergleich Original vs. Rekonstruktion
os.makedirs(output_dir, exist_ok=True)
with PdfPages(plot_output_path) as pdf:
    for i in range(min(100, len(original_np))):
        fig, axes = plt.subplots(1, 2, figsize=(8, 4))
        axes[0].imshow(original_np[i], cmap="viridis")
        axes[0].set_title("Original")
        axes[0].axis("off")
        axes[1].imshow(recon_np[i], cmap="viridis")
        axes[1].set_title("Rekonstruiert")
        axes[1].axis("off")
        fig.suptitle(f"Sample {i}")
        pdf.savefig(fig)
        plt.close(fig)

print(f" Rekonstruktionen gespeichert unter: {plot_output_path}")

import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

mu_np_flat = mu_np.reshape(mu_np.shape[0], -1)  # Shape: (11152, 176)

# PCA auf 2D
pca = PCA(n_components=2)
pca_result = pca.fit_transform(mu_np_flat)  # Shape: (11152, 2)

# Plot
plt.figure(figsize=(8, 6))
plt.scatter(pca_result[:, 0], pca_result[:, 1], s=3, alpha=0.5, cmap="viridis")
plt.title("PCA des Latent Space (flattened mu)")
plt.xlabel("Hauptkomponente 1")
plt.ylabel("Hauptkomponente 2")
plt.grid(True)
plt.tight_layout()
plt.show()

# #####wenn man das modell einfach nur laden möchte


# # Parameter und Einstellungen
# Pfad zur Excel-Datei mit den Messdaten
new_input_excel = "./Honig_Ergebnisse/All_Test_exact/all_exact_peaks_data.xlsx"
# Ordner für Ausgaben:

# output_dir → Hauptordner, in dem Ergebnisse gespeichert werden.
# output_plot_dir → Ordner wo Plots gespeichertw werden
output_dir = "./All_test/"
output_plot_dir = "./All_test/_2plots"
# Pfad zur gespeicherten VAE-Modell-Datei
model_path = os.path.join("./All_test/vae_model_minimal.pt")  # Modell laden von hier
# Es werden nur diese Honigsorten aus der Excel-Datei geladen
allowed_honey_types = ["Lavendel", "Linde", "Eukalyptus"]  # oder: None für alle
# Legt fest, ob das Modell auf der CPU oder GPU läuft
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# DEVICE = torch.device("cpu")


# Daten laden
# Liest die Excel-Datei in einen Pandas DataFrame
# Filtert nur Zeilen, deren honey_type in der Liste allowed_honey_types steht
df_new = pd.read_excel(new_input_excel)
if allowed_honey_types is not None:
    df_new = df_new[df_new['honey_type'].isin(allowed_honey_types)].reset_index(drop=True)
    if df_new.empty:
        raise ValueError("Keine Daten für die angegebenen honey_types gefunden")
# Lädt jede .npy-Datei (gespeicherte Peak-Daten) in ein NumPy-Array
peak_windows_new = [np.load(path) for path in df_new['npy_file']]
peak_windows_new = np.array(peak_windows_new)

# original_shape_new merkt sich die ursprüngliche 2D-Form jedes Samples für spätere Rekonstruktion.
original_shape_new = peak_windows_new.shape[1:]
print("Neue Datenform:", peak_windows_new.shape)

# Normalisieren
# Jedes Peak-Bild wird auf den Wertebereich 0–1 skaliert
# Falls alle Werte gleich sind (max_val - min_val = 0), wird ein Nullbild erzeugt (keine Peaks vorhanden)
peak_windows_normalized_new = []
for window in peak_windows_new:
    min_val = window.min()
    max_val = window.max()
    if max_val - min_val == 0:
        normalized = np.zeros_like(window)
    else:
        normalized = (window - min_val) / (max_val - min_val)
    peak_windows_normalized_new.append(normalized)
peak_windows_normalized_new = np.array(peak_windows_normalized_new)
# Wandelt jedes 2D-Bild in einen langen Vektor um (für neuronales Netz)
peak_windows_flat_2 = peak_windows_normalized_new.reshape(peak_windows_normalized_new.shape[0], -1)
print("Flattened shape:", peak_windows_flat_2.shape)
# Konvertiert das NumPy-Array in einen PyTorch-Tensor (Float32).
X_tensor_new = torch.tensor(peak_windows_flat_2, dtype=torch.float32)

# VAE Architektur (wie beim Training)
x_dim = X_tensor_new.shape[1]
latent_dim = 16
hidden_dim = 400


# Encoder:Mehrere Linear-Layer mit LeakyReLU-Aktivierung
# Gibt Mittelwert und Log-Varianz für die Verteilung im latenten Raum zurück
class Encoder(nn.Module):
    def __init__(self, input_dim, hidden_dim, latent_dim):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.mean = nn.Linear(hidden_dim, latent_dim)
        self.logvar = nn.Linear(hidden_dim, latent_dim)
        self.relu = nn.LeakyReLU(0.2)

    def forward(self, x):
        h = self.relu(self.fc1(x))
        h = self.relu(self.fc2(h))
        return self.mean(h), self.logvar(h)


# Decoder
# Umgekehrter Aufbau: beginnt bei latent_dim und geht zurück auf die Eingabegröße.
class Decoder(nn.Module):
    def __init__(self, latent_dim, hidden_dim, output_dim):
        super().__init__()
        self.fc1 = nn.Linear(latent_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.out = nn.Linear(hidden_dim, output_dim)
        self.relu = nn.LeakyReLU(0.2)

    def forward(self, z):
        h = self.relu(self.fc1(z))
        h = self.relu(self.fc2(h))
        return torch.sigmoid(self.out(h))
        # return self.out(h)


class Encoder(nn.Module):

    def __init__(self, input_dim, hidden_dim, latent_dim):
        super(Encoder, self).__init__()

        self.FC_input = nn.Linear(input_dim, 128)
        self.FC_input2 = nn.Linear(128, 128)
        # self.FC_input3 = nn.Linear(128, 128)
        self.FC_input4 = nn.Linear(128, 64)
        # self.FC_input5 = nn.Linear(64, 64)
        # self.FC_input6 = nn.Linear(64, 64)
        self.FC_input7 = nn.Linear(64, 32)
        # self.FC_input8 = nn.Linear(32, 32)
        self.FC_input9 = nn.Linear(32, 32)
        self.FC_input10 = nn.Linear(32, 16)
        self.FC_mean = nn.Linear(16, latent_dim)
        self.FC_var = nn.Linear(16, latent_dim)

        self.LeakyReLU = nn.LeakyReLU(0.2)

        self.training = True

    def forward(self, x):
        h_ = self.LeakyReLU(self.FC_input(x))
        # h_ = self.LeakyReLU(self.FC_input2(h_))
        # h_ = self.LeakyReLU(self.FC_input3(h_))
        h_ = self.LeakyReLU(self.FC_input4(h_))
        # h_ = self.LeakyReLU(self.FC_input5(h_))
        # h_ = self.LeakyReLU(self.FC_input6(h_))
        h_ = self.LeakyReLU(self.FC_input7(h_))
        # h_ = self.LeakyReLU(self.FC_input8(h_))
        h_ = self.LeakyReLU(self.FC_input9(h_))
        h_ = self.LeakyReLU(self.FC_input10(h_))
        mean = self.FC_mean(h_)
        log_var = self.FC_var(h_)
        return mean, log_var


class Decoder(nn.Module):
    def __init__(self, latent_dim, hidden_dim, output_dim):
        super(Decoder, self).__init__()

        self.FC_hidden1 = nn.Linear(latent_dim, 16)
        self.FC_hidden10 = nn.Linear(16, 32)
        self.FC_hidden2 = nn.Linear(32, 32)
        # self.FC_hidden3 = nn.Linear(32, 32)
        self.FC_hidden4 = nn.Linear(32, 64)
        # self.FC_hidden5 = nn.Linear(64, 64)
        # self.FC_hidden6 = nn.Linear(64, 64)
        self.FC_hidden7 = nn.Linear(64, 128)
        # self.FC_hidden8 = nn.Linear(128, 128)
        self.FC_hidden9 = nn.Linear(128, 128)
        self.FC_output = nn.Linear(128, output_dim)

        self.LeakyReLU = nn.LeakyReLU(0.2)

    def forward(self, z):
        h = self.LeakyReLU(self.FC_hidden1(z))
        h = self.LeakyReLU(self.FC_hidden10(h))
        h = self.LeakyReLU(self.FC_hidden2(h))
        # h = self.LeakyReLU(self.FC_hidden3(h))
        h = self.LeakyReLU(self.FC_hidden4(h))
        # h = self.LeakyReLU(self.FC_hidden5(h))
        # h = self.LeakyReLU(self.FC_hidden6(h))
        h = self.LeakyReLU(self.FC_hidden7(h))
        # h = self.LeakyReLU(self.FC_hidden8(h))
        h = self.LeakyReLU(self.FC_hidden9(h))
        x_hat = self.FC_output(h)
        return x_hat


# VAE-Klasse
# Kombiniert Encoder und Decoder
class VAE(nn.Module):
    def __init__(self, encoder, decoder):
        super().__init__()
        self.encoder = encoder
        self.decoder = decoder

    def reparameterize(self, mu, logvar):
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std

    def forward(self, x):
        mu, logvar = self.encoder(x)
        z = self.reparameterize(mu, logvar)
        return self.decoder(z), mu, logvar


# Modell laden
# Erstellt Encoder, Decoder und kombiniert sie zum VAE
# Lädt die trainierten Gewichte aus der .pt-Datei
# eval() → Schaltet das Modell in den Inferenzmodus
encoder = Encoder(x_dim, hidden_dim, latent_dim)
decoder = Decoder(latent_dim, hidden_dim, x_dim)
model = VAE(encoder, decoder).to(DEVICE)
model.load_state_dict(torch.load(model_path, map_location=DEVICE))
model.eval()
print(f"Modell geladen von: {model_path}")

# Vorhersagen / Rekonstruktion
# Batch-Verarbeitung, um Speicher zu sparen
# recon_list_new --> rekonstruierte Daten
# mu_list_new --> Mittelwerte des latenten Vektors (Features)
batch_size = 1000
recon_list_new = []
mu_list_new = []

# Daten durch den VAE laufen lassen --> Rekonstruktionen & latente Mittelwerte speichern
with torch.no_grad():
    for i in range(0, X_tensor_new.size(0), batch_size):
        batch = X_tensor_new[i:i + batch_size].to(DEVICE)
        recon_batch, mu, _ = model(batch)
        recon_list_new.append(recon_batch.cpu())
        mu_list_new.append(mu.cpu())
# Zusammensetzen der Batch-Ergebnisse
# Zurückformen in Originalgröße.
# latent_features = kompakte Feature-Vektoren
recon_np_new = torch.cat(recon_list_new, dim=0).numpy().reshape(-1, *original_shape_new)
original_np_new = X_tensor_new.cpu().numpy().reshape(-1, *original_shape_new)
latent_features = torch.cat(mu_list_new, dim=0).numpy()

# Plot speichern
os.makedirs(output_dir, exist_ok=True)
plot_output_path_new = os.path.join(output_dir, "reconstructions_new_data_2pdf")
with PdfPages(plot_output_path_new) as pdf:
    for i in range(len(original_np_new)):
        fig, axes = plt.subplots(1, 2, figsize=(8, 4))
        axes[0].imshow(original_np_new[i], cmap="viridis")
        axes[0].set_title("Original (neu)")
        axes[0].axis("off")
        axes[1].imshow(recon_np_new[i], cmap="viridis")
        axes[1].set_title("Rekonstruiert (neu)")
        axes[1].axis("off")
        fig.suptitle(f"Neues Sample {i}")
        pdf.savefig(fig)
        plt.close(fig)

print(f"Neue Rekonstruktionen gespeichert unter: {plot_output_path_new}")
os.makedirs(output_dir, exist_ok=True)
plot_output_path_png = os.path.join(output_dir, "reconstructions_5samples_2.png")

# Anzahl der Samples, die geplottet werden
num_samples = 3
fig, axes = plt.subplots(num_samples, 2, figsize=(8, 2 * num_samples))

for i in range(num_samples):
    axes[i, 0].imshow(original_np_new[i], cmap="viridis")
    axes[i, 0].set_title(f"Original {i}")
    axes[i, 0].axis("off")

    axes[i, 1].imshow(recon_np_new[i], cmap="viridis")
    axes[i, 1].set_title(f"Rekonstruiert {i}")
    axes[i, 1].axis("off")

fig.tight_layout()
plt.savefig(plot_output_path_png, dpi=300, bbox_inches="tight")
plt.close(fig)

print(f" PNG-Datei mit 5 Rekonstruktionen gespeichert unter: {plot_output_path_png}")

latent_features = torch.cat(mu_list_new, dim=0).numpy()

# Falls latent_features mehrdimensional sind --> flach machen
if latent_features.ndim > 2:
    latent_features = latent_features.reshape(latent_features.shape[0], -1)

# # #  PCA


#     #PCA(n_components=2) --> Erstellt ein PCA-Objekt, das auf 2 Hauptkomponenten reduziert.
pca = PCA(n_components=2)
#    #fit_transform()--> fit = berechnet die Hauptkomponenten und ihre Varianzrichtungen
# transform = projiziert die Daten in den neuen Raum
# pca_result--> enthält nun für jedes Peakfenster 2 Werte--> (PC1, PC2)
pca_result = pca.fit_transform(latent_features)

# Die Varainz berechnen und speichern
explained_var1 = pca.explained_variance_ratio_[0] * 100
explained_var2 = pca.explained_variance_ratio_[1] * 100

# t-SNE
# Erstellt ein t-SNE-Objekt mit den wichtigsten Parametern:
# n_components=2 --> Ergebnis wird für den Plot in 2 Dimensionen reduziert
# random_state=42 --> Zufallsstart reproduzierbar machen
# perplexity=30 --> Steuert den "Effektivbereich" der Nachbarschaft
# n_iter=1000 --> Anzahl der Iterationen zur Optimierung der Einbettung
# fit_transform()--> Berechnet die Ähnlichkeiten der hochdimensionalen Datenpunkte (fit); Optimiert die Positionen in 2D so, dass ähnliche Punkte nah beieinander liegen (transform)

tsne = TSNE(n_components=2, perplexity=30, n_iter=1000, random_state=42)
tsne_result = tsne.fit_transform(latent_features)

# Speichern & Plotten
os.makedirs(output_plot_dir, exist_ok=True)
df_vis = pd.DataFrame(pca_result, columns=["PCA 1", "PCA 2"])
df_vis["tSNE 1"] = tsne_result[:, 0]
df_vis["tSNE 2"] = tsne_result[:, 1]
df_vis["honey_type"] = df_new["honey_type"].values
df_vis["peak_number"] = df_new.index
df_vis.to_excel(os.path.join(f"./All_test/pca_tsne_latent_space_{latent_dim}D_2.xlsx"), index=False)

# Farben
unique_honey_types = df_vis["honey_type"].unique()
color_map = {
    "Raps": "yellowgreen", "Lavendel": "mediumorchid", "Koriander": "dodgerblue",
    "Tanne": "forestgreen", "Akazie": "darkorange", "Buchweizen": "saddlebrown",
    "Sonnenblume": "goldenrod", "Linde": "limegreen", "Eukalyptus": "darkcyan",
    "Citrus": "darkorange", "Kastanie": "firebrick", "Klee": "mediumvioletred",
    "Unbekannt": "gray"
}
for honey in unique_honey_types:
    if honey not in color_map:
        color_map[honey] = np.random.rand(3, )

# #PCA Plot

fig, ax = plt.subplots(1, 2, figsize=(18, 8))
ax[0].set_title(f"PCA: Latent Space\n(Varianz PCA1: {explained_var1:.1f}%, PCA2: {explained_var2:.1f}%)")
ax[0].set_xlabel("PCA 1")
ax[0].set_ylabel("PCA 2")
for honey in unique_honey_types:
    idxs = df_new["honey_type"] == honey
    ax[0].scatter(pca_result[idxs, 0], pca_result[idxs, 1],
                  color=color_map[honey], label=honey, alpha=0.7)
ax[0].legend()
ax[0].grid(True)
plt.savefig(os.path.join(f"./All_test/pca_latentspace_2_{latent_dim}D_2.png"), dpi=300, bbox_inches='tight')
plt.close()

# t-SNE Plot
fig_tsne, ax_tsne = plt.subplots(figsize=(10, 8))
for honey in unique_honey_types:
    idxs = df_vis["honey_type"] == honey
    ax_tsne.scatter(df_vis.loc[idxs, "tSNE 1"], df_vis.loc[idxs, "tSNE 2"],
                    color=color_map[honey], alpha=0.7, label=honey)
ax_tsne.set_title("t-SNE: Latent Space")
ax_tsne.set_xlabel("t-SNE 1")
ax_tsne.set_ylabel("t-SNE 2")
ax_tsne.grid(True)
ax_tsne.legend()
plt.savefig(os.path.join(f"./a/tsne_latentspace_{latent_dim}D.png"), dpi=300, bbox_inches='tight')
plt.close()

print(" PCA und t-SNE abgeschlossen und gespeichert.")

latent_features = torch.cat(mu_list_new, dim=0).numpy()

if latent_features.ndim > 2:
    latent_features = latent_features.reshape(latent_features.shape[0], -1)
# np.unique() --> Liste der verschiedenen Honigsorten
# color_map --> fixe Farbzuordnung zu bekannten Sorten, graue Farben für unbekannte
unique_honey_types = df_new["honey_type"].unique()
color_map = {
    "Raps": "yellowgreen", "Lavendel": "mediumorchid", "Koriander": "dodgerblue",
    "Tanne": "forestgreen", "Akazie": "darkorange", "Buchweizen": "saddlebrown",
    "Sonnenblume": "goldenrod", "Linde": "limegreen", "Eukalyptus": "darkcyan",
    "Citrus": "darkorange", "Kastanie": "firebrick", "Klee": "mediumvioletred",
    "Unbekannt": "gray"
}
for honey in unique_honey_types:
    if honey not in color_map:
        color_map[honey] = np.random.rand(3, )
shown_peak_numbers = []

# PCA
# PCA(n_components=2) --> Erstellt ein PCA-Objekt, das auf 2 Hauptkomponenten reduziert.
pca = PCA(n_components=2)
# fit_transform()--> fit = berechnet die Hauptkomponenten und ihre Varianzrichtungen
# transform = projiziert die Daten in den neuen Raum
# pca_result--> enthält nun für jedes Peakfenster 2 Werte--> (PC1, PC2)
pca_result = pca.fit_transform(latent_features)

#  DataFrame für Export
latent_dim = latent_features.shape[1]
pca_df = pd.DataFrame(pca_result, columns=["PCA 1", "PCA 2"])
pca_df["honey_type"] = df_new["honey_type"].values
pca_df["peak_number"] = df_new.index

#  PCA-Plot + Heatmaps
# Erzeugt eine Figur mit 2 Spalten
# Links--> PCA-Scatterplot
# Rechts--> Die Heatmaps
# subtitle--> Gesamttitel
# Linke Seite
# Zeichnet Punkte im PCA-Raum, farblich nach Honigsorte
# alpha=0.7 für leichte Transparenz.

fig, ax = plt.subplots(1, 2, figsize=(18, 8))
fig.suptitle("PCA: Latente Merkmale mit den zugehörigen Heatmaps", fontsize=16)
ax[0].set_title("PCA: Latente Merkmale")
ax[0].set_xlabel("PCA Komponente 1")
ax[0].set_ylabel("PCA Komponente 2")
# np.unique() --> Liste der verschiedenen Honigsorten
# color_map --> fixe Farbzuordnung zu bekannten Sorten, graue Farben für unbekannte
for honey in unique_honey_types:
    idxs = df_new["honey_type"] == honey
    ax[0].scatter(pca_result[idxs, 0], pca_result[idxs, 1],
                  color=color_map[honey], label=honey, alpha=0.7)
ax[0].legend(title="Honigtyp")
ax[0].grid(True)

# Heatmap
# Rechte Seite
# Achsen werden ausgeblendet (nur Bilder + Text)
# current_y --> vertikale Position zum Platzieren
reconstructed_2d = recon_np_new  # deine 2D Rekonstruktionen
ax[1].axis("off")

ax[1].set_title("Heatmaps")
# Für jede Sorte werden die ersten 3 Peaks ausgewählt, um sie im Plot und Heatmaps zu zeigen
for honey in unique_honey_types:
    indices = pca_df[pca_df["honey_type"] == honey].index[:3]
    shown_peak_numbers.extend(indices)

current_y = 0.8

# Heatmap der Beispiel-Peaks
# Iteriert über die ausgewählten Peak-Indizes dieser Sorte
# heatmap = X[idx] --> holt das Originaldatenfenster aus dem Array X
# OffsetImage()--> Wandelt das 2D-Array heatmap in ein Bild um
# --> cmap="viridis" --> Farbskala
# zoom=5.0 --> Heatmap vergrößern
# x_pos--> Startet bei 0.4 --> linke Position der Heatmaps
# AnnotationBbox():Platziert das Bild an (x_pos, current_y) in Achsen-Koordinaten
# frameon=False --> kein Rahmen um die Bilder
# add_artist() --> fügt das Bild dem Plot hinzu


for honey in unique_honey_types:
    thumbnails = []
    for idx, row in df_new[df_new["honey_type"] == honey].head(3).iterrows():
        img = reconstructed_2d[idx]
        imgbox = OffsetImage(img, zoom=5.0, cmap="viridis")
        thumbnails.append((idx, imgbox))
    # Beschriftet die Pealfenster zu den zugörigen Heatmaps
    for idx, row in pca_df.iterrows():
        if row["peak_number"] in shown_peak_numbers:
            ax[0].text(row["PCA 1"], row["PCA 2"], str(row["peak_number"]),
                       fontsize=5, ha='center', va='center', color='black')

    # Peak-Nummern unter die Heatmaps schreiben
    # Schreibt die Peak-ID (idx) unter jede Heatmap
    #  current_y - 0.09 --> leicht nach unten verschoben, damit es unter dem Bild steht
    #  Zentriert horizontal (ha='center')
    #  Nach jeder Honigsorte wird current_y um 0.3 nach unten gesetzt
    # Erstelunng eines Kreises für die entsprechende Honigsorte
    # Erstellt einen farbigen Kreis (Radius 0.015) --> relativ zur Achse
    # (0.05, current_y) --> Position in Achsen-Koordinaten (0,0 unten links; 1,1 oben rechts
    # clip_on=False --> Kreis wird auch gezeichnet, wenn er außerhalb des Plots liegt
    # add_artist() --> fügt den Kreis als manuelles Plot-Element hinzu

    if thumbnails:
        ax[1].add_artist(plt.Circle((0.05, current_y), 0.015, color=color_map[honey], transform=ax[1].transAxes))
        ax[1].text(0.1, current_y, honey, transform=ax[1].transAxes, verticalalignment='center', fontsize=10)
        for i, (peak_num, imgbox) in enumerate(thumbnails):
            x_pos = 0.4 + i * 0.3
            ab = AnnotationBbox(imgbox, (x_pos, current_y), xycoords='axes fraction', frameon=False)
            ax[1].add_artist(ab)
            ax[1].text(x_pos, current_y - 0.09, str(peak_num), transform=ax[1].transAxes,
                       ha='center', va='top', fontsize=8)
        current_y -= 0.3

os.makedirs(output_dir, exist_ok=True)
os.makedirs(output_plot_dir, exist_ok=True)
plt.savefig(os.path.join(f"./All_test/pca_latentspace_{latent_dim}D_2.png"), dpi=300, bbox_inches='tight')
plt.close()

# t-SNE
# Erstellt ein t-SNE-Objekt mit den wichtigsten Parametern:
# n_components=2 --> Ergebnis wird in 2 Dimensionen (für Plot) reduziert
# random_state=42 --> Zufallsstart reproduzierbar machen
# perplexity=30 --> Steuert den "Effektivbereich" der Nachbarschaft
# n_iter=1000 --> Anzahl der Iterationen zur Optimierung der Einbettung
# fit_transform()--> Berechnet die Ähnlichkeiten der hochdimensionalen Datenpunkte (fit); Optimiert die Positionen in 2D so, dass ähnliche Punkte nah beieinander liegen (transform)

tsne = TSNE(n_components=2, perplexity=30, n_iter=1000, random_state=42)
tsne_result = tsne.fit_transform(latent_features)

pca_df["tSNE 1"] = tsne_result[:, 0]
pca_df["tSNE 2"] = tsne_result[:, 1]
pca_df.to_excel(os.path.join(f"./All_test/pca_tsne_latent_space_{latent_dim}D.xlsx"), index=False)

# t-SNE Plot + Heatmaps
# Erzeugt eine Figur mit 2 Spalten
# Links--> PCA-Scatterplot
# Rechts--> Die Heatmaps
# subtitle--> Gesamttitel
fig_tsne, ax_tsne = plt.subplots(1, 2, figsize=(14, 7))
fig_tsne.suptitle("t-SNE: Latente Merkmale mit den zugehörigen Heatmaps", fontsize=16)

ax_tsne[0].set_title("t-SNE: Latente Merkmale")
ax_tsne[0].set_xlabel("t-SNE Komponente 1")
ax_tsne[0].set_ylabel("t-SNE Komponente 2")
# np.unique() --> Liste der verschiedenen Honigsorten
# color_map --> fixe Farbzuordnung zu bekannten Sorten, graue Farben für unbekannte
for honey in unique_honey_types:
    idxs = df_new["honey_type"] == honey
    ax_tsne[0].scatter(tsne_result[idxs, 0], tsne_result[idxs, 1],
                       color=color_map[honey], alpha=0.7, label=honey)
ax_tsne[0].legend(title="Honigtyp")
ax_tsne[0].grid(True)

# Hier die Peak-Nummern an den Punkten anzeigen:
# Nur die ersten 3 Peaks pro Honigtyp beschriften
for honey in unique_honey_types:
    subset = pca_df[pca_df["honey_type"] == honey].head(3)
    for idx, row in subset.iterrows():
        ax_tsne[0].text(row["tSNE 1"], row["tSNE 2"], str(row["peak_number"]),
                        fontsize=6, ha='center', va='center', color='black')

# Heatmap (Thumbnails)
ax_tsne[1].axis("off")
ax_tsne[1].set_title("Heatmaps")

current_y = 0.8

# Heatmap der Beispiel-Peaks
# Iteriert über die ausgewählten Peak-Indizes dieser Sorte
# heatmap = X[idx] --> holt das Originaldatenfenster aus dem Array X
# OffsetImage()--> Wandelt das 2D-Array heatmap in ein Bild um
# --> cmap="viridis" --> Farbskala
# zoom=5.0 --> Heatmap vergrößern
# x_pos--> Startet bei 0.4 --> linke Position der Heatmaps
# AnnotationBbox():Platziert das Bild an (x_pos, current_y) in Achsen-Koordinaten
# frameon=False --> kein Rahmen um die Bilder
# add_artist() --> fügt das Bild dem Plot hinzu


for honey in unique_honey_types:
    thumbnails = []
    for idx, row in df_new[df_new["honey_type"] == honey].head(3).iterrows():
        img = reconstructed_2d[idx]
        imgbox = OffsetImage(img, zoom=5.0, cmap="viridis")
        thumbnails.append((idx, imgbox))

    # Peak-Nummern unter die Heatmaps schreiben
    # Schreibt die Peak-ID (idx) unter jede Heatmap
    #  current_y - 0.09 --> leicht nach unten verschoben, damit es unter dem Bild steht
    #  Zentriert horizontal (ha='center')
    #  Nach jeder Honigsorte wird current_y um 0.3 nach unten gesetzt
    # Erstelunng eines Kreises für die entsprechende Honigsorte
    # Erstellt einen kleinen farbigen Kreis (Radius 0.015 --> relativ zur Achse
    # (0.05, current_y) --> Position in Achsen-Koordinaten (0,0 unten links; 1,1 oben rechts
    # clip_on=False --> Kreis wird auch gezeichnet, wenn er außerhalb des Plots liegt
    # add_artist() --> fügt den Kreis als manuelles Plot-Element hinzu
    if thumbnails:
        ax_tsne[1].add_artist(
            plt.Circle((0.05, current_y), 0.015, color=color_map[honey], transform=ax_tsne[1].transAxes))
        ax_tsne[1].text(0.1, current_y, honey, transform=ax_tsne[1].transAxes, verticalalignment='center', fontsize=10)
        for i, (peak_num, imgbox) in enumerate(thumbnails):
            x_pos = 0.4 + i * 0.3
            ab = AnnotationBbox(imgbox, (x_pos, current_y), xycoords='axes fraction', frameon=False)
            ax_tsne[1].add_artist(ab)
            ax_tsne[1].text(x_pos, current_y - 0.09, str(peak_num), transform=ax_tsne[1].transAxes,
                            ha='center', va='top', fontsize=8)
        current_y -= 0.2
# speichern
# plt.savefig(os.path.join(f"./finish/tsne_latentspace_heatmap_{latent_dim}D_10.png"), dpi=300, bbox_inches='tight')
# plt.close()


# def run_pca_with_heatmaps_from_file(excel_file_path, output_dir, output_plot_dir):
#     import os
#     import numpy as np
#     import pandas as pd
#     import matplotlib.pyplot as plt
#     from matplotlib.offsetbox import OffsetImage, AnnotationBbox
#     from sklearn.decomposition import PCA

#     #Excel-Datei laden
#     #Es wird eine Excel-Datei mit Peak-Daten geladen
#     #Gefiltert werden nur die Zeilen, deren honey_type zu den zulässigen Honigsorten gehören
#     #reset_index(drop=True) sorgt dafür, dass die Indizes danach neu von 0 hochgezählt werden
#     if not os.path.exists(excel_file_path):
#         print(f"Datei nicht gefunden: {excel_file_path}")
#         return

#     df = pd.read_excel(excel_file_path)

#     zulässige_typen = ["Lavendel", "Linde", "Eukalyptus"]
#     df = df[df["honey_type"].isin(zulässige_typen)].reset_index(drop=True)

#     #NPY-Dateien lade
#     #hier werden die Peakfenster gespeichert, die später in PCA/t-SNE eingespeist werden
#     window_arrays = []
#     #speichert den zugörigen Honigtyp für jedes geladene Peakfenster
#     honey_types = []

# #Durch alle Zeilen im Dataframe iterieren
# #df enthält die aus der Excel-Datei eingelesenen Metadaten zu den Peaks.
# #npy_file ist ein Spaltenname im Excel, der den Pfad zur NPY-Datei enthält
# #Jede .npy-Datei ist ein Peakfenster-Array
# #np.load lädt die gespeicherte NumPy-Matrix aus der Datei
# #Nur gültige Fenster werden weiterverarbeitet
#     for idx, row in df.iterrows():
#         npy_path = row['npy_file']
#         try:
#             window = np.load(npy_path)
#             if window.shape[0] == window.shape[1]:
#                 window_arrays.append(window)
#                 honey_types.append(row['honey_type'])
#         except Exception as e:
#             print(f"Fehler beim Laden von {npy_path}: {e}")
# #Falls keine einzige Datei erfolgreich geladen wurde, wird die Funktion beendet
#     if not window_arrays:
#         print("Keine gültigen Fenster gefunden.")
#         return

#     # 3. PCA
#     #np.array(): Wandelt die Liste window_arrays in ein NumPy-Array um
#     #window_arrays enthält die Peakfenster
#     #x--> ein mehrdimensionales Array
#     X = np.array(window_arrays)
#     #reshape(): Formt das Array um
#     #X.shape[0] --> Anzahl der Samples (Fenster)
#     #-1--> alle weiteren Dimensionen werden in eine flache Vektorform gebracht
#     X_flat = X.reshape(X.shape[0], -1)
#     #PCA(n_components=2) --> Erstellt ein PCA-Objekt, das auf 2 Hauptkomponenten reduziert.
#     pca = PCA(n_components=2)
#     #fit_transform()--> fit = berechnet die Hauptkomponenten und ihre Varianzrichtungen
#     #transform = projiziert die Daten in den neuen Raum
#     #pca_result--> enthält nun für jedes Peakfenster 2 Werte--> (PC1, PC2)
#     pca_result = pca.fit_transform(X_flat)

#     #Die Varainz speichern
#     explained_variance = pca.explained_variance_ratio_
#     print(f"Erklärte Varianzanteile: {explained_variance}")

#     varianz_df = pd.DataFrame({
#         "PCA Komponente": [f"PCA {i+1}" for i in range(len(explained_variance))],
#         "Erklärte Varianz": explained_variance
#     })
#     varianz_df.to_excel(os.path.join(output_dir, "pca_explained_variance.xlsx"), index=False)

#     pca_df = pd.DataFrame(pca_result, columns=["PCA 1", "PCA 2"])
#     pca_df["honey_type"] = honey_types
#     pca_df["peak_number"] = np.arange(len(X))


#     # Excel speichern
#     os.makedirs(output_dir, exist_ok=True)
#     pca_df.to_excel(os.path.join(output_dir, "pca_original_peak_windows.xlsx"), index=False)

#     # Plot erstellen
#     #Erzeugt eine Figur mit 2 Spalten
#     #Links--> PCA-Scatterplot
#     #Rechts--> Die Heatmaps
#     #subtitle--> Gesamttitel
#     fig, ax = plt.subplots(1, 2, figsize=(10, 4))
#     fig.suptitle("PCA: Originaldaten mit den zugehörigen Heatmaps", fontsize=16)

# #np.unique() --> Liste der verschiedenen Honigsorten
# #color_map --> fixe Farbzuordnung zu bekannten Sorten, graue Farben für unbekannte
#     unique_honey_types = np.unique(honey_types)
#     color_map = {
#         "Raps": "yellowgreen", "Lavendel": "mediumorchid", "Koriander": "dodgerblue",
#         "Tanne": "forestgreen", "Akazie": "darkorange", "Buchweizen": "saddlebrown",
#         "Sonnenblume": "goldenrod", "Linde": "limegreen", "Eukalyptus": "darkcyan",
#         "Citrus": "darkorange", "Kastanie": "firebrick", "Klee": "mediumvioletred",
#         "Unbekannt": "gray"
#     }

#     for honey in unique_honey_types:
#         if honey not in color_map:
#             color_map[honey] = np.random.rand(3,)

#      #Für jede Sorte werden die ersten 3 Peaks ausgewählt, um sie im Plot und Heatmaps zu zeigen
#     shown_peak_numbers = []
#     for honey in unique_honey_types:
#         indices = pca_df[pca_df["honey_type"] == honey].index[:3]
#         shown_peak_numbers.extend(indices)

#     # Linke Seite
#     #Zeichnet Punkte im PCA-Raum, farblich nach Honigsorte
#     #alpha=0.7 für leichte Transparenz.
#     ax[0].set_title("PCA: Originale Peakfenster")
#     ax[0].set_xlabel(f"PCA Komponente 1")
#     ax[0].set_ylabel(f"PCA Komponente 2")

#     for honey in unique_honey_types:
#         idxs = pca_df["honey_type"] == honey
#         ax[0].scatter(pca_df.loc[idxs, "PCA 1"], pca_df.loc[idxs, "PCA 2"],
#                       label=honey, color=color_map[honey], alpha=0.7)

#     #Beschriftet die Peakfenster zu den zugörigen Heatmaps
#     for idx, row in pca_df.iterrows():
#         if row["peak_number"] in shown_peak_numbers:
#             ax[0].text(row["PCA 1"], row["PCA 2"], str(row["peak_number"]),
#                        fontsize=8, ha='center', va='center', color='black')
#     ax[0].legend(title="Honigtyp", fontsize=9)
#     ax[0].grid(True)

#     # Rechte Seite
#     #Achsen werden ausgeblendet (nur Bilder + Text)
#     #current_y --> vertikale Position zum Platzieren.
#     ax[1].set_title("Heatmaps")
#     ax[1].axis("off")
#     current_y = 0.8

# #Fügt farbige Punkte und Textlabels zu den entsprechenden Honigsorten hinzu
# #Platziert die Heatmaps (OffsetImage) neben den Sortennamen
# #Iteration über Honigsorten
# #Jede Honigsorte bekommt einen eigenen Block im rechten Plot.
# #pca_df["honey_type"] == honey --> filtert alle Zeilen mit dieser Honigsorte
# #.index[:3] --> nimmt nur die ersten 3 Peaks dieser Sorte--> Das sind die später angezeigten Heatmaps.
#     for honey in unique_honey_types:
#         indices = pca_df[pca_df["honey_type"] == honey].index[:3]
#         #Falls eine Sorte gar keine Daten hat, wird sie einfach übersprungen, damit der Plot nicht crasht.
#         if len(indices) == 0:
#             continue

# #Erstelung eines Kreises für die entsprechende Honigsorte
# #Erstellt einen kleinen farbigen Kreis (Radius 0.015 --> relativ zur Achse
# #(0.05, current_y) --> Position in Achsen-Koordinaten (0,0 unten links; 1,1 oben rechts
# #clip_on=False --> Kreis wird auch gezeichnet, wenn er außerhalb des Plots liegt
# #add_artist() --> fügt den Kreis als manuelles Plot-Element hinzu

#         circle = plt.Circle((0.05, current_y), 0.015, color=color_map[honey],
#                             transform=ax[1].transAxes, clip_on=False)
#         ax[1].add_artist(circle)
#         ax[1].text(0.1, current_y, honey, transform=ax[1].transAxes,
#                    verticalalignment='center', fontsize=10, color=color_map[honey])
# #Heatmap der Beispiel-Peaks
# #Iteriert über die ausgewählten Peak-Indizes dieser Sorte
# #heatmap = X[idx] --> holt das Originaldatenfenster aus dem Array X
# #OffsetImage()--> Wandelt das 2D-Array heatmap in ein Bild um
#               #--> cmap="viridis" --> Farbskala
#               #zoom=5.0 --> Heatmap vergrößern
#               #x_pos--> Startet bei 0.4 --> linke Position der Heatmaps
#   #AnnotationBbox():Platziert das Bild an (x_pos, current_y) in Achsen-Koordinaten
#   #frameon=False --> kein Rahmen um die Bilder
#   #add_artist() --> fügt das Bild dem Plot hinzu


#         for i, idx in enumerate(indices):
#             heatmap = X[idx]
#             imagebox = OffsetImage(heatmap, cmap="viridis", zoom=5.0)
#             x_pos = 0.4 + i * 0.3
#             ab = AnnotationBbox(imagebox, (x_pos, current_y), xycoords="axes fraction", frameon=False)
#             ax[1].add_artist(ab)


# #Peak-Nummern unter die Heatmaps schreiben
# #Schreibt die Peak-ID (idx) unter jede Heatmap
# #  current_y - 0.09 --> leicht nach unten verschoben, damit es unter dem Bild steht
# #  Zentriert horizontal (ha='center')
# #  Nach jeder Honigsorte wird current_y um 0.3 nach unten gesetzt
# #
#             ax[1].text(x_pos, current_y - 0.09, str(idx), transform=ax[1].transAxes,
#                        ha='center', va='top', fontsize=8, color='black')

#         current_y -= 0.3

#     # Speichern
#     os.makedirs(output_plot_dir, exist_ok=True)
#     plot_path = os.path.join(output_plot_dir, "pca_original_peak_windows_mit_heatmaps.png")
#     plt.savefig(plot_path, dpi=300, bbox_inches='tight')
#     plt.close()
#     print(f"PCA-Plot gespeichert unter: {plot_path}")

#     # === t-SNE ===
# 	    # === t-SNE ===
#     from sklearn.manifold import TSNE

#     #Erstellt ein t-SNE-Objekt mit den wichtigsten Parametern:
#         #n_components=2 --> Ergebnis wird in 2 Dimensionen (für Plot) reduziert
#         #random_state=42 --> Zufallsstart reproduzierbar machen
#         #perplexity=30 --> Steuert den "Effektivbereich" der Nachbarschaft
#         #n_iter=1000 --> Anzahl der Iterationen zur Optimierung der Einbettung
#         #fit_transform()--> Berechnet die Ähnlichkeiten der hochdimensionalen Datenpunkte (fit); Optimiert die Positionen in 2D so, dass ähnliche Punkte nah beieinander liegen (transform)

#     tsne = TSNE(n_components=2, random_state=42, perplexity=30, n_iter=1000)
#     tsne_result = tsne.fit_transform(X_flat)

#     # Ergebnisse ergänzen und speichern
#     #Fügt zwei neue Spalten zu pca_df hinzu--> Die beiden t-SNE-Koordinaten für jedes Sample
#     pca_df["tSNE 1"] = tsne_result[:, 0]
#     pca_df["tSNE 2"] = tsne_result[:, 1]
#     pca_df.to_excel(os.path.join(output_dir, "tsne_original_peak_windows.xlsx"), index=False)

#     # t-SNE-Plot
#     fig_tsne, ax_tsne = plt.subplots(figsize=(10, 8))
#     ax_tsne.set_title("t-SNE - Original Peak-Fenster", fontsize=14)
#     ax_tsne.set_xlabel("t-SNE Komponente 1")
#     ax_tsne.set_ylabel("t-SNE Komponente 2")

#     for honey in unique_honey_types:
#         idxs = pca_df["honey_type"] == honey
#         ax_tsne.scatter(pca_df.loc[idxs, "tSNE 1"], pca_df.loc[idxs, "tSNE 2"],
#                         label=honey, color=color_map[honey], alpha=0.7)

#     for idx, row in pca_df.iterrows():
#         if row["peak_number"] in shown_peak_numbers:
#             ax_tsne.text(row["tSNE 1"], row["tSNE 2"], str(row["peak_number"]),
#                          fontsize=8, ha='center', va='center', color='black')

#     ax_tsne.legend(title="Honigtyp", fontsize=9)
#     ax_tsne.grid(True)

#     # Speichern
#     tsne_plot_path = os.path.join(output_plot_dir, "tsne_original_peak_windows.png")
#     plt.savefig(tsne_plot_path, dpi=300, bbox_inches='tight')
#     plt.close()
#     print(f"t-SNE-Plot gespeichert unter: {tsne_plot_path}")


# run_pca_with_heatmaps_from_file(
#     excel_file_path="./Honig_Ergebnisse/exact_2/all_exact_peaks_data.xlsx",
#     output_dir="./finish/orginal_PCA",
#     output_plot_dir="./finish/orginal_PCA"
# )