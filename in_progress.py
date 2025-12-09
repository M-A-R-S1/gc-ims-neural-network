import os
from pathlib import Path
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from matplotlib import pyplot as plt
import networkx as nx
from scipy.spatial import cKDTree
from mpl_toolkits.axes_grid1.inset_locator import inset_axes


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

    # Calculate connected components.
    graph, components, peak_dataframe = calculate_connected_components(peak_dataframe,
                                                                       output_dir,
                                                                       threshold,
                                                                       batch_size=20000)

    #############################################################################
    # # Skalierung der Retentions- und Driftzeiten für spätere Zuweisung
    scaler = MinMaxScaler()
    scaled_times = scaler.fit_transform(peak_dataframe[['ret_time', 'drift_time']].values)

    # Berechnet die Honigtyp-Anteile pro Komponente
    honey_stats = count_honey_type_proportions(components, peak_dataframe, scaled_times)

    # Plottet und speichert das Ergebnis der Zusammenhangskomponenten
    plot_connected_components(graph, components, output_dir)
    komponente = components[109]  # oder eine andere Komponente

    plot_einzene_komponente(graph, komponente, output_dir, filename="komponente_drift_retention.png")

    get_average_peaks(graph, peak_dataframe, components, output_dir, filename="scatter_peaks_with_components")

    # Berechnet die Durchschnittspunkte für jede Komponente
    avg_peaks = get_average_peaks(graph, peak_dataframe, components, output_dir, filename="scatter_peaks_with_components")

    # Extrahiert die Honiganteile für jede Komponente
    component_honey_counts = [(honey['Linde_Count'], honey['Lavendel_Count'], honey['Eukalyptus_Count']) for honey in
                              honey_stats.values()]

    # Plottet Durchschnittspunkte mit den gemischten Farben basierend auf den Honiganteilen
    plot_peaks_by_honey_type(avg_peaks, component_honey_counts, output_dir, filename_prefix="peaks_by_honey_type")


# Funktion: baut einen Graphen aus den Peak-Daten und bildet Zusammenhangskomponenten
def calculate_connected_components(peak_dataframe: pd.DataFrame,
                                   output_dir: Path,
                                   threshold: float,
                                   batch_size: int):

    # Initialize a graph.
    graph = nx.Graph()

    # Extract retention- and drifttime.
    ret_time_list = peak_dataframe['ret_time'].tolist()
    drift_time_list = peak_dataframe['drift_time'].tolist()

    # Combine the retention and drifttimes into one 2D array and normalize the values [0-1].
    scaler = MinMaxScaler()
    ret_and_drift_array = np.column_stack((ret_time_list, drift_time_list))
    scaled_times = scaler.fit_transform(ret_and_drift_array).astype(np.float64)

    # TODO -> Each peak entry consists of 121 different neighbor peaks. Each of these peaks must be added as a node.
    # Jeder Peaks wird als Knoten eingefügt
    # Knoten-ID: die skalierte Koordinate (scaled_ret_time, scaled_drift_time).
    # Knoten bekommen zusätzliche Informationen--> honey_type; npy_file und index
    for idx in range(len(peak_dataframe)):
        node = tuple(scaled_times[idx])
        peak_data = peak_dataframe.iloc[idx]
        graph.add_node(node_for_adding=node, label=peak_data['label'], npy_file=peak_data['npy_file'], index=idx)
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
                    graph.add_edge(node1, node2)

    # Sucht alle Zusammenhangskomponenten
    # Jede Komponente ist eine Menge von Knoten, die über Kanten verbunden sind
    components = list(nx.connected_components(graph))
    # Erstellt ein Dictionary, das jedem Peak-Index seine component_id zuordnet.
    component_mapping = {}
    for component_id, component in enumerate(components):
        for node in component:
            index = graph.nodes[node]['index']
            component_mapping[index] = component_id
    # Fügt die component_id in den ursprünglichen DataFrame ein.
    peak_dataframe['component_id'] = peak_dataframe.index.map(component_mapping)
    # Baut eine Liste mit allen Peaks + ihren Attributen
    # Verwendet skalierte Koordinaten (node[0], node[1]).
    detailed_components = []
    for component_id, component in enumerate(components):
        for node in component:
            peak_data = graph.nodes[node]
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
    return graph, components, peak_dataframe


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
