import ims
from pathlib import Path
from scipy.ndimage import uniform_filter
import numpy as np
import plot
from multiprocessing import Pool
import os


import pandas as pd
import multiprocessing
from skimage.morphology import max_tree_local_maxima
from PIL import Image, ImageDraw, ImageFont
import uuid
from matplotlib import pyplot as plt
import seaborn as sns


# Overhauled function. Original function = preprocess_and_visualize_spectra
def start(input_dir: Path,
          output_dir: Path,
          create_plots: str = "all",
          drift_cut: tuple[float, float] = (1.02, 2.5),
          retention_cut: tuple[int, int] = (80, 900),
          percentile: float = 5.0,
          uniform_filter_size: tuple[int, int] = (11, 11)) -> list[ims.Spectrum]:
    """
    This function takes care of the preprocess steps for .mea files.
    All .mea files inside a given input directory (input_dir), as well as their subdirectories are used as datasets.
    Each dataset corresponds to one directory and is preprocessed by the following:
    - 1. Interpolation to a common Reactant Ion Peaks (RIP)

    This functions forwards the interpolated spectra files to the "preprocess_spectra" function for parallel computation.
    Each cpu core acts on one spectrum.
    This function then returns all preprocessed spectra as a list.

    :param input_dir: The directory where the .mea files are located in.
    :param output_dir: Saving path of the plotting image.
    :param create_plots: Specifies which images to create. [none = no images | single = one image for each .mea file |
    overview = one overview image for each folder which contains .mea files | all = combination of 'overview' + 'single']
    :param drift_cut: Tuple of cutting coordinates for the drifttime (x-axis) in milliseconds (Start , End).
    :param retention_cut: Tuple of cutting coordinates for the retentiontime (y-axis) in seconds (Start, End).
    :param percentile: Value for the background noise reduction. [e.g. percentile=5.0 removes the lowest 5% of the data from a spectrum]
    :param uniform_filter_size: Tuple for the uniform filter size.

    :return: list of preprocessed spectra.
    """

    # List of processed spectra.
    preprocessed_data = []

    # list of plotting strategies.
    plotting_strategy = ["none", "all", "single", "overview"]
    # check if the user plotting strategy exists. If not default to "all".
    if not create_plots.lower() in plotting_strategy:
        create_plots = "all"
    else:
        create_plots = create_plots.lower()

    # Create a set of all subdirectories of the given input_dir which have .mea files in them.
    dir_set = set(p.parent for p in input_dir.rglob('*.mea'))

    # If there are no .mea files at all report this to the user.
    if not dir_set:
        print(f"No .mea files found in {input_dir} and sub directories.")
        return preprocessed_data

    # Walk through all found subdirectories.
    for current_input_dir in sorted(list(dir_set)):
        try:
            # Create the dataset for all .mea files in the current subdirectory.
            dataset = ims.Dataset.read_mea(current_input_dir)
        except Exception as e:
            print("=======================================================")
            print(f"ERROR: could not read files at {current_input_dir}: {e} ---- Skipping.")
            continue

        print("=======================================================")
        print(f"Opening dataset: {dataset.name} ({len(dataset.data)} Spectra)")
        print("-------------------------------------------------------")

        # Set the output directory
        current_output_dir = output_dir / current_input_dir.relative_to(input_dir)
        # Interpolates all spectra to a common RIP (Reactant Ion Peaks)
        dataset.interp_riprel()

        # Check how many cpu cores are available.
        cpu_cores = os.cpu_count()
        tasks = []

        # Collect needed arguments for each spectrum.
        for idx, spectrum in enumerate(dataset.data):
            if spectrum.values.size == 0:
                print(f"- Spectrum {idx + 1}/{len(dataset.data)}")
                print(f"- Empty spectrum --> Skipping")
                continue

            task_args = (spectrum,
                         current_output_dir,
                         idx,
                         len(dataset.data),
                         create_plots,
                         drift_cut,
                         retention_cut,
                         percentile,
                         uniform_filter_size)

            tasks.append(task_args)

        # Start parallel processing. One cpu core handels one spectrum.
        with Pool(cpu_cores) as p:
            preprocessed_data = p.starmap(preprocess_spectra, tasks)

        # Plot overview of all spectra inside the current subdirectory.
        if create_plots in ["all", "overview"]:
            plot.overview_gcims_plot(dataset=preprocessed_data,
                                     output_dir=current_output_dir,
                                     condition="processed")

    return preprocessed_data


