import json

# get json file from score web interface
import numpy

from scipy.optimize import minimize
from scorelib.converter import Converter

from parsers.score_project_json import JSONTest, convert_json
from source.score_solver import ScoreSolver

# from source.tubulars_catalog.roque_catalog_to_df import new_casing_catalog

with open("source/score_projects/project476.json", 'r', encoding="latin-1") as f:
    data = json.load(f)

cs_id = 3

instance = JSONTest()
instance.input = convert_json(data)
project = Converter.to_lccv_project(instance)
ss = ScoreSolver(project=project)

for section in ss.project.casing_strings[cs_id].string_sections:
    section.material.young_modulus = 30E6
    section.material.poisson_ratio = 0.28

pressure_test_result = ss.solve_pressure_test(casing_string_id=cs_id)
cementing_result = ss.solve_cementing_load(casing_string_id=cs_id)
lost_returns_result = ss.solve_lost_returns(casing_string_id=cs_id)
gas_kick_result = ss.solve_gas_kick(casing_string_id=cs_id)
influx_result = ss.solve_influx(casing_string_id=cs_id)
well_full_of_gas_result = ss.solve_WellFullOfGas(casing_string_id=cs_id)
cementing_fs = cementing_result.get_api_collapse_safety_factor()
cementing_fs_mises = cementing_result.get_api_von_mises_safety_factor()
lost_returns_fs = lost_returns_result.get_api_collapse_safety_factor()
lost_returns_fs_mises = lost_returns_result.get_api_von_mises_safety_factor()
pressure_test_fs = pressure_test_result.get_api_burst_safety_factor()
pressure_test__fs_mises = pressure_test_result.get_api_von_mises_safety_factor()
gas_kick_fs = gas_kick_result.get_api_burst_safety_factor()
gas_kick_fs_mises = gas_kick_result.get_api_von_mises_safety_factor()
influx_fs = influx_result.get_api_burst_safety_factor()
influx_fs_mises = influx_result.get_api_von_mises_safety_factor()
well_full_of_gas_fs = well_full_of_gas_result.get_api_burst_safety_factor()
well_full_of_gas_fs_mises = well_full_of_gas_result.get_api_von_mises_safety_factor()

burst = 1.1
collapse = 1.0
triaxial = 1.25

# data['well_strings'][cs_id]['string_sections'][0]['pipe']['weight']
# data['well_strings'][cs_id]['string_sections'][0]['pipe']['grade']['name']
# data['well_strings'][cs_id]['string_sections'][0]['pipe']['Price']
# data['well_strings'][cs_id]['string_sections'][0]['pipe']['od']
data['well_strings'][cs_id]['string_sections'][0]['pipe']['wt']
data['well_strings'][cs_id]['string_sections'][0]['pipe']['grade']['fymn']


def objective(parameters):
    wt = parameters[0]
    fy = parameters[1]
    price = -959.6359 + 5278.6361 * wt + 0.01115 * fy
    return price


def fscementing(parameters, data_):
    wt = parameters[0]
    fy = parameters[1]
    data_['well_strings'][cs_id]['string_sections'][0]['pipe']['wt'] = wt
    data_['well_strings'][cs_id]['string_sections'][0]['pipe']['grade']['fymn'] = fy
    instance_ = JSONTest()
    instance_.input = convert_json(data_)
    project = Converter.to_lccv_project(instance_)
    ss = ScoreSolver(project=project)
    for section in ss.project.casing_strings[cs_id].string_sections:
        section.material.young_modulus = 30E6
        section.material.poisson_ratio = 0.28
    cementing_result = ss.solve_cementing_load(casing_string_id=cs_id)
    cementing_fs = cementing_result.get_api_collapse_safety_factor()
    cementing_fs = numpy.array(cementing_fs)

    return cementing_fs[:, 1].min() - collapse


constraintfscementing = {'type': 'ineq', 'fun': fscementing, 'args': (data,)}

bounds = [(0.27, 0.6), (40000, 160000)]
bounds1 = [(0.2, None), (110000, 110000)]

x0 = [1, 15e4]

minsolve = minimize(objective, x0, constraints=(constraintfscementing,), bounds=bounds1, method='SLSQP')
print(minsolve)
