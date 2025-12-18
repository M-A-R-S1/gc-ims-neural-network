import numpy as np
from matplotlib import pyplot as plt
from pathlib import Path
import seaborn as sns
import math
import ims
import networkx as nx

def single_gcims_plot(spectrum: ims.Spectrum,
                      plot_dir: Path,
                      condition: str,
                      size: tuple[int, int] = (10,6),
                      peak_cords: np.ndarray[tuple[int]] = None) -> None:
    """
    This function creates a plot for a given gc-ims spectrum and saves it at the "output_dir/condition" path.
    The created plot shows the spectrum of one .mea file.

    :param spectrum: The gc-ims spectrum of one .mea file.
    :param plot_dir: Saving path of the plotting image.
    :param condition: The condition of the dataset [e.g. "raw" for raw data, or "processed" for preprocessed data"]
    :param size: Size of the plot (Default size is 10,6)
    :param peak_cords: Numpy Array of peak coordinate tuples (retention index, drift index).

    :return: None.
    """

    # Check if the condition parameter is not empty.
    if not condition:
        condition = "unspecified"

    # Get the name of the spectrum.
    spectrum_name = Path(spectrum.name)

    # Create the output directory.
    plot_dir = plot_dir / condition
    if not plot_dir.exists():
        plot_dir.mkdir(parents=True, exist_ok=True)

    # Creat the plot.
    plt.figure(figsize=size)
    spectrum.plot()

    # Plot Peaks (if in the function arguments)
    if peak_cords is not None and len(peak_cords) > 0:
        plt.title(f"{spectrum_name} [{len(peak_cords)} {condition}]")
        for coord in peak_cords:
            ret_idx, drift_idx = coord
            plt.plot(spectrum.drift_time[drift_idx], spectrum.ret_time[ret_idx], 'y+', markersize=2)
    else:
        plt.title(f"{spectrum_name} [{condition}]")

    plt.xlabel("Drifttime [ms]")
    plt.ylabel("Retentiontime [s]")
    cbar = plt.gcf().axes[-1]
    cbar.set_ylabel("Intensity", fontsize=10)
    # Saving the plot image.
    image_name = plot_dir / f"{spectrum_name}_{condition}.png"
    plt.savefig(image_name, dpi=300, bbox_inches='tight')
    plt.close()


def overview_gcims_plot(dataset: list[ims.Spectrum],
                        plot_dir: Path,
                        condition: str,
                        size: tuple[int, int] = (5, 6)) -> None:
    """
    This function creates an overview plot for a given gc-ims dataset and saves it at the root of the "output_dir"
    parameter path. The created plot contains up to 16 subplots and uses all .mea files of the "output_dir" parameter
    path.

    :param dataset: The gc-ims dataset with all spectra of a directory.
    :param plot_dir: Saving path of the plotting image.
    :param condition: The condition of the dataset [e.g. "raw" for raw data, or "processed" for preprocessed data"]
    :param size: Size tuple for the subplot figures. Default size (5,6)

    :return: None.
    """
    # Create the output directory.
    if not plot_dir.exists():
        plot_dir.mkdir(parents=True, exist_ok=True)

    # Define plot layout parameters.
    SPECTRA_NUM = min(len(dataset), 16)
    COLS = 4
    ROWS = math.ceil(SPECTRA_NUM / COLS)

    fig, axes = plt.subplots(ROWS, COLS, figsize=(COLS * size[0], ROWS * size[1]), sharex=True, sharey=True)
    plt.suptitle(f"Spectra overview plot [{plot_dir.name} - {condition}]", fontsize=16)

    # Walk through all spectra and create the plots.
    for idx, spectrum in enumerate(dataset):
        # Create the Plot in the gc-ims design.
        axes[idx].imshow(spectrum.values,
                  origin="lower",
                  aspect='auto',
                  cmap="RdBu_r",
                  vmin=30,
                  vmax=400,
                  extent=(min(spectrum.drift_time),
                          max(spectrum.drift_time),
                          min(spectrum.ret_time),
                          max(spectrum.ret_time),
                          ))
        axes[idx].set_title(f"{spectrum.name}", fontsize=10)
        axes[idx].set_xlabel("Drifttime [ms]", fontsize=10)
        axes[idx].set_ylabel("Retentiontime [s]", fontsize=10)

    # Hide the axis of empty subplot areas.
    for idx in range(SPECTRA_NUM, len(axes)):
        axes[idx].axis('off')

    # Saving the plot image.
    image_name = plot_dir / f"overview_plot_{plot_dir.name}_{condition}.png"
    plt.tight_layout(rect=(0, 0.03, 1, 0.97))
    plt.savefig(image_name, dpi=300, bbox_inches='tight')
    plt.close()


