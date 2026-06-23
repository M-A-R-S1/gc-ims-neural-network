from matplotlib import pyplot as plt
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import ConfusionMatrixDisplay

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

    # Color definitions.
    bg_color = '#2e2e2e'
    text_color = '#ebebeb'

    # Create a figure and axis.
    fig, ax = plt.subplots(figsize=(8, 6))

    # Apply the background color to the figure and the axis.
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)

    # Create a confusion matrix without the colorbar legend.
    ConfusionMatrixDisplay.from_estimator(
        model,
        test_feature,
        test_label,
        cmap='Blues',
        ax=ax,
        colorbar=False
    )

    plt.tight_layout()
    # Set title/axis text and color.
    plt.title("Confusion Matrix", color=text_color, pad=25)
    ax.set_xlabel("")
    ax.set_ylabel("")

    # Color and rotate the ticks.
    plt.xticks(rotation=45, color=text_color)
    plt.yticks(color=text_color)

    # More color stuff for the axis spines.
    for spine in ax.spines.values():
        spine.set_color('#666666')

    # Save the figure.
    plt.savefig(output_dir / "confusion_matrix.png",
                dpi=300,
                facecolor=fig.get_facecolor(),
                bbox_inches='tight')
    plt.close()