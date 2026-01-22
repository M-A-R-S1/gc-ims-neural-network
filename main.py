from pathlib import Path
import preprocess
import peak
import model
from model import vae_loss
import dataloader
import torch
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader

import matplotlib.pyplot as plt
import numpy as np
from sklearn.manifold import TSNE


def plot_tsne(latent_tensor, labels, epoch, save_path):

    tsne = TSNE(n_components=2, random_state=42, perplexity=30, max_iter=300)
    latents_2d = tsne.fit_transform(latent_tensor)

    labels = labels.numpy()

    # Plot erstellen
    plt.figure(figsize=(8, 6))
    scatter = plt.scatter(latents_2d[:, 0], latents_2d[:, 1], c=labels, cmap="tab10", alpha=0.5, s=5)
    plt.colorbar(scatter, ticks=np.unique(labels), label='Class')
    plt.title(f"Latent Space t-SNE Visualization (Epoch {epoch+1})")
    plt.xlabel("t-SNE Dimension 1")
    plt.ylabel("t-SNE Dimension 2")

    # Speichern
    plt.savefig(f"{save_path}/tsne_epoch_{epoch+1}.png", dpi=300)
    plt.close()


if __name__ == '__main__':

    # Step 0: Define all necessary directories.
    # The root input dir.
    input_dir = Path("./data/IMS_Olive_Oil_Geography_small")
    # The root output dir.
    output_dir = Path("./output/IMS_Olive_Oil_Geography_small")
    # Plot dir for original and reconstructed peak heatmaps.
    plot_dir = Path("./output/IMS_Olive_Oil_Geography_small/vae_results")

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
                                                        load_existing=True)

    
    # Step 2: Calculate peaks on preprocessed data.
    try:
        peak_dataframe = peak.get_all_peaks(preprocessed_spectra=preprocessed_data,
                                            peak_radius=5,
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
                                 max_node_distance=0.006)
    """

    epochs = 200
    latent_dim = 8
    batch_size = 32
    lr = 0.0001
    hidden_dim = 64
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

    model = model.VariationalAutoencoderV1(input_layers=1, hidden_layers=hidden_dim, latent_dimension=latent_dim).to(device)
    #model = model.VariationalAutoencoderV2(hidden_layers=hidden_dim, latent_dimension=latent_dim).to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    for epoch in range(epochs):
        model.train()
        train_loss = 0
        latents = []
        labels = []

        for feature, label in train_loader:
            feature = feature.to(device)
            label_prediction, mean, log_variance = model(feature)
            loss = vae_loss(feature, label_prediction, mean, log_variance)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            train_loss += loss.item()

            latents.append(mean.detach().cpu())
            labels.append(label)

        # Concatenate latents and labels for the epoch
        latents_tensor = torch.cat(latents)
        labels_tensor = torch.cat(labels)

        model.eval()
        test_loss = 0
        with torch.inference_mode():
            for feature, label in test_loader:
                feature = feature.to(device)
                label_prediction, mean, log_variance = model(feature)
                loss = vae_loss(feature, label_prediction, mean, log_variance)
                test_loss += loss.item()


                if (epoch+1) % 50 == 0 or epoch == 0:
                    n_images = 20
                    origs = feature[:n_images].cpu().numpy()
                    recons = label_prediction[:n_images].cpu().numpy()

                    fig, axes = plt.subplots(2, n_images, figsize=(30, 6))
                    for i in range(n_images):
                        ax_orig = axes[0, i]
                        im_orig = ax_orig.imshow(origs[i].squeeze(), cmap='RdBu_r')
                        ax_orig.set_title(f"Original {i + 1}")
                        ax_orig.axis('off')

                        # Rekonstruktion
                        ax_recon = axes[1, i]
                        im_recon = ax_recon.imshow(recons[i].squeeze(), cmap='RdBu_r')
                        ax_recon.set_title(f"Recon. {i + 1}")
                        ax_recon.axis('off')

                    filename = plot_dir / f"epoch_{epoch + 1}.png"
                    plt.tight_layout()
                    plt.savefig(filename)
                    plt.close()

                    plot_tsne(latents_tensor, labels_tensor, epoch, plot_dir)

        print(
            f"Epoch {epoch + 1}: Train Loss = {train_loss / len(train_dataset):.4f}, Test Loss = {test_loss / len(test_dataset):.4f}")
