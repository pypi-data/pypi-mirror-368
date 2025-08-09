import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List, Optional, Union
from ..layers.sage import ProjectiveSAGEConv
from ...projective import ProjectiveUHG

class ProjectiveGraphSAGE(nn.Module):
    """UHG-compliant GraphSAGE model for graph learning.
    
    This model implements GraphSAGE using pure projective geometry,
    following UHG principles without any manifold concepts.
    
    Args:
        in_channels: Size of input features
        hidden_channels: Size of hidden features
        out_channels: Size of output features
        num_layers: Number of GraphSAGE layers
        dropout: Dropout probability
        bias: Whether to use bias
    """
    def __init__(
        self,
        in_channels: int,
        hidden_channels: int,
        out_channels: int,
        num_layers: int = 2,
        dropout: float = 0.0,
        bias: bool = True
    ):
        super().__init__()
        self.uhg = ProjectiveUHG()
        self.num_layers = num_layers
        self.dropout = dropout
        
        # Create list to hold all layers
        self.layers = nn.ModuleList()
        
        # Input layer
        self.layers.append(
            ProjectiveSAGEConv(
                in_features=in_channels,
                out_features=hidden_channels,
                bias=bias
            )
        )
        
        # Hidden layers
        for _ in range(num_layers - 2):
            self.layers.append(
                ProjectiveSAGEConv(
                    in_features=hidden_channels,
                    out_features=hidden_channels,
                    bias=bias
                )
            )
            
        # Output layer
        self.layers.append(
            ProjectiveSAGEConv(
                in_features=hidden_channels,
                out_features=out_channels,
                bias=bias
            )
        )
        
    def projective_dropout(self, x: torch.Tensor, p: float) -> torch.Tensor:
        """Apply dropout while preserving projective structure."""
        if not self.training or p == 0:
            return x
            
        # Create dropout mask for spatial (feature) part
        spatial = x[..., :-1]
        time_like = x[..., -1:]
        mask = torch.bernoulli(torch.full_like(spatial, 1 - p))
        spatial_dropped = spatial * mask
        
        # Recompute time-like to ensure Minkowski norm -1
        new_time = torch.sqrt(torch.clamp(1.0 + torch.sum(spatial_dropped * spatial_dropped, dim=-1, keepdim=True), min=1e-8))
        out = torch.cat([spatial_dropped, new_time], dim=-1)
        return out
        
    def forward(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
        edge_weight: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """Forward pass of projective GraphSAGE.
        
        Args:
            x: Node feature matrix
            edge_index: Graph connectivity
            edge_weight: Optional edge weights
            
        Returns:
            Node embeddings
        """
        # Add homogeneous coordinate to input
        x = torch.cat([x, torch.ones_like(x[..., :1])], dim=-1)
        
        # Forward pass through all layers
        for i, layer in enumerate(self.layers):
            # Apply layer
            x = layer(x, edge_index)
            
            # If not last layer, re-append homogeneous and nonlinearity
            if i < len(self.layers) - 1:
                x = torch.cat([x, torch.ones_like(x[..., :1])], dim=-1)
                
                # Apply projective ReLU
                x_features = x[..., :-1]
                x_features = F.relu(x_features)
                x = torch.cat([x_features, x[..., -1:]], dim=-1)
                
                # Normalize to maintain projective structure
                norm = torch.norm(x, p=2, dim=-1, keepdim=True)
                x = x / (norm + 1e-8)
                
                # Apply projective dropout
                x = self.projective_dropout(x, self.dropout)
        
        # For the last layer, x is [N, out_channels]; return as logits
        return x