def preprocess_spectra(spectrum: ims.Spectrum,
                       output_dir: Path,
                       idx: int,
                       dataset_length: int,
                       create_plots: str = "all",
                       drift_cut: tuple[float, float] = (1.02, 2.5),
                       retention_cut: tuple[int, int] = (80, 900),
                       percentile: float = 5.0,
                       uniform_filter_size: tuple[int, int] = (11, 11)) -> ims.Spectrum:
    """
        This function takes care of the parallel preprocessing of gc-ims spectra. Each cpu core acts on one spectrum.
        All .mea files inside a given input directory (input_dir), as well as their subdirectories are used as datasets.
        Each spectrum is preprocessed by the following:
        - 1. Baseline correction for drift- and retention time.
        - 2. Background noise reduction (1) for each axis, computed with a given percentile.
        - 3. Background noise reduction (2) smooth the spectrum by applying a uniform filter.

        This function then returns the preprocessed spectrum.

        The gc-ims spectrum can be plotted and saved as .png files if the function parameter is set accordingly:
        - "single" -> Creates a plot image for each individual .mea file.
        - "overview" -> Creates a plot image for up to 16 .mea files inside the same directory.
        - "all" -> Creates both single and overview plot images.
        - "none" -> Creates no plot images.

        :param spectrum: The spectrum which is about to be preprocessed.
        :param output_dir: Saving path of the plotting image.
        :param idx: The index of this spectrum in the current dataset.
        :param dataset_length: The length of the current dataset (Number of spectra in the dataset).
        :param create_plots: Specifies which images to create. [none = no images | single = one image for each .mea file |
        overview = one overview image for each folder which contains .mea files | all = combination of 'overview' + 'single']
        :param drift_cut: Tuple of cutting coordinates for the drifttime (x-axis) in milliseconds (Start , End).
        :param retention_cut: Tuple of cutting coordinates for the retentiontime (y-axis) in seconds (Start, End).
        :param percentile: Value for the background noise reduction. [e.g. percentile=5.0 removes the lowest 5% of the data from a spectrum]
        :param uniform_filter_size: Tuple for the uniform filter size.

        :return: preprocessed spectra.
        """

    print(f"- Spectrum {idx + 1}/{dataset_length}")

    # Plot the raw spectrum.
    if create_plots in ["all", "single"]:
        plot.single_gcims_plot(spectrum=spectrum,
                               output_dir=output_dir,
                               condition="raw")

    # Baseline correction for drift- and retention time.
    spectrum.cut_dt(start=drift_cut[0], stop=drift_cut[1])
    spectrum.cut_rt(start=retention_cut[0], stop=retention_cut[1])
    # Background noise reduction for each axis, computed with a given percentile.
    # Adjust negative values to 0.
    # Smooth the adjusted spectrum values and reduce noise.
    spectrum.values -= np.percentile(a=spectrum.values, q=percentile, axis=0, keepdims=True)
    spectrum.values -= np.percentile(a=spectrum.values, q=percentile, axis=1, keepdims=True)
    spectrum.values[spectrum.values < 0] = 0

    # spectrum.values = uniform_filter(input=spectrum.values, size=uniform_filter_size)
    # TODO -> Testing Gaussian filter
    from scipy.ndimage import gaussian_filter
    spectrum.values = gaussian_filter(spectrum.values, sigma=2.0)

    # Plot the processed spectrum.
    if create_plots in ["all", "single"]:
        plot.single_gcims_plot(spectrum=spectrum,
                               output_dir=output_dir,
                               condition="processed")

    # Return the preprocessed spectrum.
    return spectrum


def get_all_peaks(filtered_data, window_size, output_dir, condition) -> pd.DataFrame:

    all_peak_data_list = []

    # Check how many cpu cores are available.
    cpu_cores = os.cpu_count()
    tasks = []

    # Collect needed arguments for each peak finding computation.
    for idx, spectrum in enumerate(filtered_data):

        task_args = (spectrum,
                     idx,
                     window_size,
                     output_dir,
                     condition)

        tasks.append(task_args)

    # Start parallel processing. One cpu core handels one spectrum.
    with Pool(cpu_cores) as p:
        all_peak_data_list = p.starmap(peak_detection, tasks)

    all_peak_df = pd.DataFrame(all_peak_data_list)

    return all_peak_df


