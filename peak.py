import ims
import plot
import config
import os
import numpy as np
import pandas as pd
from pathlib import Path
from skimage.morphology import max_tree, h_maxima, area_opening
from skimage.measure import label, regionprops
from sklearn.preprocessing import MinMaxScaler
from multiprocessing import Pool
import networkx as nx
from collections import defaultdict
from scipy.spatial import KDTree



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

    # Start parallel processing. One cpu core handles one spectrum.
    with Pool(cpu_cores) as p:
        directory_list = p.starmap(peak_detection, tasks)

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
                # peak_window_ret_times = spectrum.ret_time[start_ret_idx:end_ret_idx]
                # peak_window_drift_times = spectrum.drift_time[start_drift_idx:end_drift_idx]
                # ret_matrix, drift_matrix = np.meshgrid(peak_window_ret_times, peak_window_drift_times, indexing='ij')
                # peak_window = np.stack((peak_window_intensities, ret_matrix, drift_matrix), axis=-1)
                peak_window = peak_window_intensities

                # Plot the peak heatmaps.
                if create_heatmaps:
                    plot.plot_peak_heatmap(spectrum=spectrum,
                                           heatmap_window=peak_window_intensities,
                                           ret_idx=ret_idx,
                                           drift_idx=drift_idx,
                                           window_size=peak_radius,
                                           plot_dir=output_dir / "heatmap" / "peak")


                # Check if the peak window has the correct shape. This should always be the case!
                if peak_window_intensities.shape != (4*peak_radius + 1, 4*peak_radius + 1):
                    raise ValueError(f"\tPeak Window has the wrong shape: {peak_window_intensities.shape}. "
                                     f"Expected Shape: ({4*peak_radius + 1}, {4*peak_radius + 1})")

                # 5. Save peak information as .npy file ----------------------------------------------------------------
                # Define the numpy filename and create the needed directories.
                if create_npy:
                    npy_dir = output_dir / "npy" / "peak" / spectrum.name
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


def extract_consensus_peaks(excel_file: Path,
                            output_dir: Path,
                            create_plots: str,
                            filter_types: list[str] = None,
                            max_node_distance: float = 0.006) -> None:
    """
    Not yet described ... TODO

    :param excel_file: Excel file path which contains all the detected peaks.
    :param output_dir: The output directory for plots and other files.
    :param create_plots: Specifies which plots to create. [none = no plots | single = plots for each connected component
    | overview = one overview plot for the connected components and one for each label |  all = combination of 'overview' + 'single']
    :param filter_types: Can be used to filter for specific labels.
    :param max_node_distance: The max. euclidean distance between nodes for the connected components calculation.

    :return: None.
    """

    print("=======================================================")
    print("III. CONSENSUS PEAK EXTRACTION")

    # Check if the Excel file exists.
    if not check_peak_excel_file(excel_file=excel_file, filter_types=filter_types):
        print("Consensus peak extraction aborted")
        return

    # list of plotting strategies.
    plotting_strategy = ["none", "all", "single", "overview"]
    # check if the user plotting strategy exists. If not default to "all".
    if not create_plots.lower() in plotting_strategy:
        create_plots = "all"
    else:
        create_plots = create_plots.lower()

    # Load the Excel file.
    peak_dataframe = pd.read_excel(excel_file)

    # Normalize the retention and drifttime.
    scaler = MinMaxScaler()
    times_normalized = scaler.fit_transform(peak_dataframe[['ret_time', 'drift_time']].values)

    # Create a list with all unique labels from inside the dataframe.
    unique_labels = peak_dataframe['label'].unique().tolist()

    # Calculate connected components.
    graph, peak_dataframe = calculate_connected_components(peak_dataframe=peak_dataframe,
                                                           output_dir=output_dir,
                                                           max_node_distance=max_node_distance,
                                                           times_normalized=times_normalized)

    # Overview plot with all components.
    if create_plots in ['all' , 'overview']:
        plot.plot_connected_component_overview(graph=graph,
                                               output_dir=output_dir)

    # Create a plot for each component.
    if create_plots in ['all', 'single']:
        components = list(nx.connected_components(graph))
        component_plot_dir = output_dir / "components"
        # Check and create the component directory.
        if not component_plot_dir.exists():
            component_plot_dir.mkdir(parents=True, exist_ok=True)

        for component_idx, component in enumerate(components):
            plot.plot_single_connected_component(graph=graph,
                                                 component=component,
                                                 component_idx=component_idx,
                                                 output_dir=component_plot_dir)

    # Calculate consensus peaks.
    consensus_peaks = calculate_consensus_peaks(graph=graph,
                                                unique_labels=unique_labels,
                                                output_dir=output_dir)

    # Plot the calculated consensus peaks.
    if create_plots in ['all', 'overview']:
        plot.plot_consensus_peaks(consensus_peaks=consensus_peaks,
                                  unique_labels=unique_labels,
                                  output_dir=output_dir)

    print("Consensus peaks successfully extracted")


