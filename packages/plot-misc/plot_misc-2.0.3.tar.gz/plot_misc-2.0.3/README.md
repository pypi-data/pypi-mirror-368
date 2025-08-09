# A collection of plotting functions
__version__: `2.0.3`

This repository collects plotting modules written on top of `matplotlib`.
The functions are intended to set up light-touch, basic illustrations that
can be customised using the standard matplotlib interface via axes and figures.
Functionality is included to create illustrations commonly used in medical research,
covering forest plots, volcano plots, incidence matrices/bubble charts,
illustrations to evaluate prediction models (e.g. feature importance, net benefit, calibration plots),
and more.

The documentation for plot-misc can be found [here](https://SchmidtAF.gitlab.io/plot-misc/). 

## Installation 
The package is available on PyPI, and conda, with the latest source code 
available on gitlab. 

### Installation using PyPI

To install the package from PyPI, run:

```sh
pip install plot-misc
```

This installs the latest stable release along with its dependencies.

### Installation using conda

A Conda package is maintained in my personal Conda channel.
To install from this channel, run:


```sh
conda install afschmidt::plot_misc
```

### Installation using gitlab

If you require the latest updates, potentially not yet formally released, you can install the package directly from GitLab.

First, clone the repository and move into its root directory:

```sh
git clone git@gitlab.com:SchmidtAF/plot-misc.git
cd plot-misc
```

Install the dependencies:

```sh
# From the root of the repository
conda env create --file ./resources/conda/envs/conda_create.yaml
```

To add to an existing environment use:

```sh
# From the root of the repository
conda env update --file ./resources/conda/envs/conda_update.yaml
```

Next the package can be installed: 

```sh
python -m pip install .
```

Or for an editable (developer) install run the command below from the 
root of the repository.
The difference with this is that you can just run `git pull` to 
update repository, or switch branches without re-installing:

```sh
python -m pip install -e .

```

#### Validating the package

After installing the package from GitLab, you may wish to run the test
suite to confirm everything is working as expected:

```sh
# From the root of the repository
pytest tests
```

## Usage

Please have a look at the examples in 
[resources](https://gitlab.com/SchmidtAF/plot-misc/-/tree/master/resources/examples)
for some possible recipes. 

