from matplotlib import pyplot as plt
from pathlib import Path
import math
import ims


def single_gcims_plot(spectrum: ims.Spectrum,
                      output_dir: Path,
                      condition: str,
                      size: tuple[int, int] = (10,6)) -> None:
    """
    This function creates a plot for a given GC-IMS spectrum and saves it at the "output_dir/condition" path.
    The created plot shows the spectrum of one .mea file.

    :param spectrum: The GC-IMS spectrum of one .mea file.
    :param output_dir: Saving path of the plotting image.
    :param condition: The condition of the dataset [e.g. "raw" for raw data, or "processed" for preprocessed data"]
    :param size: Size of the plot (Default size is 10,6)
    :return: None.
    """

    # Check if the condition parameter is not empty.
    if not condition:
        condition = "unspecified"

    # Get the name of the spectrum.
    spectrum_name = Path(spectrum.name)

    # Create the output directory.
    output_dir = output_dir / condition
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    # Creat the plot.
    plt.figure(figsize=size)
    spectrum.plot()
    plt.title(f"{spectrum_name} [{condition}]")
    plt.xlabel("Drifttime [ms]")
    plt.ylabel("Retentiontime [s]")
    cbar = plt.gcf().axes[-1]
    cbar.set_ylabel("Intensity", fontsize=10)
    # Saving the plot image.
    image_name = output_dir / f"{spectrum_name}_{condition}.png"
    plt.savefig(image_name, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"- Plot saved [{spectrum_name}_{condition}.png]")


def overview_gcims_plot(dataset: list[ims.Spectrum],
                        output_dir: Path,
                        condition: str,
                        size: tuple[int, int] = (5, 6)) -> None:
    """
    This function creates an overview plot for a given GC-IMS dataset and saves it at the root of the "output_dir"
    parameter path. The created plot contains up to 16 subplots and uses all .mea files of the "output_dir" parameter
    path.

    :param dataset: The GC-IMS dataset with all spectra of a directory.
    :param output_dir: Saving path of the plotting image.
    :param condition: The condition of the dataset [e.g. "raw" for raw data, or "processed" for preprocessed data"]
    :param size: Size tuple for the subplot figures. Default size (5,6)
    :return: None.
    """
    # Create the output directory.
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    # Define plot layout parameters.
    SPECTRA_NUM = min(len(dataset), 16)
    COLS = 4
    ROWS = math.ceil(SPECTRA_NUM / COLS)

    fig, axes = plt.subplots(ROWS, COLS, figsize=(COLS * size[0], ROWS * size[1]), sharex=True, sharey=True)
    plt.suptitle(f"Spectra overview plot [{output_dir.name} - {condition}]", fontsize=16)

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
    image_name = output_dir / f"overview_plot_{output_dir.name}_{condition}.png"
    plt.tight_layout(rect=(0, 0.03, 1, 0.97))
    plt.savefig(image_name, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"- Overview plot saved [{output_dir.name}_{condition}.png]")