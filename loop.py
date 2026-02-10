import torch
import plot
import config
from timeit import default_timer as timer
from pathlib import Path
from typing import Callable
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import numpy as np

def print_passed_time(start: float,
                      end: float,
                      device: torch.device,
                      decimal_places: int) -> None:
    """
    This function calculates the needed time between two time points.
    To calculate the time difference set the start and end point by calling the timer() function of the timeit.default_timer module.
    Requires the timeit.default_timer module.
    (e.g ...
         start_time = timeit.default_timer()
         # Some Code ....
         ....
         ....
         end_time = timeit.default_timer()

         # Now call this function like ...
         print_passed_time(start_time, end_time, device)

    :param start: Start Point in time.
    :param end: End Point in time.
    :param decimal_places: Number of decimal places to display.
    :param device: Torch Device = "cpu" or "cuda".

    :return: None.
    """

    time_needed = end - start
    print(f"### Time passed on device {device}: {time_needed:.{decimal_places}f}s ###")


def train_model(model: torch.nn.Module,
                dataloader: torch.utils.data.DataLoader,
                loss_fn: Callable[[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, float], torch.Tensor],
                optimizer: torch.optim.Optimizer,
                device: torch.device) -> float:
    """
    Trains a given model and dataloader and returns the calculated loss.

    :param model: The model to train.
    :param dataloader: The dataloader to train with.
    :param loss_fn: the loss function which is used to calculate the loss.
    :param optimizer: the optimizer function which is used for backpropagation.
    :param device: the device where the model and tensors are running.

    :return: Model loss as float value.
    """

    model.train()
    train_loss = 0

    for feature, label in dataloader:
        # Put image and label on the device.
        feature, label = feature.to(device), label.to(device)

        # 1. Forward pass.
        label_prediction, mean, log_variance = model(feature)
        # 2. Calculate the loss.
        loss = loss_fn(feature, label_prediction, mean, log_variance)
        # Divide the loss with the bach size.
        normalized_loss = loss / feature.size(0)
        # 3 Clear the gardient.
        optimizer.zero_grad()
        # 4. Backpropagation.
        normalized_loss.backward()
        # 5. Adjust parameters through gradient decent.
        optimizer.step()

        train_loss += loss.item()

    # Normalize the values to Loss per epoch.
    train_loss = train_loss / len(dataloader.dataset)

    return train_loss


def eval_model(model: torch.nn.Module,
               dataloader: torch.utils.data.DataLoader,
               loss_fn: Callable[[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, float], torch.Tensor],
               device: torch.device,
               current_epoch: int,
               plot_interval: int,
               plot_dir: Path) -> tuple[float, list, list]:
    """
    Evaluates a given model and dataloader by calculating the loss.

    :param model: The model to evaluate.
    :param dataloader: The dataloader to evaluate.
    :param loss_fn: the loss function which is used to calculate the loss.
    :param device: the device where the model and tensors are running.
    :param current_epoch: The current evaluation epoch.
    :param plot_interval: Defines after how many epochs a comparison plot is created.
    :param plot_dir: Saving directory for comparison plots.

    :return: Model loss as float value, a list with all mean latents and another list with associated labels.
    """

    test_loss = 0
    mean_latents = []
    labels = []

    model.eval()
    with torch.inference_mode():
        for feature, label in dataloader:
            # Put features and labels on the device.
            feature, label = feature.to(device), label.to(device)
            # 1. Forward pass.
            label_prediction, mean, log_variance = model(feature)
            # 2. Calculate the test loss.
            loss = loss_fn(feature, label_prediction, mean, log_variance)
            test_loss += loss.item()

            # Collect means and labels for T-SNE plot.
            mean_latents.append(mean.detach().cpu())
            labels.append(label)

    # Normalize the values to Loss per epoch.
    test_loss = test_loss / len(dataloader.dataset)

    # Every X epochs create a plot and compare the original with the reconstructed image.
    if (current_epoch + 1) % plot_interval == 0 or current_epoch == 0:
        plot.plot_original_and_reconstruction(feature=feature,
                                              feature_reconstructed=label_prediction,
                                              plot_dir=plot_dir,
                                              epoch=current_epoch,
                                              image_number=20)

    return test_loss, mean_latents, labels


