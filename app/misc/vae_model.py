import torch
from torch import nn
from pathlib import Path

def reparameterize(mean: torch.Tensor,
                   log_variance: torch.Tensor) -> torch.Tensor:
    """
    This function uses the mean and the logarithmic variance to calculate a distinct latent space representation.
    The logarithmic variance is transformed to the standard deviation which is then fitted to a gaussian normal
    distribution. This yields a "randomly" picked standard deviation which is finally added to the mean and returned as
    a distinct latent space representation.

    :param mean: torch tensor with the mean of the latent space.
    :param log_variance: torch tensor with the logarithmic variance of the latent space.

    :return: torch tensor with a "randomly" picked latent space vector.
    """

    standard_deviation = torch.exp(0.5 * log_variance)
    random_multiplicator = torch.randn_like(standard_deviation)
    return mean + random_multiplicator * standard_deviation


def vae_loss(feature: torch.Tensor,
             feature_constructed: torch.Tensor,
             mean: torch.Tensor,
             log_variance: torch.Tensor,
             beta: float) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    This function calculates the loss for given feature, feature reconstruction and the latent space mean and
    logarithmic variance. The "Kullback–Leibler divergence" (kld) is used to determine how the latent space variables
    are distributed. The loss is determined by the "correctness" of the reconstruction and the Kullback–Leibler
    divergence multiplied with the beta multiplicator. A high beta multiplicator is in favor of a cleaner latent
    space organization, while a lower beta multiplicator is in favor of a better reconstruction.

    :param feature: torch Tensor with the original feature.
    :param feature_constructed: torch Tensor with the constructed feature.
    :param mean: torch Tensor with the mean latent space.
    :param log_variance: torch Tensor with the logarithmic variance of the latent space.
    :param beta: Return multiplicator which helps to shift the loss towards a better latent space representation
    (beta > 1.0) or a more accurate reconstruction (beta < 1.0).

    :return: torch tensor with the calculated loss.
    """

    recon = nn.functional.binary_cross_entropy(feature_constructed, feature, reduction='sum')
    kld = -0.5 * torch.sum(1 + log_variance - mean.pow(2) - log_variance.exp())
    return recon + beta * kld, recon, kld


class VariationalAutoencoderCNN(nn.Module):
    def __init__(self, input_layers: int, hidden_layers: int, latent_dimension: int) -> None:
        super().__init__()

        # Set Convolution layer hyperparameters.
        self.kernel = 3
        self.stride = 1
        self.padding = 1
        self.pooling_kernel = 2

        self.encoder = nn.Sequential(
            # First Conv-Block
            nn.Conv2d(in_channels=input_layers, out_channels=2*hidden_layers, kernel_size=self.kernel, stride=self.stride, padding=self.padding),
            nn.LeakyReLU(0.1),
            nn.Conv2d(in_channels=2*hidden_layers, out_channels=2*hidden_layers, kernel_size=self.kernel, stride=self.stride, padding=self.padding),
            nn.LeakyReLU(0.1),
            nn.BatchNorm2d(2*hidden_layers),
            nn.MaxPool2d(kernel_size=self.pooling_kernel),

            # Second Conv-Block
            nn.Conv2d(in_channels=2*hidden_layers, out_channels=hidden_layers, kernel_size=self.kernel, stride=self.stride, padding=self.padding),
            nn.LeakyReLU(0.1),
            nn.Conv2d(in_channels=hidden_layers, out_channels=hidden_layers, kernel_size=self.kernel, stride=self.stride, padding=self.padding),
            nn.LeakyReLU(0.1),
            nn.BatchNorm2d(hidden_layers),
            nn.MaxPool2d(kernel_size=self.pooling_kernel),

            nn.Flatten()
        )

        self.flatten_dimension = hidden_layers * 5 * 5
        self.latent_mean = nn.Linear(self.flatten_dimension, latent_dimension)
        self.latent_log_variance = nn.Linear(self.flatten_dimension, latent_dimension)

        self.decoder = nn.Sequential(
            nn.Linear(latent_dimension, self.flatten_dimension),
            nn.Unflatten(1, (hidden_layers, 5, 5)),

            # Reverse of second Conv-Block
            nn.Upsample(scale_factor=2, mode='nearest'),
            nn.Conv2d(in_channels=hidden_layers, out_channels=hidden_layers, kernel_size=self.kernel, stride=self.stride, padding=self.padding),
            nn.LeakyReLU(0.1),
            nn.Conv2d(in_channels=hidden_layers, out_channels=2*hidden_layers, kernel_size=self.kernel, stride=self.stride, padding=self.padding),
            nn.LeakyReLU(0.1),

            # Reverse of the first Conv-Block
            nn.Upsample(size=(21, 21), mode='nearest'),
            nn.Conv2d(in_channels=2*hidden_layers, out_channels=2*hidden_layers, kernel_size=self.kernel, stride=self.stride, padding=self.padding),
            nn.LeakyReLU(0.1),
            nn.Conv2d(in_channels=2*hidden_layers, out_channels=input_layers, kernel_size=self.kernel, stride=self.stride, padding=self.padding),
            nn.Sigmoid()
        )

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        bottleneck_layer = self.encoder(x)

        mean = self.latent_mean(bottleneck_layer)
        log_variance = self.latent_log_variance(bottleneck_layer)

        x = reparameterize(mean, log_variance)
        return self.decoder(x), mean, log_variance


    def save_model(self, model_dir: Path, file_name: str) -> None:
        """
        Save the state dict of this model to a specified directory and filename.

        :param model_dir: the relative path where the models are saved.
        :param file_name: the name of the saved model

        :return: None.
        """

        # Create the directory if not already there.
        model_path = Path(model_dir)
        model_path.mkdir(parents=True, exist_ok=True)

        # Creat the relative path to the file.
        model_save_path = model_path / file_name

        # Save the state dict of this model.
        torch.save(obj=self.state_dict(), f=model_save_path)


    def load_model(self, model_dir: Path, file_name: str, device: torch.device) -> None:
        """
        Load the state dict of this model from the specified directory and filename

        :param model_dir: the relative path where the models are saved.
        :param file_name: the name of the saved model
        :param device: The device on which the tensors are used [cpu or cuda].

        :return: None.
        """

        # Create the directory if not already there.
        model_path = Path(model_dir)
        model_path.mkdir(parents=True, exist_ok=True)

        # Creat the relative path to the file.
        model_load_path = model_path / file_name

        # Load the model if it exists.
        if model_load_path.exists():
            self.load_state_dict(torch.load(f=model_load_path, map_location=device))


class ClassificationModel(nn.Module):
    def __init__(self, input_layer: int = 32, hidden_layer: int = 64, output_layer: int = 10):
        super(ClassificationModel, self).__init__()

        self.multilayer = nn.Sequential(
            # First layer.
            nn.Linear(input_layer, hidden_layer),
            nn.ReLU(),
            nn.Dropout(0.2),
            # Second layer.
            nn.Linear(hidden_layer, hidden_layer),
            nn.ReLU(),
            nn.Dropout(0.2),
            # Third layer.
            nn.Linear(hidden_layer, hidden_layer // 2),
            nn.ReLU(),
            nn.Dropout(0.2),
            # Output layer.
            nn.Linear(hidden_layer // 2, output_layer)
        )


    def forward(self, x):
        result = self.multilayer(x)
        return result

    def save_model(self, model_dir: str, file_name: str) -> None:
        """
        Save the state dict of this model to a specified directory and filename.

        :param model_dir: the relative path where the models are saved.
        :param file_name: the name of the saved model
        :return: None.
        """

        # Create the directory if not already there.
        model_path = Path(model_dir)
        model_path.mkdir(parents=True, exist_ok=True)

        # Creat the relative path to the file.
        model_save_path = model_path / file_name

        # Save the state dict of this model.
        torch.save(obj=self.state_dict(), f=model_save_path)
        print(f"Model saved at {model_save_path}")


    def load_model(self, model_dir: str, file_name: str) -> None:
        """
        Load the state dict of this model from the specified directory and filename

        :param model_dir: the relative path where the models are saved.
        :param file_name: the name of the saved model
        :return: None.
        """

        # Create the directory if not already there.
        model_path = Path(model_dir)
        model_path.mkdir(parents=True, exist_ok=True)

        # Creat the relative path to the file.
        model_load_path = model_path / file_name

        # Load the model if it exists.
        if model_load_path.exists():
            self.load_state_dict(torch.load(f=model_load_path))