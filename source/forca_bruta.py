import json

# get json file from score web interface
from matplotlib import pyplot
from scorelib.converter import Converter
from scorelib.models.string_section import StringSectionBuilder, StringSection

from parsers.score_project_json import JSONTest, convert_json
from scripts.score_solver import ScoreSolver
from scripts.tubulars_catalog.roque_catalog_to_df import new_casing_catalog

with open("C:/casing_selection-master/scripts/score_projects/project476.json", 'r', encoding="latin-1") as f:
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
#full_evacuation_result = ss.solve_full_evacuation(casing_string_id=cs_id)
#partial_evacuation_result = ss.solve_partial_evacuation(casing_string_id=cs_id)
#wcd_collapse_result = ss.solve_wcd_collapse(casing_string_id=cs_id)
influx_result = ss.solve_influx(casing_string_id=cs_id)
well_full_of_gas_result = ss.solve_WellFullOfGas(casing_string_id=cs_id)
cementing_fs = cementing_result.get_api_collapse_safety_factor()
lost_returns_fs = lost_returns_result.get_api_collapse_safety_factor()
pressure_test_fs = pressure_test_result.get_api_burst_safety_factor()
gas_kick_fs = gas_kick_result.get_api_burst_safety_factor()
influx_fs = influx_result.get_api_burst_safety_factor()
well_full_of_gas_fs = well_full_of_gas_result.get_api_burst_safety_factor()




#cementing_fs_burst = cementing_result.get_api_burst_safety_factor()
#Caso de cimentação
fs_original = []
depths = []
for fs_result in cementing_fs:
    depths.append(fs_result[0])
    fs_original.append(fs_result[1])

pyplot.plot(fs_original, depths, label='original tubular, $fs_{min}$=%.2f' %(min(fs_original)))
#Caso de perda de circulação
fs_original = []
depths = []
for fs_result in lost_returns_fs:
    depths.append(fs_result[0])
    fs_original.append(fs_result[1])

pyplot.plot(fs_original, depths, label='original tubular_lost_returns, $fs_{min}$=%.2f' %(min(fs_original)))
#caso de  teste de pressão
fs_original = []
depths = []
for fs_result in pressure_test_fs:
    depths.append(fs_result[0])
    fs_original.append(fs_result[1])

pyplot.plot(fs_original, depths, label='original tubular_teste_de_pressão, $fs_{min}$=%.2f' %(min(fs_original)))
# working on production string (id=3), we want to change the current tubular of the project to the first one in the dataframe
new_cs = 1  # index on dataframe
data['well_strings'][cs_id]['string_sections'][0]['pipe']['weight'] = new_casing_catalog.loc[new_cs, 'Weight']
data['well_strings'][cs_id]['string_sections'][0]['pipe']['wt'] = new_casing_catalog.loc[new_cs, 'wt']
data['well_strings'][cs_id]['string_sections'][0]['pipe']['grade']['name'] = new_casing_catalog.loc[new_cs, 'Grade']
data['well_strings'][cs_id]['string_sections'][0]['pipe']['grade']['fymn'] = new_casing_catalog.loc[new_cs, 'fy']

# other parameters must be also changed to work with ULS

instance.input = convert_json(data)
project = Converter.to_lccv_project(instance)
ss = ScoreSolver(project=project)
cementing_result = ss.solve_cementing_load(casing_string_id=cs_id)
lost_returns_result = ss.solve_lost_returns(casing_string_id=cs_id)
cementing_fs = cementing_result.get_api_collapse_safety_factor()
lost_returns_fs = lost_returns_result.get_api_collapse_safety_factor()


fs_new = []
depths = []
for fs_result in cementing_fs:
    depths.append(fs_result[0])
    fs_new.append(fs_result[1])

pyplot.plot(fs_new, depths, label='our selection tubular, $fs_{min}$=%.2f' %(min(fs_new)))

#Lost_returns
fs_original = []
depths = []
for fs_result in lost_returns_fs:
    depths.append(fs_result[0])
    fs_original.append(fs_result[1])

pyplot.plot(fs_original, depths, label='our selection tubular_lost_returns, $fs_{min}$=%.2f' %(min(fs_original)))
pyplot.legend()
pyplot.show()