def check_peak_excel_file(excel_file: Path,
                          filter_types: list[str]) -> bool:
    """
    Not yet described ... TODO

    :param excel_file: Excel file path which contains all the detected peaks.
    :param filter_types: Can be used to filter for specific labels.

    :return: True if the Excel file can be used | False if not.
    """

    # Check if the Excel file exists.
    if not excel_file.exists():
        print(f"File not found: {excel_file}")
        return False

    # Load the Excel file.
    peak_dataframe = pd.read_excel(excel_file)
    # Filter entries by type.
    if filter_types:
        peak_dataframe = peak_dataframe[peak_dataframe['label'].isin(filter_types)].reset_index(drop=True)

    # Check if the Excel file has all required columns.
    required_cols = {'ret_time', 'drift_time', 'label'}
    if not required_cols.issubset(peak_dataframe.columns):
        raise ValueError(f"Missing columns. Required: {required_cols}")

    return True


def calculate_connected_components(peak_dataframe: pd.DataFrame,
                                   output_dir: Path,
                                   max_node_distance: float,
                                   times_normalized: np.ndarray,
                                   batch_size: int = 20000) -> tuple[nx.Graph, pd.DataFrame]:
    """
    Not yet described ... TODO

    :param peak_dataframe: Dataframe with all peak information.
    :param output_dir: The output directory for plots and other files.
    :param max_node_distance: The max. distance between nodes for the connected components calculation.
    :param times_normalized: Min/Max normalized retention and drift times.
    :param batch_size: Limits the number of nodes during computation [prevents ram overflow problems].

    :return: Unidirected graph and a dataframe with connected components.
    """

    # Initialize a graph.
    graph = nx.Graph()

    # Each peak is added as a node to the graph.
    for idx in range(len(peak_dataframe)):
        # Each node coordinate is set to the normalized peak coordinate.
        node = tuple(times_normalized[idx])
        # Get the peak data of this index from the dataframe.
        peak_data = peak_dataframe.iloc[idx]

        # Calculate how often this peak was detected.
        # This is important because nodes with the same drift & retention time are only saved as one node!
        # By saving additional information the actual peaks count, labels and npy_files are not lost.
        peak_count = peak_dataframe[(peak_dataframe['ret_time'] == peak_data['ret_time']) &
                                    (peak_dataframe['drift_time'] == peak_data['drift_time'])]

        # Save some peak information from the dataframe for later use.
        labels = peak_count['label'].to_list()
        npy_files = peak_count['npy_file'].to_list()
        dataframe_indicies = peak_count.index.to_list()
        spectrum_names = peak_count['spectrum'].to_list()
        intensities = peak_count['intensity'].to_list()

        # Add the node to the graph.
        graph.add_node(node_for_adding=node, labels=labels, npy_files=npy_files, dataframe_idx=dataframe_indicies,
                       ret_time=peak_data['ret_time'], drift_time=peak_data['drift_time'], peak_count=len(peak_count),
                       spectrum_names=spectrum_names, intensities=intensities)

    # Create a nearest neighbor tree for fast lookup of neighbor nodes.
    tree = KDTree(times_normalized)
    # Number of nodes in the graph.
    node_count = graph.number_of_nodes()

    # Create edges between all nodes within a defined radius. Create batches of nodes and walk through them.
    # neighbor_nodes is a list with lists inside. The position of the list is the index of the node.
    # The inner list contains the positions of nodes which are considered the nodes neighbors.
    for start_node in range(0, node_count, batch_size):
        end_node = min(start_node + batch_size, node_count)
        sub_nodes = times_normalized[start_node:end_node]
        neighbor_nodes = tree.query_ball_point(sub_nodes, r=max_node_distance, p=2)

        for sub_node_idx, neighbors in enumerate(neighbor_nodes):
            global_idx = start_node + sub_node_idx
            node_1 = tuple(times_normalized[global_idx])
            for neighbor_idx in neighbors:
                node_2 = tuple(times_normalized[neighbor_idx])
                if not node_1 == node_2:
                    graph.add_edge(node_1, node_2)

    # Get connected components from the graph (connected nodes within the graph).
    # Each connected component will be identified as one consensus peak.
    connected_components = list(nx.connected_components(graph))
    # Create a list of dictionaries which contain peak component information.
    peak_component_list = []
    # Walk through all components and nodes and connect the component index to the dataframe index and save node
    # information to a list of dictionaries.
    for component_idx, component in enumerate(connected_components):
        for node in component:
            # Get node data.
            node_data = graph.nodes[node]

            # Load node information from previously created lists.
            indicies = node_data['dataframe_idx']
            labels = node_data['labels']
            npy_files = node_data['npy_files']
            spectrum_names = node_data['spectrum_names']
            intensities = node_data['intensities']

            # Save node information as a dictionary and append it to a list.
            for index in range(len(indicies)):
                peak_component_list.append({'index': indicies[index],
                                            'label': labels[index],
                                            'spectrum': spectrum_names[index],
                                            'ret_time': node_data['ret_time'],
                                            'drift_time': node_data['drift_time'],
                                            'intensity': intensities[index],
                                            'npy_file': npy_files[index],
                                            'component_idx': component_idx})

    # Create a new dataframe which contains the new component information.
    peak_component_dataframe = pd.DataFrame(peak_component_list)
    # Save peak component dataframe as Excel file.
    excel_filename = output_dir / "02_peak_components.xlsx"
    peak_component_dataframe.to_excel(excel_filename, index=False)

    return graph, peak_component_dataframe


