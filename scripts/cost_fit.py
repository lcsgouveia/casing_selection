import numpy
from scipy.optimize import least_squares
from source.tubulars_catalog.roque_catalog_to_df import new_casing_catalog


def linear_cost_diff_to_catalog(line_parameters, wt_data, fy_data, cost_data):
    return sum((line_parameters[0] * wt_data + line_parameters[1] * fy_data + line_parameters[2] - cost_data))


def quadratic_cost_diff_to_catalog(line_parameters, wt_data, fy_data, cost_data):
    return sum(line_parameters[0] * wt_data ** 2 + line_parameters[1] * fy_data ** 2 + line_parameters[2] * wt_data * fy_data +
               line_parameters[3] * wt_data + line_parameters[4] * fy_data +
               line_parameters[5] -
               cost_data)


od = 7
od_catalog = new_casing_catalog.loc[new_casing_catalog['OD'] == od, :]
od_wt_data = od_catalog['wt']
od_fy_data = od_catalog['fy']
od_cost_data = od_catalog['Price']

linear_parameters = least_squares(linear_cost_diff_to_catalog, x0=(5280, 0.011, -960), args=(od_wt_data, od_fy_data, od_cost_data))
quadratic_parameters = least_squares(quadratic_cost_diff_to_catalog, x0=(0, 0, 0, 5280, 0.011, -960), args=(od_wt_data, od_fy_data, od_cost_data))

for wt, fy, cost in zip(od_wt_data, od_fy_data, od_cost_data):
    print('linear', (linear_cost_diff_to_catalog(linear_parameters.x,
                                                 numpy.array([wt]),
                                                 numpy.array([fy]),
                                                 numpy.array([0]))),
          'error: ', (linear_cost_diff_to_catalog(linear_parameters.x,
                                                  numpy.array([wt]),
                                                  numpy.array([fy]),
                                                  numpy.array([cost]))),
          'quadratic', (quadratic_cost_diff_to_catalog(quadratic_parameters.x,
                                                       numpy.array([wt]),
                                                       numpy.array([fy]),
                                                       numpy.array([0]))),
          'error: ', (quadratic_cost_diff_to_catalog(quadratic_parameters.x,
                                                     numpy.array([wt]),
                                                     numpy.array([fy]),
                                                     numpy.array([cost])))
          )

