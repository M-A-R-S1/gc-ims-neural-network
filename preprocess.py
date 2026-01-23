import ims
from pathlib import Path
import plot
from multiprocessing import Pool
import os

def start(input_dir: Path,
          output_dir: Path,
          create_plots: str = "all",
          drift_cut: tuple[float, float] = (1.02, 2.5),
          retention_cut: tuple[int, int] = (80, 900),
          load_existing: bool = True) -> tuple[list[ims.Spectrum], list[Path]]:
    """
    This function takes care of the preprocess steps for .mea files.
    All .mea files inside a given input directory (input_dir), as well as their subdirectories are used as datasets.

    This functions computes a baseline correction for drift- and retention time and forwards the interpolated spectra
    files to the "preprocess_spectra" function for parallel computation. Each cpu core acts on one spectrum.
    This function then returns all preprocessed spectra as a list and another list with their output paths.

    :param input_dir: The directory where the .mea files are located in.
    :param output_dir: Saving path of the plotting image.
    :param create_plots: Specifies which images to create. [none = no images | single = one image for each .mea file |
    overview = one overview image for each folder which contains .mea files | all = combination of 'overview' + 'single']
    :param drift_cut: Tuple of cutting coordinates for the drifttime (x-axis) in milliseconds (Start , End).
    :param retention_cut: Tuple of cutting coordinates for the retentiontime (y-axis) in seconds (Start, End).
    :param load_existing: If set to True the algorithm trys to load an already preprocessed hdf5 spectrum file.
    This will then skip the preprocessing step for this spectrum.

    :return: Tuple with a list of preprocessed spectra and a list of their paths.
    """

    print("=======================================================")
    print(f"I: PREPROCESSING")

    # List of processed spectra.
    preprocessed_data = []
    # List of paths to the spectra directories.
    spectra_paths = []
    # List of loaded spectra [Spectra which were preprocessed earlier].
    loaded_spectra = []

    # list of plotting strategies.
    plotting_strategy = ["none", "all", "single", "overview"]
    # check if the user plotting strategy exists. If not default to "all".
    if not create_plots.lower() in plotting_strategy:
        create_plots = "all"
    else:
        create_plots = create_plots.lower()

    dataset = ims.Dataset.read_mea(path=str(input_dir),
                                   subfolders=True,
                                   sequential=True,
                                   compr="binning")

    # Try to load .hdf5 files for each spectrum. An .hdf5 file indicates that a spectrum was already processed.
    if load_existing:
        for idx, spectrum in enumerate(dataset.data):
            spectrum_path = output_dir / dataset.labels[idx] / "hdf5" / f"{spectrum.name}.hdf5"
            if spectrum_path.exists():
                loaded_spectrum = ims.Spectrum.read_hdf5(spectrum_path)
                loaded_spectra.append(loaded_spectrum)
                # Save the output directory of the spektrum
                spectra_paths.append(output_dir / dataset.labels[idx])
                print(f"\t- Spectrum {idx + 1}/{len(dataset.data)} - Save file found [loaded]")

    # Skip processing this folder if all dictionary spectra could be loaded from .hdf5 files.
    if len(loaded_spectra) == len(dataset.data):
        return loaded_spectra, spectra_paths

    # Interpolates all spectra to a common RIP (Reactant Ion Peaks)
    dataset.interp_riprel()
    # Check how many cpu cores are available.
    cpu_cores = os.cpu_count()
    tasks = []

    # Collect needed arguments for each spectrum.
    for idx, spectrum in enumerate(dataset.data):
        if spectrum.values.size == 0:
            print(f"\t- Spectrum {idx + 1}/{len(dataset.data)}")
            print(f"\t- Empty spectrum --> Skipping")
            continue

        spectrum_path = output_dir / dataset.labels[idx]

        # Check if the spectrum has already a save file, if so skip the preprocessing step for this spectrum.
        if load_existing:
            hdf5_path = spectrum_path / "hdf5" / f"{spectrum.name}.hdf5"
            if hdf5_path.exists():
                continue

        # Save the spektrum path.
        spectra_paths.append(spectrum_path)

        task_args = (spectrum,
                     spectrum_path,
                     idx,
                     len(dataset.data),
                     create_plots,
                     drift_cut,
                     retention_cut)

        tasks.append(task_args)

    # Start parallel processing. One cpu core handels one spectrum.
    with Pool(cpu_cores) as p:
        dataset_data = p.starmap(preprocess_spectra, tasks)

    # Plot overview of all spectra inside the current subdirectory.
    if create_plots in ["all", "overview"]:
        plot.overview_gcims_plot(dataset=dataset_data,
                                 plot_dir=output_dir,
                                 condition="processed")

    preprocessed_data.extend(dataset_data)
    # Add the loaded spectra to the newly preprocessed spectra.
    preprocessed_data.extend(loaded_spectra)

    return preprocessed_data, spectra_paths