def calculate_consensus_peaks(graph: nx.Graph,
                              unique_labels: list[str],
                              output_dir: Path) -> list[dict]:
    """
    Not yet described ... TODO

    :param graph: Unidirected graph with all peaks as nodes.
    :param unique_labels: List of unique labels.
    :param output_dir: The output directory for plots and other files.

    :return: List with consensus peak dictionaries [One dictionary per consensus peak].
    """

    # List of all connected components.
    components = list(nx.connected_components(graph))
    # List of dictionaries with consensus peak information (returned by this function).
    consensus_peaks = []

    # Walk through all components.
    for component_idx, component in enumerate(components):
        # Create a temporary dictionary which counts the occurrences of each label per component.
        temp_dictionary = defaultdict(int)
        total_peaks = 0

        # Create a peak dictionary and fill it with peak and label information.
        peak_dictionary = {}

        # Create lists with all retention and drift times for the current component.
        ret_times = []
        drift_times = []
        min_intensity = -1

        # Walk through each node.
        for node in component:
            # Get all labels of this node
            # If multiple labels are there, it means that this node consists of multiple peaks.
            node_data = graph.nodes[node]
            labels = node_data['labels']

            if min_intensity == -1 or min_intensity > min(node_data['intensities']):
                min_intensity = min(node_data['intensities'])

            # Each label represents one peak of this node. This loop makes sure that each peak of a node is
            # considered for the consensus peak calculation.
            for label in labels:
                ret_times.append(node_data['ret_time'])
                drift_times.append(node_data['drift_time'])
                temp_dictionary[label] += 1
                total_peaks += 1

        # TODO - Experimental
        # Skip a component, if it only consists of x peaks. This removes rare encountered peaks.
        if total_peaks <= 5:
            continue

        # Calculate the consensus peak retention and drift time.
        mean_ret_time = sum(ret_times) / len(ret_times)
        mean_drift_time = sum(drift_times) / len(drift_times)

        # Insert consensus peak information to the peak_dictionary.
        peak_dictionary["mean_ret_time"] = mean_ret_time
        peak_dictionary["mean_drift_time"] = mean_drift_time
        peak_dictionary["min_intensity"] = min_intensity
        peak_dictionary["component_idx"] = component_idx
        peak_dictionary["Peaks_Total"] = total_peaks

        for label in unique_labels:
            count_key = label + "_Peaks"

            # Insert the node count for this label OR 0 if none node for this label was found.
            if label in temp_dictionary:
                peak_dictionary[count_key] = temp_dictionary[label]
            else:
                peak_dictionary[count_key] = 0

        # Append a dictionary to the list.
        consensus_peaks.append(peak_dictionary)

    # Save consensus peaks.
    consensus_peaks_dataframe = pd.DataFrame(consensus_peaks)
    filename = output_dir / "03_consensus_peaks.xlsx"
    consensus_peaks_dataframe.to_excel(filename, index=False)

    return consensus_peaks


