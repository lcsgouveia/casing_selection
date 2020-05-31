import json

# get json file from score web interface
import numpy
from matplotlib import pyplot

from scipy.optimize import minimize, fsolve
from scorelib.converter import Converter

from parsers.score_project_json import JSONTest, convert_json
from source.score_solver import ScoreSolver

# from source.tubulars_catalog.roque_catalog_to_df import new_casing_catalog

with open("./source/score_projects/"
          "project476.json", 'r', encoding="latin-1") as f:
    data = json.load(f)

cs_id = 3

instance = JSONTest()
instance.input = convert_json(data)
project = Converter.to_lccv_project(instance)

for section in project.casing_strings[cs_id].string_sections:
    section.material.young_modulus = 30E6
    section.material.poisson_ratio = 0.28

ss = ScoreSolver(project=project)
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

    for section in project.casing_strings[cs_id].string_sections:
        section.material.young_modulus = 30E6
        section.material.poisson_ratio = 0.28

    ss = ScoreSolver(project=project)
    cementing_result = ss.solve_cementing_load(casing_string_id=cs_id)
    cementing_fs = cementing_result.get_api_collapse_safety_factor()
    cementing_fs = numpy.array(cementing_fs)

    return cementing_fs[:, 1].min() - collapse


# wts = numpy.linspace(0.1, 0.6)
# fys = numpy.linspace(1e4, 1.5e5, 7)
# for fy in fys:
#     pyplot.plot(wts, [fscementing([wt, fy], data_=data) for wt in wts], label='fy='+str(fy))
# pyplot.legend()
# pyplot.gca().set_xlabel('wt')
# pyplot.gca().set_ylabel('constraint')
#
# pyplot.figure()
# wts = numpy.linspace(0.1, 0.6, 7)
# fys = numpy.linspace(1e4, 1.5e5)
# for wt in wts:
#     pyplot.plot(fys, [fscementing([wt, fy], data_=data) for fy in fys], label='wt='+str(wt))
# pyplot.legend()
# pyplot.gca().set_xlabel('fy')
# pyplot.gca().set_ylabel('constraint')

pyplot.figure()
# price curves. mudar para contour plot.
wts = numpy.linspace(0.1, 0.6)
fys = numpy.linspace(1e4, 1.5e5)
WTS, FYS = numpy.meshgrid(wts, fys)

PRICES = numpy.array(objective([WTS, FYS]))

cost_contour = pyplot.contour(WTS, FYS, PRICES)
pyplot.clabel(cost_contour, inline=1)

wts = numpy.linspace(0.1, 0.6, 100)

fy_of_constraint = numpy.array([fsolve(lambda fy: fscementing([wt, fy[0]], data_=data), x0=numpy.array(1e5))[0] for wt in wts])
constraint = []
for wt, fy in zip(wts, fy_of_constraint):
    constraint.append(fscementing([wt, fy], data_=data))

constraint = numpy.array(constraint)
constraint_ids = numpy.where(abs(constraint) < 1e-2)

pyplot.plot(wts[constraint_ids[0]], fy_of_constraint[constraint_ids[0]], label='fs constraint')

pyplot.legend()
pyplot.gca().set_ylim(0, 150000)
