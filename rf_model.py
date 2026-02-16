import plot
import config
from pathlib import Path
import torch
import re
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, ConfusionMatrixDisplay


def start_random_forest(model: torch.nn.Module,
                        device: torch.device) -> None:

    """
    This function prepares and executes the random forest algorithm.
    1. All .npy files from the consensus peaks are located and loaded.
    2. The latent mean vector from the autoencoder is calculated for each .npy file and appended by the
    retention and drifttime. Together this information is stored as a new vector.
    3. All these new vectors are split into train and test datasets.
    4. A random forest classifier is trained and tested with these vectors.
    5. The results are plotted and saved additionally as an Excel file.

    :param model: the trained Autoencoder model for the peak reconstruction.
    :param device: the device to run the model on.

    :return: None.
    """

    print("=======================================================")
    print("VI. RANDOM FOREST CLASSIFICATION")

    output_dir = Path(config.OUTPUT_DIR)
    # Get all consensus .npy files.
    npy_paths = list(output_dir.glob("*/npy/consensus peak/*/*.npy"))
    # Set with all consensus peak times.
    unique_consensus_times = set()

    # Collect all unique consensus peak times and save them in a set.
    for path in npy_paths:
        filename = path.stem
        consensus_time = re.search(r'(RT[\d.]+_(DT[\d.]+))', filename)

        if consensus_time:
            unique_consensus_times.add(consensus_time.group(1))

    model.eval()

    # Walk through all consensus times and create a random forest for each individual consensus peak.
    for idx, consensus_time in enumerate(unique_consensus_times):
        # List of all features and labels which will be used for the random forest algorithm.
        rf_features = []
        labels = []
        original_features = []
        reconstructions = []

        # Get the retention and drifttimes from the filename.
        # This code uses a regular expression. It looks for the pattern 'RT' followed by a number, followed by a dot.
        # Like RT125.154 -> By using group(1) the RT part is omitted and only "125.154" is selected.
        rt_val = float(re.search(r'RT([\d.]+)', consensus_time).group(1))
        dt_val = float(re.search(r'DT([\d.]+)', consensus_time).group(1))

        # Walk through all npy paths.
        for path in npy_paths:
            filename = path.stem

            if consensus_time not in filename:
                continue

            parts = filename.split('_')

            # Get the label from the filename.
            label = parts[1]
            # Load the peak window from the path.
            peak_window = np.load(path)
            # Calculating the peak window size.
            peak_window_dimension = 4 * config.PEAK_RADIUS + 1
            # Changing the peak window to a tensor and converting the tensor format.
            peak_window_tensor = torch.from_numpy(peak_window).float().view(1, 1, peak_window_dimension,
                                                                            peak_window_dimension).to(device)

            # Calculate the latent dimension vector for the current peak window.
            with torch.inference_mode():
                #encoded_feature = model.encoder(peak_window_tensor)
                #mean = model.latent_mean(encoded_feature)
                reconstruction, mean, _ = model(peak_window_tensor)
                latent_vector = mean.cpu().numpy().flatten()

            # Combine the latent vector with the retention and drifttime.
            combined_feature = np.hstack((latent_vector, [rt_val, dt_val]))

            # Append the feature and labe to the list.
            original_features.append(peak_window_tensor)
            reconstructions.append(reconstruction)
            rf_features.append(combined_feature)
            labels.append(label)


        # Check if features and labels were found. If not, continue with the next consensus peak.
        if len(rf_features)*0.2 <= 4:
            print(f"Index: {idx + 1} - Skipping. Not enough peak windows: {len(rf_features)}x")
            continue

        # Split in Training und Test datasets.
        train_feature, test_feature, train_label, test_label = train_test_split(rf_features,
                                                                                labels,
                                                                                test_size=0.2,
                                                                                random_state=42)
        # Initialize the random forest algorithm.
        rf_model = RandomForestClassifier(n_estimators=1000,
                                          class_weight='balanced',
                                          random_state=42)

        # Start the random forest training.
        rf_model.fit(train_feature, train_label)
        # Get the random forest predictions.
        label_predictions = rf_model.predict(test_feature)
        # Save the results as a dictionary.
        results_dict = classification_report(test_label, label_predictions, output_dict=True)
        # Convert the dictionary to a pandas dataframe.
        results_dataframe = pd.DataFrame(results_dict).transpose()

        # Print the results to the console.
        print(f"Index: {idx + 1} - {(results_dict['accuracy'] * 100): .0f} % - RT{rt_val: .2f}_DT{dt_val: .2f} - {results_dict['weighted avg']['support']}x")

        # Check and create the directory.
        filedir = Path(config.PLOT_DIR) / "random forest" / f"{(results_dict['accuracy']*100):.0f}% - RT{rt_val:.2f}_DT{dt_val:.2f} - {results_dict['weighted avg']['support']}x"
        if not filedir.exists():
            filedir.mkdir(parents=True, exist_ok=True)
         # Save the dataframe as an Excel file.
        filename = filedir /"classification_results.xlsx"
        results_dataframe.to_excel(filename, index=True)

        # Plot the all used peak windows and their reconstructions as an overlay image.
        plot.plot_all_rf_peak_windows(labels=labels,
                                      features=original_features,
                                      feature_recons=reconstructions,
                                      plot_dir=filedir)

        # Plot the Importance graph.
        plot.random_forest_importance_plot(model=rf_model,
                                           output_dir=filedir)
        # Plot the confusion matrix.
        plot.random_forest_confusion_matrix(model=rf_model,
                                            test_feature=test_feature,
                                            test_label=test_label,
                                            output_dir=filedir)
        # Plot the comparison boxplot.
        plot.random_forest_boxplot(features=rf_features,
                                   labels=labels,
                                   output_dir=filedir)
