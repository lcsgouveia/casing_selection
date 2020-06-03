import json

# get json file from score web interface
import numpy

from scipy.optimize import minimize, least_squares
from scorelib.converter import Converter

from parsers.score_project_json import JSONTest, convert_json
from score_solver import ScoreSolver

cs_id = 3
burst = 1.1
collapse = 1.0
triaxial = 1.25

with open("source/score_projects/project476.json", 'r', encoding="latin-1") as f:
    data = json.load(f)

instance = JSONTest()
instance.input = convert_json(data)
project = Converter.to_lccv_project(instance)


def fscementing(parameters, project, casing_string_id):
    wt = parameters[0]
    fy = parameters[1]
    ss = ScoreSolver(project=project)
    for section in ss.project.casing_strings[casing_string_id].string_sections:
        section.wt = wt
        section.material.minimum_yield_strength = fy

        section.material.young_modulus = 30E6
        section.material.poisson_ratio = 0.28
    cementing_result = ss.solve_cementing_load(casing_string_id=cs_id)
    cementing_fs = cementing_result.get_api_collapse_safety_factor()
    cementing_fs = numpy.array(cementing_fs)

    return cementing_fs[:, 1].min() - collapse





def linear_constraint_diff_to_score_solver(line_parameters, wt, fy, fs_constraint):
    return sum((line_parameters[0] * wt + line_parameters[1] * fy + line_parameters[2] - fs_constraint))


def quadratic_constraint_diff_to_score_solver(line_parameters, wt, fy, fs_constraint):
    return sum(line_parameters[0] * wt ** 2 + line_parameters[1] * fy ** 2 + line_parameters[2] * wt * fy +
               line_parameters[3] * wt + line_parameters[4] * fy +
               line_parameters[5] -
               fs_constraint)


od = 7
od_catalog = new_casing_catalog.loc[new_casing_catalog['OD'] == od, :]
wt_data = od_catalog['wt']
fy_data = od_catalog['fy']
cost_data = od_catalog['Price']

linear_parameters = least_squares(linear_cost_diff_to_catalog, x0=(5280, 0.011, -960), args=(wt_data, fy_data, cost_data))
quadratic_parameters = least_squares(quadratic_cost_diff_to_catalog, x0=(0, 0, 0, 5280, 0.011, -960), args=(wt_data, fy_data, cost_data))

for wt, fy, cost in zip(wt_data, fy_data, cost_data):
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

