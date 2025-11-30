import ims
from pathlib import Path
from scipy.ndimage import uniform_filter
import numpy as np
import plot
from multiprocessing import Pool
import os
import pandas as pd
from skimage.morphology import max_tree_local_maxima

from PIL import Image, ImageDraw, ImageFont


# Overhauled function. Original function = preprocess_and_visualize_spectra
def start(input_dir: Path,
          plot_dir: Path,
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
    :param plot_dir: Saving path of the plotting image.
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
        except Exception as err:
            print("=======================================================")
            print(f"ERROR: could not read files at {current_input_dir}: {err=} ---- Skipping.")
            continue

        print("=======================================================")
        print(f"Opening dataset: {dataset.name} ({len(dataset.data)} Spectra)")
        print("-------------------------------------------------------")

        # Set the plotting directory
        current_plot_dir = plot_dir / current_input_dir.relative_to(input_dir)
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
                         current_plot_dir,
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
                                     plot_dir=current_plot_dir,
                                     condition="processed")

    return preprocessed_data


def preprocess_spectra(spectrum: ims.Spectrum,
                       plot_dir: Path,
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
        :param plot_dir: Saving path of the plotting image.
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
                               plot_dir=plot_dir,
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
                               plot_dir=plot_dir,
                               condition="processed")

    # Return the preprocessed spectrum.
    return spectrum


