# A collection of plotting functions
__version__: `2.0.2`


This repository collects plotting modules written on top of `matplotlib` or
`seaborn`. 
The functions are intended to set-up a light-touch basic illustration which 
can be customised using the normal matplotlib interface using axes and figures. 


The documentation for plot-misc can be found [here](https://SchmidtAF.gitlab.io/plot-misc/). 


## Installation 
At present, this package is undergoing development and no packages exist yet on PyPI.
Therefore it is recommended that you install in either of the two ways below.

### Installation using conda
I maintain a conda package in my personal conda channel. To install from this please run:

```
conda install afschmidt::plot_misc
```

### Installation using pip

You can install using pip from the root of the cloned repository,
first clone and cd into the repository root:

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

Or for an editable (developer) install run the command below from the root of 
the repository.
The difference with this is that you can just run `git pull` to 
update repository, or switch branches without re-installing:

```sh
python -m pip install -e .

```

## Next steps...
After installation you might wish to try the `pytest` to confirm 
everything is in working order. 

```sh
# From the root of the repository
pytest tests
```

## Usage

Please have a look at the examples in 
[resources](https://gitlab.com/SchmidtAF/plot-misc/-/tree/master/resources/examples)
for some possible recipes. 

