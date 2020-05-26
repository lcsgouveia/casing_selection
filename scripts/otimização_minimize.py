import json
from math import inf
from random import randrange

import numpy
from numpy import full

from scipy.optimize import minimize
# get json file from score web interface

from numpy import dot, transpose
from scorelib.converter import Converter



from parsers.score_project_json import JSONTest, convert_json
from source.score_solver import ScoreSolver
from source.tubulars_catalog.roque_catalog_to_df import new_casing_catalog

from scorelib.design.casing_design import MinimumAllowableSafetyFactorsBuilder

with open("C:/Users/laris/Desktop/DOUGLAS/LCCV/casing_selection-master-Douglas/source/score_projects/"
          "project476.json", 'r', encoding="latin-1") as f:
    data = json.load(f)

instance = JSONTest()
instance.input = convert_json(data)
project = Converter.to_lccv_project(instance)

# acesso aos resultados de FS e Pf para o revestimento produtor cs_id=3
cs_id = 3
ss = ScoreSolver(project=project)
pressure_test_result = ss.solve_pressure_test(casing_string_id=cs_id)
cementing_result = ss.solve_cementing_load(casing_string_id=cs_id)
lost_returns_result = ss.solve_lost_returns(casing_string_id=cs_id)
gas_kick_result = ss.solve_gas_kick(casing_string_id=cs_id)
# full_evacuation_result = ss.solve_full_evacuation(casing_string_id=cs_id)
# partial_evacuation_result = ss.solve_partial_evacuation(casing_string_id=cs_id)
# wcd_collapse_result = ss.solve_wcd_collapse(casing_string_id=cs_id)
influx_result = ss.solve_influx(casing_string_id=cs_id)
well_full_of_gas_result = ss.solve_WellFullOfGas(casing_string_id=cs_id)
cementing_fs = cementing_result.get_api_collapse_safety_factor()
lost_returns_fs = lost_returns_result.get_api_collapse_safety_factor()
pressure_test_fs = pressure_test_result.get_api_burst_safety_factor()
gas_kick_fs = gas_kick_result.get_api_burst_safety_factor()
influx_fs = influx_result.get_api_burst_safety_factor()
well_full_of_gas_fs = well_full_of_gas_result.get_api_burst_safety_factor()
# cementing_fs_burst = cementing_result.get_api_burst_safety_factor()


# Cementing Case
fs_original_cementing = []
depths_cementing = []
for fs_result in cementing_fs:
    depths_cementing.append(fs_result[0])
    fs_original_cementing.append(fs_result[1])

# Lost Returns Case
fs_original_lostReturn = []
depths_lostReturn = []
for fs_result in lost_returns_fs:
    depths_lostReturn.append(fs_result[0])
    fs_original_lostReturn.append(fs_result[1])

# Pressure Test Case
fs_original_PressureTest = []
depths_PressureTest = []
for fs_result in pressure_test_fs:
    depths_PressureTest.append(fs_result[0])
    fs_original_PressureTest.append(fs_result[1])

# Working on production string (id=3), we want to change the current tubular of the project to the first one in the dataframe
burst = 1.1
collapse = 1.0
triaxial = 1.25
'''
for new_cs in range(44):
    data['well_strings'][cs_id]['string_sections'][0]['pipe']['weight'] = new_casing_catalog.loc[new_cs, 'Weight']
    data['well_strings'][cs_id]['string_sections'][0]['pipe']['wt'] = new_casing_catalog.loc[new_cs, 'wt']
    data['well_strings'][cs_id]['string_sections'][0]['pipe']['grade']['name'] = new_casing_catalog.loc[new_cs, 'Grade']
    data['well_strings'][cs_id]['string_sections'][0]['pipe']['grade']['fymn'] = new_casing_catalog.loc[new_cs, 'fy']
    data['well_strings'][cs_id]['string_sections'][0]['pipe']['Price'] = new_casing_catalog.loc[new_cs, 'Price']
    data['well_strings'][cs_id]['string_sections'][0]['pipe']['od'] = new_casing_catalog.loc[new_cs, 'OD']

#other parameters must be also changed to work with ULS
    instance.input = convert_json(data)
    project = Converter.to_lccv_project(instance)
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
    #    well_full_of_gas_fs_axial = well_full_of_gas_result.get_api_axial_safety_factor()

#Verificação dos fatores de segurança
    tamanho = len(depths_cementing)
    passou = True
    for i in range(tamanho - 3):
        cementing_collapso = cementing_fs[i][1]
        # Cenários de Collapso
        if cementing_fs[i][1] < collapse or lost_returns_fs[i][1] < collapse:
            passou = False
            break
        # Cenários de Burst
        if pressure_test_fs[i][1] < burst or gas_kick_fs[i][1] < burst or influx_fs[i][1] < burst or \
                well_full_of_gas_fs[i][1] < burst:
            passou = False
            break
        # Cenário triaxial
        if cementing_fs_mises[i][1] < triaxial or lost_returns_fs_mises[i][1] < triaxial or \
                pressure_test__fs_mises[i][1] < triaxial or gas_kick_fs_mises[i][1] < triaxial or \
                influx_fs_mises[i][1] < triaxial or well_full_of_gas_fs_mises[i][1] < triaxial:
            passou = False
            break
    if passou:
        print('Tubo ótimo escolhido')
        print('od:', data['well_strings'][cs_id]['string_sections'][0]['pipe']['od'])
        print('Weight:', data['well_strings'][cs_id]['string_sections'][0]['pipe']['weight'])
        print('wt:', data['well_strings'][cs_id]['string_sections'][0]['pipe']['wt'])
        print('grade:', data['well_strings'][cs_id]['string_sections'][0]['pipe']['grade']['name'])
        print('Price:', data['well_strings'][cs_id]['string_sections'][0]['pipe']['Price'])
        break
'''
instance.input = convert_json(data)
project = Converter.to_lccv_project(instance)
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