def save_all_consensus_peak_windows(preprocessed_spectra: list[ims.Spectrum],
                                    peak_radius: int,
                                    spectra_paths: list[Path],
                                    consensus_excel_file: Path,
                                    create_heatmaps: bool = True,
                                    create_npy: bool = True) -> None:
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
    print("V. SAVING CONSENSUS PEAK WINDOWS")
    # Walk through each preprocessed spectrum and collect needed arguments for the peak finding computation.
    for idx, spectrum in enumerate(preprocessed_spectra):
        task_args = (spectrum, peak_radius, spectra_paths[idx], consensus_excel_file, create_heatmaps, create_npy)
        # Append the tuple of arguments to the tasks list.
        tasks.append(task_args)

    # Start parallel processing. One cpu core handles one spectrum.
    with Pool(cpu_cores) as p:
        p.starmap(save_spektrum_consensus_peak_windows, tasks)



def save_spektrum_consensus_peak_windows(spectrum: ims.Spectrum,
                                         peak_radius: int,
                                         output_dir: Path,
                                         consensus_excel_file: Path,
                                         create_heatmaps: bool,
                                         create_npy: bool) -> None:

    # 1. Spectrum normalization. ---------------------------------------------------------------------------------------
    print(f"\t- Saving Consensus Peak Windows [{spectrum.name}]")
    # Keep the non normalized values for later use.
    values_non_normalized = spectrum.values.copy()
    # Normalize the spectrum [0-1].
    spectrum.normalization()

    # Load the Excel file as a dataframe object.
    consensus_peaks_dataframe = pd.read_excel(consensus_excel_file)

    padded_values = np.pad(
        spectrum.values,
        pad_width=peak_radius,
        mode='constant',
        constant_values=0
    )

    padded_values_non_normalized = np.pad(
        values_non_normalized,
        pad_width=peak_radius,
        mode='constant',
        constant_values=0
    )

    saved_consensus_windows = 0
    all_consensus_windows = 0

    # Walk through all rows.
    for idx, consensus_peak in consensus_peaks_dataframe.iterrows():
        # Calculate the retention and drifttime indices from the actual times saved in the Excel file.
        ret_idx = np.abs(spectrum.ret_time - consensus_peak['mean_ret_time']).argmin()
        drift_idx = np.abs(spectrum.drift_time - consensus_peak['mean_drift_time']).argmin()

        start_ret_idx = ret_idx - peak_radius
        end_ret_idx = ret_idx + 3 * peak_radius + 1
        start_drift_idx = drift_idx - peak_radius
        end_drift_idx = drift_idx + 3 * peak_radius + 1
        peak_window_intensities = padded_values[start_ret_idx:end_ret_idx, start_drift_idx:end_drift_idx]
        peak_window_intensities_non_normalized = padded_values_non_normalized[start_ret_idx:end_ret_idx, start_drift_idx:end_drift_idx]

        if np.max(peak_window_intensities_non_normalized) >= consensus_peak['min_intensity']:
            # Plot the peak heatmaps.
            if create_heatmaps:
                plot.plot_peak_heatmap(spectrum=spectrum,
                                       heatmap_window=peak_window_intensities,
                                       ret_idx=ret_idx,
                                       drift_idx=drift_idx,
                                       window_size=peak_radius,
                                       plot_dir=output_dir / "heatmap" / "consensus peak")

            # 5. Save peak information as .npy file ----------------------------------------------------------------
            # Define the numpy filename and create the needed directories.
            if create_npy:
                npy_dir = output_dir / "npy" / "consensus peak" / spectrum.name
                if not npy_dir.exists():
                    npy_dir.mkdir(parents=True, exist_ok=True)

                npy_filename = npy_dir / f"PW_{output_dir.name}_{spectrum.name}_RT{spectrum.ret_time[ret_idx]}_DT{spectrum.drift_time[drift_idx]}_{4 * peak_radius + 1}x{4 * peak_radius + 1}.npy"
                np.save(npy_filename, peak_window_intensities)

            # Increase the counter of the saved consensus peak windows.
            saved_consensus_windows += 1

        # Increase the counter of all consensus peak windows.
        all_consensus_windows += 1

    # Notify that the peak detection on this spectrum is finished and print the number of peaks.
    print(f"\t- {saved_consensus_windows}/{all_consensus_windows} consensus peaks saved [{spectrum.name}]")


