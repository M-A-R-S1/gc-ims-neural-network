from pathlib import Path
import config
import preprocess
import peak
import model
import loop
from model import vae_loss
import dataloader
import torch
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader
import re
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, ConfusionMatrixDisplay

if __name__ == '__main__':

    # Step 0: Define all necessary directories.
    # The root input dir.
    input_dir = Path(config.INPUT_DIR)
    # The root output dir.
    output_dir = Path(config.OUTPUT_DIR)
    # Plot dir for original and reconstructed peak heatmaps.
    plot_dir = Path(config.PLOT_DIR)

    # Check and create output if necessary.
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    if not plot_dir.exists():
        plot_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Preprocess the .mea files
    if config.PREPROCESSING or config.PEAK_DETECTION or config.SAVE_CONSENSUS_WINDOWS:
        preprocessed_data, spectra_paths = preprocess.start(input_dir=input_dir,
                                                            output_dir=output_dir,
                                                            create_plots="Single",
                                                            drift_cut=config.DRIFT_CUT,
                                                            retention_cut=config.RETENTION_CUT,
                                                            load_existing=True)


        # Step 2: Calculate peaks on preprocessed data.
        if config.PEAK_DETECTION:
            peak_dataframe = peak.get_all_peaks(preprocessed_spectra=preprocessed_data,
                                                peak_radius=config.PEAK_RADIUS,
                                                spectra_paths=spectra_paths,
                                                create_heatmaps=True,
                                                create_npy=True)

            # Save peak data to Excel file.
            excel_filename = output_dir / "01_peak_data.xlsx"
            peak_dataframe.to_excel(excel_filename, index=False)

        # Step 3: Consensus peak calculation.
        if config.CONSENSUS_PEAK_CALCULATION:
            excel_filename = output_dir / "01_peak_data.xlsx"
            peak.extract_consensus_peaks(excel_file=excel_filename,
                                         output_dir=output_dir,
                                         create_plots="overview",
                                         max_node_distance=config.MAX_NODE_DISTANCE)


        # Step 4: Save consensus peak windows as .npy files.
        if config.SAVE_CONSENSUS_WINDOWS:
            peak.save_all_consensus_peak_windows(preprocessed_spectra=preprocessed_data,
                                                 peak_radius=config.PEAK_RADIUS,
                                                 spectra_paths=spectra_paths,
                                                 consensus_excel_file = output_dir / "03_consensus_peaks_test.xlsx",
                                                 create_npy=True,
                                                 create_heatmaps=True)


    # Step 4: Training the VAE.
    if config.USE_NEURAL_NETWORK:
        # Device agnostic code.
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Receive all peak files and their labels/classes.
        root_dir = output_dir
        npy_paths = list(root_dir.glob("*/npy/peak/*/*.npy"))

        classes = sorted(entry.name for entry in root_dir.iterdir() if entry.is_dir())
        class_dict = {class_name: idx for idx, class_name in enumerate(classes)}

        # Split the data into training and test data.
        train_paths, test_paths = train_test_split(npy_paths,
                                                    test_size=0.20,
                                                    random_state=42,
                                                    shuffle=True)

        # Create the datasets and dataloaders.
        train_dataset = dataloader.VaeDataset(train_paths, class_dict)
        # Create the test dataset. Use all the data or split it.
        if config.TEST_WITH_ALL_DATA:
            test_dataset = dataloader.VaeDataset(npy_paths, class_dict)
        else :
            test_dataset = dataloader.VaeDataset(test_paths, class_dict)

        train_dataloader = DataLoader(train_dataset, batch_size=config.BATCH_SIZE, shuffle=True)
        test_dataloader = DataLoader(test_dataset, batch_size=config.BATCH_SIZE, shuffle=False)

        # Initialize the model.
        model = model.VariationalAutoencoderCNN(input_layers=1,
                                                hidden_layers=config.HIDDEN_DIM,
                                                latent_dimension=config.LATENT_DIM).to(device)

        # Check if there is already a saved model matching the filename and directory and load it.
        model.load_model(model_dir=config.SAVE_DIR, file_name=config.FILE_NAME)

        # Define the optimizer.
        optimizer = torch.optim.Adam(model.parameters(), lr=config.LEARNING_RATE)

        # Start training and testing if training is active.
        if config.DO_TRAINING:
            loop.training_loop(model=model,
                               train_dataloader=train_dataloader,
                               test_dataloader=test_dataloader,
                               loss_fn=vae_loss,
                               optimizer=optimizer,
                               device=device,
                               epochs=config.EPOCHS,
                               plot_dir=plot_dir)

        # Start testing unseen data to evaluate the model.
        if config.DO_TESTING:
            loop.testing_loop(model=model,
                              dataloader=test_dataloader,
                              loss_fn=vae_loss,
                              device=device,
                              plot_dir=plot_dir)

        # Save the model.
        if config.SAVING:
            model.save_model(model_dir=config.SAVE_DIR, file_name=config.FILE_NAME)


    # Step 5: Preparing and using the random forest algorithm for classification.
    if config.RANDOM_FOREST_CLASSIFICATION:
        # Listen für unsere Features und Labels
        # Device agnostic code.
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Initialize the model.
        model = model.VariationalAutoencoderCNN(input_layers=1,
                                                hidden_layers=config.HIDDEN_DIM,
                                                latent_dimension=config.LATENT_DIM).to(device)

        # Check if there is already a saved model matching the filename and directory and load it.
        model.load_model(model_dir=config.SAVE_DIR, file_name=config.FILE_NAME)

        X_features = []
        y_labels = []

        # Get all consensus .npy files.
        npy_paths = list(output_dir.glob("*/npy/consensus peak/*/*.npy"))

        # Den Encoder in den Eval-Modus setzen
        model.eval()

        for path in npy_paths:
            filename = path.stem  # z.B. PW_Italy_151204_224012_RT77_DT29_21x21
            parts = filename.split('_')

            # 1. Label extrahieren (Stelle 1, da PW Stelle 0 ist)
            label = parts[1]

            # 2. Suche nach Zahlen inkl. Dezimalpunkt
            rt_val = float(re.search(r'RT([\d.]+)', filename).group(1))
            dt_val = float(re.search(r'DT([\d.]+)', filename).group(1))

            # 3. .npy Datei laden und durch Encoder schicken
            peak_data = np.load(path)
            # Sicherstellen, dass das Format (1, 1, H, W) für den Encoder stimmt
            input_tensor = torch.from_numpy(peak_data).float().view(1, 1, 21, 21).to(device)

            with torch.inference_mode():
                x = model.encoder(input_tensor)
                z = model.latent_mean(x)
                latent_vector = z.cpu().numpy().flatten()

            # 4. Latenten Vektor + RT + DT kombinieren
            combined_row = np.hstack((latent_vector, [rt_val, dt_val]))

            X_features.append(combined_row)
            y_labels.append(label)

        X = np.array(X_features)
        y = np.array(y_labels)


        # Split in Training und Test
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        # Random Forest initialisieren
        rf_model = RandomForestClassifier(n_estimators=1000,
                                          class_weight='balanced',
                                          random_state=42)
        # Training
        rf_model.fit(X_train, y_train)
        # Vorhersage
        y_pred = rf_model.predict(X_test)
        # Ergebnisse anzeigen
        print(classification_report(y_test, y_pred))


        import matplotlib.pyplot as plt

        importances = rf_model.feature_importances_
        feature_names = [f'z_{i}' for i in range(config.LATENT_DIM)] + ['RT_Time', 'DT_Time']
        plt.figure(figsize=(10, 6))
        plt.bar(feature_names, importances)
        plt.title("Wichtigkeit der Merkmale für die Olivenöl-Bestimmung")
        plt.ylabel("Importance Score")
        plt.savefig(plot_dir / "random forest" / "importance_score.png", dpi=300)
        plt.close()

        # Erstellt die Confusion Matrix
        fig, ax = plt.subplots(figsize=(8, 6))
        ConfusionMatrixDisplay.from_estimator(rf_model, X_test, y_test,cmap='Blues', ax=ax)
        plt.title("Wo liegen die Verwechslungen?")
        plt.savefig(plot_dir / "random forest" / "confusion_matrix.png", dpi=300)
        plt.close()


        import seaborn as sns
        import pandas as pd
        # Erstelle einen DataFrame für die Visualisierung
        df_plot = pd.DataFrame(X[:, :config.LATENT_DIM], columns=[f'z_{i}' for i in range(config.LATENT_DIM)])
        df_plot['Country'] = y
        # Schmelze den DataFrame für Seaborn
        df_melted = df_plot.melt(id_vars='Country', var_name='Latent_Var', value_name='Value')
        plt.figure(figsize=(12, 6))
        sns.boxplot(data=df_melted, x='Latent_Var', y='Value', hue='Country')
        plt.title("Vergleich der latenten Merkmale nach Land")
        plt.savefig(plot_dir / "random forest" / "latent_space_comparison.png", dpi=300)
        plt.close()