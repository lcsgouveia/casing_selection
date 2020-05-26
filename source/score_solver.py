from scorelib.design.casing_design import CasingDesign
from scorelib.design.standards.n_2752_y_2014_design_standard import N2752Y2014SimpleConnectionTriaxialDesignStandard
from scorelib.loads.backup_pressure.cementing_backup import CementingBackupAttributes, CementingBackup
from scorelib.loads.collapse_loads.cementing_load import CementingAttributes, Cementing
from scorelib.loads.scenarios.load_scenario import LoadScenario
from scorelib.loads.backup_pressure.fluid_gradient import FluidGradientBackup
from scorelib.loads.collapse_loads.lost_returns import LostReturnsAttributes, LostReturns, LostReturnsCalculator
from scorelib.loads.burst_loads.pressure_test import PressureTestAttributes, PressureTest, PressureTestCalculator
from scorelib.loads.burst_loads.gas_kick import GasKickAttributes, GasKick, GasKickCalculator
from scorelib.loads.collapse_loads.full_evacuation import FullEvacuationAttributes, FullEvacuation, \
                                                            FullEvacuationCalculator
from scorelib.loads.collapse_loads.partial_evacuation import PartialEvacuationAttributes, PartialEvacuation,\
                                                                PartialEvacuationCalculator
