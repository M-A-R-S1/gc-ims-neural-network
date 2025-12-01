from pathlib import Path
import preprocess


if __name__ == '__main__':
    print("TEST")

    # Step 0: Define all necessary directories.
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
                                         create_plots="all")


    # Step 2: Calculate peaks on preprocessed data.
    try:
        peak_dataframe = preprocess.get_all_peaks(preprocessed_data=preprocessed_data,
                                                  neighbor_distance=5,
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

###########################################################################################################################################################################
