from sympy.stats.frv_types import numpy


def cost_from_catalog(parameters, catalog):
    wt = parameters[0]
    fy = parameters[1]
    wt_catalog = catalog.loc[catalog['wt'] >= wt, :]
    wt_fy_catalog = wt_catalog.loc[wt_catalog['fy'] >= fy, :]
    if len(wt_fy_catalog) > 0:
        price = wt_fy_catalog.iloc[0, -1]
    else:
        price = numpy.inf
    return price


def cost_linear_fitted(parameters):
    wt = parameters[0]
    fy = parameters[1]
    price = -959.6359 + 5278.6361 * wt + 0.01115 * fy
    return price

