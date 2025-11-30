from pathlib import Path
import preprocess


if __name__ == '__main__':
    print("TEST")

    # 0. Define all necessary directories.
    input_dir = Path("./data/IMS_Olive_Oil_Geography/Greece/O-034")
    plot_dir = Path("./output/spectra/")
    npy_dir = Path("./output/npy_files")
    # Check and create directories if necessary.
    if not plot_dir.exists():
        plot_dir.mkdir(parents=True, exist_ok=True)
    if not npy_dir.exists():
        npy_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Preprocess the .mea files
    # - RIP Interpolation (for each dataset)
    # - Background noise reduction
    # - Gaussian smoothing
    preprocessed_data = preprocess.start(input_dir=input_dir,
                                         plot_dir=plot_dir,
                                         create_plots="None")

    # Step 2: Calculate peaks on preprocessed data.
    try:
        peak_dataframe = preprocess.get_all_peaks(preprocessed_data=preprocessed_data,
                                                  window_size=5,
                                                  plot_dir=plot_dir,
                                                  npy_dir=npy_dir)

        # Save peak date to csv file.
        csv_filename = npy_dir / "All_peak_data.csv"
        peak_dataframe.to_csv(csv_filename, index=False)
        print(f"All peaks saved as .csv file")
        # Save peak date to Excel file.
        excel_filename = npy_dir / "All_peak_data.xlsx"
        peak_dataframe.to_excel(excel_filename, index=False)
        print(f"All peaks saved as .xlsx file")
    except Exception as err:
        print(f" Error during peak detection: {err=}, {type(err)=}")
        raise


    """
    window_size = 5
    min_margin = 5
    Zustand = "processed"
    plot_dir = Path("./output/testing/plot")
    if not plot_dir.exists():
        plot_dir.mkdir(parents=True, exist_ok=True)

    try:
        all_peak_df = preprocess.parallel_process_spectra(processed_data, window_size, output_dir, Zustand, min_margin)
    except Exception as e:
        print(f"Fehler bei der Peak-Erkennung: {str(e)}")

    # Speichert die kombinierten Peak-Daten als CSV
    all_peak_df.to_csv(os.path.join(output_dir, "11x11_raw_all_peak_data_exact_nachbarn_weniger.csv"), index=False)
    # print("Alle Peak-Daten gespeichert.")

    # Speichert die kombinierten Peak-Daten als Excel-Datei
    all_peak_df.to_excel(os.path.join(output_dir, "11x11_raw_all_peak_data_exact_nachbarn_weniger.xlsx"), index=False)
    """


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


###########################################################################################################################################################################