# Minimize Implementation
#data['well_strings'][cs_id]['string_sections'][0]['pipe']['weight'] = new_casing_catalog.loc[0, 'Weight']
#data['well_strings'][cs_id]['string_sections'][0]['pipe']['wt'] = new_casing_catalog.loc[0, 'wt']
#data['well_strings'][cs_id]['string_sections'][0]['pipe']['grade']['name'] = new_casing_catalog.loc[0, 'Grade']
#data['well_strings'][cs_id]['string_sections'][0]['pipe']['grade']['fymn'] = new_casing_catalog.loc[0, 'fy']
#data['well_strings'][cs_id]['string_sections'][0]['pipe']['Price'] = new_casing_catalog.loc[0, 'Price']
#data['well_strings'][cs_id]['string_sections'][0]['pipe']['od'] = new_casing_catalog.loc[0, 'OD']

'''
def objective(tubeInMenu):
    data['well_strings'][cs_id]['string_sections'][0]['pipe']['weight']
    data['well_strings'][cs_id]['string_sections'][0]['pipe']['wt']
    data['well_strings'][cs_id]['string_sections'][0]['pipe']['grade']['name']
    data['well_strings'][cs_id]['string_sections'][0]['pipe']['grade']['fymn']
    data['well_strings'][cs_id]['string_sections'][0]['pipe']['Price']
    data['well_strings'][cs_id]['string_sections'][0]['pipe']['od']
    return tubeInMenu.dot(transpose(new_casing_catalog['Price']))


def fsCementingConstraint(fsCementing):
    minValue = inf
    fsCementing = cementing_fs
    for i in range(len(fsCementing)):
        if fsCementing[i][1] < minValue:
            minValue = fsCementing[i][1]
    return minValue - collapse

def fsLostReturnsConstraint(fsLostReturns):
    minValue = inf
    fsLostReturns = lost_returns_fs
    for i in range(len(fsLostReturns)):
        if fsLostReturns[i][1] < minValue:
            minValue = fsLostReturns[i][1]
    return minValue - collapse

def fsPressureTestConstraint(fsPressureTest):
    minValue = inf
    fsPressureTest = pressure_test_fs
    for i in range(len(fsPressureTest)):
        if fsPressureTest[i][1] < minValue:
            minValue = fsPressureTest[i][1]
    return minValue - burst

def fsGasKickConstraint(fsGasKick):
    minValue = inf
    fsGasKick = gas_kick_fs
    for i in range(len(fsGasKick)):
        if fsGasKick[i][1] < minValue:
            minValue = fsGasKick[i][1]
    return minValue - burst

def fsInfluxConstraint(fsInflux):
    minValue = inf
    fsInflux = influx_fs
    for i in range(len(fsInflux)):
        if fsInflux[i][1] < minValue:
            minValue = fsInflux[i][1]
    return minValue - burst

def fsWellFullOfGasConstraint(fsWellFullOfGas):
    minValue = inf
    fsWellFullOfGas = well_full_of_gas_fs
    for i in range(len(fsWellFullOfGas)):
        if fsWellFullOfGas[i][1] < minValue:
            minValue = fsWellFullOfGas[i][1]
    return minValue - burst

def fsCementingMisesConstraint(fsCementingMises):
    minValue = inf
    fsCementingMises = cementing_fs_mises
    for i in range(len(fsCementingMises)):
        if fsCementingMises[i][1] < minValue:
            minValue = fsCementingMises[i][1]
    return minValue - triaxial

def fsLostReturnMisesConstraint(fsLostReturnMises):
    minValue = inf
    fsLostReturnMises = lost_returns_fs_mises
    for i in range(len(fsLostReturnMises)):
        if fsLostReturnMises[i][1] < minValue:
            minValue = fsLostReturnMises[i][1]
    return minValue - triaxial

def fsPressureTestMisesConstraint(fsPressureTestMises):
    minValue = inf
    fsPressureTestMises = pressure_test__fs_mises
    for i in range(len(fsPressureTestMises)):
        if fsPressureTestMises[i][1] < minValue:
            minValue = fsPressureTestMises[i][1]
    return minValue - triaxial

def fsGasKickMisesConstraint(fsGasKickMises):
    minValue = inf
    fsGasKickMises = gas_kick_fs_mises
    for i in range(len(fsGasKickMises)):
        if fsGasKickMises[i][1] < minValue:
            minValue = fsGasKickMises[i][1]
    return minValue - triaxial

def fsInfluxMisesConstraint(fsInfluxMises):
    minValue = inf
    fsInfluxMises = influx_fs_mises
    for i in range(len(fsInfluxMises)):
        if fsInfluxMises[i][1] < minValue:
            minValue = fsInfluxMises[i][1]
    return minValue - triaxial

def fsWellFullOfGasMisesConstraint(fsWellFullOfGasMises):
    minValue = inf
    fsWellFullOfGasMises = well_full_of_gas_fs_mises
    for i in range(len(fsWellFullOfGasMises)):
        if fsWellFullOfGasMises[i][1] < minValue:
            minValue = fsWellFullOfGasMises[i][1]
    return minValue - triaxial

def justOneTubeConstraint(tubeInMenu):
    tube = 0
    for t in tubeInMenu:
        tube += t
    return tube - 1

x0 = zeros(len(new_casing_catalog))

bounds = full((len(new_casing_catalog), 2), (0, 1))

const1 = {'type': 'ineq', 'fun': fsCementingConstraint}
const2 = {'type': 'ineq', 'fun': fsLostReturnsConstraint}
const3 = {'type': 'ineq', 'fun': fsPressureTestConstraint}
const4 = {'type': 'ineq', 'fun': fsGasKickConstraint}
const5 = {'type': 'ineq', 'fun': fsInfluxConstraint}
const6 = {'type': 'ineq', 'fun': fsWellFullOfGasConstraint}
const7 = {'type': 'ineq', 'fun': fsCementingMisesConstraint}
const8 = {'type': 'ineq', 'fun': fsPressureTestMisesConstraint}
const9 = {'type': 'ineq', 'fun': fsLostReturnMisesConstraint}
const10 = {'type': 'ineq', 'fun': fsGasKickMisesConstraint}
const11 = {'type': 'ineq', 'fun': fsInfluxMisesConstraint}
const12 = {'type': 'ineq', 'fun': fsWellFullOfGasMisesConstraint}
const13 = {'type': 'ineq', 'fun': justOneTubeConstraint}

constraints = [const1, const2, const3, const4, const5, const6,
               const7, const8, const9, const10, const11, const12, const13]

minimizeSolution = minimize(objective, x0, bounds, method='SLSQP', constraints=constraints)
'''
def objective(tube):
    price = tube.dot(transpose(new_casing_catalog['Price']))
    return price
