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
                             filter_types: list[str],
                             threshold: float = 0.001) -> pd.DataFrame:

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

    # Calculate connected components.
    graph, components, peak_dataframe = calculate_connected_components(peak_dataframe=peak_dataframe,
                                                                       output_dir=output_dir,
                                                                       threshold=threshold,
                                                                       times_normalized=times_normalized,
                                                                       batch_size=20000)

    # Calculates the label proportions for all components.
    label_proportion_dictionary = calculate_label_proportions(graph=graph,
                                                              components=components)

    # Plotting stuff here ...
    plot.overview_connected_components_plot(graph=graph,
                                            components=components,
                                            output_dir=output_dir)
    component = components[5]

    plot.single_connected_components_plot(graph=graph,
                                          component=component,
                                          output_dir=output_dir)


    #############################################################################
    # Berechnet die Durchschnittspunkte für jede Komponente
    """
    avg_peaks = get_average_peaks(graph, peak_dataframe, components, output_dir, filename="scatter_peaks_with_components")

    # Extrahiert die Honiganteile für jede Komponente
    component_honey_counts = [(honey['Linde_Count'], honey['Lavendel_Count'], honey['Eukalyptus_Count']) for honey in
                              label_proportion_dictionary.values()]

    # Plottet Durchschnittspunkte mit den gemischten Farben basierend auf den Honiganteilen
    plot_peaks_by_honey_type(avg_peaks, component_honey_counts, output_dir, filename_prefix="peaks_by_honey_type")
    """

# Funktion: baut einen Graphen aus den Peak-Daten und bildet Zusammenhangskomponenten
def calculate_connected_components(peak_dataframe: pd.DataFrame,
                                   output_dir: Path,
                                   threshold: float,
                                   times_normalized: np.ndarray,
                                   batch_size: int) -> tuple[nx.Graph, list[nx.components], pd.DataFrame]:

    # Initialize a graph.
    graph = nx.Graph()

    # TODO -> Each peak entry consists of 121 different neighbor peaks. Each of these peaks must be added as a node.

    # Each peak is added as a node in the graph.
    for idx in range(len(peak_dataframe)):
        node = tuple(times_normalized[idx])
        peak_data = peak_dataframe.iloc[idx]
        graph.add_node(node_for_adding=node, label=peak_data['label'], npy_file=peak_data['npy_file'], dataframe_idx=idx)

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
                if global_idx != neighbor_idx:
                    node_2 = tuple(times_normalized[neighbor_idx])
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
            component_mapping[node_data['dataframe_idx']] = component_idx
            # Save node information as dictionary in list.
            peak_component_list.append({'index': node_data['dataframe_idx'],
                                        'label': node_data['label'],
                                        'ret_time': node[0],
                                        'drift_time': node[1],
                                        'npy_file': node_data['npy_file'],
                                        'component_idx': component_idx})

    # insert a new colum to the peak_dataframe which contains the component index.
    peak_dataframe['component_idx'] = peak_dataframe.index.map(component_mapping)

    peak_component_dataframe = pd.DataFrame(peak_component_list)
    # Save peak component dataframe as Excel and csv file.
    csv_filename = output_dir / "peak_components.csv"
    peak_component_dataframe.to_csv(csv_filename, index=False)
    excel_filename = output_dir / "peak_components.xlsx"
    peak_component_dataframe.to_excel(excel_filename, index=False)

    return graph, connected_components, peak_dataframe


def calculate_label_proportions(graph: nx.Graph,
                                components: list[nx.components]) -> dict[dict, ...]:

    # List of dictionaries which is returned.
    component_label_portion = {}

    # Walk through each component.
    for component_idx, component in enumerate(components):
        # Create a label dictionary which counts the occurrences of each label for a component.
        label_dictionary = defaultdict(int)
        total_nodes = 0

        # Walk through each node, check the label and increase the count in the label_dictionary.
        for node in component:
            node_data = graph.nodes[node]
            label = node_data['label']
            label_dictionary[label] += 1
            total_nodes += 1

        # Create a new dictionary and fill it with label information.
        new_label_dictionary = {}
        for key, count in label_dictionary.items():
            count_key = key + "_Count"
            ratio_key = key + "_%"
            new_label_dictionary[count_key] = count
            new_label_dictionary[ratio_key] = round(((count / total_nodes) * 100 if total_nodes > 0 else 0), 2)

        new_label_dictionary["Total_Count"] = total_nodes
        component_label_portion[component_idx + 1] = new_label_dictionary

    return component_label_portion



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
