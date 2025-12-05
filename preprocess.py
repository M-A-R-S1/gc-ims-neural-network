import ims
from pathlib import Path
from scipy.ndimage import uniform_filter
import numpy as np
import plot
from multiprocessing import Pool
import os
import pandas as pd
from skimage.morphology import max_tree, h_maxima, area_opening

from PIL import Image, ImageDraw, ImageFont


# Overhauled function. Original function = preprocess_and_visualize_spectra
def start(input_dir: Path,
          output_dir: Path,
          create_plots: str = "all",
          drift_cut: tuple[float, float] = (1.02, 2.5),
          retention_cut: tuple[int, int] = (80, 900),
          percentile: float = 5.0,
          uniform_filter_size: tuple[int, int] = (11, 11),
          load_existing: bool = True) -> tuple[list[ims.Spectrum], list[Path]]:
    """
    This function takes care of the preprocess steps for .mea files.
    All .mea files inside a given input directory (input_dir), as well as their subdirectories are used as datasets.
    Each dataset corresponds to one directory and is preprocessed by the following:
    - 1. Interpolation to a common Reactant Ion Peaks (RIP)

    This functions forwards the interpolated spectra files to the "preprocess_spectra" function for parallel computation.
    Each cpu core acts on one spectrum.
    This function then returns all preprocessed spectra as a list and their output paths.

    :param input_dir: The directory where the .mea files are located in.
    :param output_dir: Saving path of the plotting image.
    :param create_plots: Specifies which images to create. [none = no images | single = one image for each .mea file |
    overview = one overview image for each folder which contains .mea files | all = combination of 'overview' + 'single']
    :param drift_cut: Tuple of cutting coordinates for the drifttime (x-axis) in milliseconds (Start , End).
    :param retention_cut: Tuple of cutting coordinates for the retentiontime (y-axis) in seconds (Start, End).
    :param percentile: Value for the background noise reduction. [e.g. percentile=5.0 removes the lowest 5% of the data from a spectrum]
    :param uniform_filter_size: Tuple for the uniform filter size.
    :param load_existing: If set to True the algorithm trys to load an already preprocessed hdf5 spectrum file.
    This will then skip the preprocessing step for this spectrum.

    :return: Tuple with a list of preprocessed spectra and a list of their paths.
    """

    print("=======================================================")
    print(f"I: Preproccessing started")
    print("-------------------------------------------------------")

    # List of processed spectra.
    preprocessed_data = []
    # List of paths to the spectra directories.
    spectra_paths = []
    # List of loaded spectra [Spectra which were preprocessed earlier].
    loaded_data = []

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
        return preprocessed_data, spectra_paths

    # Walk through all found subdirectories.
    for current_input_dir in sorted(list(dir_set)):
        try:
            # Create the dataset for all .mea files in the current subdirectory.
            dataset = ims.Dataset.read_mea(current_input_dir)
        except Exception as err:
            print(f"ERROR: could not read files at {current_input_dir}: {err=} ---- Skipping.")
            print("-------------------------------------------------------")
            continue

        print(f"Opening dataset: {current_input_dir.parent.name}/{dataset.name} ({len(dataset.data)} Spectra)")
        print("-------------------------------------------------------")

        # Set the output directory.
        current_output_dir = output_dir / current_input_dir.relative_to(input_dir)

        # Try to load .hdf5 files for each spectrum. An .hdf5 file indicates that a spectrum was already processed.
        if load_existing:
            for idx, spectrum in enumerate(dataset.data):
                spectrum_path = current_output_dir / "hdf5" / f"{spectrum.name}.hdf5"
                if spectrum_path.exists():
                    loaded_spectrum = ims.Spectrum.read_hdf5(spectrum_path)
                    loaded_data.append(loaded_spectrum)
                    loaded_spectrum.rip_ms = 1
                    # Save the output directory of the spektrum
                    spectra_paths.append(current_output_dir)
                    print(f"- Spectrum {idx + 1}/{len(dataset.data)} - Save file found [loaded]")

        # Skip processing this folder if all dictionary spectra could be loaded from .hdf5 files.
        if len(loaded_data) == len(dataset.data):
            continue

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

            # Check if the spectrum has already a save file, if so skip the preprocessing step for this spectrum.
            if load_existing:
                spectrum_path = current_output_dir / "hdf5" / f"{spectrum.name}.hdf5"
                if spectrum_path.exists():
                    continue

            # Save the spektrum path.
            spectra_paths.append(current_output_dir)

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
            dataset_data = p.starmap(preprocess_spectra, tasks)

        # Plot overview of all spectra inside the current subdirectory.
        if create_plots in ["all", "overview"]:
            plot.overview_gcims_plot(dataset=dataset_data,
                                     plot_dir=current_output_dir,
                                     condition="processed")

        preprocessed_data.extend(dataset_data)

    # Add the loaded spectra to the newly preprocessed spectra.
    preprocessed_data.extend(loaded_data)

    return preprocessed_data, spectra_paths


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
                               plot_dir=output_dir,
                               condition="raw")

    spectrum.rip_ms = 1
    # Baseline correction - removing the noisy background by subtracting the mean of an empty area.
    spectrum.sub_first_rows(50)
    spectrum.cut_dt(start=drift_cut[0], stop=drift_cut[1])
    spectrum.cut_rt(start=retention_cut[0], stop=retention_cut[1])

    #spectrum.values = uniform_filter(input=spectrum.values, size=uniform_filter_size)
    #from scipy.ndimage import gaussian_filter
    #spectrum.values = gaussian_filter(spectrum.values, sigma=1.0)

    # Smoothing the spectrum with the Savitzky–Golay filter.
    spectrum.savgol(window_length=10, polyorder=4)

    # Remove negative values after applying the smooth filter.
    spectrum.values[spectrum.values < 0] = 0.0

    # Plot the processed spectrum.
    if create_plots in ["all", "single"]:
        plot.single_gcims_plot(spectrum=spectrum,
                               plot_dir=output_dir,
                               condition="processed")

    # Before saving, check if the file already exists. The file must be deleted first! Overriding does not work.
    spectrum_path = output_dir / "hdf5"
    if not spectrum_path.exists():
        spectrum_path.mkdir(parents=True, exist_ok=True)

    spectrum_file = spectrum_path / f"{spectrum.name}.hdf5"
    if spectrum_file.exists():
        spectrum_file.unlink()

    # Save the processed spectrum.
    spectrum.to_hdf5(spectrum_path)

    # Return the preprocessed spectrum.
    return spectrum


