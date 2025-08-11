import lhcb_rex.settings.globals as myGlobals

import torch
import torch.nn as nn
from torch import Tensor
import pytorch_lightning as pl
from diffusers import DDPMScheduler


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


class TimeEmbedding(nn.Module):
    def __init__(self, embedding_dim):
        super().__init__()
        self.embedding_dim = embedding_dim
        self.linear1 = nn.Linear(1, embedding_dim)
        self.act = nn.SiLU()
        self.linear2 = nn.Linear(embedding_dim, embedding_dim)

    def forward(self, t):
        # t is shape [batch_size], scale to float and unsqueeze
        t = t.unsqueeze(-1).float()
        emb = self.linear1(t)
        emb = self.act(emb)
        emb = self.linear2(emb)
        return emb


class Diffuser(pl.LightningModule):
    def __init__(self, targets_dims, conditions_dims, hidden_channels, latent_dims):
        super(Diffuser, self).__init__()

        self.time_embedding_dim = 5
        self.time_embed = TimeEmbedding(self.time_embedding_dim)

        if not isinstance(hidden_channels, list):
            hidden_channels = [hidden_channels, hidden_channels, hidden_channels]

        self.fc1 = nn.Linear(
            targets_dims + latent_dims + conditions_dims + self.time_embedding_dim,
            hidden_channels[0],
        )
        self.fc2 = nn.Linear(hidden_channels[0], hidden_channels[1])
        self.fc3 = nn.Linear(hidden_channels[1], hidden_channels[2])

        self.final_layer = nn.Linear(hidden_channels[2], targets_dims)

        # Batch normalization layers
        self.bn1 = nn.BatchNorm1d(hidden_channels[0])
        self.bn2 = nn.BatchNorm1d(hidden_channels[1])
        self.bn3 = nn.BatchNorm1d(hidden_channels[2])

        self.dropout = nn.Dropout(0.2)

    # def forward(self, latent, conditions):
    def forward(
        self,
        batch,
        conditions,
        timesteps,
    ) -> Tensor:
        timestep_embedding = self.time_embed(timesteps)

        x = torch.cat([batch, conditions, timestep_embedding], dim=1)

        # First hidden layer
        x = self.fc1(x)
        x = torch.nn.functional.leaky_relu(x)  # Activation function
        x = self.bn1(x)  # Batch normalization
        x = self.dropout(x)  # Dropout

        # Second hidden layer
        x = self.fc2(x)
        x = torch.nn.functional.leaky_relu(x)  # Activation function
        x = self.bn2(x)  # Batch normalization
        x = self.dropout(x)  # Dropout

        # Third hidden layer
        x = self.fc3(x)
        x = torch.nn.functional.leaky_relu(x)  # Activation function
        x = self.bn3(x)  # Batch normalization
        x = self.dropout(x)  # Dropout

        targets = self.final_layer(x)

        return targets


class vanillaDiffusion(nn.Module):
    def __init__(
        self, targets_dims, conditions_dims, hidden_channels, latent_dims, silent=False
    ):
        super(vanillaDiffusion, self).__init__()

        if not silent:
            print("\n")
            print("Network params (vanillaDiffusion) -----------------")
            print("targets_dims:", targets_dims)
            print("conditions_dims:", conditions_dims)
            print("hidden_channels:", hidden_channels)
            print("latent_dims:", latent_dims)
            print("\n")

        self.latent_dims = latent_dims

        # self.noise_scheduler = DDPMScheduler(num_train_timesteps=model.gan.steps, clip_sample=True, clip_sample_range=5.5, beta_schedule="squaredcos_cap_v2")
        self.noise_scheduler = DDPMScheduler(
            num_train_timesteps=25, beta_schedule="squaredcos_cap_v2"
        )

        self.targets_dims = targets_dims
        self.diffuser = Diffuser(
            targets_dims, conditions_dims, hidden_channels, latent_dims
        )

    def sample_starting_noise(self, shape, device):
        """
        I think this might have to be random normal 0,1
        """
        return torch.randn(shape, device=device)

    def inference(self, test_batch_size, batch: torch.Tensor) -> torch.Tensor:
        device = batch.device
        current_state = self.sample_starting_noise(
            (batch.shape[0], self.targets_dims), device=device
        )
        latent = torch.randn((batch.shape[0], self.latent_dims), device=device)
        conditions = batch

        for t in reversed(range(self.noise_scheduler.config.num_train_timesteps)):
            timesteps = torch.full(
                (batch.shape[0],), t, device=device, dtype=torch.long
            )

            batch_i = torch.cat((current_state, latent), dim=1)
            noise_pred = self.diffuser(
                batch=batch_i,
                conditions=conditions,
                timesteps=timesteps,
            )

            current_state = self.noise_scheduler.step(
                model_output=noise_pred, timestep=t, sample=current_state
            ).prev_sample

        return current_state
