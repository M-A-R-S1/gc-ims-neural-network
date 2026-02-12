import numpy as np
import torch
from matplotlib import pyplot as plt
from pathlib import Path
import seaborn as sns
import math
import ims
import networkx as nx
from sklearn.manifold import TSNE
from matplotlib.ticker import MaxNLocator

def single_gcims_plot(spectrum: ims.Spectrum,
                      plot_dir: Path,
                      condition: str,
                      size: tuple[int, int] = (10,6),
                      peak_cords: np.ndarray[tuple[int]] = None) -> None:
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
    if peak_cords is not None and len(peak_cords) > 0:
        plt.title(f"{spectrum_name} [{len(peak_cords)} {condition}]")
        for coord in peak_cords:
            ret_idx, drift_idx = coord
            plt.plot(spectrum.drift_time[drift_idx], spectrum.ret_time[ret_idx], 'y+', markersize=2)
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


def plot_peak_heatmap(spectrum: ims.Spectrum,
                      heatmap_window: np.ndarray[tuple[int]],
                      ret_idx: int,
                      drift_idx: int,
                      window_size: int,
                      plot_dir: Path) -> None:
    """
       This function creates a heatmap plot for a detected peak and saves it. The created plot covers the entire area
       of the centered peak.

       :param spectrum: The gc-ims spectrum.
       :param heatmap_window: The peak window.
       :param ret_idx: The retention index of the center peak.
       :param drift_idx: The drift index of the center peak.
       :param window_size: The size of the peak window.
       :param plot_dir: Saving path of the plotting image.

       :return: None.
       """

    heatmap_dir = plot_dir / "heatmap" / spectrum.name
    if not heatmap_dir.exists():
        heatmap_dir.mkdir(parents=True, exist_ok=True)

    heatmap_file = heatmap_dir / f"HM_{spectrum.name}_RT{ret_idx}_DT{drift_idx}_{4 * window_size + 1}x{4 * window_size + 1}.png"

    # Create the heatmap plot
    plt.figure(figsize=(10, 10))
    sns.heatmap(
        heatmap_window,
        annot=False,
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
    plt.gca().invert_yaxis()
    fig_caption = f"RT: {spectrum.ret_time[ret_idx]:.4f} [s] , DT: {spectrum.drift_time[drift_idx]:.4f} [ms]"
    plt.figtext(0.445, 0.04, fig_caption, ha="center", va="center", fontsize=10)
    # Save the heatmap image.
    plt.savefig(heatmap_file, bbox_inches="tight")
    plt.close()


def plot_connected_component_overview(graph: nx.Graph,
                                      output_dir: Path) -> None:

    """
    This function creates an overview plot for the connected components.

    :param graph: Unidirected graph with all peaks as nodes.
    :param output_dir: The output directory for the plots.

    :return: None.
    """

    # List of all connected components.
    components = list(nx.connected_components(graph))
    # Defines a color list. One color for each component.
    colors = plt.colormaps["hsv"](np.linspace(0, 1, len(components)+1))
    # Specifies the position for each connected component.
    pos = {node: (node[1], node[0]) for node in graph.nodes()}

    plt.figure(figsize=(10, 6))
    plt.xlabel("Drifttime [ms]")
    plt.ylabel("Retentiontime [s]")
    plt.title("Connected components")

    # Walk through all components and add them to the plot.
    for component_idx, component in enumerate(components):
        node_tuples = list(component)

        nx.draw_networkx(G=graph.subgraph(node_tuples),
                         pos=pos,
                         node_size=5,
                         node_color=[colors[component_idx]] * len(node_tuples),
                         edge_color=[colors[component_idx]] * len(node_tuples),
                         with_labels=False)

    # Save the plot.
    filename = output_dir / "overview_connected_components.png"
    plt.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close()


def plot_single_connected_component(graph: nx.Graph,
                                    component: set,
                                    component_idx: int,
                                    output_dir: Path):

    """
    This function creates a plot for each of the connected components and saves it in the "components" subdirectory.

    :param graph: Unidirected graph with all peaks as nodes.
    :param component: One connected component.
    :param component_idx: The index of the connected component.
    :param output_dir: The output directory for the plots.

    :return: None
    """
    pos = {node: (node[1], node[0]) for node in component}

    plt.figure(figsize=(10, 6))
    plt.xlabel("Drifttime [ms]")
    plt.ylabel("Retentiontime [s]")
    plt.title(f"Single Connected Component [ID: {component_idx} - Node Count: {len(component)}]")

    subgraph = graph.subgraph(component)
    nx.draw_networkx(
        subgraph,
        pos,
        node_size=20,
        node_color="tab:blue",
        edge_color="lightgray",
        with_labels=False
    )

    filename = output_dir / f"component_{component_idx}.png"
    plt.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close()


def plot_consensus_peaks(consensus_peaks: list[dict],
                         unique_labels: list[str],
                         output_dir: Path) -> None:
    """
    This function creates one consensus peak plot for each label.

    :param consensus_peaks: list with consensus plot dictionaries.
    :param unique_labels: List with all unique labels.
    :param output_dir: The output directory for the plots.

    :return: None.
    """

    # find the component with the highest node count and save this count values.
    max_nodes = max(peak['Peaks_Total'] for peak in consensus_peaks)

    # Define the different label marker colors.
    colors = plt.colormaps["hsv"](np.linspace(0, 1, len(unique_labels)+1))

    # Walk through all labels and create a scatter plot for each label.
    for plot_label_idx, plot_label in enumerate(unique_labels):
        plt.figure(figsize=(10, 6), dpi=300*len(unique_labels))
        plt.title(f"Consensus Peaks [{plot_label}]")
        plt.xlabel("Drifttime [ms]")
        plt.ylabel("Retentiontime [s]")

        for peak in consensus_peaks:
            ret_time = peak["mean_ret_time"]
            drift_time = peak["mean_drift_time"]
            component_idx = peak["component_idx"]
            total_node_count = peak["Peaks_Total"]
            current_node_count = peak[plot_label + "_Peaks"]

            # Check if this is a pure consensus peak (Pure = Consists of components from one unique label).
            if total_node_count == current_node_count and current_node_count > 0:
                plt.scatter(drift_time, ret_time, color=colors[plot_label_idx], marker='.', s=30)
                plt.text(drift_time, ret_time,f"{component_idx}", fontsize=5, ha='right', va='center', color='black')
            else:
                all_node_counts = [peak[label + "_Peaks"] for label in unique_labels]
                if not total_node_count in all_node_counts and current_node_count > 0:
                    color = mixed_peak_color(unique_labels, peak)
                    plt.scatter(drift_time, ret_time, color=color, marker='x', s=15)
                    plt.text(drift_time, ret_time, f"{component_idx}", fontsize=5, ha='right', va='center', color='black')

        # Save plot as image.
        filename = output_dir / f"consensus_peaks_{plot_label}.png"
        plt.savefig(filename, dpi=300, bbox_inches="tight")
        plt.close()


def mixed_peak_color(unique_labels: list[str],
                     peak: dict) -> tuple:
    """
    This function uses the label proportion of a peak and creates a mixed color.

    :param unique_labels: List of all unique labels.
    :param peak: One consensus peak.

    :return: tuple with combined color values.
    """

    # The total number of nodes of this consensus peak.
    total_node_count = peak["Peaks_Total"]

    # Define the different label marker colors.
    colors = plt.colormaps["hsv"](np.linspace(0, 1, len(unique_labels)+1))

    # Check if there are nodes, if not return a black color.
    if total_node_count == 0:
        return (0, 0, 0)

    color_ratios = []
    # Walk through all unique labels and check how often each label is part of the consensus peak.
    for label_idx, label in enumerate(unique_labels):
        if peak[label + "_Peaks"] > 0:
            color_ratios.append( (peak[label + "_Peaks"] / total_node_count) * colors[label_idx])

    # Sum the individual label colors up to crate a mixed color for this consensus peak.
    mixed_color = sum(color_ratios)

    return tuple(mixed_color)


def plot_original_and_reconstruction(feature: torch.Tensor,
                                     feature_reconstructed: torch.Tensor,
                                     plot_dir: Path,
                                     test_loss: float = None,
                                     epoch: int = None,
                                     image_number: int = 20) -> None:
    """
    This function is called during the testing of a pretrained model and creates plots which compares the original
    feature image with the reconstructed image created from the variational autoencoder.

    :param feature: The original feature image.
    :param feature_reconstructed: The reconstructed feature image of the variational autoencoder.
    :param plot_dir: Directory to save the plots.
    :param test_loss: The test loss after testing the pretrained model.
    :param epoch: The current epoch.
    :param image_number: Number of images to plot.

    :return: None
    """

    num_to_plot = min(feature.size(0), image_number)

    original_image = feature[:num_to_plot].detach().cpu().numpy()
    reconstructed_image = feature_reconstructed[:num_to_plot].detach().cpu().numpy()

    fig, axes = plt.subplots(2, num_to_plot, figsize=(num_to_plot * 1.5, 6))
    for i in range(num_to_plot):
        # Original image.
        ax_orig = axes[0, i]
        ax_orig.imshow(original_image[i].squeeze(), cmap='RdBu_r')
        ax_orig.set_title(f"Original {i + 1}")
        ax_orig.axis('off')

        # Reconstructed image.
        ax_recon = axes[1, i]
        ax_recon.imshow(reconstructed_image[i].squeeze(), cmap='RdBu_r')
        ax_recon.set_title(f"Recon. {i + 1}")
        ax_recon.axis('off')

    if test_loss is not None:
        filename = plot_dir / f"tested_loss-{test_loss:.4f}.png"
    else:
        filename = plot_dir / f"epoch_{epoch+1}.png"
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()


def plot_tsne(latents: torch.Tensor,
              labels: torch.Tensor,
              epoch: int,
              plot_dir: Path) -> None:
    """
    This function creats and saves a T-SNE plot for a given epoch and their latent space vectors.
    A T-SNE plot visualizes how the latent space is distributed. E.g. are similar peak forms saved in proximity?

    :param latents: Tensor with all laten space vectors of the current epoch.
    :param labels: Tensor with all labels for the given latents.
    :param epoch: Current training/testing epoch.
    :param plot_dir: Saving path for the .png file.

    :return: None.
    """

    # Initialize TSNE.
    tsne = TSNE(n_components=2, random_state=42, perplexity=30, max_iter=300)
    latents_2d = tsne.fit_transform(latents)
    labels = labels.cpu().numpy()

    # Create the plot.
    plt.figure(figsize=(8, 6))
    scatter = plt.scatter(latents_2d[:, 0], latents_2d[:, 1], c=labels, cmap="tab10", alpha=0.5, s=5)
    plt.colorbar(scatter, ticks=np.unique(labels), label='Class')
    plt.title(f"Latent Space t-SNE Visualization (Epoch {epoch+1})")
    plt.xlabel("t-SNE Dimension 1")
    plt.ylabel("t-SNE Dimension 2")

    # Save the plot.
    plt.savefig(f"{plot_dir}/tsne_epoch_{epoch+1}.png", dpi=300)
    plt.close()


def plot_loss_curve(losses: dict[str, list[float]],
                    plot_dir: Path) -> None:
    """
    This function plots the train and test losses over time.

    :param losses: Dictionary with lists for different train and test losses [total, recon, kld].
    :param plot_dir: The directory to save the plots.

    :return: None
    """

    # Define the epoch lenght for the x-axis.
    epochs_range = range(1, len(losses['train_total']) + 1)

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 15), sharex=True)

    # 1. Total Loss
    ax1.plot(epochs_range, losses['train_total'], color="blue", label="Train Total")
    ax1.plot(epochs_range, losses['test_total'], color="red", linestyle="--", label="Test Total")
    ax1.set_title("Total VAE Loss (Reconstruction + beta * KLD)")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # 2. BCE Loss (Reconstruction)
    ax2.plot(epochs_range, losses['train_recon'], color="blue", label="Train BCE")
    ax2.plot(epochs_range, losses['test_recon'], color="red", linestyle="--", label="Test BCE")
    ax2.set_title("Reconstruction Loss (Reconstruction Quality)")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # 3. KLD Loss (Regularisation)
    ax3.plot(epochs_range, losses['train_kld'], color="green", label="Train KLD")
    ax3.plot(epochs_range, losses['test_kld'], color="orange", linestyle="--", label="Test KLD")
    ax3.set_title("KLD Loss (Latent Space Regularization)")
    ax3.set_xlabel("Epoch")
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(plot_dir / "detailed_loss_curves.png", dpi=300)
    plt.close()

