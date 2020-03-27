import json

# get json file from score web interface
from scorelib.converter import Converter
from scorelib.design.casing_design import CasingDesign
from scorelib.design.standards.n_2752_y_2014_design_standard import N2752Y2014SimpleConnectionTriaxialDesignStandard
from scorelib.loads.backup_pressure.cementing_backup import CementingBackupAttributes, CementingBackup
from scorelib.loads.collapse_loads.cementing_load import CementingAttributes, Cementing
from scorelib.loads.scenarios.load_scenario import LoadScenario

from parsers.score_project_json import JSONTest, convert_json

with open("./scripts/score_projects/project476.json", 'r', encoding="latin-1") as f:
    data = json.load(f)

instance = JSONTest()
instance.input = convert_json(data)

project = Converter.to_lccv_project(instance)

# definir fase a ser analisada
casing_string = project.casing_strings[2]

# definir e calcular carregamentos
attributes = CementingAttributes(displacement_fluid=casing_string.displacement_fluid,
                                 surface_pressure_during_setting=casing_string.surface_pressure_during_setting)
internal_pressure_load = Cementing(project=project,
                                   casing_string=casing_string,
                                   attributes=attributes)
backup_attributes = CementingBackupAttributes(slurry_density=casing_string.slurry_density,
                                              mud_weight=casing_string.mud_weight,
                                              toc_md=casing_string.toc_md,
                                              second_slurry_density=casing_string.second_slurry_density,
                                              second_slurry_length=casing_string.second_slurry_length)
backup = CementingBackup(project=project,
                         casing_string=casing_string,
                         attributes=backup_attributes)

result = LoadScenario(internal_pressure_load=internal_pressure_load,
                      external_pressure_load=backup
                      ).solve()

casing_design = CasingDesign(string_sections=casing_string.string_sections,
                             load_result=result,
                             design_standard=N2752Y2014SimpleConnectionTriaxialDesignStandard)

print(casing_design.load_result.internal_profile)
print(casing_design.load_result.external_profile)
print(casing_design.load_result.axial_profile)

print(casing_design.get_api_burst_safety_factor())
print(casing_design.get_api_collapse_safety_factor())
print(casing_design.get_api_axial_safety_factor())
print(casing_design.get_api_von_mises_safety_factor())

print(casing_design.get_api_barlow_failure_probability_profile())
print(casing_design.get_api_collapse_failure_probability_profile())
print(casing_design.get_api_axial_failure_probability_profile())
print(casing_design.get_von_mises_failure_probability_profile())