def plot_peak_heatmap(spectrum: ims.Spectrum,
                      heatmap_window: np.ndarray[tuple[int]],
                      ret_idx: int,
                      drift_idx: int,
                      window_size: int,
                      plot_dir: Path) -> None:
    """
       This function creates a heatmap plot for a detected peak and saves it. The created plot covers the entire area
       of the centered peak.

       :param spectrum: The gc-ims spectrum.
       :param heatmap_window: The peak window.
       :param ret_idx: The retention index of the center peak.
       :param drift_idx: The drift index of the center peak.
       :param window_size: The size of the peak window.
       :param plot_dir: Saving path of the plotting image.

       :return: None.
       """

    heatmap_dir = plot_dir / "heatmap" / spectrum.name
    if not heatmap_dir.exists():
        heatmap_dir.mkdir(parents=True, exist_ok=True)

    heatmap_file = heatmap_dir / f"HM_{spectrum.name}_RT{ret_idx}_DT{drift_idx}_{4 * window_size + 1}x{4 * window_size + 1}.png"

    # Create the heatmap plot
    plt.figure(figsize=(10, 10))
    sns.heatmap(
        heatmap_window,
        annot=True,
        fmt=".1f",
        cmap="RdBu_r",
        cbar=True,
        linecolor='white',
        linewidths=0.5,
        annot_kws={"size": 5}
    )
    plt.title(f"{spectrum.name} Peak Heatmap")
    plt.xlabel("Drifttime [relative index]")
    plt.ylabel("Retentiontime [relative index]")
    plt.gca().invert_yaxis()
    fig_caption = f"RT: {spectrum.ret_time[ret_idx]:.4f} [s] , DT: {spectrum.drift_time[drift_idx]:.4f} [ms]"
    plt.figtext(0.445, 0.04, fig_caption, ha="center", va="center", fontsize=10)
    # Save the heatmap image.
    plt.savefig(heatmap_file, bbox_inches="tight")
    plt.close()


def plot_connected_component_overview(graph: nx.Graph,
                                      output_dir: Path) -> None:

    """
    This function creates an overview plot for the connected components.

    :param graph: Unidirected graph with all peaks as nodes.
    :param output_dir: The output directory for the plots.

    :return: None.
    """

    # List of all connected components.
    components = list(nx.connected_components(graph))
    # Defines a color list. One color for each component.
    colors = plt.colormaps["hsv"](np.linspace(0, 1, len(components)+1))
    # Specifies the position for each connected component.
    pos = {node: (node[1], node[0]) for node in graph.nodes()}

    plt.figure(figsize=(10, 6))
    plt.xlabel("Drifttime [ms]")
    plt.ylabel("Retentiontime [s]")
    plt.title("Connected components")

    # Walk through all components and add them to the plot.
    for component_idx, component in enumerate(components):
        node_tuples = list(component)

        nx.draw_networkx(G=graph.subgraph(node_tuples),
                         pos=pos,
                         node_size=5,
                         node_color=[colors[component_idx]] * len(node_tuples),
                         edge_color=[colors[component_idx]] * len(node_tuples),
                         with_labels=False)

    # Save the plot.
    filename = output_dir / "overview_connected_components.png"
    plt.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close()


def plot_single_connected_component(graph: nx.Graph,
                                    component: set,
                                    component_idx: int,
                                    output_dir: Path):

    """
    This function creates a plot for each of the connected components and saves it in the "components" subdirectory.

    :param graph: Unidirected graph with all peaks as nodes.
    :param component: One connected component.
    :param component_idx: The index of the connected component.
    :param output_dir: The output directory for the plots.

    :return: None
    """
    pos = {node: (node[1], node[0]) for node in component}

    plt.figure(figsize=(10, 6))
    plt.xlabel("Drifttime [ms]")
    plt.ylabel("Retentiontime [s]")
    plt.title(f"Single Connected Component [ID: {component_idx} - Node Count: {len(component)}]")

    subgraph = graph.subgraph(component)
    nx.draw_networkx(
        subgraph,
        pos,
        node_size=20,
        node_color="tab:blue",
        edge_color="lightgray",
        with_labels=False
    )

    filename = output_dir / f"component_{component_idx}.png"
    plt.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close()


def plot_consensus_peaks(consensus_peaks: list[dict],
                         unique_labels: list[str],
                         output_dir: Path) -> None:
    """
    This function creates one consensus peak plot for each label.

    :param consensus_peaks: list with consensus plot dictionaries.
    :param unique_labels: List with all unique labels.
    :param output_dir: The output directory for the plots.

    :return: None.
    """

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
    """
    This function uses the label proportion of a peak and creates a mixed color.

    :param unique_labels: List of all unique labels.
    :param peak: One consensus peak.

    :return: tuple with combined color values.
    """

    # The total number of nodes of this consensus peak.
    total_node_count = peak["Peaks_Total"]

    # Define the different label marker colors.
    colors = plt.colormaps["hsv"](np.linspace(0, 1, len(unique_labels)+1))

    # Check if there are nodes, if not return a black color.
    if total_node_count == 0:
        return (0, 0, 0)

    color_ratios = []
    # Walk through all unique labels and check how often each label is part of the consensus peak.
    for label_idx, label in enumerate(unique_labels):
        if peak[label + "_Peaks"] > 0:
            color_ratios.append( (peak[label + "_Peaks"] / total_node_count) * colors[label_idx])

    # Sum the individual label colors up to crate a mixed color for this consensus peak.
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
