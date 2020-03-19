import numpy as np
import pandas as pd

# nucleosynth
from nucleosynth.config import tables_config
from nucleosynth import network

"""
Functions for extracting data from a raw hdf5 skynet file
"""


# ===============================================================
#              Columns
# ===============================================================
def extract_columns(tracer_file, columns=None):
    """Extract table of columns from a skynet output file

    Returns : pd.DataFrame

    parameters
    ----------
    tracer_file : h5py.File
    columns : [str]
    """
    table = pd.DataFrame()

    if columns is None:
        columns = tables_config.columns

    for column in columns:
        col_low = column.lower()
        table[col_low] = tracer_file[column]

        # rescale if needed
        scale = tables_config.column_scales.get(col_low)
        if scale is not None:
            table[col_low] *= scale

    return table


# ===============================================================
#              Network
# ===============================================================
def extract_network(tracer_file):
    """Extract tracer network of isotopes from skynet output file

    parameters
    ----------
    tracer_file : h5py.File
    """
    tracer_network = pd.DataFrame()
    iso_list = []

    for key in ['Z', 'A']:
        tracer_network[key] = np.array(tracer_file[key], dtype=int)

    for i in range(len(tracer_network)):
        row = tracer_network.loc[i]
        iso_str = network.get_isotope_str(z=row['Z'], a=row['A'])
        iso_list += [iso_str]

    tracer_network['isotope'] = iso_list
    return tracer_network[['isotope', 'Z', 'A']]


# ===============================================================
#              Abundance (Y)
# ===============================================================
def extract_y(tracer_file, tracer_network):
    """Extract table of isotopic abundances (Y) from skynet tracer file

    parameters
    ----------
    tracer_file : h5py.File
    tracer_network : pd.DataFrame
    """
    y_table = pd.DataFrame(tracer_file['Y'])
    y_table.columns = list(tracer_network['isotope'])
    return y_table
