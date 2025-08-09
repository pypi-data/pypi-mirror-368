# Copyright (c) 2024-2025 University College London
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import torch
import torch.nn.functional as F


class Diffusion:
    def __init__(self, timesteps=300, device="cpu"):
        self.timesteps = timesteps
        self.device = device

        # Linear beta schedule
        self.betas = torch.linspace(0.0001, 0.02, timesteps).to(device)

        # Precomputed terms
        self.alphas = 1.0 - self.betas
        self.alphas_cumprod = torch.cumprod(
            self.alphas, dim=0
        )  # running cum sum at each timestep
        self.alphas_cumprod_prev = F.pad(
            self.alphas_cumprod[:-1], (1, 0), value=1.0
        )  # removes last term and adds 1.00 as the first term

        self.sqrt_alphas_cumprod = torch.sqrt(
            self.alphas_cumprod
        )  # takes square root of all values
        self.sqrt_one_minus_alphas_cumprod = torch.sqrt(
            1.0 - self.alphas_cumprod
        )  # takes square root of (one minus values)

        self.sqrt_recip_alphas = torch.sqrt(
            1.0 / self.alphas
        )  # takes square root of 1/alphas
        self.posterior_variance = (
            self.betas * (1.0 - self.alphas_cumprod_prev) / (1.0 - self.alphas_cumprod)
        )

    def q_sample(self, x_start, t):
        """
        Add noise to x_start at timestep t using the forward diffusion equation.
        Returns the noisy version and the noise used.
        """
        noise = torch.randn_like(x_start)

        sqrt_alphas_cumprod_t = self._extract(
            self.sqrt_alphas_cumprod, t, x_start.shape
        )
        sqrt_one_minus_alphas_cumprod_t = self._extract(
            self.sqrt_one_minus_alphas_cumprod, t, x_start.shape
        )

        """batch_size, num_channels, _, _ = x_start.shape
        sqrt_alphas_cumprod_t = self.sqrt_alphas_cumprod[t].view(batch_size, num_channels, 1, 1)
        sqrt_one_minus_alphas_cumprod_t = self.sqrt_one_minus_alphas_cumprod[t].view(batch_size, num_channels, 1, 1)"""

        # x_start and noise have 100 channels but supposed to be 10
        x_noisy = (
            sqrt_alphas_cumprod_t * x_start + sqrt_one_minus_alphas_cumprod_t * noise
        )
        return x_noisy, noise

    def _extract(self, a, t, x_shape):
        """
        Extracts values from a based on timestep t and reshapes to match x_shape.
        """
        batch_size = t.shape[0]
        out = a.gather(0, t.cpu())
        out_reshape = out.reshape(batch_size, *((1,) * (len(x_shape) - 1))).to(
            self.device
        )

        return out_reshape