def get_all_peaks(preprocessed_data: list[ims.Spectrum],
                  neighbor_distance: int,
                  spectra_paths: list[Path],
                  create_heatmaps: bool = True) -> pd.DataFrame:
    """
    This function forwards to the peak detection algorithm for preprocessed gc-ims spectra.
    It manages the multiprocessing task on multiple cpu cores (if available) and forwards spectra specific
    information to the "peak_detection" function for parallel computing.

    :param preprocessed_data: A list of preprocessed gc-ims spectra.
    :param neighbor_distance: Defines the radius around a detected peak within which neighbor peaks are created.
    [e.g. neighbor_distance = 3. In an area of (2*3 +1)² = 7² = 49 indices, neighbor peaks are created.
    By doing this, every detected peak is not just represented by a center peak window, but by slightly shifted peak
    windows surrounding this center peak. In this example, a total of 48 shifted peak windows + the center peak window
    would be created = total of 49 peak windows.]
    :param spectra_paths: Saving paths of the spectra.
    :param create_heatmaps: Specifies if heatmaps are created. [0 = creates no heatmaps | 1 = creats heatmaps (default)]

    :return: Pandas dataframe with detected peak information.
    """

    # Check how many cpu cores are available.
    cpu_cores = os.cpu_count()
    # List with arguments in form of tuples for the parallel processing function.
    tasks = []

    print("=======================================================")
    print("II. Peak detection started ...")
    print("-------------------------------------------------------")
    # Walk through each preprocessed spectrum and collect needed arguments for the peak finding computation.
    for idx, spectrum in enumerate(preprocessed_data):
        task_args = (spectrum, idx, neighbor_distance, spectra_paths[idx], create_heatmaps)
        # Append the tuple of arguments to the tasks list.
        tasks.append(task_args)

    # Start parallel processing. One cpu core handels one spectrum.
    with Pool(cpu_cores) as p:
        directory_list = p.starmap(peak_detection, tasks)

    # TODO -> Create an overview plot of all spectra with their detected peaks [without neighbor peaks]
    # See "combine_peak_plots_to_single_figure" for inspiration

    # Extract all peak information (item) from within the list of directories.
    peak_data = [item for directory in directory_list for item in directory]
    # Convert the peak_data list to a pandas dataframe.
    peak_dataframe = pd.DataFrame(peak_data)

    return peak_dataframe


