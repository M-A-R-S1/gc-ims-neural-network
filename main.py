from pathlib import Path

import config
import preprocess
import peak
import model
import loop
from config import *
from model import vae_loss
import dataloader
import torch
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader

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

    """
    # Step 1: Preprocess the .mea files
    preprocessed_data, spectra_paths = preprocess.start(input_dir=input_dir,
                                                        output_dir=output_dir,
                                                        create_plots="Single",
                                                        drift_cut=config.DRIFT_CUT,
                                                        retention_cut=config.RETENTION_CUT,
                                                        load_existing=True)


    # Step 2: Calculate peaks on preprocessed data.
    try:
        peak_dataframe = peak.get_all_peaks(preprocessed_spectra=preprocessed_data,
                                            peak_radius=config.PEAK_RADIUS,
                                            spectra_paths=spectra_paths,
                                            create_heatmaps=True,
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
                                 max_node_distance=config.MAX_NODE_DISTANCE)

    """
    # Step 4: Training the VAE.
    # Device agnostic code.
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Receive all peak files and their labels/classes.
    root_dir = output_dir
    npy_paths = list(root_dir.rglob("*.npy"))
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

    train_dataloader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    test_dataloader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)

    # Initialize the model.
    model = model.VariationalAutoencoderCNN(input_layers=1,
                                            hidden_layers=HIDDEN_DIM,
                                            latent_dimension=LATENT_DIM).to(device)

    # Check if there is already a saved model matching the filename and directory and load it.
    model.load_model(model_dir=config.SAVE_DIR, file_name=config.FILE_NAME)

    # Define the optimizer.
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

    # Start training and testing if training is active.
    if config.DO_TRAINING:
        loop.training_loop(model=model,
                           train_dataloader=train_dataloader,
                           test_dataloader=test_dataloader,
                           loss_fn=vae_loss,
                           optimizer=optimizer,
                           device=device,
                           epochs=EPOCHS,
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
