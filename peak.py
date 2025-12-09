from scipy.ndimage import uniform_filter
import ims
import os
import numpy as np
import pandas as pd
from pathlib import Path
from skimage.morphology import max_tree, h_maxima, area_opening
from skimage.measure import label, regionprops
from multiprocessing import Pool
import plot

from PIL import Image, ImageDraw, ImageFont


def get_all_peaks(preprocessed_data: list[ims.Spectrum],
                  neighbor_distance: int,
                  spectra_paths: list[Path],
                  create_heatmaps: bool = True,
                  create_npy: bool = True) -> pd.DataFrame:
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
    :param create_heatmaps: Specifies if heatmaps are created [default = True].
    :param create_npy: Specifies if npy files are created. These files are important for the consensus peak detection of
    the next step [default = True].

    :return: Pandas dataframe with detected peak information.
    """

    # Check how many cpu cores are available.
    cpu_cores = os.cpu_count()
    # List with arguments in form of tuples for the parallel processing function.
    tasks = []

    print("=======================================================")
    print("II. PEAK DETECTION")
    # Walk through each preprocessed spectrum and collect needed arguments for the peak finding computation.
    for idx, spectrum in enumerate(preprocessed_data):
        task_args = (spectrum, neighbor_distance, spectra_paths[idx], create_heatmaps, create_npy)
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
                   neighbor_distance: int,
                   output_dir: Path,
                   create_heatmaps: bool,
                   create_npy: bool) -> list[dict]:
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
    :param neighbor_distance: Defines the radius around a detected peak within which neighbor peaks are created.
    [e.g. neighbor_distance = 3. In an area of (2*3 +1)² = 7² = 49 indices, neighbor peaks are created.
    By doing this, every detected peak is not just represented by a center peak window, but by slightly shifted peak
    windows surrounding this center peak. In this example, a total of 48 shifted peak windows + the center peak window
    would be created = total of 49 peak windows.]
    :param output_dir: Saving path for the plotting image.
    :param create_heatmaps: Specifies if heatmaps are created.
    :param create_npy: Specifies if npy files are created.

    :return: List of dictionaries which contain peak_window information (as specified above in step 7).
    """

    print(f"\t- Peak Detection Started [{spectrum.name}]")
    # Keep the non normalized values for later use.
    values_non_normalized = spectrum.values.copy()
    # Normalize the spectrum [0-1].
    spectrum.normalization()
    # List of dictionaries which contain selected peak information. This list is returned at the end of this function.
    spectrum_peak_data = []

    try:
        label_name = output_dir.name

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

        """ COMPONENT TREE FUNCTION """
        # Create a max tree.
        parent, tree_traverser = max_tree(spectrum.values, connectivity=2)
        # Define the min. area threshold size in pixel.
        area_threshold = 5
        # Collapses nodes which are smaller than the area_threshold with their parents.
        filtered_local_maxima = area_opening(spectrum.values,
                                             area_threshold=area_threshold,
                                             connectivity=2,
                                             parent=parent,
                                             tree_traverser=tree_traverser)

        # What's the min. height differenz (normalized) for two nodes to be discriminated as 2 different peaks?
        height_differenz = 0.02
        # Remove nodes which are to small compared to their node neighbors (node height differenz < height_differenz)
        peak_mask = h_maxima(filtered_local_maxima, h=height_differenz)
        # label the found nodes.
        label_mask = label(peak_mask, connectivity=2)
        # Create regions from the original spectrum values of the labeled nodes.
        regions = regionprops(label_mask, intensity_image=spectrum.values)
        # create a new empty array with the size of found regions (Each region = 1 peak).
        all_peak_coords = np.zeros((len(regions), 2), dtype=int)

        # Walk through all found regions, calculate the weighted center coordinates and save these as a peak.
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

            # Walk through all peak coordinates.
            for ret_idx, drift_idx in peak_coords:
                start_ret_idx = ret_idx - neighbor_distance
                end_ret_idx = ret_idx + 3 * neighbor_distance + 1
                start_drift_idx = drift_idx - neighbor_distance
                end_drift_idx = drift_idx + 3 * neighbor_distance + 1
                peak_window_intensities = padded_values[start_ret_idx:end_ret_idx, start_drift_idx:end_drift_idx]
                peak_window_ret_times = spectrum.ret_time[start_ret_idx:end_ret_idx]
                peak_window_drift_times = spectrum.drift_time[start_drift_idx:end_drift_idx]
                ret_matrix, drift_matrix = np.meshgrid(peak_window_ret_times, peak_window_drift_times, indexing='ij')
                peak_window = np.stack((peak_window_intensities, ret_matrix, drift_matrix), axis=-1)

                # Plot the peak heatmaps.
                if create_heatmaps:
                    plot.plot_peak_heatmap(spectrum=spectrum,
                                           heatmap_window=peak_window_intensities,
                                           ret_idx=ret_idx,
                                           drift_idx=drift_idx,
                                           window_size=neighbor_distance,
                                           plot_dir=output_dir)


                # Check if the peak window has the correct shape. This should always be the case!
                if peak_window_intensities.shape != (4*neighbor_distance + 1, 4*neighbor_distance + 1):
                    raise ValueError(f"\tPeak Window has the wrong shape: {peak_window_intensities.shape}. "
                                     f"Expected Shape: ({4*neighbor_distance + 1}, {4*neighbor_distance + 1})")


                # Define the numpy filename and create the needed directories.
                if create_npy:
                    npy_dir = output_dir / "npy" / spectrum.name
                    if not npy_dir.exists():
                        npy_dir.mkdir(parents=True, exist_ok=True)

                    npy_filename = npy_dir / f"PW_{spectrum.name}_RT{ret_idx}_DT{drift_idx}_{4*neighbor_distance + 1}x{4*neighbor_distance + 1}.npy"
                    np.save(npy_filename, peak_window)
                else:
                    npy_filename = "-"

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

            # Create an Excel file that contains the found peaks and their information (See peak_data dictionary above).
            table_dir = output_dir / "table"
            if not table_dir.exists():
                table_dir.mkdir(parents=True, exist_ok=True)

            table_filename = table_dir / f"{spectrum.name}_peaks.xlsx"
            peaks_dataframe = pd.DataFrame(spectrum_peak_data)
            peaks_dataframe.to_excel(table_filename, index=False)

            # Notify that the peak detection on this spectrum is finished and print the number of peaks.
            print(f"\t- {len(peak_coords)} Peaks saved [{spectrum.name}]")

        else:
            # Notify that the peak detection on this spectrum is finished and print the number of peaks.
            print(f"\t- No Peaks saved [{spectrum.name}]")

    except Exception as err:
        print(f"\tError on {spectrum.name} - Skipped: {err=}, {type(err)=}")
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
