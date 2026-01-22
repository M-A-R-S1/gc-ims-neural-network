import torch
from torch import nn

def reparameterize(mean: torch.Tensor, log_variance: torch.Tensor) -> torch.Tensor:
    standard_deviation = torch.exp(0.5 * log_variance)
    random_multiplicator = torch.randn_like(standard_deviation)
    return mean + random_multiplicator * standard_deviation

def vae_loss(feature, feature_constructed, mean, log_variance, beta=1.5):
    recon = nn.functional.mse_loss(feature_constructed, feature, reduction='sum')
    #recon = nn.functional.binary_cross_entropy(feature_constructed, feature, reduction='sum')
    kld = -0.5 * torch.sum(1 + log_variance - mean.pow(2) - log_variance.exp())
    return recon + beta * kld

class VariationalAutoencoderV1(nn.Module):
    def __init__(self, input_layers: int, hidden_layers: int, latent_dimension: int) -> None:
        super().__init__()

        # Set Convolution layer hyperparameters.
        self.kernel = 3
        self.stride = 2
        self.padding = 1

        self.encoder = nn.Sequential(
            # First Conv-Block
            nn.Conv2d(in_channels=input_layers, out_channels=hidden_layers, kernel_size=self.kernel, stride=self.stride, padding=self.padding),
            nn.LeakyReLU(0.2),
            nn.Conv2d(in_channels=hidden_layers, out_channels=hidden_layers, kernel_size=1),
            nn.LeakyReLU(0.2),
            nn.BatchNorm2d(hidden_layers),

            # Second Conv-Block
            nn.Conv2d(in_channels=hidden_layers, out_channels=2*hidden_layers, kernel_size=self.kernel, stride=self.stride, padding=self.padding),
            nn.LeakyReLU(0.2),
            nn.Conv2d(in_channels=2*hidden_layers, out_channels=2*hidden_layers, kernel_size=1),
            nn.LeakyReLU(0.2),
            nn.BatchNorm2d(2*hidden_layers),

            nn.Flatten()
        )

        self.flatten_dimension = 2*hidden_layers * 8 * 8
        self.latent_mean = nn.Linear(self.flatten_dimension, latent_dimension)
        self.latent_log_variance = nn.Linear(self.flatten_dimension, latent_dimension)

        self.decoder = nn.Sequential(
            nn.Linear(latent_dimension, self.flatten_dimension),
            nn.Unflatten(1, (2*hidden_layers, 8, 8)),

            # Reverse of second Conv-Block
            nn.Conv2d(in_channels=2*hidden_layers, out_channels=2*hidden_layers, kernel_size=1),
            nn.LeakyReLU(0.2),
            nn.ConvTranspose2d(in_channels=2*hidden_layers, out_channels=hidden_layers, kernel_size=self.kernel, stride=self.stride, padding=self.padding),
            nn.LeakyReLU(0.2),

            # Reverse of the first Conv-Block
            nn.Conv2d(in_channels=hidden_layers, out_channels=hidden_layers, kernel_size=1),
            nn.LeakyReLU(0.2),
            nn.ConvTranspose2d(in_channels=hidden_layers, out_channels=input_layers, kernel_size=self.kernel, stride=self.stride, padding=self.padding),
            nn.Sigmoid()
        )

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        bottleneck_layer = self.encoder(x)

        mean = self.latent_mean(bottleneck_layer)
        log_variance = self.latent_log_variance(bottleneck_layer)

        x = reparameterize(mean, log_variance)
        return self.decoder(x), mean, log_variance



class VariationalAutoencoderV2(nn.Module):
    def __init__(self, hidden_layers: int, latent_dimension: int) -> None:
        super().__init__()

        self.flatten_dimension = 29 * 29

        self.encoder = nn.Sequential(
            nn.Flatten(),
            nn.Linear(in_features=self.flatten_dimension, out_features=hidden_layers),
            nn.LeakyReLU(0.2),
            nn.Linear(in_features=hidden_layers, out_features=hidden_layers),
            nn.LeakyReLU(0.2),
            nn.Linear(in_features=hidden_layers, out_features=hidden_layers),
            nn.LeakyReLU(0.2),
            nn.Linear(in_features=hidden_layers, out_features=16),
            nn.LeakyReLU(0.2)
        )

        self.latent_mean = nn.Linear(16, latent_dimension)
        self.latent_log_variance = nn.Linear(16, latent_dimension)

        self.decoder = nn.Sequential(
            nn.Linear(in_features=latent_dimension, out_features=16),
            nn.LeakyReLU(0.2),
            nn.Linear(in_features=16, out_features=hidden_layers),
            nn.LeakyReLU(0.2),
            nn.Linear(in_features=hidden_layers, out_features=hidden_layers),
            nn.LeakyReLU(0.2),
            nn.Linear(in_features=hidden_layers, out_features=hidden_layers),
            nn.LeakyReLU(0.2),
            nn.Linear(in_features=hidden_layers, out_features=self.flatten_dimension),
            nn.Unflatten(1, (1,29,29))
        )

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        bottleneck_layer = self.encoder(x)

        mean = self.latent_mean(bottleneck_layer)
        log_variance = self.latent_log_variance(bottleneck_layer)

        x = reparameterize(mean, log_variance)
        return self.decoder(x), mean, log_variance
