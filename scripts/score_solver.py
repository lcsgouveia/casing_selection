from scorelib.design.casing_design import CasingDesign
from scorelib.design.standards.n_2752_y_2014_design_standard import N2752Y2014SimpleConnectionTriaxialDesignStandard
from scorelib.loads.backup_pressure.cementing_backup import CementingBackupAttributes, CementingBackup
from scorelib.loads.collapse_loads.cementing_load import CementingAttributes, Cementing
from scorelib.loads.scenarios.load_scenario import LoadScenario


class ScoreSolver:

    def __init__(self, project):
        self.project = project

    def solve_cementing_load(self, casing_string_id):
        casing_string = self.project.casing_strings[casing_string_id]

        attributes = CementingAttributes(displacement_fluid=casing_string.displacement_fluid,
                                         surface_pressure_during_setting=casing_string.surface_pressure_during_setting)
        internal_pressure_load = Cementing(project=self.project, casing_string=casing_string, attributes=attributes)
        backup_attributes = CementingBackupAttributes(slurry_density=casing_string.slurry_density,
                                                      mud_weight=casing_string.mud_weight,
                                                      toc_md=casing_string.toc_md,
                                                      second_slurry_density=casing_string.second_slurry_density,
                                                      second_slurry_length=casing_string.second_slurry_length)
        backup = CementingBackup(project=self.project, casing_string=casing_string, attributes=backup_attributes)

        result = LoadScenario(internal_pressure_load=internal_pressure_load, external_pressure_load=backup).solve()

        return CasingDesign(string_sections=casing_string.string_sections,
                            load_result=result,
                            design_standard=N2752Y2014SimpleConnectionTriaxialDesignStandard)