def preprocess_spectra(spectrum: ims.Spectrum,
                       output_dir: Path,
                       idx: int,
                       dataset_length: int,
                       create_plots: str = "all",
                       drift_cut: tuple[float, float] = (1.02, 2.5),
                       retention_cut: tuple[int, int] = (80, 900)) -> ims.Spectrum:
    """
    This function takes care of the parallel preprocessing of gc-ims spectra. Each cpu core acts on one spectrum.
    All .mea files inside a given input directory (input_dir), as well as their subdirectories are used as a dataset.
    Each spectrum is preprocessed by the following:
    - 1. Smoothing the spectrum -> Savitzky–Golay filter.
    - 2. Remove negative intensities by setting them to 0.
    - 3. Saves the preprocessed data as a .hdf5 file.

    This function then returns the preprocessed spectrum.

    The gc-ims spectrum can be plotted and saved as .png files if the function parameter is set accordingly:
    - "single" -> Creates a plot image for each individual .mea file.
    - "overview" -> Creates a plot image for up to 16 .mea files inside the same directory.
    - "all" -> Creates both single and overview plot images.
    - "none" -> Creates no plot images.

    :param spectrum: The spectrum which is about to be preprocessed.
    :param output_dir: Saving path of the plotting image.
    :param idx: The index of this spectrum in the current dataset.
    :param dataset_length: The length of the current dataset (Number of spectra in the dataset).
    :param create_plots: Specifies which images to create. [none = no images | single = one image for each .mea file |
    overview = one overview image for each folder which contains .mea files | all = combination of 'overview' + 'single']
    :param drift_cut: Tuple of cutting coordinates for the drifttime (x-axis) in milliseconds (Start , End).
    :param retention_cut: Tuple of cutting coordinates for the retentiontime (y-axis) in seconds (Start, End).

    :return: preprocessed spectra.
    """

    print(f"\t- Spectrum {idx + 1}/{dataset_length}")

    # Plot the raw spectrum.
    if create_plots in ["all", "single"]:
        plot.single_gcims_plot(spectrum=spectrum,
                               plot_dir=output_dir,
                               condition="raw")

    # Baseline correction - removing the noisy background by subtracting the mean of an empty area.
    spectrum.sub_first_rows(50)
    spectrum.cut_dt(start=drift_cut[0], stop=drift_cut[1])
    spectrum.cut_rt(start=retention_cut[0], stop=retention_cut[1])

    # Smoothing the spectrum with the Savitzky–Golay filter.
    spectrum.savgol(window_length=10, polyorder=4)

    # Remove negative values after applying the smooth filter.
    spectrum.values[spectrum.values < 0] = 0.0

    # Plot the processed spectrum.
    if create_plots in ["all", "single"]:
        plot.single_gcims_plot(spectrum=spectrum,
                               plot_dir=output_dir,
                               condition="processed")

    # Before saving, check if the file already exists. The file must be deleted first! Overriding does not work.
    spectrum_path = output_dir / "hdf5"
    if not spectrum_path.exists():
        spectrum_path.mkdir(parents=True, exist_ok=True)

    spectrum_file = spectrum_path / f"{spectrum.name}.hdf5"
    if spectrum_file.exists():
        spectrum_file.unlink()

    # Save the processed spectrum.
    spectrum.to_hdf5(spectrum_path)

    # Return the preprocessed spectrum.
    return spectrum
