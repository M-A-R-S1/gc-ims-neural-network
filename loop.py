import torch
import plot
from timeit import default_timer as timer
from pathlib import Path
from typing import Callable

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
                optimizer: torch.optim,
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
        # 3 Clear the gardient.
        optimizer.zero_grad()
        # 4. Backpropagation.
        loss.backward()
        # 5. Adjust parameters through gradient decent.
        optimizer.step()

        train_loss += loss.item()

    # Normalize the values to Loss per epoch.
    train_loss = train_loss / len(dataloader.dataset)

    return train_loss


def eval_model(model: torch.nn.Module,
               dataloader: torch.utils.data.dataloader,
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
        plot.plot_feature_and_reconstruction(feature=feature,
                                             label_prediction=label_prediction,
                                             epoch=current_epoch,
                                             plot_dir=plot_dir,
                                             image_number=20)

    return test_loss, mean_latents, labels


def start_loop(model: torch.nn.Module,
               train_dataloader: torch.utils.data.DataLoader,
               test_dataloader: torch.utils.data.DataLoader,
               loss_fn: Callable[[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, float], torch.Tensor],
               optimizer: torch.optim,
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
    plot_interval = 50

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

        # Concatenate latents and labels for the epoch
        latents_tensor = torch.cat(mean_latents)
        labels_tensor = torch.cat(labels)

        # Every X epochs create a T-SNE plot.
        if (epoch + 1) % plot_interval == 0 or epoch == 0:
            plot.plot_tsne(latents=latents_tensor,
                           labels=labels_tensor,
                           epoch=epoch,
                           plot_dir=plot_dir)

        print(f"Epoch: {epoch + 1}/{epochs}")
        print(f"- Train loss: {train_loss:.4f} | Test loss: {test_loss:.4f}")
        print("################################################")

    # Print the needed training Time
    train_end_time = timer()
    print_passed_time(start=train_start_time, end=train_end_time,  device=device, decimal_places=5)
