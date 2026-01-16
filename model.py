import torch
from torch import nn

def reparameterize(mean: torch.Tensor, log_variance: torch.Tensor) -> torch.Tensor:
    standard_deviation = torch.exp(0.5 * log_variance)
    random_multiplicator = torch.randn_like(standard_deviation)
    return mean + random_multiplicator * standard_deviation


class VariationalAutoencoderV1(nn.Module):
    def __init__(self, input_layers: int, hidden_layers: int, latent_dimension: int) -> None:
        super().__init__()

        # Set Convolution layer hyperparameters.
        self.kernel = 3
        self.stride = 1
        self.padding = 1
        self.pooling_kernel = 2

        # Calculate the flatten layer dimension.
        self.flatten_height = 11
        self.flatten_width = 11
        self.flatten_dimension = self.flatten_height * self.flatten_width * hidden_layers

        # TinyVGG model inspired CNN encoder.
        self.encoder = nn.Sequential(
            # First Conv-Block
            nn.Conv2d(in_channels=input_layers, out_channels=hidden_layers, kernel_size=self.kernel, stride=self.stride, padding=self.padding),
            nn.ReLU(),
            nn.Conv2d(in_channels=hidden_layers, out_channels=hidden_layers, kernel_size=self.kernel, stride=self.stride, padding=self.padding),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=self.pooling_kernel),

            # Second Conv-Block
            nn.Conv2d(in_channels=hidden_layers, out_channels=hidden_layers, kernel_size=self.kernel, stride=self.stride, padding=self.padding),
            nn.ReLU(),
            nn.Conv2d(in_channels=hidden_layers, out_channels=hidden_layers, kernel_size=self.kernel, stride=self.stride, padding=self.padding),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=self.pooling_kernel),

            nn.Flatten()
        )

        self.latent_mean = nn.Linear(self.flatten_dimension, latent_dimension)
        self.latent_log_variance = nn.Linear(self.flatten_dimension, latent_dimension)

        # TinyVGG model inspired CNN decoder.
        self.decoder = nn.Sequential(
            nn.Linear(latent_dimension, self.flatten_dimension),
            nn.Unflatten(1, (hidden_layers, self.flatten_height, self.flatten_width)),

            # Reverse of second Conv-Block
            nn.ConvTranspose2d(in_channels=hidden_layers, out_channels=hidden_layers, kernel_size=2, stride=2),
            nn.ReLU(),
            nn.ConvTranspose2d(in_channels=hidden_layers, out_channels=hidden_layers, kernel_size=self.kernel, stride=self.stride, padding=self.padding),
            nn.ReLU(),
            nn.ConvTranspose2d(in_channels=hidden_layers, out_channels=hidden_layers, kernel_size=self.kernel, stride=self.stride, padding=self.padding),
            nn.ReLU(),

            # Reverse of the first Conv-Block
            nn.ConvTranspose2d(in_channels=hidden_layers, out_channels=hidden_layers, kernel_size=2, stride=2),
            nn.ReLU(),
            nn.ConvTranspose2d(in_channels=hidden_layers, out_channels=hidden_layers, kernel_size=self.kernel, stride=self.stride, padding=self.padding),
            nn.ReLU(),
            nn.ConvTranspose2d(in_channels=hidden_layers, out_channels=input_layers, kernel_size=self.kernel, stride=self.stride, padding=self.padding),
            nn.Sigmoid()
        )

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        bottleneck_layer = self.encoder(x)

        mean = self.latent_mean(bottleneck_layer)
        log_variance = self.latent_log_variance(bottleneck_layer)

        x = reparameterize(mean, log_variance)
        return self.decoder(x), mean, log_variance
