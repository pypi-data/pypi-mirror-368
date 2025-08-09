<center><h1>stGAN</h1></center>

A Python package to simulate spatial transcriptomic datasets from few training
examples.

## Installation

`stGAN` requires `pytorch` and `torchvision`. Full requirements for building a
`conda` environment are in [`requirements.txt`](requirements.txt).

## Usage

`stGAN` implements several simulation algorithms built on top of generative
adversarial networks: one that implements diffusion layers on top of the
samples, and one that implements more standard augmentations (e.g. rotations,
flips).

### Diffusion GAN

Run with:

```bash
python difgan/train_difgan.py <input_path> <output_path>
```

where `<input_path>` and `<output_path>` are the locations of the input and
output data, respectively. A full list of its arguments is given by `python
difgan/train_difgan.py --help`.

<details>
<summary>Click to reveal full list of arguments</summary>

```
usage: train_difgan.py [-h] [--epochs EPOCHS] [--batch-size BATCH_SIZE]
                       [--lr LR] [--device {cpu,gpu}] [--latent-dim LATENT_DIM]
                       [--in-channels IN_CHANNELS] [--ngf NGF] [--ndf NDF]
                       [--num-gpu NUM_GPU] [--outer-loop-iter OUTER_LOOP_ITER]
                       input_path output_path

positional arguments:
  input_path            path to input data
  output_path           path where output data should be stored

options:
  -h, --help            show this help message and exit
  --epochs EPOCHS       number of epochs
  --batch-size BATCH_SIZE
                        batch size
  --lr LR               learning rate
  --device {cpu,gpu}    device to use
  --latent-dim LATENT_DIM
                        number of latent dimensions input into generator
  --in-channels IN_CHANNELS
                        number of channels (one per gene)
  --ngf NGF             size of feature maps in generator
  --ndf NDF             size of feature maps in discriminator
  --num-gpu NUM_GPU     number of GPUs available
  --outer-loop-iter OUTER_LOOP_ITER
                        number of iterations of outer loop
```

</details>

### Augmented GAN

```bash
python gan/AugmentedGAN.py <input_path> <outer_loop_iteration>
```

where `input_path` is the location of the input data and `outer_loop_iteration`
is an number dictating the names of the output data (output samples are
suffixed with this number to allow them to be passed into the next iteration of
the training process).

## Copyright and Licensing

`stGAN` is copyright 2024-2025 University College London. It has been developed
by Leilani Hoffmann and George Hall and is licensed under the [MIT
license](LICENSE).
