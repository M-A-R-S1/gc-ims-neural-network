import torch
import config
from typing import Callable

def train_model(model: torch.nn.Module,
                dataloader: torch.utils.data.DataLoader,
                loss_fn: Callable[[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, float], torch.Tensor],
                optimizer: torch.optim.Optimizer,
                beta: float,
                device: torch.device) -> dict[str, float]:
    """
    Trains a given model and dataloader and returns the calculated loss.

    :param model: The model to train.
    :param dataloader: The dataloader to train with.
    :param loss_fn: the loss function which is used to calculate the loss.
    :param optimizer: the optimizer function which is used for backpropagation.
    :param beta: Beta value for the loss function.
    :param device: the device where the model and tensors are running.

    :return: Dictionary with total, reconstruction and Kullback–Leibler divergence loss.
    """

    model.train()
    loss = {'total' : 0,
            'recon' : 0,
            'kld' : 0 }

    for feature, label in dataloader:
        # Put image and label on the device.
        feature, label = feature.to(device), label.to(device)

        # 1. Forward pass.
        reconstruction, mean, log_variance = model(feature)
        # 2. Calculate the loss.
        total_loss, recon_loss, kld_loss = loss_fn(feature, reconstruction, mean, log_variance, beta)
        # Divide the loss with the bach size.
        normalized_loss = total_loss / feature.size(0)
        # 3 Clear the gardient.
        optimizer.zero_grad()
        # 4. Backpropagation.
        normalized_loss.backward()
        # 5. Adjust parameters through gradient decent.
        optimizer.step()

        loss['total'] += total_loss.item()
        loss['recon'] += recon_loss.item()
        loss['kld'] += kld_loss.item()

    # Normalize the values to Loss per epoch.
    loss['total'] = loss['total'] / len(dataloader.dataset)
    loss['recon'] = loss['recon'] / len(dataloader.dataset)
    loss['kld'] = loss['kld'] / len(dataloader.dataset)

    return loss


def eval_model(model: torch.nn.Module,
               dataloader: torch.utils.data.DataLoader,
               loss_fn: Callable[[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, float], torch.Tensor],
               device: torch.device,
               beta: float) -> tuple[dict[str, float], list, list]:
    """
    Evaluates a given model and dataloader by calculating the loss.

    :param model: The model to evaluate.
    :param dataloader: The dataloader to evaluate.
    :param loss_fn: the loss function which is used to calculate the loss.
    :param device: the device where the model and tensors are running.
    :param beta: Beta value for the loss function.

    :return: Model loss as float value, a list with all mean latents and another list with associated labels.
    """

    loss = {'total' : 0,
            'recon' : 0,
            'kld' : 0 }

    mean_latents = []
    labels = []

    model.eval()
    with torch.inference_mode():
        for feature, label in dataloader:
            # Put features and labels on the device.
            feature, label = feature.to(device), label.to(device)
            # 1. Forward pass.
            reconstruction, mean, log_variance = model(feature)
            # 2. Calculate the test loss.
            total_loss, recon_loss, kld_loss = loss_fn(feature, reconstruction, mean, log_variance, beta)

            loss['total'] += total_loss.item()
            loss['recon'] += recon_loss.item()
            loss['kld'] += kld_loss.item()

            # Collect means and labels for T-SNE plot.
            mean_latents.append(mean.detach().cpu())
            labels.append(label)

    # Normalize the values to Loss per epoch.
    loss['total'] = loss['total'] / len(dataloader.dataset)
    loss['recon'] = loss['recon'] / len(dataloader.dataset)
    loss['kld'] = loss['kld'] / len(dataloader.dataset)

    return loss, mean_latents, labels


def training_loop(model: torch.nn.Module,
                  train_dataloader: torch.utils.data.DataLoader,
                  test_dataloader: torch.utils.data.DataLoader,
                  loss_fn: Callable[[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, float], tuple[torch.Tensor, torch.Tensor, torch.Tensor]],
                  optimizer: torch.optim.Optimizer,
                  device: torch.device,
                  epochs: int) -> None:
    """
    Loops through the given number of epochs and performs training and evaluation steps on the given model and data.

    :param model: the model which should be trained.
    :param train_dataloader: The training dataloader.
    :param test_dataloader: The testing dataloader.
    :param loss_fn: The loss function
    :param optimizer: The used optimizer.
    :param device: The device where the computation takes place on.
    :param epochs: The number of training epochs.

    :return: None.
    """

    # Dictionary with lists in which all training and test losses are saved.
    loss_dict = {'train_total': [],
                 'train_recon': [],
                 'train_kld': [],
                 'test_total' : [],
                 'test_recon': [],
                 'test_kld': [] }

    beta_warmup = config.BETA_WARMUP
    target_beta = config.TARGET_BETA

    # walk through all epochs.
    for epoch in range(epochs):

        # Calculate the current beta value [Beta annealing].
        if epoch < beta_warmup:
            current_beta =  target_beta * (epoch / beta_warmup)
        else:
            current_beta = target_beta

        # Train the model
        train_loss = train_model(model=model,
                                 dataloader=train_dataloader,
                                 loss_fn=loss_fn,
                                 optimizer=optimizer,
                                 beta=current_beta,
                                 device=device)

        # Evaluates the model
        test_loss, mean_latents, labels = eval_model(model=model,
                                                     dataloader=test_dataloader,
                                                     loss_fn=loss_fn,
                                                     device=device,
                                                     beta=current_beta)

        # Add the losses to lists and save them for later.
        loss_dict['train_total'].append(train_loss['total'])
        loss_dict['train_recon'].append(train_loss['recon'])
        loss_dict['train_kld'].append(train_loss['kld'])
        loss_dict['test_total'].append(test_loss['total'])
        loss_dict['test_recon'].append(test_loss['recon'])
        loss_dict['test_kld'].append(test_loss['kld'])


def testing_loop(model: torch.nn.Module,
                 dataloader: torch.utils.data.DataLoader,
                 loss_fn: Callable[[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, float], tuple[torch.Tensor, torch.Tensor, torch.Tensor]],
                 device: torch.device) -> None:
    """
    Evaluates a given model and dataloader on unseen test data.

    :param model: The model to evaluate.
    :param dataloader: The dataloader to evaluate.
    :param loss_fn: the loss function which is used to calculate the loss.
    :param device: the device where the model and tensors are running.

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
            loss, _, _ = loss_fn(feature, label_prediction, mean, log_variance, config.TARGET_BETA)
            test_loss += loss.item()

            # Collect means and labels for T-SNE plot.
            mean_latents.append(mean.detach().cpu())
            labels.append(label)