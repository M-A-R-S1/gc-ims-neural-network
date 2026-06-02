import numpy as np
import torch
from matplotlib import pyplot as plt
from pathlib import Path
import seaborn as sns
import pandas as pd
import math
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import ConfusionMatrixDisplay


def random_forest_importance_plot(model: RandomForestClassifier,
                                  output_dir: Path,
                                  coordinates: bool)-> None:

    """
    This function plots the importance of the random forest model as a bar graph.
    Zhis bar graph displays the importance of all latent vector variables and the retention and drifttime.

    :param model: The trained random forest model.
    :param output_dir: The directory to save the plot.
    :param coordinates: Is set to True, if coordinates are transmitted. This is only the case for the ALL IN ONE
    random forest classification. If set to True, the retention and drifttimes are also plotted with their importance.

    :return: None
    """

    importances = model.feature_importances_
    feature_names = [f'M{i+1}' for i in range(16)] + [f'V{i+1}' for i in range(16)]

    if coordinates:
        feature_names = feature_names + ['RT', 'DT']

    colors = []
    for name in feature_names:
        if name.startswith('M'):
            colors.append('#3498db')  # Blue color
        elif name.startswith('V'):
            colors.append('#e74c3c')  # red color
        else:
            colors.append('#2ecc71')  # green color

    plt.figure(figsize=(10, 6))
    plt.bar(feature_names, importances, color=colors, edgecolor='black', alpha=0.8)
    plt.title("Random Forest attribute importance")
    plt.ylabel("Importance Score")
    plt.xticks(rotation=45)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.savefig(output_dir / "importance_score.png", dpi=300)
    plt.close()


def random_forest_confusion_matrix(model: RandomForestClassifier,
                                   test_feature: list,
                                   test_label: list,
                                   output_dir: Path)-> None:

    """
    This function plots the confusion matrix of the random forest model.

    :param model: the trained random forest model.
    :param test_feature: the test features.
    :param test_label: the test labels.
    :param output_dir: The directory to save the plot.

    :return: None.
    """

    # --- FARB-SETUP FÜR DEINEN DARK MODE ---
    bg_color = '#2e2e2e'
    text_color = '#ebebeb'

    fig, ax = plt.subplots(figsize=(8, 6))

    # 1. Den Hintergrund der Figure und der Achsen dunkel färben
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)

    # 2. Matrix zeichnen (NEU: colorbar=False blendet die Farbskala aus!)
    ConfusionMatrixDisplay.from_estimator(
        model,
        test_feature,
        test_label,
        cmap='Blues',
        ax=ax,
        colorbar=False
    )

    # tight_layout berechnet die Platzverhältnisse neu
    plt.tight_layout()

    # 3. Textfarben anpassen (Titel und X/Y Labels)
    plt.title("Confusion Matrix", color=text_color, pad=25)
    ax.set_xlabel("")
    ax.set_ylabel("")

    # 4. Tick-Marks (Die Beschriftungen der Labels) einfärben
    plt.xticks(rotation=45, color=text_color)
    plt.yticks(color=text_color)

    # 5. Ränder (Spines) dezent grau machen
    for spine in ax.spines.values():
        spine.set_color('#666666')

    # bbox_inches='tight' verhindert abgeschnittene Labels
    plt.savefig(output_dir / "confusion_matrix.png",
                dpi=300,
                facecolor=fig.get_facecolor(),
                bbox_inches='tight')
    plt.close()


def random_forest_boxplot(features: list,
                          labels: list,
                          output_dir: Path) -> None:

    """
    This function plots one boxplot for each mean + variance pair of the latent space.

    :param features: List of all calculated peak window latent variables.
    :param labels: Corresponding list of labels of the features list.
    :param output_dir: The directory to save the plot.

    :return: None.
    """

    # Create a Dataframe to work with.
    # Create the column names. E.g. M1 | V1 | M2 | V2 | ...
    column_names = [f'M{i + 1}' for i in range(16)] + [f'V{i + 1}' for i in range(16)]
    # Create the actual dataset and combine it with the column names.
    dataframe = pd.DataFrame(np.array(features)[:, :2 * 16], columns=column_names)
    # Addend a new column with the labels.
    dataframe['Label'] = labels

    # Define and create the output directory.
    boxplot_dir = output_dir / "boxplot"
    boxplot_dir.mkdir(parents=True, exist_ok=True)

    # Walk through all latent space values separately.
    for idx in range(1, 16 + 1):
        mean_column = f'M{idx}'
        variance_column = f'V{idx}'

        subset = dataframe[[mean_column, variance_column, 'Label']]
        melted_subset = subset.melt(id_vars='Label', var_name='Latent Variable', value_name='Value')

        plt.figure(figsize=(8, 5))
        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['right'].set_visible(False)
        plt.xticks(rotation=45)
        sns.boxplot(data=melted_subset, x='Latent Variable', y='Value', hue='Label', palette='Set2')
        plt.title(f"Latent Dimension {idx} Variables")
        plt.xlabel("Latent Feature Type")
        plt.ylabel("Value")
        plt.legend(title='Label', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig(boxplot_dir / f"boxplot_{idx}.png", dpi=300)
        plt.close()


def plot_all_rf_peak_windows(labels: list[str],
                             features: list[torch.Tensor],
                             feature_recons: list[torch.Tensor],
                             plot_dir: Path,
                             cols: int=5) -> None:
    """
    This function creates an overview plot for each unique label which is used for the random forest classifier.
    Each overview depicts all used consensus peaks and their reconstructions.

    :param labels: List of labels.
    :param features: List of consensus peaks.
    :param feature_recons: List of reconstructed consensus peaks.
    :param plot_dir: The directory to save the plot.
    :param cols: Number of columns for the plot.

    :return: None
    """

    # Convert the list to numpy arrays (This allows the use of making)!
    labels = np.array(labels)
    features = torch.stack(features)
    feature_recons = torch.stack(feature_recons)

    # List of all unique labels.
    unique_labels = np.unique(labels)

    for label in unique_labels:
        # Create a mask for the current label and select all features and recons which fit this mask.
        mask = (labels == label)
        current_label_features = features[mask].cpu().numpy()
        current_label_recons = feature_recons[mask].cpu().numpy()
        num_peaks = len(current_label_features)

        if num_peaks == 0:
            continue

        # Calculate the layout for the plot.
        rows = math.ceil(num_peaks / cols)
        fig = plt.figure(figsize=(cols * 4, rows * 2))

        for i in range(num_peaks):
            row_idx = i // cols
            col_idx = (i % cols) * 2

            # Original feature.
            ax_raw = plt.subplot2grid((rows, cols * 2), (row_idx, col_idx))
            ax_raw.imshow(current_label_features[i, 0].squeeze(), cmap='RdBu_r')
            ax_raw.axis('off')
            # Titel nur in der ersten Zeile zur Orientierung
            if row_idx == 0: ax_raw.set_title(f"Peak (Raw)")

            # Reconstructed feature.
            ax_recon = plt.subplot2grid((rows, cols * 2), (row_idx, col_idx + 1))
            ax_recon.imshow(current_label_recons[i, 0].squeeze(), cmap='RdBu_r')
            ax_recon.axis('off')
            if row_idx == 0: ax_recon.set_title(f"Peak (Recon)")

        filename = plot_dir / f"peak_overview_{label}.png"
        plt.savefig(filename, dpi=150)
        plt.close()