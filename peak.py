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


def get_all_peaks(preprocessed_spectra: list[ims.Spectrum],
                  peak_radius: int,
                  spectra_paths: list[Path],
                  create_heatmaps: bool = True,
                  create_npy: bool = True) -> pd.DataFrame:
    """
    This function forwards to the peak detection algorithm for preprocessed gc-ims spectra.
    It manages the multiprocessing task on multiple cpu cores (if available) and forwards spectra specific
    information to the "peak_detection" function for parallel computing.

    :param preprocessed_spectra: A list of preprocessed gc-ims spectra.
    :param peak_radius: Defines the radius around a detected peak within which the intensities are saved as a npy file.
    [e.g. peak_radius = 3. In an area of (2*3 +1)² = 7² = 49 indices, peak intensities are saved.
    Doing this saves not just the detected peak itself, but also it's surrounding.]
    :param spectra_paths: Paths to the spectra output files [plots | hdf5 files].
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
    for idx, spectrum in enumerate(preprocessed_spectra):
        task_args = (spectrum, peak_radius, spectra_paths[idx], create_heatmaps, create_npy)
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
                   peak_radius: int,
                   output_dir: Path,
                   create_heatmaps: bool,
                   create_npy: bool) -> list[dict]:
    """
    This function handels the peak detection for preprocessed gc-ims spectra in a series of steps.
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
    print(f"\t- Peak Detection Started [{spectrum.name}]")
    # Keep the non normalized values for later use.
    values_non_normalized = spectrum.values.copy()
    # Normalize the spectrum [0-1].
    spectrum.normalization()
    # List of dictionaries which contain selected peak information. This list is returned at the end of this function.
    spectrum_peak_data = []

    try:
        label_name = output_dir.name

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

            # 4. Plot the detected peaks. ------------------------------------------------------------------------------
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
                pad_width=peak_radius,
                mode='constant',
                constant_values=0
            )

            # Walk through all peak coordinates.
            for ret_idx, drift_idx in peak_coords:
                start_ret_idx = ret_idx - peak_radius
                end_ret_idx = ret_idx + 3 * peak_radius + 1
                start_drift_idx = drift_idx - peak_radius
                end_drift_idx = drift_idx + 3 * peak_radius + 1
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
                                           window_size=peak_radius,
                                           plot_dir=output_dir)


                # Check if the peak window has the correct shape. This should always be the case!
                if peak_window_intensities.shape != (4*peak_radius + 1, 4*peak_radius + 1):
                    raise ValueError(f"\tPeak Window has the wrong shape: {peak_window_intensities.shape}. "
                                     f"Expected Shape: ({4*peak_radius + 1}, {4*peak_radius + 1})")

                # 5. Save peak information as .npy file ----------------------------------------------------------------
                # Define the numpy filename and create the needed directories.
                if create_npy:
                    npy_dir = output_dir / "npy" / spectrum.name
                    if not npy_dir.exists():
                        npy_dir.mkdir(parents=True, exist_ok=True)

                    npy_filename = npy_dir / f"PW_{spectrum.name}_RT{ret_idx}_DT{drift_idx}_{4*peak_radius + 1}x{4*peak_radius + 1}.npy"
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