def peak_detection(spectrum, idx, window_size, output_dir, condition):
    # copy: Sicherung der vorverarbeiteten Daten (values_backup), damit die Peak-Findung nicht die echten Werte verändert.
    values_backup = spectrum.values.copy()

    # Normalization in just one line of code ...
    spectrum.normalization()

    spectrum_peak_data = []

    try:
        honey_type = "Unknown"

        # Create a max tree.
        peak_tree = max_tree_local_maxima(spectrum.values, connectivity=2)
        # Define the upper tree hierarchy threshold.
        hierarchy_threshold = int(peak_tree.max() * 0.95)
        # Define the min intensity thresghold.
        min_intensity_threshold = 0.035

        # List of tuples with peak coordinates (Retention-index, Drift-index) which satisfy the selection conditions.
        selected_peak_coords = np.column_stack(
            np.where(
                (peak_tree >= 0.5) &
                (peak_tree <= hierarchy_threshold) &
                (spectrum.values > min_intensity_threshold)
            )
        )

        # Get all retention indicies from the selected peak coordinates.
        ret_idx = selected_peak_coords[:, 0]
        # Get all drift indicies from the selected peak coordinates.
        drift_idx = selected_peak_coords[:, 1]
        # List of normalized intensities which correlate to the coordinates of the "selected_peak_coords" list.
        selected_peak_intensities = spectrum.values[ret_idx, drift_idx]

        # Are there peaks?
        # If so, select only peaks, which belong to the upper 4.5% intensities.
        if len(selected_peak_intensities) > 0:
            intensity_threshold = np.percentile(selected_peak_intensities, 95.5)
            # Create a mask with True/False values for the threshold condition.
            intensity_mask = selected_peak_intensities >= intensity_threshold
            # Use the mask on the selected peak coordinates.
            # Only Coordinates where the mask is set to "True" are considered.
            strongest_peak_coords = selected_peak_coords[intensity_mask]
        else:
            # No peaks. Create an empty numpy array.
            strongest_peak_coords = np.array([])

        # Split the retention and drift indices.
        ret_idx = strongest_peak_coords[:, 0]
        drift_idx = strongest_peak_coords[:, 1]
        # Get the max retention and drift indices.
        ret_max_idx, drift_max_idx = values_backup.shape

        # Create mask conditions.
        mask_ret_min = ret_idx >= window_size
        mask_ret_max = ret_idx < (ret_max_idx - window_size)
        mask_drift_min = drift_idx >= window_size
        mask_drift_max = drift_idx < (drift_max_idx - window_size)
        # Combine all 4 mask conditions to one mask condition.
        final_validity_mask = (mask_ret_min &
                               mask_ret_max &
                               mask_drift_min &
                               mask_drift_max)

        # Use the mask on the strongest peak coordinates.
        # Only Coordinates where the mask is set to "True" are considered.
        strongest_peak_coords = strongest_peak_coords[final_validity_mask]

        # Reload the value backups ... But why?
        spectrum.values = values_backup

        # Contains the strongest peak coordinates and all of their neighbor coords within a radius of the window size.
        neighbor_peak_coords = []

        # Walk through all the strongest peak coordinates.
        for ret_idx, drift_idx in strongest_peak_coords:
            # Now walk through the peak neighborhood within a radius of the window size.
            for dx in range(-window_size, window_size+1):
                for dy in range(-window_size, window_size+1):
                    new_ret = ret_idx + dx
                    new_drift = drift_idx + dy
                    # Add every neighbor coordinate to the list.
                    neighbor_peak_coords.append((new_ret, new_drift))

        # Remove duplicate coordinate pairs from the list by converting the list temporarily to a set.
        neighbor_peak_coords = list(set(neighbor_peak_coords))


        # TODO -> Hier geht es weiter
        neuer_name = spectrum.name

        # Visualisierung
        # spectrum.plot() zeichnet das komplette 2D-Spektrum
        #
        plt.figure(figsize=(12, 8))
        spectrum.plot()

        # highest_hierarchy_peaks: enthält die Matrix-Indices (ret_index, drift_index) der Peak
        # spectrum.drift_time[drift_index]--> Umrechnung von Spaltenindex zu realer Driftzeit
        # spectrum.ret_time[ret_index]--> Umrechnung von Zeilenindex zu realer Retentionszeit.
        # r+', markersize=3--> rotes Kreuz '+' für die einzelnen Peaks
        # peak_ids.append()--> speichert die Peak-Koordinaten in einer Liste
        peak_ids = []
        for coord in strongest_peak_coords:
            ret_index, drift_index = coord
            plt.plot(spectrum.drift_time[drift_index], spectrum.ret_time[ret_index], 'r+', markersize=3)
            peak_ids.append((spectrum.ret_time[ret_index], spectrum.drift_time[drift_index]))

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
        # Jede coord ist ein Tupel(ret_index, drift_index)--> Indizes im 2D-Datenarray (values_backup)
        # values_backup: Roh-Intensitätsmatrix des Spektrums
        # peak_intensity: Intensität an genau dieser Koordinate
        # ret_time und drift_time: Physikalische Werte statt Array-Indizes
        # spectrum.ret_time[ret_index] --> Retentionszeit in Sekunden
        # spectrum.drift_time[drift_index] --> Driftzeit in Millisekunden
        # ret_index, drift_index = coord
        # peak_intensity = values_backup[ret_index, drift_index]
        # ret_time = spectrum.ret_time[ret_index]
        # drift_time = spectrum.drift_time[drift_index]

        for coord in neighbor_peak_coords:
            ret_index, drift_index = coord
            peak_intensity = values_backup[ret_index, drift_index]
            ret_time = spectrum.ret_time[ret_index]
            drift_time = spectrum.drift_time[drift_index]
            # Erzeugt 8-stellige eindeutige Kennung (aus einer UUID), damit Dateinamen nicht kollidieren.
            unique_id = uuid.uuid4().hex[:8]
            # extract_window--> externe Funktion, welches ein 11x11 Peakfenster aus dem GC-IMS ausschneidet
            # gibt eine Peakfenster mit einer Intensitätsmatrix wieder.
            peak_window, intensity = extract_window(spectrum,
                                                    {"ret_time": ret_time, "drift_time": drift_time},
                                                    window_size,
                                                    output_dir,
                                                    condition,
                                                    unique_id)

            # Gültigkeitsprüfung des Fensters
            # Ist das Fenster leer (size == 0) oder hat es nicht die erwartete Form--> überspringen, da der Peak am Rand liegen könnte oder fehlerhaft ist
            if peak_window.size == 0 or peak_window.shape != (2 * window_size + 1, 2 * window_size + 1):
                print(f"Ungültiges Fenster für Peak bei RT={ret_time}, DT={drift_time}. Überspringe.")
                continue

            # Speichert den Fensterausschnitt als NumPy-Datei
            # Dateiname enthält:spectrum.name (Probenname);Retentions- & Driftzeit (6 Nachkommastellen), unique_id; Fenstergröße 11x11
            window_filename = os.path.join(
                output_dir, f"{spectrum.name}_peak_window_RT_{ret_time:.6f}_DT_{drift_time:.6f}_{unique_id}_11x11.npy"
            )

            # np.save(window_filename, peak_window)

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
        if spectrum.name not in all_peaks_data:
            all_peaks_data[spectrum.name] = []

        all_peaks_data[spectrum.name].extend(peak_ids)

        # Aus spectrum_peak_data wird ein Pandas-DataFrame
        # Export als Excel-Datei (.xlsx), Sheetname = "Peak Data".
        # Enthält alle Metadaten zum Spektrum.

        spectrum_df = pd.DataFrame(spectrum_peak_data)
        excel_filename = os.path.join(output_dir,
                                      f"{spectrum.name}_peak_data_highest_hierarchy_Mean-Average-Filter_baseline_mit_nachbarn.xlsx")
        with pd.ExcelWriter(excel_filename) as writer:
            spectrum_df.to_excel(writer, index=False, sheet_name='Peak Data')
        print(f"Peak-Daten für {spectrum.name} gespeichert in {excel_filename}")

        # Falls etwas im Loop schiefgeht --> Fehlermeldung mit Spektrumsnummer und Name

    except Exception as e:
        print(f"Fehler bei der Verarbeitung von Spektrum {spectrum_index + 1} ({spectrum.name}): {str(e)}")
    # Gibt spectrum_peak_data zurück --> Liste aller Peak-Infos dieses Spektrums.
    print(f"Spektrum {spectrum_index + 1} abgeschlossen: {spectrum.name}")
    return spectrum_peak_data



