def get_all_peaks(preprocessed_data: list[ims.Spectrum],
                  neighbor_distance: int,
                  plot_dir: Path,
                  npy_dir: Path) -> pd.DataFrame:
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
    :param plot_dir: Saving path for the plotting image.
    :param npy_dir: Saving path for the npy files.

    :return: Pandas dataframe with detected peak information.
    """

    # Check how many cpu cores are available.
    cpu_cores = os.cpu_count()
    # List with arguments in form of tuples for the parallel processing function.
    tasks = []

    # Walk through each preprocessed spectrum and collect needed arguments for the peak finding computation.
    for idx, spectrum in enumerate(preprocessed_data):
        task_args = (spectrum, idx, neighbor_distance, plot_dir, npy_dir)
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
                   plot_dir: Path,
                   npy_dir: Path) -> list[dict]:
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
            - 'honey_type' -> The honey type of the used spectrum.
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
        :param plot_dir: Saving path for the plotting image.
        :param npy_dir: Saving path for the npy files.

        :return: List of dictionaries which contain peak_window information (as specified above in step 7).
        """

    print(f"Peak Detection Started on: Spectrum {idx + 1}")
    # Keep the non normalized values for later use.
    values_non_normalized = spectrum.values.copy()
    # Normalization in just one line of code ...
    spectrum.normalization()
    # List of dictionaries which contain selected peak information.
    spectrum_peak_data = []

    try:
        honey_type = "Unknown"

        # Create a max tree.
        peak_tree = max_tree_local_maxima(spectrum.values, connectivity=2)
        # Define the upper tree hierarchy threshold.
        hierarchy_threshold = int(peak_tree.max() * 0.95)
        # Define the min intensity threshold.
        min_intensity_threshold = 0.035

        # List of tuples with peak coordinates (Retention-index, Drift-index) which satisfy the selection conditions.
        selected_peak_coords = np.column_stack(
            np.where(
                (peak_tree >= 0.5) &
                (peak_tree <= hierarchy_threshold) &
                (spectrum.values > min_intensity_threshold)
            )
        )

        # Get all retention indices from the selected peak coordinates.
        ret_idx = selected_peak_coords[:, 0]
        # Get all drift indices from the selected peak coordinates.
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
        ret_max_idx, drift_max_idx = values_non_normalized.shape

        # Create mask conditions.
        mask_ret_min = ret_idx >= neighbor_distance
        mask_ret_max = ret_idx < (ret_max_idx - neighbor_distance)
        mask_drift_min = drift_idx >= neighbor_distance
        mask_drift_max = drift_idx < (drift_max_idx - neighbor_distance)
        # Combine all 4 mask conditions to one mask condition.
        final_validity_mask = (mask_ret_min &
                               mask_ret_max &
                               mask_drift_min &
                               mask_drift_max)

        # Use the mask on the strongest peak coordinates.
        # Only Coordinates where the mask is set to "True" are considered.
        strongest_peak_coords = strongest_peak_coords[final_validity_mask]

        # Print the number of found peaks.
        print(f"{len(strongest_peak_coords)} Peaks found in: Spectrum {idx + 1}")

        # Reload the non normalized values.
        spectrum.values = values_non_normalized

        # Plot the current spectrum with the strongest peaks marked with a red X.
        plot.single_gcims_plot(spectrum=spectrum,
                               plot_dir=plot_dir,
                               condition="peaks",
                               size=(12, 8),
                               peak_cords=strongest_peak_coords)

        # Contains the strongest peak coordinates and all of their neighbor coords within a radius of the window size.
        neighbor_peak_coords = []

        # Create padding_values and copy from the spectrum.values and add a padding of 0 around them.
        # Why? If a peak was detected near the spectrum edge, this could lead to errors in the shape and or saved
        # intensities of the peak windows. The padding guarantees the correct shape and failsafe the intensities of
        # indices outside the spectrum edges to 0.
        padded_values = np.pad(
            spectrum.values,
            pad_width=neighbor_distance,
            mode='constant',
            constant_values=0
        )

        # Walk through all the strongest peak coordinates.
        for ret_idx, drift_idx in strongest_peak_coords:

            # Create the heatmap window.
            start_ret_idx = ret_idx - neighbor_distance
            end_ret_idx = ret_idx + 3 * neighbor_distance + 1
            start_drift_idx = drift_idx - neighbor_distance
            end_drift_idx = drift_idx + 3 * neighbor_distance + 1
            heatmap_window = padded_values[start_ret_idx:end_ret_idx, start_drift_idx:end_drift_idx]

            # Plot the peak heatmaps.
            plot.plot_peak_heatmap(spectrum=spectrum,
                                   heatmap_window=heatmap_window,
                                   ret_idx=ret_idx,
                                   drift_idx=drift_idx,
                                   window_size=neighbor_distance,
                                   plot_dir=plot_dir,
                                   condition="peaks")

            # Now walk through the peak neighborhood within a radius of the window size.
            for dx in range(-neighbor_distance, neighbor_distance+1):
                for dy in range(-neighbor_distance, neighbor_distance+1):
                    new_ret = ret_idx + dx
                    new_drift = drift_idx + dy
                    # Add every neighbor coordinate to the list.
                    neighbor_peak_coords.append((new_ret, new_drift))

        # Remove duplicate coordinate pairs from the list by converting the list temporarily to a set.
        neighbor_peak_coords = list(set(neighbor_peak_coords))

        for coord in neighbor_peak_coords:
            ret_idx, drift_idx = coord

            # Create a peak window for each pair of retention and drift indices.
            start_ret_idx = ret_idx
            end_ret_idx = ret_idx + 2*neighbor_distance + 1
            start_drift_idx = drift_idx
            end_drift_idx = drift_idx + 2*neighbor_distance + 1
            peak_window = padded_values[start_ret_idx:end_ret_idx, start_drift_idx:end_drift_idx]

            # Check if the peak window has the corret shape. This should always be the case!
            if peak_window.shape != (2 * neighbor_distance + 1, 2 * neighbor_distance + 1):
                raise ValueError(f"Peak Window has the wrong shape: {peak_window.shape}. "
                                 f"Expected Shape: ({2*neighbor_distance + 1}, {2*neighbor_distance + 1})")

            # Define the numpy filename and create the needed directories.
            numpy_dir = npy_dir / spectrum.name
            if not numpy_dir.exists():
                numpy_dir.mkdir(parents=True, exist_ok=True)

            numpy_filename = numpy_dir / f"PW_{spectrum.name}_RT{ret_idx}_DT{drift_idx}_{neighbor_distance*2+1}x{neighbor_distance*2+1}.npy"

            # Save numpy file.
            np.save(numpy_filename, peak_window)

            # Dictionary with selected information about peaks.
            peak_data = {
                'honey_type': honey_type,
                'spectrum': spectrum.name,
                'ret_time': spectrum.ret_time[ret_idx],
                'drift_time': spectrum.drift_time[drift_idx],
                'intensity': spectrum.values[ret_idx, drift_idx],
                'npy_file': numpy_filename,
            }

            spectrum_peak_data.append(peak_data)

        # TODO -> Save a csv/excel file for each spectrum separately.

        """
        spectrum_df = pd.DataFrame(spectrum_peak_data)
        excel_filename = os.path.join(output_dir,
                                      f"{spectrum.name}_peak_data_highest_hierarchy_Mean-Average-Filter_baseline_mit_nachbarn.xlsx")
        with pd.ExcelWriter(excel_filename) as writer:
            spectrum_df.to_excel(writer, index=False, sheet_name='Peak Data')
        print(f"Peak-Daten für {spectrum.name} gespeichert in {excel_filename}")
        # Falls etwas im Loop schiefgeht --> Fehlermeldung mit Spektrumsnummer und Name
        """

        print(f"- {len(neighbor_peak_coords)} Peaks extracted - Spectrum {idx + 1} [{spectrum.name}]")

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
