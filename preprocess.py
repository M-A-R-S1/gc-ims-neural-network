import os
import ims
from pathlib import Path
from scipy.ndimage import uniform_filter
import matplotlib.pyplot as plt
import numpy as np


def preprocess_spectra(input_dir: Path, output_dir: Path) -> list:
    # read .ims data.
    dataset = ims.Dataset.read_mea(input_dir)
    print(f"Opening dataset: {dataset.name} ({len(dataset.data)} Spectra)")

    # Define the output directories for the plotted spectra images.
    output_dir_raw = output_dir / dataset.name / 'raw'
    output_dir_processed = output_dir / dataset.name / 'processed'
    if not output_dir_raw.exists():
        output_dir_raw.mkdir(parents=True, exist_ok=True)
    if not output_dir_processed.exists():
        output_dir_processed.mkdir(parents=True, exist_ok=True)

    # Interpolates all spectra to a common RIP (Reactant Ion Peaks)
    dataset.interp_riprel()

    processed_data = []
    # Renaming table
    # TODO -> Adjust, based on future .mea file names ... or remove it completely.
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

    # Walk through all spectra of the dataset.
    for idx, spectrum in enumerate(dataset.data):
        print("############################################################")
        print(f"Spectrum {idx + 1}/{len(dataset.data)}")
        if spectrum.values.size == 0:
            print(f"Spectrum empty ---- Skipping.")
            continue

        # Relative path of the spectrum file.
        spectrum_path = Path(spectrum.name)

        # Create the name for the current spectrum.
        # TODO -> Adjust, based on future .mea file names.
        name_parts = spectrum_path.stem.split('_')
        if len(name_parts) >= 6:
            name_original = name_parts[2]
            number_1 = name_parts[3]
            number_2 = name_parts[5]
            name_short = name_map.get(name_original, name_original)
            spectrum_name = f"{name_short}_{number_1}_{number_2}"
        else:
            spectrum_name = spectrum_path

        # Raw spectrum plotting.
        plt.figure(figsize=(10, 6))
        spectrum.plot()
        plt.title(f"{spectrum_name} [raw]")
        plt.xlabel("Drifttime [ms]")
        plt.ylabel("Retentiontime [s]")
        # Change the colorbar label.
        cbar = plt.gcf().axes[-1]
        cbar.set_ylabel("Intensity", fontsize=10)
        # Saving the image.
        imagename_raw = output_dir_raw /  f"{spectrum_name}_raw.png"
        plt.savefig(imagename_raw, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Raw spectra saved [{spectrum_name}_raw.png]")

        # Baseline correction for drift- and retention time.
        spectrum.cut_dt(start=1.02, stop=2.5)
        spectrum.cut_rt(start=80, stop=900)
        # Why???
        # TODO -> Ask why, and IF this is correct. -> The uniform_filter is used but only on the copied data!?
        spectrum.values_processed = np.copy(spectrum.values)

        # Baseline-Korrektur
        # Zeilenweise und spaltenweise wird ein niedriger Perzentilwert (5 %) als Basislinie subtrahiert

        # Background noise reduction for each axis, computed with a given percentile.
        percentile = 5
        spectrum.values_processed -= np.percentile(spectrum.values_processed, percentile, axis=0, keepdims=True)
        spectrum.values_processed -= np.percentile(spectrum.values_processed, percentile, axis=1, keepdims=True)
        # Adjust negative values to 0.
        spectrum.values_processed[spectrum.values_processed < 0] = 0
        spectrum.values = spectrum.values_processed
        # Glättung: uniform_filter mittelt lokal über ein Fenster von 10x10 Punkten, um Rauschen zu reduzieren

        """ TODO -> In der Arbeit steht "Am Ende der Vorverarbeitung wurde mittels des Uniform-Filters mit einem
        # 11×11-Fenster gefiltert" ... Hier im Code wird aber 10x10 verwendet. Die uniform_filter function arbeitet NICHT
        # mit einem 0-index. Also müsste es auf 11x11 geändert werden?
        """
        spectrum.values_processed = uniform_filter(spectrum.values_processed, size=(10, 10))
        # TODO -> Warum wird eine Glättung NUR auf den kopierten Daten durchgeführt? Fehler? Sinn?

        # Vorverarbeitetes Spektrum visualisieren
        # Zeichnet das vorverarbeitete Spektrum
        plt.figure(figsize=(10, 6))
        spectrum.plot()
        # Beschriftung der Achsen:relative Driftzeit, Retentionszeit.
        plt.title(f"{spectrum_name} PROCESSED")
        plt.xlabel("Drifttime [ms]")
        plt.ylabel("Retentiontime [s]")
        # Legt Colorbar-Beschriftung auf "Intensität".
        cbar = plt.gcf().axes[-1]  # Annahme: letzte Achse ist die Colorbar
        cbar.set_ylabel("Intensity", fontsize=10)
        caption = ""
        plt.figtext(0.5, -0.008, caption, wrap=True, horizontalalignment='center', fontsize=7)
        # Speichert PNG-Datei im Ausgabeordner
        plot_filename_processed = os.path.join(output_dir_processed, f"{spectrum_name}_processed_minBaseline.png")
        plt.savefig(plot_filename_processed, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Processed spectra saved in {plot_filename_processed}")

        processed_data.append(spectrum)

        """
        # Grid-Plot der ersten 18 Rohspektren
        # Erstellt Rasterdarstellung (n_rows x n_cols)
        n_spectra = min(18, len(processed_data))
        n_cols = 6
        n_rows = math.ceil(n_spectra / n_cols)

        fig, axes = plt.subplots(n_rows, n_cols, figsize=(18, 3 * n_rows), sharex=True, sharey=True)
        axes = axes.flatten()
        # Zeigt jedes Spektrum in imshow mit Farbcodierung cmap="viridis"
        for idx in range(n_spectra):
            ax = axes[idx]
            spectrum = filtered_data[idx]
            ax.imshow(spectrum.values, aspect='auto', cmap='viridis')
            ax.set_title(f"{idx + 1}: {spectrum.name}", fontsize=8)
            ax.axis('off')

        # Leere Subplots ausblenden, falls weniger als 18 Spektren
        for idx in range(n_spectra, len(axes)):
            axes[idx].axis('off')

        plt.suptitle("Grid-Plot der ersten 18 Rohspektren", fontsize=16)
        plt.tight_layout(rect=[0, 0, 1, 0.95])

        grid_plot_path = os.path.join(output_dir, "grid_plot_18_rohspektren.png")
        plt.savefig(grid_plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Grid-Plot mit 18 Rohspektren gespeichert unter: {grid_plot_path}")
        """

    # Gibt alle erfolgreich vorverarbeiteten Spektren zurück
    return processed_data
