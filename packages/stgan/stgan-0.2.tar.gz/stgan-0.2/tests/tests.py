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

import pytest
import torch
import os
import torchvision
from stgan.models.difgan.diffusion import Diffusion
from stgan.utils import save_generated_samples, create_parser, augment_tensor


# test for file paths
def test_file_paths(tmp_path):
    output_dir = tmp_path / "training_samples"
    output_dir.mkdir()

    gen_samples = [torch.randn(3, 64, 64) for _ in range(15)]

    save_generated_samples(
        filtered_samples=gen_samples,
        output_dir=str(output_dir),
        outer_loop_iter=2,
    )

    saved_files = list(output_dir.glob("*.csv"))
    assert len(saved_files) == len(
        gen_samples
    ), "Should save all unique samples to input directory"


# test augmentation function
def test_augment_tensor_shape():
    sample_input = torch.randn(4, 3, 64, 64)

    augmented_output = augment_tensor(sample_input)

    assert isinstance(augmented_output, torch.Tensor)
    assert augmented_output.shape == sample_input.shape


# test diffusion q_sample and extraction function
def test_extract_shapes():
    model = Diffusion(timesteps=100, device="cpu")

    batch_size = 4
    x_shape = (batch_size, 3, 64, 64)
    t = torch.randint(0, 100, (batch_size,))
    a = torch.linspace(0.1, 0.9, 100)

    extracted = model._extract(a, t, x_shape)

    assert extracted.shape == (
        batch_size,
        1,
        1,
        1,
    ), "Extracted tensor shape is incorrect"
    assert torch.all(
        (extracted >= 0) & (extracted <= 1)
    ), "Extracted values out of expected range"


def test_q_sample_shapes():
    model = Diffusion(timesteps=100, device="cpu")

    x_start = torch.randn(4, 3, 64, 64)
    t = torch.randint(0, 100, (4,))

    x_noisy, noise = model.q_sample(x_start, t)

    assert x_noisy.shape == x_start.shape, "x_noisy shape mismatch"
    assert noise.shape == x_start.shape, "noise shape mismatch"
    assert torch.isfinite(x_noisy).all(), "x_noisy contains NaNs or Infs"
    assert torch.isfinite(noise).all(), "noise contains NaNs or Infs"


# test argument parsing
def test_parse_args_fails_if_no_args():
    parser = create_parser()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        parsed = parser.parse_args([])
    assert pytest_wrapped_e.type == SystemExit


def test_parse_args_fails_if_one_arg():
    parser = create_parser()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        parsed = parser.parse_args(["in_path"])
    assert pytest_wrapped_e.type == SystemExit


def test_parse_args_succeeds_if_three_args():
    parser = create_parser()
    parsed = parser.parse_args(["difgan", "in_path", "out_path"])
