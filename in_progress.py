import os
from pathlib import Path
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from matplotlib import pyplot as plt
import networkx as nx
from scipy.spatial import KDTree
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from collections import defaultdict

import plot


def process_peaks_from_excel(excel_file: Path,
                             output_dir: Path,
                             filter_types: list[str] = None,
                             threshold: float = 0.004) -> pd.DataFrame:

    # Check if the Excel file exists.
    if not excel_file.exists():
        print(f"File not found: {excel_file}")
        return

    # Load the Excel file.
    peak_dataframe = pd.read_excel(excel_file)
    # Filter entries by type.
    if filter_types:
        peak_dataframe = peak_dataframe[peak_dataframe['label'].isin(filter_types)].reset_index(drop=True)

    # Check if the Excel file has all required columns.
    required_cols = {'ret_time', 'drift_time', 'label'}
    if not required_cols.issubset(peak_dataframe.columns):
        raise ValueError(f"Missing columns. Required: {required_cols}")

    # Create connected components.
    process_peaks_and_plot(peak_dataframe=peak_dataframe, output_dir=output_dir, threshold=threshold)

    print("Completed - calculations and plots")
    return peak_dataframe


def process_peaks_and_plot(peak_dataframe: pd.DataFrame,
                           output_dir: Path,
                           threshold: float) -> None:

    # Normalize the retention and drifttime.
    scaler = MinMaxScaler()
    times_normalized = scaler.fit_transform(peak_dataframe[['ret_time', 'drift_time']].values)

    # Create a list with all unique labels from inside the dataframe.
    unique_labels = peak_dataframe['label'].unique().tolist()

    # Calculate connected components.
    graph, peak_dataframe = calculate_connected_components(peak_dataframe=peak_dataframe,
                                                           output_dir=output_dir,
                                                           threshold=threshold,
                                                           times_normalized=times_normalized,
                                                           batch_size=20000)

    # Plotting stuff here ...
    # 1. Overview plot with all components.
    plot.overview_connected_components_plot(graph=graph,
                                            output_dir=output_dir)

    # 2. Create a plot for each component.
    components = list(nx.connected_components(graph))
    component_plot_dir = output_dir / "components"
    # Check and create the component directory.
    if not component_plot_dir.exists():
        component_plot_dir.mkdir(parents=True, exist_ok=True)

    for component_idx, component in enumerate(components):
        plot.single_connected_components_plot(graph=graph,
                                              component=component,
                                              component_idx=component_idx,
                                              output_dir=component_plot_dir)


    # Calculate consensus peaks and label proportions for each component.
    consensus_peaks = calculate_consensus_peaks(graph=graph,
                                                unique_labels=unique_labels,
                                                output_dir=output_dir)

    # Plottet Durchschnittspunkte mit den gemischten Farben basierend auf den Honiganteilen
    plot_consensus_peaks(consensus_peaks=consensus_peaks,
                         unique_labels=unique_labels,
                         output_dir=output_dir)



