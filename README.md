# nucleosynth
Python modules for nucleosynthesis of core-collapse supernova models.

Currently the purpose is to setup/extract mass tracers for the nucleosynthesis code `skynet`.

# Python Dependencies
* python 3.7
* h5py
* matplotlib
* numpy
* pandas

Use the included `environment.yml` file to easily set up a working [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-with-commands) environment with the above dependencies.

Simply run 

`conda env create -f environment.yml`

which will create a python environment called `nucleosynth`, which you can then activate with 

`conda activate nucleosynth`

While not required, you may also want to install ipython after activating the environment, with

`conda install ipython`

# Setup
Two environment variables need to be set in your shell (e.g. in your `.bashrc`):
* `NUCLEOSYNTH` - path to this repo, e.g. `export NUCLEOSYNTH=${HOME}/codes/nucleosynth`
* `SKYNET_OUTPUT` - path to output data from skynet models, e.g. `export SKYNET_OUTPUT=${HOME}/skynet/output`

To import in python, append the repo location to your python path (again in your `.bashrc`): `export PYTHONPATH=${NUCLEOSYNTH}:${PYTHONPATH}`