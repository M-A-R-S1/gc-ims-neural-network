import ims
from pathlib import Path
from scipy.ndimage import uniform_filter
import numpy as np
import plot


# Overhauled function. Original function = preprocess_and_visualize_spectra
def preprocess_spectra(input_dir: Path,
                       output_dir: Path,
                       create_plots: str = "all",
                       drift_cut: tuple[float, float] = (1.02, 2.5),
                       retention_cut: tuple[int, int] = (80, 900),
                       percentile: float = 5.0,
                       uniform_filter_size: tuple[int, int] = (11, 11)) -> list[ims.Spectrum]:
    """
    This function takes care of the preprocess steps for .mea files.
    All .mea files inside a given input directory (input_dir), as well as their subdirectories are used as datasets.
    Each dataset corresponds to one directory and is preprocessed by the following:
    - 1. Interpolation to a common Reactant Ion Peaks (RIP)
    - 2. Baseline correction for drift- and retention time.
    - 3. Background noise reduction (1) for each axis, computed with a given percentile.
    - 4. Background noise reduction (2) smooth the spectrum by applying a uniform filter.
    This function returns the preprocessed spectra as a list.

    The GC-IMS spectra can be plotted and saved as .png files if the function parameter is set accordingly:
    - "single" -> Creates a plot image for each individual .mea file.
    - "overview" -> Creates a plot image for up to 16 .mea files inside the same directory.
    - "all" -> Creates both single and overview plot images.
    - "none" -> Creates no plot images.

    :param input_dir: The directory where the .mea files are located in.
    :param output_dir: Saving path of the plotting image.
    :param create_plots: Specifies which images to create. [none = no images | single = one image for each .mea file |
    overview = one overview image for each folder which contains .mea files | all = combination of 'overview' + 'single']
    :param drift_cut: Tuple of cutting coordinates for the drifttime (x-axis) in milliseconds (Start , End).
    :param retention_cut: Tuple of cutting coordinates for the retentiontime (y-axis) in seconds (Start, End).
    :param percentile: Value for the background noise reduction. [e.g. percentile=5.0 removes the lowest 5% of the data from a spectrum]
    :param uniform_filter_size: Tuple for the uniform filter size.
    :return: list of preprocessed spectra.
    """

    # List of processed spectra.
    processed_data = []

    # list of plotting strategies.
    plotting_strategy = ["none", "all", "single", "overview"]
    # check if the user plotting strategy exists. If not default to "all".
    if not create_plots.lower() in plotting_strategy:
        create_plots = "all"
    else:
        create_plots = create_plots.lower()

    # Create a set of all subdirectories of the given input_dir which have .mea files in them.
    dir_set = set(p.parent for p in input_dir.rglob('*.mea'))

    # If there are no .mea files at all report this to the user.
    if not dir_set:
        print(f"No .mea files found in {input_dir} and sub directories.")
        return processed_data

    # Walk through all found subdirectories.
    for current_input_dir in sorted(list(dir_set)):
        try:
            # Create the dataset for all .mea files in the current subdirectory.
            dataset = ims.Dataset.read_mea(current_input_dir)
        except Exception as e:
            print("=======================================================")
            print(f"ERROR: could not read files at {current_input_dir}: {e} ---- Skipping.")
            continue

        print("=======================================================")
        print(f"Opening dataset: {dataset.name} ({len(dataset.data)} Spectra)")
        print("-------------------------------------------------------")

        # Set the output directory
        current_output_dir = output_dir / current_input_dir.relative_to(input_dir)

        # Interpolates all spectra to a common RIP (Reactant Ion Peaks)
        dataset.interp_riprel()

        # Walk through all spectra of the dataset.
        for idx, spectrum in enumerate(dataset.data):
            print(f"- Spectrum {idx + 1}/{len(dataset.data)}")
            if spectrum.values.size == 0:
                print(f"- Spectrum empty ---- Skipping.")
                continue

            # Plot the raw spectrum.
            if create_plots in ["all", "single"]:
                plot.single_gcims_plot(spectrum=spectrum,
                                       output_dir=current_output_dir,
                                       condition="raw")

            # Baseline correction for drift- and retention time.
            spectrum.cut_dt(start=drift_cut[0], stop=drift_cut[1])
            spectrum.cut_rt(start=retention_cut[0], stop=retention_cut[1])
            # Background noise reduction for each axis, computed with a given percentile.
            # Adjust negative values to 0.
            # Smooth the adjusted spectrum values and reduce noise.
            spectrum.values -= np.percentile(a=spectrum.values, q=percentile, axis=0, keepdims=True)
            spectrum.values -= np.percentile(a=spectrum.values, q=percentile, axis=1, keepdims=True)
            spectrum.values[spectrum.values < 0] = 0
            spectrum.values = uniform_filter(input=spectrum.values, size=uniform_filter_size)

            # Plot the processed spectrum.
            if create_plots in ["all", "single"]:
                plot.single_gcims_plot(spectrum=spectrum,
                                       output_dir=current_output_dir,
                                       condition="processed")

            # Add the processed spectrum to the list.
            processed_data.append(spectrum)

        # Plot overview of all spectra inside the current subdirectory.
        if create_plots in ["all", "overview"]:
            plot.overview_gcims_plot(dataset=dataset,
                                     output_dir=current_output_dir,
                                     condition="processed")

    return processed_data