##################################################################################################################################################################################################################

# verarbeitet mehrere Spektren parallel
# filtered_data --> Liste von „Samples“ oder Spektren, die verarbeitet werden sollen
# window_size --> Größe des Fensters um Peaks (für Peak-Extraktion)
# plot_dir --> Ordner für Heatmaps oder Peak-Plots
# Zustand
# min_margin --> Minimaler Abstand zum Rand
def parallel_process_spectra(filtered_data, window_size, plot_dir, Zustand, min_margin):
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
        # all_peak_data --> gemeinsam genutztes Dictionary für Peak-Infos; Zustand, min_margin
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
        # combined_plot_filename = os.path.join(plot_dir, "combined_peak_plots_vorverarbeitet_max_tree_local_maxima.png")
        # combine_peak_plots_to_single_figure(plot_dir, combined_plot_filename, Zustand)

        return all_peak_df




# Parameter:
# sample: ein einzelnes Spektrum-Objekt
# spectrum_index: Nummer des Spektrums
# window_size: halbe Fenstergröße für Peak-Ausschnit--> window_size=5=Fenster 11×11
# output_dir: Speicherort für Ergebnisse
# processed_spectra: Dictionary, um bereits verarbeitete Spektren zu markieren
# all_peaks_data: globale Peak-Daten für alle Spektren
# min_margin: Mindestabstand vom Rand, damit ein Peak-Fenster nicht aus dem Bild fällt
def process_spectrum_parallel(sample, spectrum_index, window_size, output_dir, processed_spectra, all_peaks_data,
                              Zustand, min_margin=5):
    # copy: Sicherung der vorverarbeiteten Daten (original_values), damit die Peak-Findung nicht die echten Werte verändert.
    original_values = sample.values.copy()

    # Why? There is an intern normalization function insde the gc-ims-module!!
    # It's the same output! I tested it.
    # Min-Max-Normalisierung auf Wertebereich [0,1] für die Peak-Findung
    min_val = original_values.min()
    max_val = original_values.max()

    if max_val - min_val == 0:
        normalized_values = np.zeros_like(original_values)
    else:
        normalized_values = (original_values - min_val) / (max_val - min_val)
    # Setzen von sample.values auf die normalisierte Matrix für die Peak-Findung.
    sample.values = normalized_values

    # Normalization in just one line of code ...
    #sample.normalization()

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
        local_maxima = max_tree_local_maxima(sample.values, connectivity=2)
        # local_maxima.max(): gibt die höchste Hierarchie-Stufe im Bild
        # Multiplikation mit 0.95 setzt einen Schwellenwert bei 95 % der maximalen Hierarchiestufe
        # int()--> Abrunden auf Ganzzahlen--> Hierarchie-Stufen sind ganzzahlig
        relative_hierarchy_threshold = int(local_maxima.max() * 0.95)
        # Entfernt alle Pixel mit zu niedriger Hierarchie-Stufe

        min_intensity_threshold = 0.035

        high_hierarchy_peaks = np.column_stack(
            np.where(
                (local_maxima >= 0.5) &
                (local_maxima <= relative_hierarchy_threshold) &
                (sample.values > min_intensity_threshold)
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
            peak_window, intensity = extract_window(sample,
                                                    {"ret_time": ret_time, "drift_time": drift_time},
                                                    window_size,
                                                    output_dir,
                                                    Zustand,
                                                    unique_id)

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

            # np.save(window_filename, peak_window)

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





# Funktion für die Extraktion der Peakfenster aus dem GC-IMS-Spektrum
# sample: ein einzelnes Spektrum-Objekt
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


    """
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
    """

    # Rückgabe
    # peak_window --> 2D-Array des ausgeschnittenen Fensters
    # intensity --> Original-Intensität am Peakzentrum
    return peak_window, intensity
