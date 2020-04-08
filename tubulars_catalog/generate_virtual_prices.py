import json

import numpy
from pandas import read_excel, concat, Series
from scipy.optimize import minimize, basinhopping

with open("./scripts/tubulars_catalog/materials-20190214.json", 'r', encoding="latin-1") as f:
    tubulars_catalog = json.load(f)

casing_properties = read_excel('./rep/roque1996.xlsx')

xdata = casing_properties.loc[:, ['OD', 'Collapse', 'Burst', 'Axial']].to_numpy()
ydata = casing_properties.loc[:, ['Price']].to_numpy().reshape((casing_properties.shape[0],))


def linear_function_price(param, X):
    od = X[0]
    burst = X[1]
    collapse = X[2]
    axial = X[3]

    a, b, c, d, bias = param

    return a * od + b * burst + c * collapse + d * axial + bias


def linear_function_price_fit(param, X, price_table):
    od = X[:, 0]
    burst = X[:, 1]
    collapse = X[:, 2]
    axial = X[:, 3]

    a, b, c, d, bias = param

    return numpy.linalg.norm(a*od + b*burst + c*collapse + d*axial + bias - price_table)

param_linear = minimize(linear_function_price_fit, x0=numpy.array([1]*5), args=(xdata, ydata))
print(linear_function_price(param_linear.x, [7, 4980, 4320, 364000]))

calc_price = []
for t in casing_properties.iterrows():
    calc_price.append(linear_function_price(param_linear.x, [t[1]['OD'], t[1]['Burst'], t[1]['Collapse'], t[1]['Axial']]))

casing_properties['Calc Price'] = calc_price
