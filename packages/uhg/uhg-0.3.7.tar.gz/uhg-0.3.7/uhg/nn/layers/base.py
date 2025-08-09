import torch
import torch.nn as nn
from typing import Optional, Tuple, Union
from ...projective import ProjectiveUHG

class UHGLayer(nn.Module):
    """Base class for all UHG-compliant neural network layers.
    
    This layer ensures all operations preserve cross-ratios and follow UHG principles.
    Uses float64 precision and regularization for numerical stability.
    """
    def __init__(self):
        super().__init__()
        self.uhg = ProjectiveUHG()
        self.eps = 1e-15  # Smaller epsilon for float64
        
    def _to_double(self, x: torch.Tensor) -> torch.Tensor:
        """Convert input to float64 if needed."""
        return x.double() if x.dtype != torch.float64 else x
        
    def projective_transform(self, x: torch.Tensor, weight: torch.Tensor) -> torch.Tensor:
        """Apply projective transformation preserving cross-ratios.
        
        Uses float64 precision and careful regularization to maintain numerical stability
        and preserve cross-ratios accurately.
        """
        # Convert to float64 for better precision
        x = self._to_double(x)
        weight = self._to_double(weight)
        
        # Build a (D+1)x(D+1) projective matrix with O(2) spatial block and fixed homogeneous coord
        D = x.size(-1) - 1
        M = torch.eye(D + 1, dtype=torch.float64, device=x.device)
        # Ensure weight has correct shape for spatial mapping
        W = weight
        # Build spatial rotation as identity except a 2x2 orthogonal block on the first two coords
        R = torch.eye(D, dtype=torch.float64, device=x.device)
        if W.size(0) >= 2 and W.size(1) >= 2:
            W2 = W[:2, :2]
            C2 = W2.t() @ W2
            e2, V2 = torch.linalg.eigh(C2)
            inv_sqrt2 = V2 @ torch.diag(torch.clamp(e2, min=self.eps).rsqrt()) @ V2.t()
            R2 = W2 @ inv_sqrt2  # 2x2 orthogonal
            R[:2, :2] = R2
        M[:-1, :-1] = R
        M[:-1, -1] = 0.0
        M[-1, :-1] = 0.0
        M[-1, -1] = 1.0
        
        # Apply transform in homogeneous coordinates
        out = x @ M.t()
        
        # Recompute time-like to maintain Minkowski norm -1
        spatial = out[..., :-1]
        time_like = torch.sqrt(torch.clamp(1.0 + torch.sum(spatial * spatial, dim=-1, keepdim=True), min=self.eps))
        return torch.cat([spatial, time_like], dim=-1)
        
    def forward(self, *args, **kwargs):
        raise NotImplementedError("Subclasses must implement forward method")

class ProjectiveLayer(UHGLayer):
    """Layer that operates in projective space while preserving UHG principles.
    
    This layer implements the core projective operations needed by other layers.
    All transformations preserve cross-ratios and hyperbolic structure.
    """
    def __init__(self, in_features: int, out_features: int):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        # Initialize weights in float64
        self.weight = nn.Parameter(torch.empty(out_features, in_features, dtype=torch.float64))
        self.reset_parameters()
        
    def reset_parameters(self):
        """Initialize weights to preserve hyperbolic structure."""
        # Use a smaller gain for better numerical stability
        gain = (2**0.5) * 0.1
        nn.init.kaiming_uniform_(self.weight, a=gain)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Apply projective transformation preserving UHG structure."""
        return self.projective_transform(x, self.weight)