from pathlib import Path
import preprocess
import peak
import in_progress

if __name__ == '__main__':

    # Step 0: Define all necessary directories.
    # The root input dir.
    input_dir = Path("./data/IMS_Olive_Oil_Geography/Test")
    # The root output dir.
    output_dir = Path("./output/test")

    # Check and create output if necessary.
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Preprocess the .mea files
    # - RIP Interpolation (for each dataset)
    # - Background noise reduction
    # - Smoothing filter
    preprocessed_data, spectra_paths = preprocess.start(input_dir=input_dir,
                                                        output_dir=output_dir,
                                                        create_plots="Single",
                                                        load_existing=True)

    # Step 2: Calculate peaks on preprocessed data.
    try:
        peak_dataframe = peak.get_all_peaks(preprocessed_data=preprocessed_data,
                                            neighbor_distance=5,
                                            spectra_paths=spectra_paths,
                                            create_heatmaps=False,
                                            create_npy=True)

        # Save peak data to csv file.
        csv_filename = output_dir / "All_peak_data.csv"
        peak_dataframe.to_csv(csv_filename, index=False)
        # Save peak date to Excel file.
        excel_filename = output_dir / "All_peak_data.xlsx"
        peak_dataframe.to_excel(excel_filename, index=False)
    except Exception as err:
        print(f" Error during peak detection: {err=}, {type(err)=}")
        raise

    """
    in_progress.process_peaks_from_excel(excel_file=excel_filename,
                                         output_dir=output_dir,
                                         threshold=0.002,
                                         filter_types=["Greece", "Italy", "Spain"])
    """

###########################################################################################################################################################################
