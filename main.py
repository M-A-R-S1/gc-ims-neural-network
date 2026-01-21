from pathlib import Path
import preprocess
import peak
import model
import dataloader
import torch
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, TensorDataset

if __name__ == '__main__':

    # Step 0: Define all necessary directories.
    # The root input dir.
    input_dir = Path("./data/IMS_Olive_Oil_Geography_small")
    # The root output dir.
    output_dir = Path("./output/IMS_Olive_Oil_Geography_small")

    # Check and create output if necessary.
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    """
    # Step 1: Preprocess the .mea files
    preprocessed_data, spectra_paths = preprocess.start(input_dir=input_dir,
                                                        output_dir=output_dir,
                                                        create_plots="Single",
                                                        load_existing=True)

    
    # Step 2: Calculate peaks on preprocessed data.
    try:
        peak_dataframe = peak.get_all_peaks(preprocessed_spectra=preprocessed_data,
                                            peak_radius=7,
                                            spectra_paths=spectra_paths,
                                            create_heatmaps=False,
                                            create_npy=True)

        # Save peak data to Excel file.
        excel_filename = output_dir / "01_peak_data.xlsx"
        peak_dataframe.to_excel(excel_filename, index=False)
    except Exception as err:
        print(f" Error during peak detection: {err=}, {type(err)=}")
        raise
    

    # Step 3: Consensus peak calculation.
    excel_filename = output_dir / "01_peak_data.xlsx"
    peak.extract_consensus_peaks(excel_file=excel_filename,
                                 output_dir=output_dir,
                                 create_plots="overview",
                                 max_node_distance=0.006)
    """

    epochs = 50
    latent_dim = 16
    batch_size = 128
    lr = 1e-3
    x_dim = 1
    hidden_dim = 32
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    root_dir = output_dir
    npy_paths = list(root_dir.rglob("*.npy"))
    classes = sorted(entry.name for entry in root_dir.iterdir() if entry.is_dir())
    class_dict = {class_name: idx for idx, class_name in enumerate(classes)}

    train_paths, test_paths = train_test_split(
        npy_paths,
        test_size=0.20,
        random_state=42,
        shuffle=True
    )

    train_dataset = dataloader.VaeDataset(train_paths, class_dict)
    test_dataset = dataloader.VaeDataset(test_paths, class_dict)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    model = model.VariationalAutoencoderV1(input_layers=x_dim,
                                           hidden_layers=hidden_dim,
                                           latent_dimension=latent_dim).to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    for epoch in range(epochs):
        model.train()
        train_loss = 0
        for feature, label in train_loader:
            feature = feature.to(device)
            label_prediction, mean, log_variance = model(feature)
            loss = model.vae_loss(feature, label_prediction, mean, log_variance)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            train_loss += loss.item()

        model.eval()
        test_loss = 0
        with torch.inference_mode():
            for feature, label in test_loader:
                feature = feature.to(device)
                label_prediction, mean, log_variance = model(feature)
                loss = model.vae_loss(feature, label_prediction, mean, log_variance)
                test_loss += loss.item()

        print(
            f"Epoch {epoch + 1}: Train Loss = {train_loss / len(train_dataset):.4f}, Test Loss = {test_loss / len(test_dataset):.4f}")