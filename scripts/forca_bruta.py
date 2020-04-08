import json

# get json file from score web interface
from matplotlib import pyplot
from scorelib.converter import Converter

from parsers.score_project_json import JSONTest, convert_json
from score_solver import ScoreSolver
from tubulars_catalog.roque_catalog_to_df import new_casing_catalog

with open("./scripts/score_projects/project476.json", 'r', encoding="latin-1") as f:
    data = json.load(f)

instance = JSONTest()
instance.input = convert_json(data)
project = Converter.to_lccv_project(instance)

# acesso aos resultados de FS e Pf para o revestimento produtor cs_id=3
cs_id = 3
ss = ScoreSolver(project=project)
cementing_result = ss.solve_cementing_load(casing_string_id=cs_id)
cementing_fs = cementing_result.get_api_collapse_safety_factor()

fs_original = []
depths = []
for fs_result in cementing_fs:
    depths.append(fs_result[0])
    fs_original.append(fs_result[1])

pyplot.plot(fs_original, depths, label='original tubular, $fs_{min}$=%.2f' %(min(fs_original)))

# working on production string (id=any), we want to change the current tubular of the project to the first one in the dataframe
new_cs = 3  # index on dataframe
data['well_strings'][cs_id]['string_sections'][0]['pipe']['weight'] = new_casing_catalog.loc[new_cs, 'Weight']
data['well_strings'][cs_id]['string_sections'][0]['pipe']['wt'] = new_casing_catalog.loc[new_cs, 'wt']
data['well_strings'][cs_id]['string_sections'][0]['pipe']['grade']['name'] = new_casing_catalog.loc[new_cs, 'Grade']
data['well_strings'][cs_id]['string_sections'][0]['pipe']['grade']['fymn'] = new_casing_catalog.loc[new_cs, 'fy']

# other parameters must be also changed to work with ULS

instance.input = convert_json(data)
project = Converter.to_lccv_project(instance)
ss = ScoreSolver(project=project)
cementing_result = ss.solve_cementing_load(casing_string_id=cs_id)
cementing_fs = cementing_result.get_api_collapse_safety_factor()
fs_new = []
depths = []
for fs_result in cementing_fs:
    depths.append(fs_result[0])
    fs_new.append(fs_result[1])

pyplot.plot(fs_new, depths, label='our selection tubular, $fs_{min}$=%.2f' %(min(fs_new)))
pyplot.legend()
pyplot.gca().invert_yaxis()
pyplot.show()