#tube = array([1, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0])

def constraint1(tube):
    return len(numpy.where(tube > 0)[0]) - 1

def fscementing(tube):
    data['well_strings'][cs_id]['string_sections'][0]['pipe']['wt'] = new_casing_catalog.loc[numpy.where(tube > 0)[0][0], 'wt'] * tube[numpy.where(tube > 0)[0][0]]
    instance.input = convert_json(data)
    project = Converter.to_lccv_project(instance)
    ss = ScoreSolver(project=project)
    cementing_result = ss.solve_cementing_load(casing_string_id=cs_id)
    cementing_fs = cementing_result.get_api_collapse_safety_factor()
    cementing_fs = numpy.array(cementing_fs)
    return cementing_fs[:, 1].min() - collapse

cementing_fs_min = []

for i in range(len(new_casing_catalog)):
    data['well_strings'][cs_id]['string_sections'][0]['pipe']['wt'] = new_casing_catalog.loc[i, 'wt']
    instance.input = convert_json(data)
    project = Converter.to_lccv_project(instance)
    ss = ScoreSolver(project=project)
    cementing_result = ss.solve_cementing_load(casing_string_id=cs_id)
    cementing_fs = cementing_result.get_api_collapse_safety_factor()
    cementing_fs = numpy.array(cementing_fs)
    cementing_fs_min.append(cementing_fs[:, 1].min())

cons2 = {'type': 'ineq', 'fun': lambda tube: tube.dot(transpose(cementing_fs_min)) - collapse}

x0 = numpy.zeros(45)
x0[0] = 1

const1 = {'type': 'eq', 'fun': constraint1}
const2 = {'type': 'ineq', 'fun': fscementing}
bounds = full((45, 2), (0, 1))
sol = minimize(objective, x0, method='SLSQP', constraints=[const1, cons2], bounds=bounds)

print(sol)