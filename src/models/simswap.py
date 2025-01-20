import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List, Tuple

class ResBlock(nn.Module):
    def __init__(self, in_channels: int):
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(in_channels, in_channels, 3, 1, 1),
            nn.InstanceNorm2d(in_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels, in_channels, 3, 1, 1),
            nn.InstanceNorm2d(in_channels)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x + self.block(x)

class Encoder(nn.Module):
    def __init__(self, in_channels: int = 3, latent_dim: int = 512, n_layers: int = 3):
        super().__init__()
        
        # Initial Convolution
        layers = [
            nn.Conv2d(in_channels, 64, 7, 1, 3),
            nn.InstanceNorm2d(64),
            nn.ReLU(inplace=True)
        ]
        
        # Downsampling
        in_features = 64
        for _ in range(n_layers):
            out_features = min(in_features * 2, 512)
            layers.extend([
                nn.Conv2d(in_features, out_features, 4, 2, 1),
                nn.InstanceNorm2d(out_features),
                nn.ReLU(inplace=True)
            ])
            in_features = out_features
            
        # Residual Blocks
        for _ in range(3):
            layers.append(ResBlock(out_features))
            
        # Projection to latent space
        self.shared = nn.Sequential(*layers)
        self.mu = nn.Conv2d(out_features, latent_dim, 1, 1, 0)
        self.logvar = nn.Conv2d(out_features, latent_dim, 1, 1, 0)
        
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        features = self.shared(x)
        mu = self.mu(features)
        logvar = self.logvar(features)
        return mu, logvar

class Generator(nn.Module):
    def __init__(self, latent_dim: int = 512, out_channels: int = 3):
        super().__init__()
        
        # Initial processing
        self.fc = nn.Linear(latent_dim, 4 * 4 * 512)
        
        # Upsampling blocks
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(512, 512, 4, 2, 1),
            nn.InstanceNorm2d(512),
            nn.ReLU(inplace=True),
            
            nn.ConvTranspose2d(512, 256, 4, 2, 1),
            nn.InstanceNorm2d(256),
            nn.ReLU(inplace=True),
            
            nn.ConvTranspose2d(256, 128, 4, 2, 1),
            nn.InstanceNorm2d(128),
            nn.ReLU(inplace=True),
            
            nn.ConvTranspose2d(128, 64, 4, 2, 1),
            nn.InstanceNorm2d(64),
            nn.ReLU(inplace=True),
            
            nn.Conv2d(64, out_channels, 7, 1, 3),
            nn.Tanh()
        )
        
    def forward(self, z: torch.Tensor) -> torch.Tensor:
        x = self.fc(z).view(-1, 512, 4, 4)
        return self.decoder(x)

class SimSwap(nn.Module):
    def __init__(self, config: dict = None):
        super().__init__()
        self.config = config or {}
        
        # Komponenten
        self.encoder = Encoder(
            latent_dim=self.config.get('latent_dim', 512),
            n_layers=self.config.get('n_layers', 3)
        )
        self.generator = Generator(
            latent_dim=self.config.get('latent_dim', 512)
        )
        
    def encode(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        return self.encoder(x)
        
    def decode(self, z: torch.Tensor) -> torch.Tensor:
        return self.generator(z)
        
    def reparameterize(self, mu: torch.Tensor, logvar: torch.Tensor) -> torch.Tensor:
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std
        
    def forward(self, source: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        # Encode both images
        source_mu, source_logvar = self.encode(source)
        target_mu, target_logvar = self.encode(target)
        
        # Mix latent codes
        z = self.reparameterize(source_mu, source_logvar)
        
        # Generate swapped image
        return self.decode(z) 