def training_loop(model: torch.nn.Module,
                  train_dataloader: torch.utils.data.DataLoader,
                  test_dataloader: torch.utils.data.DataLoader,
                  loss_fn: Callable[[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, float], torch.Tensor],
                  optimizer: torch.optim.Optimizer,
                  device: torch.device,
                  epochs: int,
                  plot_dir: Path) -> None:
    """
    Loops through the given number of epochs and performs training and evaluation steps on the given model and data.

    :param model: the model which should be trained.
    :param train_dataloader: The training dataloader.
    :param test_dataloader: The testing dataloader.
    :param loss_fn: The loss function
    :param optimizer: The used optimizer.
    :param device: The device where the computation takes place on.
    :param epochs: The number of training epochs.
    :param plot_dir: Saving path for T-SNE and comparison plots.

    :return: None.
    """

    # Set the start time.
    train_start_time = timer()
    # After how many epochs should a T-SNE and comparison plot be created?
    plot_interval = config.PLOT_INTERVAL

    # Lists in which all training and test losses are saved (This is used later for the train/test loss plot)
    train_losses = []
    test_losses = []

    print(f"Starting the model training process for {epochs} epochs... Please wait")
    # walk through all epochs.
    for epoch in range(epochs):
        # Train the model
        train_loss = train_model(model=model,
                                 dataloader=train_dataloader,
                                 loss_fn=loss_fn,
                                 optimizer=optimizer,
                                 device=device)

        # Evaluates the model
        test_loss, mean_latents, labels = eval_model(model=model,
                                                     dataloader=test_dataloader,
                                                     loss_fn=loss_fn,
                                                     device=device,
                                                     current_epoch=epoch,
                                                     plot_interval=plot_interval,
                                                     plot_dir=plot_dir)

        # Add the train and test loss to lists and save them for later.
        train_losses.append(train_loss)
        test_losses.append(test_loss)

        # Concatenate latents and labels for the epoch
        latents_tensor = torch.cat(mean_latents)
        labels_tensor = torch.cat(labels)

        # Every X epochs create a T-SNE plot.
        if (epoch + 1) % plot_interval == 0 or epoch == 0:
            plot.plot_tsne(latents=latents_tensor,
                           labels=labels_tensor,
                           epoch=epoch,
                           plot_dir=plot_dir)

            discover_clusters(model=model,
                              mean_latents=mean_latents,
                              epoch=epoch,
                              device=device,
                              plot_dir=plot_dir,
                              n_clusters=20)

        print(f"Epoch: {epoch + 1}/{epochs} - Train loss: {train_loss:.4f} | Test loss: {test_loss:.4f}")

    # Plot the train/test loss curve after looping through all epoches.
    plot.plot_loss_curve(train_losses=train_losses,
                         test_losses=test_losses,
                         plot_dir=plot_dir)

    # Print the needed training Time
    train_end_time = timer()
    print_passed_time(start=train_start_time, end=train_end_time,  device=device, decimal_places=5)


def testing_loop(model: torch.nn.Module,
                 dataloader: torch.utils.data.DataLoader,
                 loss_fn: Callable[[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, float], torch.Tensor],
                 device: torch.device,
                 plot_dir: Path) -> None:
    """
    Evaluates a given model and dataloader on unseen test data.

    :param model: The model to evaluate.
    :param dataloader: The dataloader to evaluate.
    :param loss_fn: the loss function which is used to calculate the loss.
    :param device: the device where the model and tensors are running.
    :param plot_dir: Saving directory for comparison plots.

    :return: Model loss as float value, a list with all mean latents and another list with associated labels.
    """

    print(f"Starting the model testing process... Please wait")
    test_loss = 0
    mean_latents = []
    labels = []

    model.eval()
    with torch.inference_mode():
        for feature, label in dataloader:
            # Put features and labels on the device.
            feature, label = feature.to(device), label.to(device)
            # 1. Forward pass.
            label_prediction, mean, log_variance = model(feature)
            # 2. Calculate the test loss.
            loss = loss_fn(feature, label_prediction, mean, log_variance)
            test_loss += loss.item()

            # Collect means and labels for T-SNE plot.
            mean_latents.append(mean.detach().cpu())
            labels.append(label)

    # Normalize the values to Loss per epoch.
    test_loss = test_loss / len(dataloader.dataset)
    print(f"Test loss: {test_loss:.4f}")

    # Create a plot and compare the original with the reconstructed image.
    plot.plot_original_and_reconstruction(feature=feature,
                                          feature_reconstructed=label_prediction,
                                          plot_dir=plot_dir,
                                          test_loss=test_loss,
                                          image_number=20)


def discover_clusters(model: torch.nn.Module,
                      mean_latents: list,
                      epoch: int,
                      device: torch.device,
                      plot_dir: Path,
                      n_clusters: int) -> None:
    """
     Find clusters in the latent space and reconstruct a centroid image for each cluster.

    :param model: the trained model.
    :param mean_latents: list of mean latents.
    :param epoch: current epoch.
    :param device: The device where the computation takes place on.
    :param plot_dir: Saving path for the cluster reconstruction image.
    :param n_clusters: number of clusters.

    :return: None.
    """

    model.eval()

    # Collect all latents and put them into one list.
    all_latents = torch.cat(mean_latents, dim=0).numpy()

    # 2. K-Means Clustering on the mean vector.
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(all_latents)
    # Center points of each cluster.
    center_points = kmeans.cluster_centers_

    fig, axes = plt.subplots(1, n_clusters, figsize=(n_clusters * 3, 4))
    if n_clusters == 1: axes = [axes]

    with torch.no_grad():
        for i in range(n_clusters):
            center_tensor = torch.tensor(center_points[i], dtype=torch.float32).to(device)
            center_tensor = center_tensor.unsqueeze(0)

            feature_reconstructed = model.decoder(center_tensor)
            image = feature_reconstructed.cpu().squeeze().numpy()

            # Plotten
            ax = axes[i]
            ax.imshow(image, cmap='RdBu_r')
            ax.set_title(f"Cluster {i + 1}\n(n={np.sum(cluster_labels == i)})")
            ax.axis('off')

    plt.tight_layout()
    save_path = plot_dir / f"clusters_{epoch+1}.png"
    plt.savefig(save_path)
    plt.close()