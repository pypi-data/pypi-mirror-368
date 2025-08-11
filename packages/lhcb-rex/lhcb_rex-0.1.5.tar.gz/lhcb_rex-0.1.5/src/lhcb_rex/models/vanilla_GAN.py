import lhcb_rex.settings.globals as myGlobals

import torch
import torch.nn as nn
from torch import Tensor
import pytorch_lightning as pl


def _weights_init(m):
    """Custom weight initialization."""
    if isinstance(m, nn.Linear):
        # Xavier initialization
        nn.init.xavier_normal_(m.weight)
        if m.bias is not None:
            nn.init.constant_(m.bias, 0.0)
    elif isinstance(m, nn.BatchNorm1d):
        # BatchNorm weights should be initialized to 1 and biases to 0
        nn.init.constant_(m.weight, 1.0)
        nn.init.constant_(m.bias, 0.0)


class Discriminator(nn.Module):
    def __init__(self, targets_dims, conditions_dims, hidden_channels, latent_dims):
        super(Discriminator, self).__init__()

        if not isinstance(hidden_channels, list):
            hidden_channels = [hidden_channels, hidden_channels, hidden_channels]

        self.fc1 = nn.Linear(targets_dims + conditions_dims, hidden_channels[0])
        self.fc2 = nn.Linear(hidden_channels[0], hidden_channels[1])
        self.fc3 = nn.Linear(hidden_channels[1], hidden_channels[2])

        self.final_layer = nn.Linear(hidden_channels[2], 1)

        # Batch normalization layers
        self.bn1 = nn.BatchNorm1d(hidden_channels[0])
        self.bn2 = nn.BatchNorm1d(hidden_channels[1])
        self.bn3 = nn.BatchNorm1d(hidden_channels[2])

        self.dropout = nn.Dropout(0.2)

        self.apply(_weights_init)

    def forward(self, targets, conditions):
        x = torch.cat([targets, conditions], dim=1)

        # First hidden layer
        x = self.fc1(x)
        x = torch.nn.functional.leaky_relu(x)  # Activation function
        # x = self.bn1(x)  # Batch normalization
        # x = self.dropout(x)  # Dropout

        # Second hidden layer
        x = self.fc2(x)
        # x = self.bn2(x)  # Batch normalization
        x = torch.nn.functional.leaky_relu(x)  # Activation function
        # x = self.dropout(x)  # Dropout

        # Third hidden layer
        x = self.fc3(x)
        # x = self.bn3(x)  # Batch normalization
        x = torch.nn.functional.leaky_relu(x)  # Activation function
        # x = self.dropout(x)  # Dropout

        # Latent variables (mean and log variance for the VAE)
        disc = torch.sigmoid(self.final_layer(x))  # Mean of the latent space

        return disc


class Generator(pl.LightningModule):
    def __init__(self, targets_dims, conditions_dims, hidden_channels, latent_dims):
        super(Generator, self).__init__()

        if not isinstance(hidden_channels, list):
            hidden_channels = [hidden_channels, hidden_channels, hidden_channels]

        self.fc1 = nn.Linear(latent_dims + conditions_dims, hidden_channels[0])
        self.fc2 = nn.Linear(hidden_channels[0], hidden_channels[1])
        self.fc3 = nn.Linear(hidden_channels[1], hidden_channels[2])

        self.final_layer = nn.Linear(hidden_channels[2], targets_dims)

        # Batch normalization layers
        self.bn1 = nn.BatchNorm1d(hidden_channels[0])
        self.bn2 = nn.BatchNorm1d(hidden_channels[1])
        self.bn3 = nn.BatchNorm1d(hidden_channels[2])

        self.dropout = nn.Dropout(0.2)

        self.apply(_weights_init)

    # def forward(self, latent, conditions):
    def forward(
        self,
        latent: Tensor,
        conditions: Tensor,
    ) -> Tensor:
        x = torch.cat([latent, conditions], dim=1)

        # First hidden layer
        x = self.fc1(x)
        x = torch.nn.functional.leaky_relu(x)  # Activation function
        x = self.bn1(x)  # Batch normalization
        # x = self.dropout(x)  # Dropout

        # Second hidden layer
        x = self.fc2(x)
        x = torch.nn.functional.leaky_relu(x)  # Activation function
        x = self.bn2(x)  # Batch normalization
        # x = self.dropout(x)  # Dropout

        # Third hidden layer
        x = self.fc3(x)
        x = torch.nn.functional.leaky_relu(x)  # Activation function
        x = self.bn3(x)  # Batch normalization
        # x = self.dropout(x)  # Dropout

        # Latent variables (mean and log variance for the VAE)
        targets = torch.tanh(self.final_layer(x))  # Mean of the latent space

        return targets


class vanillaGAN(nn.Module):
    def __init__(
        self, targets_dims, conditions_dims, hidden_channels, latent_dims, silent=False
    ):
        super(vanillaGAN, self).__init__()

        if not silent:
            print("\n")
            print("Network params (vanillaGAN) -----------------")
            print("targets_dims:", targets_dims)
            print("conditions_dims:", conditions_dims)
            print("hidden_channels:", hidden_channels)
            print("latent_dims:", latent_dims)
            print("\n")

        self.latent_dims = latent_dims

        self.discriminator = Discriminator(
            targets_dims, conditions_dims, hidden_channels, latent_dims
        )

        self.generator = Generator(
            targets_dims, conditions_dims, hidden_channels, latent_dims
        )

    def inference(self, batch_size, conditions):
        # Sample latent variables for both graph and node using reparameterization trick
        z = torch.randn((batch_size, self.latent_dims)).to(myGlobals.device)
        conditions = conditions.to(myGlobals.device)
        self.generator = self.generator.to(myGlobals.device)

        # Decode the latent representation
        reconstructed = self.generator(z, conditions)

        return reconstructed
