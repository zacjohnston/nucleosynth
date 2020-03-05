# nucleosynth
Python modules for nucleosynthesis of core-collapse supernova models.

Currently the purpose is to setup/extract mass tracers for the nucleosynthesis code `skynet`.

# Python Dependencies
* python 3.7
* h5py
* matplotlib
* numpy
* pandas

# Setup
Two environment variables need to be set in your shell (e.g. in your `.bashrc`):
* `NUCLEOSYNTH` - path to this repo, e.g. `export NUCLEOSYNTH=${HOME}/codes/nucleosynth`
* `SKYNET_OUTPUT` - path to output data from skynet models, e.g. `export SKYNET_OUTPUT=${HOME}/skynet/output`