from scorelib.loads.burst_loads.influx import InfluxAttributes, Influx, InfluxCalculator
from scorelib.loads.burst_loads.well_full_of_gas import WellFullOfGasAttributes, WellFullOfGas, WellFullOfGasCalculator
from scorelib.loads.collapse_loads.wcd_collapse import WCDCollapseAttributes, WCDCollapse, WCDCollapseCalculator

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

    def solve_lost_returns(self, casing_string_id):
        casing_string = self.project.casing_strings[casing_string_id]
        calcular = LostReturnsCalculator(project=self.project, casing_string=casing_string, calculate_parameters=True)
        attributes = LostReturnsAttributes(evacuation_tvd=calcular.evacuation_tvd,
                                     mud_weight=calcular.mud_weight,
                                     loss_tvd=calcular.loss_tvd,
                                     pore_gradient=calcular.pore_gradient)
        internal_pressure_load = LostReturns(project=self.project, casing_string=casing_string, attributes=attributes)
        backup = FluidGradientBackup(project=self.project, casing_string=casing_string)
        result = LoadScenario(internal_pressure_load=internal_pressure_load, external_pressure_load=backup).solve()
        return CasingDesign(string_sections=casing_string.string_sections,
                            load_result=result, design_standard=N2752Y2014SimpleConnectionTriaxialDesignStandard)

    def solve_pressure_test(self, casing_string_id):
        casing_string = self.project.casing_strings[casing_string_id]
        calcular = PressureTestCalculator(project=self.project, casing_string=casing_string)
        attributes = PressureTestAttributes(fluid=calcular.fluid, test_pressure=calcular.get_fit_test_pressure())
        internal_pressure_load = PressureTest(project=self.project, casing_string=casing_string, attributes=attributes)
        backup = FluidGradientBackup(project=self.project, casing_string=casing_string)
        result = LoadScenario(internal_pressure_load=internal_pressure_load, external_pressure_load=backup).solve()
        return CasingDesign(string_sections=casing_string.string_sections,
                            load_result=result, design_standard=N2752Y2014SimpleConnectionTriaxialDesignStandard)

    def solve_gas_kick(self, casing_string_id):
        casing_string = self.project.casing_strings[casing_string_id]
        calcular = GasKickCalculator(project=self.project, casing_string=casing_string, production=None,
                                     calculate_parameters=True)
        attributes = GasKickAttributes(kick_volume=calcular.kick_volume, kick_intensity=calcular.kick_intensity,
                                       gas_gravity=calcular.gas_gravity)
        internal_pressure_load = GasKick(project=self.project, casing_string=casing_string, attributes=attributes)
        backup = FluidGradientBackup(project=self.project, casing_string=casing_string)
        result = LoadScenario(internal_pressure_load=internal_pressure_load, external_pressure_load=backup).solve()
        return CasingDesign(string_sections=casing_string.string_sections,
                            load_result=result, design_standard=N2752Y2014SimpleConnectionTriaxialDesignStandard)

    def solve_full_evacuation(self, casing_string_id):
        casing_string = self.project.casing_strings[casing_string_id]
        calcular = FullEvacuationCalculator(project=self.project, casing_string=casing_string, production=1,
                                            calculate_parameters=True)
        attributes = FullEvacuationAttributes(perforation_base_depth=calcular.perforation_base_depth,
                                              packer_fluid=calcular.packer_fluid)
        internal_pressure_load = FullEvacuation(project=self.project, casing_string=casing_string,
                                                attributes=attributes)
        backup = FluidGradientBackup(project=self.project, casing_string=casing_string)
        result = LoadScenario(internal_pressure_load=internal_pressure_load, external_pressure_load=backup).solve()
        return CasingDesign(string_sections=casing_string.string_sections,
                            load_result=result, design_standard=N2752Y2014SimpleConnectionTriaxialDesignStandard)

    def solve_partial_evacuation(self, casing_string_id):
        casing_string = self.project.casing_strings[casing_string_id]
        calcular = PartialEvacuationCalculator(project=self.project, casing_string=casing_string, production=None,
                                            calculate_parameters=True)
        attributes = PartialEvacuationAttributes(evacuation_md=calcular.evacuation_md,
                                                 perforation_base_depth=calcular.perforation_base_depth,
                                                 packer_fluid=calcular.packer_fluid, fluid_gradient=None)
        internal_pressure_load = PartialEvacuation(project=self.project, casing_string=casing_string,
                                                attributes=attributes)
        backup = FluidGradientBackup(project=self.project, casing_string=casing_string)
        result = LoadScenario(internal_pressure_load=internal_pressure_load, external_pressure_load=backup).solve()
        return CasingDesign(string_sections=casing_string.string_sections,
                            load_result=result, design_standard=N2752Y2014SimpleConnectionTriaxialDesignStandard)

    def solve_influx(self, casing_string_id):
        casing_string = self.project.casing_strings[casing_string_id]
        calcular = InfluxCalculator(project=self.project, casing_string=casing_string, production=None,
                                            calculate_parameters=True)
        attributes = InfluxAttributes(influx_depth=calcular.influx_depth,
                                      influx_pore_gradient=calcular.influx_pore_gradient,
                                      next_mud_weight=calcular.next_mud_weight, influx_is_hc=calcular.influx_is_hc,
                                      influx_gradient=None, influx_gas_gravity=1., influx_api_density=None,
                                      fracture_margin=1., fluid_percentage=None)
        internal_pressure_load = Influx(project=self.project, casing_string=casing_string,
                                                   attributes=attributes)
        backup = FluidGradientBackup(project=self.project, casing_string=casing_string)
        result = LoadScenario(internal_pressure_load=internal_pressure_load, external_pressure_load=backup).solve()
        return CasingDesign(string_sections=casing_string.string_sections,
                            load_result=result, design_standard=N2752Y2014SimpleConnectionTriaxialDesignStandard)
    def solve_WellFullOfGas(self, casing_string_id):
        casing_string = self.project.casing_strings[casing_string_id]
        calcular = WellFullOfGasCalculator(project=self.project, casing_string=casing_string, production=None,
                                            calculate_parameters=True)
        attributes = WellFullOfGasAttributes(influx_depth=calcular.influx_depth,
                                             influx_pore_gradient=calcular.influx_pore_gradient,
                                             next_mud_weight=calcular.next_mud_weight, fracture_margin=1.,
                                             gas_gradient=None, gas_gravity=0.6, gas_percentage=1.)
        internal_pressure_load = WellFullOfGas(project=self.project, casing_string=casing_string,
                                                   attributes=attributes)
        backup = FluidGradientBackup(project=self.project, casing_string=casing_string)
        result = LoadScenario(internal_pressure_load=internal_pressure_load, external_pressure_load=backup).solve()
        return CasingDesign(string_sections=casing_string.string_sections,
                            load_result=result, design_standard=N2752Y2014SimpleConnectionTriaxialDesignStandard)

    def solve_wcd_collapse(self, casing_string_id):
        casing_string = self.project.casing_strings[casing_string_id]
        calcular = WCDCollapseCalculator(project=self.project, casing_string=casing_string, calculate_parameters=True)
        attributes = WCDCollapseAttributes(seawater_density=calcular.seawater_density, gas_gradient=None,
                                           gas_gravity=calcular.gas_gravity,
                                           api_density=calcular.api_density, influx_depth=calcular.influx_depth)
        internal_pressure_load = WCDCollapse(project=self.project, casing_string=casing_string,
                                                   attributes=attributes)
        backup = FluidGradientBackup(project=self.project, casing_string=casing_string)
        result = LoadScenario(internal_pressure_load=internal_pressure_load, external_pressure_load=backup).solve()
        return CasingDesign(string_sections=casing_string.string_sections,
                            load_result=result, design_standard=N2752Y2014SimpleConnectionTriaxialDesignStandard)