def calculate_connected_components(peak_dataframe: pd.DataFrame,
                                   output_dir: Path,
                                   threshold: float,
                                   times_normalized: np.ndarray,
                                   batch_size: int) -> tuple[nx.Graph, pd.DataFrame]:
    # Initialize a graph.
    graph = nx.Graph()

    # TODO -> Each peak entry consists of 121 different neighbor peaks. Each of these peaks must be added as a node?
    # Each peak is added as a node in the graph.
    for idx in range(len(peak_dataframe)):
        node = tuple(times_normalized[idx])
        peak_data = peak_dataframe.iloc[idx]

        # Calculate how often this peak was detected.
        # This is important because nodes with the same drift & retention time are only saved as one node!
        # By saving additional information the actual peaks count, labels and npy_files are not lost.
        peak_count = peak_dataframe[(peak_dataframe['ret_time'] == peak_data['ret_time']) &
                                    (peak_dataframe['drift_time'] == peak_data['drift_time'])]

        labels = peak_count['label'].to_list()
        npy_files = peak_count['npy_file'].to_list()
        dataframe_indicies = peak_count.index.to_list()
        spectrum_names = peak_count['spectrum'].to_list()
        intensities = peak_count['intensity'].to_list()

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
        neighbor_nodes = tree.query_ball_point(sub_nodes, r=threshold, p=2)

        for sub_node_idx, neighbors in enumerate(neighbor_nodes):
            global_idx = start_node + sub_node_idx
            node_1 = tuple(times_normalized[global_idx])
            for neighbor_idx in neighbors:
                node_2 = tuple(times_normalized[neighbor_idx])
                if not node_1 == node_2:
                    graph.add_edge(node_1, node_2)

    # Get connected components from the graph (connected nodes within the graph).
    connected_components = list(nx.connected_components(graph))
    # Mapping dictionary.
    component_mapping = {}
    # Create a list of dictionaries which contain peak component information.
    peak_component_list = []
    # Walk through all components and nodes and connect the component index to the dataframe index and save node
    # information to a list of dictionaries.
    for component_idx, component in enumerate(connected_components):
        for node in component:
            # Get node data.
            node_data = graph.nodes[node]

            # component_mapping[node_data['dataframe_idx']] = component_idx
            # Save node information as dictionary in list.

            indicies = node_data['dataframe_idx']
            labels = node_data['labels']
            npy_files = node_data['npy_files']
            spectrum_names = node_data['spectrum_names']
            intensities = node_data['intensities']

            for index in range(len(indicies)):
                peak_component_list.append({'index': indicies[index],
                                            'label': labels[index],
                                            'spectrum': spectrum_names[index],
                                            'ret_time': node_data['ret_time'],
                                            'drift_time': node_data['drift_time'],
                                            'intensity': intensities[index],
                                            'npy_file': npy_files[index],
                                            'component_idx': component_idx})

    # insert a new colum to the peak_dataframe which contains the component index.
    #peak_dataframe['component_idx'] = peak_dataframe.index.map(component_mapping)

    peak_component_dataframe = pd.DataFrame(peak_component_list)
    # Save peak component dataframe as Excel and csv file.
    # csv_filename = output_dir / "02_peak_components.csv"
    # peak_component_dataframe.to_csv(csv_filename, index=False)
    excel_filename = output_dir / "02_peak_components.xlsx"
    peak_component_dataframe.to_excel(excel_filename, index=False)

    return graph, peak_component_dataframe


def calculate_consensus_peaks(graph: nx.Graph,
                              unique_labels: list[str],
                              output_dir: Path) -> list[dict]:

    components = list(nx.connected_components(graph))
    # List of dictionaries (returned by this function).
    consensus_peaks = []

    for component_idx, component in enumerate(components):
        # Create a temporary dictionary which counts the occurrences of each label per component.
        temp_dictionary = defaultdict(int)
        total_nodes = 0

        # Create a peak dictionary and fill it with peak and label information.
        peak_dictionary = {}

        # Create lists with all retention and drift times for the current component.
        ret_times = []
        drift_times = []

        # Walk through each node, check the label and increase the count in the dictionary.
        for node in component:
            node_data = graph.nodes[node]
            labels = node_data['labels']

            for label in labels:
                ret_times.append(node_data['ret_time'])
                drift_times.append(node_data['drift_time'])
                temp_dictionary[label] += 1
                total_nodes += 1

        mean_ret_time = sum(ret_times) / len(ret_times)
        mean_drift_time = sum(drift_times) / len(drift_times)

        # Insert peak information to the peak_dictionary.
        peak_dictionary["mean_ret_time"] = mean_ret_time
        peak_dictionary["mean_drift_time"] = mean_drift_time
        peak_dictionary["component_idx"] = component_idx
        peak_dictionary["Peaks_Total"] = total_nodes

        # Insert peak information to the peak_dictionary.
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


