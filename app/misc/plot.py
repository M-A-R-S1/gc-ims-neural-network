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