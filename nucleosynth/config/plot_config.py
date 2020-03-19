ax_scales = {
    'density': 'log',
    'temperature': 'log',
    'heatingrate': 'log',
    'Y': 'log',
    'X': 'log',
    'ye': 'linear',
    'entropy': 'linear',
    'time': 'linear',
    'abar': 'linear',
    'sumy': 'linear',
}

ax_labels = {
    'density': r'$\rho$ (g cm$^{-3}$)',
    'temperature': '$T$ (K)',
    'heatingrate': 'Heating Rate',  # TODO (erg/s?)
    'ye': '$Y_e$',
    'entropy': '$S$',  # TODO (units?)
    'time': 'Time (s)',
    'abar': r'$\bar{A}$',
    'sumy': r'$\Sigma Y$',
    'Y': '$Y$',
    'X': '$X$',
}

ax_lims = {
    'time': [1e-2, 3],
    'density': [1e3, 1e9],
    'temperature': [1e8, 2e10],
    'Y': [1e-12, 1e1],
    'X': [1e-12, 1e1],
}
