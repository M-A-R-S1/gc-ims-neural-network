import numpy
from matplotlib import pyplot as plt
from pathlib import Path
import seaborn as sns
import math
import ims


def single_gcims_plot(spectrum: ims.Spectrum,
                      plot_dir: Path,
                      condition: str,
                      size: tuple[int, int] = (10,6),
                      peak_cords: numpy.ndarray[tuple[int, ...]] = None) -> None:
    """
    This function creates a plot for a given gc-ims spectrum and saves it at the "output_dir/condition" path.
    The created plot shows the spectrum of one .mea file.

    :param spectrum: The gc-ims spectrum of one .mea file.
    :param plot_dir: Saving path of the plotting image.
    :param condition: The condition of the dataset [e.g. "raw" for raw data, or "processed" for preprocessed data"]
    :param size: Size of the plot (Default size is 10,6)
    :param peak_cords: Numpy Array of peak coordinate tuples (retention index, drift index).

    :return: None.
    """

    # Check if the condition parameter is not empty.
    if not condition:
        condition = "unspecified"

    # Get the name of the spectrum.
    spectrum_name = Path(spectrum.name)

    # Create the output directory.
    plot_dir = plot_dir / condition
    if not plot_dir.exists():
        plot_dir.mkdir(parents=True, exist_ok=True)

    # Creat the plot.
    plt.figure(figsize=size)
    spectrum.plot()

    # Plot Peaks (if in the function arguments)
    if len(peak_cords) > 0:
        plt.title(f"{spectrum_name} [{len(peak_cords)} {condition}]")
        for coord in peak_cords:
            ret_idx, drift_idx = coord
            plt.plot(spectrum.drift_time[drift_idx], spectrum.ret_time[ret_idx], 'r+', markersize=3)
    else:
        plt.title(f"{spectrum_name} [{condition}]")

    plt.xlabel("Drifttime [ms]")
    plt.ylabel("Retentiontime [s]")
    cbar = plt.gcf().axes[-1]
    cbar.set_ylabel("Intensity", fontsize=10)
    # Saving the plot image.
    image_name = plot_dir / f"{spectrum_name}_{condition}.png"
    plt.savefig(image_name, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"- Plot saved [{spectrum_name}_{condition}.png]")


def overview_gcims_plot(dataset: list[ims.Spectrum],
                        plot_dir: Path,
                        condition: str,
                        size: tuple[int, int] = (5, 6)) -> None:
    """
    This function creates an overview plot for a given gc-ims dataset and saves it at the root of the "output_dir"
    parameter path. The created plot contains up to 16 subplots and uses all .mea files of the "output_dir" parameter
    path.

    :param dataset: The gc-ims dataset with all spectra of a directory.
    :param plot_dir: Saving path of the plotting image.
    :param condition: The condition of the dataset [e.g. "raw" for raw data, or "processed" for preprocessed data"]
    :param size: Size tuple for the subplot figures. Default size (5,6)

    :return: None.
    """
    # Create the output directory.
    if not plot_dir.exists():
        plot_dir.mkdir(parents=True, exist_ok=True)

    # Define plot layout parameters.
    SPECTRA_NUM = min(len(dataset), 16)
    COLS = 4
    ROWS = math.ceil(SPECTRA_NUM / COLS)

    fig, axes = plt.subplots(ROWS, COLS, figsize=(COLS * size[0], ROWS * size[1]), sharex=True, sharey=True)
    plt.suptitle(f"Spectra overview plot [{plot_dir.name} - {condition}]", fontsize=16)

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
    image_name = plot_dir / f"overview_plot_{plot_dir.name}_{condition}.png"
    plt.tight_layout(rect=(0, 0.03, 1, 0.97))
    plt.savefig(image_name, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"- Overview plot saved [{plot_dir.name}_{condition}.png]")


def plot_peak_heatmap(spectrum: ims.Spectrum,
                      heatmap_window: numpy.ndarray[tuple[int, ...]],
                      ret_idx: int,
                      drift_idx: int,
                      window_size: int,
                      plot_dir: Path,
                      condition: str) -> None:
    """
       This function creates a heatmap plot for a detected peak and saves it." The created plot covers the entire area
       of the centered peak itself, as well as all surrounding neighbor peaks.

       :param spectrum: The gc-ims spectrum.
       :param heatmap_window: The peak window.
       :param ret_idx: The retention index of the center peak.
       :param drift_idx: The drift index of the center peak.
       :param window_size: The size of the peak window.
       :param plot_dir: Saving path of the plotting image.
       :param condition: The condition of the dataset [In this case by default "peak"]

       :return: None.
       """

    heatmap_dir = plot_dir / condition / spectrum.name
    if not heatmap_dir.exists():
        heatmap_dir.mkdir(parents=True, exist_ok=True)

    heatmap_file = heatmap_dir / f"HM_{spectrum.name}_RT{ret_idx}_DT{drift_idx}_{4 * window_size + 1}x{4 * window_size + 1}.png"

    # Create the heatmap plot
    plt.figure(figsize=(10, 10))
    sns.heatmap(
        heatmap_window,
        annot=True,
        fmt=".1f",
        cmap="RdBu_r",
        cbar=True,
        linecolor='white',
        linewidths=0.5,
        annot_kws={"size": 5}
    )
    plt.title(f"{spectrum.name} Peak Heatmap")
    plt.xlabel("Drifttime [relative index]")
    plt.ylabel("Retentiontime [relative index]")
    fig_caption = f"RT: {spectrum.ret_time[ret_idx]:.4f} [s] , DT: {spectrum.drift_time[drift_idx]:.4f} [ms]"
    plt.figtext(0.445, 0.04, fig_caption, ha="center", va="center", fontsize=10)
    # Save the heatmap image.
    plt.savefig(heatmap_file, bbox_inches="tight")
    plt.close()
    print(f"Peak Heatmap saved: {heatmap_file.name}")