def plot_consensus_peaks(consensus_peaks: list[dict],
                         unique_labels: list[str],
                         output_dir: Path) -> None:

    # find the component with the highest node count and save this count values.
    max_nodes = max(peak['Peaks_Total'] for peak in consensus_peaks)

    # Define the different label marker colors.
    colors = plt.colormaps["hsv"](np.linspace(0, 1, len(unique_labels)+1))

    # Walk through all labels and create a scatter plot for each label.
    for plot_label_idx, plot_label in enumerate(unique_labels):
        plt.figure(figsize=(10, 6), dpi=300*len(unique_labels))
        plt.title(f"Consensus Peaks [{plot_label}]")
        plt.xlabel("Drifttime [ms]")
        plt.ylabel("Retentiontime [s]")

        for peak in consensus_peaks:
            ret_time = peak["mean_ret_time"]
            drift_time = peak["mean_drift_time"]
            component_idx = peak["component_idx"]
            total_node_count = peak["Peaks_Total"]
            current_node_count = peak[plot_label + "_Peaks"]

            # Check if this is a pure consensus peak (Pure = Consists of components from one unique label).
            if total_node_count == current_node_count and current_node_count > 0:
                plt.scatter(drift_time, ret_time, color=colors[plot_label_idx], marker='.', s=30)
                plt.text(drift_time, ret_time,f"{component_idx}", fontsize=5, ha='right', va='center', color='black')
            else:
                all_node_counts = [peak[label + "_Peaks"] for label in unique_labels]
                if not total_node_count in all_node_counts and current_node_count > 0:
                    color = mixed_peak_color(unique_labels, peak)
                    plt.scatter(drift_time, ret_time, color=color, marker='x', s=15)
                    plt.text(drift_time, ret_time, f"{component_idx}", fontsize=5, ha='right', va='center', color='black')

        # Save plot as image.
        filename = output_dir / f"consensus_peaks_{plot_label}.png"
        plt.savefig(filename, dpi=300, bbox_inches="tight")
        plt.close()

    """
    # Scatterplot für alle Peaks zusammen--> erstellt ein einziges großes Scatterplot für alle Peaks und hängt zusätzlich eine Farblegende in Form eines Dreiecks dran
    #
    fig, ax1 = plt.subplots(figsize=(12, 6))  # Erstelle das Haupt-Scatterplot
    ax1.set_title("Scatterplot der Konsensus-Peaks für alle Honigarten")
    ax1.set_xlabel("Driftzeit")
    ax1.set_ylabel("Retentionszeit")
    # avg_peaks: Liste mit Peak-Daten
    # component_honey_counts: Liste mit den Anteilen (Linde, Lavendel, Eukalyptus) für denselben Peak.

    for peak, (linden_count, lavender_count, eucalyptus_count) in zip(consensus_peaks, component_label_count):
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
    """


def mixed_peak_color(unique_labels: list[str],
                     peak: dict) -> tuple:

    # The total number of nodes of this consensus peak.
    total_node_count = peak["Peaks_Total"]

    # Define the different label marker colors.
    colors = plt.colormaps["hsv"](np.linspace(0, 1, len(unique_labels)+1))

    # Check if there are nodes, if not return a black color.
    if total_node_count == 0:
        return (0, 0, 0)

    color_ratios = []

    for label_idx, label in enumerate(unique_labels):
        if peak[label + "_Peaks"] > 0:
            color_ratios.append( (peak[label + "_Peaks"] / total_node_count) * colors[label_idx])

    mixed_color = sum(color_ratios)

    return tuple(mixed_color)


# Die Funktion erzeugt ein Farbdreieck, welches die Mischunng von drei Farben für die entsprechenden Honigytypen visualisiert
# ax: Die Haupt-Achse, auf der das Farbdreieck eingefügt wird
# size: Größe des Farbdreiecks relativ zum Plot (z.B. 0.2 = 20% der Achse)
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