def peak_detection(spectrum: ims.Spectrum,
                   idx: int,
                   neighbor_distance: int,
                   output_dir: Path,
                   create_heatmaps: bool) -> list[dict]:
    """
    This function handels the peak detection for preprocessed gc-ims spectra in a series of steps.
    1. Normalization of the spectrum to values between 0 and 1.
    2. Create a local tree of the spectrum and create hierarchy levels.
    3. Select peaks from the local tree according to specific conditions [min. intensity | min. hierarchy level | etc.]
    4. Create a plot with all selected peaks.
    5. Add neighbor peaks around each selected peak of step 3 within the neighbor_distance radius.
    6. Create a "peak window" for each peak of the size (neighbor_distance+1 * neighbor_distance+1) and save
       the intensities inside each window as a npy file.
    7. Return a list of dictionaries. One dictionary for each "peak window" with the following information.
        - 'label' -> The label/type of the used spectrum.
        - 'spectrum' -> The Name of the spectrum.
        - 'ret_time' -> Retention time [s] of the "peak window" center point.
        - 'drift_time' -> Drift time [ms] of the "peak window" center point.
        - 'intensity' -> Intensity [not normalized] of the "peak_window" center point.
        - 'npy_file' -> Saved npy file of this "peak window" which was created in step 6.

    :param spectrum: A single preprocessed gc-ims spectrum.
    :param idx: The index of the spectrum inside the current dataset.
    :param neighbor_distance: Defines the radius around a detected peak within which neighbor peaks are created.
    [e.g. neighbor_distance = 3. In an area of (2*3 +1)² = 7² = 49 indices, neighbor peaks are created.
    By doing this, every detected peak is not just represented by a center peak window, but by slightly shifted peak
    windows surrounding this center peak. In this example, a total of 48 shifted peak windows + the center peak window
    would be created = total of 49 peak windows.]
    :param output_dir: Saving path for the plotting image.
    :param create_heatmaps: Specifies if heatmaps are created. [0 = creates no heatmaps | 1 = creats heatmaps]

    :return: List of dictionaries which contain peak_window information (as specified above in step 7).
    """

    print(f"- Peak Detection Started on: Spectrum {idx + 1}")
    # Keep the non normalized values for later use.
    values_non_normalized = spectrum.values.copy()
    # Normalize the spectrum [0-1].
    spectrum.normalization()
    # List of dictionaries which contain selected peak information. This list is returned at the end of this function.
    spectrum_peak_data = []

    try:
        label = output_dir.name

        """ DETECT_PEAKS FUNCTION
        # 1. Check for peaks and put the peak coordinates in a list with tuples (Retention , Drift).
        # Define the min. peak threshold intensity [non normalized value].
        peak_threshold = 100
        # How many intensity values are there in total?
        intensity_count_max = spectrum.values.shape[0] * spectrum.values.shape[1]
        # How many intensities values are over the peak_threshold?
        threshold_intensity_count = len(np.where(values_non_normalized >= peak_threshold)[0])
        # Calculate the % of intensity values which are below the peak_threshold.
        threshold_percentile = 100 - (threshold_intensity_count / intensity_count_max) * 100
        # Peak intensity detection threshold.
        intensity_threshold = np.percentile(spectrum.values, [threshold_percentile])
        # Find peaks with the integrated find_peaks function.
        spectrum.detect_peaks(threshold_rel=intensity_threshold, peak_size=3)
        #spectrum.find_peaks(limit=peak_threshold, denoise=None)
        # List with peak coordinates as tuples [(Retention-index, Drift-index)].
        peak_coords = np.column_stack((spectrum.peaklist['y'].values, spectrum.peaklist['x'].values))
        #peak_coords = np.column_stack((spectrum.peak_table['y'].values, spectrum.peak_table['x'].values))
        """

        """ PEAK LOCAL MAX FUNCTION
        # Define the min. peak threshold intensity [non normalized value].
        peak_threshold = 75
        # How many intensity values are there in total?
        intensity_count_max = spectrum.values.shape[0] * spectrum.values.shape[1]
        # How many intensities values are over the peak_threshold?
        threshold_intensity_count = len(np.where(values_non_normalized >= peak_threshold)[0])
        # Calculate the % of intensity values which are below the peak_threshold.
        threshold_percentile = 100 - (threshold_intensity_count / intensity_count_max) * 100
        # Peak intensity detection threshold.
        intensity_threshold = np.percentile(spectrum.values, [threshold_percentile])

        peak_coords = peak_local_max(spectrum.values,
                                     threshold_abs=intensity_threshold,
                                     min_distance=5,
                                     exclude_border=False)
        """

        # Create a max tree.
        parent, tree_traverser = max_tree(spectrum.values, connectivity=2)
        # Define the min. area threshold size in pixel.
        area_threshold = 5
        # Define the min. peak threshold intensity [non normalized value].
        peak_threshold = 75
        # How many intensity values are there in total?
        intensity_count_max = spectrum.values.shape[0] * spectrum.values.shape[1]
        # How many intensities values are over the peak_threshold?
        threshold_intensity_count = len(np.where(values_non_normalized >= peak_threshold)[0])
        # Calculate the % of intensity values which are below the peak_threshold.
        threshold_percentile = 100 - (threshold_intensity_count / intensity_count_max) * 100
        # Peak intensity detection threshold.
        intensity_threshold = np.percentile(spectrum.values, [threshold_percentile])

        # Remove small areas (peaks < area_threshold) to remove 'pseudo' local maxima within noise.
        filtered_local_maxima = area_opening(spectrum.values,
                                             area_threshold=area_threshold,
                                             connectivity=2,
                                             parent=parent,
                                             tree_traverser=tree_traverser)

        # Remove peaks which are to small (peak height < intensity_threshold)
        peak_mask = h_maxima(filtered_local_maxima, h=intensity_threshold)
        # Get the retention and drift indices of all detected peaks (Indices which are non-zero).
        ret_idx, drift_idx = np.nonzero(peak_mask)
        # List with peak coordinates as tuples [(Retention-index, Drift-index)].
        peak_coords = np.column_stack((ret_idx, drift_idx))

        """
        # Get all retention indices from the selected peak coordinates.
        ret_idx = selected_peak_coords[:, 0]
        # Get all drift indices from the selected peak coordinates.
        drift_idx = selected_peak_coords[:, 1]
        # List of normalized intensities which correlate to the coordinates of the "selected_peak_coords" list.
        peak_coords = spectrum.values[ret_idx, drift_idx]

        # Are there peaks?
        # If so, select only peaks which belong to the strongest 10% intensities.
        if len(peak_coords) > 0:
            # Threshold value for the 10% strongest intensities.
            intensity_threshold = np.percentile(peak_coords, 90.0)
            # Create a mask with True/False values for the threshold condition.
            intensity_mask = peak_coords >= intensity_threshold
            # Use the mask on the selected peak coordinates.
            # Only Coordinates where the mask is set to "True" are considered.
            peak_coords = selected_peak_coords[intensity_mask]
        else:
            # No peaks. Create an empty numpy array.
            peak_coords = np.array([])
        """

        if len(peak_coords) > 0:
            # 2. Remove peaks which are located near the spectrum boarders.
            # list with all peak retention indices.
            peak_ret_idx_list = peak_coords[:, 0]
            # list with all peak drift indices.
            peak_drift_idx_list = peak_coords[:, 1]
            # Integer with the maximum retention and drift index.
            ret_idx_max, drift_idx_max = spectrum.values.shape

            # Create single mask conditions.
            mask_ret_min = peak_ret_idx_list >= neighbor_distance
            mask_ret_max = peak_ret_idx_list < (ret_idx_max - neighbor_distance)
            mask_drift_min = peak_drift_idx_list >= neighbor_distance
            mask_drift_max = peak_drift_idx_list < (drift_idx_max - neighbor_distance)
            # Combine all 4 masks to one mask condition. This mask will remove all peaks which are too close to the boarder.
            # This will create a list with tuples of the same length as the found peak list (peak_coords).
            # If all single mask conditions are met, true will be saved in this list. Otherwise, it will be set to False.
            final_validity_mask = (mask_ret_min &
                                   mask_ret_max &
                                   mask_drift_min &
                                   mask_drift_max)

            # Use the mask on the peak_coords list.
            # Only Coordinates where the mask is set to "True" are kept. The rest will be removed.
            peak_coords = peak_coords[final_validity_mask]

            # 3. Reload the non normalized values and crate a peak plot.
            # Reload the non normalized values.
            spectrum.values = values_non_normalized
            # Plot the current spectrum with the strongest peaks marked with a red X.
            plot.single_gcims_plot(spectrum=spectrum,
                                   plot_dir=output_dir,
                                   condition="peaks",
                                   size=(12, 8),
                                   peak_cords=peak_coords)

            # 4. Extend peaks. Each peak will be saved ....
            # Copy the spectrum.values and add a padding of 0 around them.
            # Why? If a peak is detected near the spectrum boarder, this could lead to errors in the shape and or saved
            # intensities of the peak windows. The padding guarantees the correct shape and failsafe the intensities of
            # indices outside the spectrum boarder to 0.
            padded_values = np.pad(
                spectrum.values,
                pad_width=neighbor_distance,
                mode='constant',
                constant_values=0
            )

            print(f" - Creating npy-files and heatmaps: Spectrum {idx + 1} [{spectrum.name}]")
            # Walk through all peak coordinates.
            for ret_idx, drift_idx in peak_coords:
                # Create the heatmap window.
                start_ret_idx = ret_idx - neighbor_distance
                end_ret_idx = ret_idx + 3 * neighbor_distance + 1
                start_drift_idx = drift_idx - neighbor_distance
                end_drift_idx = drift_idx + 3 * neighbor_distance + 1
                peak_window = padded_values[start_ret_idx:end_ret_idx, start_drift_idx:end_drift_idx]


                # Plot the peak heatmaps.
                if create_heatmaps:
                    plot.plot_peak_heatmap(spectrum=spectrum,
                                           heatmap_window=peak_window,
                                           ret_idx=ret_idx,
                                           drift_idx=drift_idx,
                                           window_size=neighbor_distance,
                                           plot_dir=output_dir)


                # Check if the peak window has the correct shape. This should always be the case!
                if peak_window.shape != (4*neighbor_distance + 1, 4*neighbor_distance + 1):
                    raise ValueError(f"Peak Window has the wrong shape: {peak_window.shape}. "
                                     f"Expected Shape: ({4*neighbor_distance + 1}, {4*neighbor_distance + 1})")

                # Define the numpy filename and create the needed directories.
                npy_dir = output_dir / "npy" / spectrum.name
                if not npy_dir.exists():
                    npy_dir.mkdir(parents=True, exist_ok=True)

                npy_filename = npy_dir / f"PW_{spectrum.name}_RT{ret_idx}_DT{drift_idx}_{4*neighbor_distance + 1}x{4*neighbor_distance + 1}.npy"

                # Save numpy file.
                np.save(npy_filename, peak_window)

                # Dictionary with information about peaks.
                peak_data = {
                    'label': label,
                    'spectrum': spectrum.name,
                    'ret_time': spectrum.ret_time[ret_idx],
                    'drift_time': spectrum.drift_time[drift_idx],
                    'intensity': spectrum.values[ret_idx, drift_idx],
                    'npy_file': npy_filename,
                }
                spectrum_peak_data.append(peak_data)

            table_dir = output_dir / "table"
            if not table_dir.exists():
                table_dir.mkdir(parents=True, exist_ok=True)

            table_filename = table_dir / f"{spectrum.name}_peaks.xlsx"

            # Save the peak data as a .xlsx file
            peaks_dataframe = pd.DataFrame(spectrum_peak_data)
            peaks_dataframe.to_excel(table_filename, index=False)

            # Notify that the peak detection on this spectrum is finished and print the number of peaks.
            print(f"- {len(peak_coords)} Peaks saved - Spectrum {idx + 1} [{spectrum.name}]")

        else:
            # Notify that the peak detection on this spectrum is finished and print the number of peaks.
            print(f"- No Peaks saved - Spectrum {idx + 1} [{spectrum.name}]")


    except Exception as err:
        print(f"Error - Spectrum {idx + 1} [{spectrum.name}] Skipped: {err=}, {type(err)=}")
        raise

    return spectrum_peak_data

##################################################################################################################################################################################################################

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
