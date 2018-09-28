import numpy as np
import pandas as pd
from scipy.integrate import dblquad


def prepare_planet_data():
    """Returns a pandas DataFrame."""
    # The number of planets shown will be three less than Kepler's total planet count
    # due to 2014A&A...570A.130S
    df = pd.read_hdf('/home/gb/dev/kepler-dashboard/data/nexsci-composite-planet-table.h5',
                     'planets')
    mask_kepler = (df['pl_facility'] == 'Kepler') | (df['pl_facility'] == 'K2')
    keplerdf = df[mask_kepler][['fpl_name', 'fpl_rade', 'fpl_orbper']].copy()

    # Add planet size categories
    keplerdf.loc[:, 'category'] = 'Earth-size'
    keplerdf.loc[(df['fpl_rade'] >= 1.25) & (df['fpl_rade'] < 2.0), 'category'] = 'Super-Earth-size'
    keplerdf.loc[(df['fpl_rade'] >= 2.0) & (df['fpl_rade'] < 6.0), 'category'] = 'Neptune-size'
    keplerdf.loc[(df['fpl_rade'] >= 6.0), 'category'] = 'Jupiter-size'

    # We sort the values to sort the legend
    keplerdf.sort_values(by='fpl_rade', ascending=False, inplace=True)
    return keplerdf


def planets_per_star(logperiod, logradius, radius_break=3.4, gamma=(0.38, 0.73),
                     alpha=(-0.19, -1.18), beta=(0.26, 0.59)):
    """Returns dN^2(R, P) / dlnR dlnP

    Sources
    -------
    https://exoplanets.nasa.gov/system/internal_resources/details/original/680_SAG13_closeout_8.3.17.pdf
    https://vanderbei.princeton.edu/SAG13/SAG13.html
    """
    radius, period = np.exp(logradius), np.exp(logperiod)
    if radius < radius_break:
        idx = 0
    else:
        idx = 1
    return gamma[idx] * (radius**alpha[idx]) * (period**beta[idx])


def occurence_rate(rmin=0.5, rmax=1.5, pmin=237, pmax=860):
    """Returns the average number of planets per star within a range of radii/periods."""
    intgrl = dblquad(planets_per_star,
                     np.log(rmin), np.log(rmax),
                     lambda x: np.log(pmin/365.), lambda x: np.log(pmax/365.))
    return intgrl[0]
