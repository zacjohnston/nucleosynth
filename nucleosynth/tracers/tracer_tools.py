import numpy as np

"""
General tools for tracer data
"""


def get_total_heating(table):
    """Calculate total heating from 'columns' table
        by integrating heatingrate over time.

    parameters
    ----------
    table : pd.DataFrame
        table containing tracer columns of 'time' and 'heatingrate'
    """
    total_heating = np.trapz(y=table['heatingrate'], x=table['time'])
    return total_heating
