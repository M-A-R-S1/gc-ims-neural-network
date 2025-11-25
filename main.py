
if __name__ == '__main__':
       # First Step -> GC-IMS Preprocessing
    # input_dir --> Ordner mit den Rohdaten der Spektren.
    # output_dir --> Ordner für die verarbeiteten Daten
    # plot_dir --> Ordner für die erzeugten Heatmaps/Plots.
    # s.makedirs(exist_ok=True)--> erstellt die Ordner, falls sie noch nicht existieren
    #     input_dir = "./Honig_Daten/mini_format/mini"
    #     output_dir = "./All_test"
    #     plot_dir = "./All_test"

    #     os.makedirs(output_dir, exist_ok=True)
    #     os.makedirs(plot_dir, exist_ok=True)
    # Liste für alle exakten Peaks

    # window_size --> Größe des Fensters für Peak-Extraktion(halb Länge = 5--> Peakfenster=11x11)
    # min_margin--> Mindestabstand zum Rand
    #     window_size = 5
    #     min_margin = 5
    #     Zustand = "raw"  # Zustand der Daten, z.B. "raw" oder "processed"

    # lädt und verarbeitet die Rohdaten
    #     filtered_data = preprocess_and_visualize_spectra(input_dir, plot_dir)

    # Nach der Vorverarbeitung: Visualisierung der vorverarbeiteten Spektren als Subplots
    #     plot_processed_spectra_in_subplots(output_dir, cols=6, title="Übersicht: Vorverarbeitete Spektren")

    #     try:
    # Parallelverarbeitung der Spektren, inklusive Peak-Erkennung
    #         all_peak_df = parallel_process_spectra(filtered_data, window_size, output_dir, plot_dir, Zustand, min_margin)
    #     except Exception as e:
    #         print(f"Fehler bei der Peak-Erkennung: {str(e)}")

    # Speichert die kombinierten Peak-Daten als CSV
    #     all_peak_df.to_csv(os.path.join(output_dir, "11x11_raw_all_peak_data_exact_nachbarn_weniger.csv"), index=False)
    #     print("Alle Peak-Daten gespeichert.")

    # Speichert die kombinierten Peak-Daten als Excel-Datei
    #     all_peak_df.to_excel(os.path.join(output_dir, "11x11_raw_all_peak_data_exact_nachbarn_weniger.xlsx"), index=False)

