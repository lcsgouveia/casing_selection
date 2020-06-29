from scorelib.design.casing_design import CasingDesign
from scorelib.design.standards.n_2752_y_2014_design_standard import N2752Y2014SimpleConnectionTriaxialDesignStandard
from scorelib.loads.backup_pressure.cementing_backup import CementingBackupAttributes, CementingBackup
from scorelib.loads.collapse_loads.cementing_load import CementingAttributes, Cementing
from scorelib.loads.scenarios.load_scenario import LoadScenario
from scorelib.loads.backup_pressure.fluid_gradient import FluidGradientBackup
from scorelib.loads.backup_pressure.fluid_gradient_mixture_water_wellhead_pressure import *
from scorelib.loads.backup_pressure.collapse_backup import *
from scorelib.loads.backup_pressure.fluid_gradient_pore_pressure import *
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
from scorelib.loads.burst_loads.tubing_leak import *
from scorelib.loads.burst_loads.injection import *

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
                            design_standard=N2752Y2014SimpleConnectionTriaxialDesignStandard,
                            tipo_carregamento=str('cementing'), tipo_carga='Serviço')

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
                            load_result=result, design_standard=N2752Y2014SimpleConnectionTriaxialDesignStandard,
                            tipo_carregamento=str('lost_returns'), tipo_carga='Serviço')

    def solve_pressure_test(self, casing_string_id):
        casing_string = self.project.casing_strings[casing_string_id]
        calcular = PressureTestCalculator(project=self.project, casing_string=casing_string)
        attributes = PressureTestAttributes(fluid=calcular.fluid, test_pressure=calcular.get_fit_test_pressure())
        internal_pressure_load = PressureTest(project=self.project, casing_string=casing_string, attributes=attributes)
        #backup = FluidGradientBackup(project=self.project, casing_string=casing_string)
        calcular_backup = FluidGradientPorePressureCalculator(project=self.project, casing_string=casing_string,
                                                              calculate_parameters=True)

        attributes_backup = FluidGradientPorePressureAttributes(toc_md=calcular_backup.toc_md,
                                                   previous_shoe_md=calcular_backup.previous_shoe_md,
                                                   fluid_gradient_above_toc=calcular_backup.fluid_gradient_above_toc,
                                                   fluid_gradient_below_toc=calcular_backup.fluid_gradient_below_toc,
                                                   enable_pore_pressure=calcular_backup.enable_pore_pressure)
        backup = FluidGradientPorePressure(project=self.project, casing_string=casing_string,
                                           attributes=attributes_backup)
        result = LoadScenario(internal_pressure_load=internal_pressure_load, external_pressure_load=backup).solve()
        return CasingDesign(string_sections=casing_string.string_sections,
                            load_result=result, design_standard=N2752Y2014SimpleConnectionTriaxialDesignStandard,
                            tipo_carregamento=str('pressure_test'), tipo_carga='Serviço')

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
                            load_result=result, design_standard=N2752Y2014SimpleConnectionTriaxialDesignStandard,
                            tipo_carregamento=str('gas_kick'), tipo_carga='Serviço')

    def solve_full_evacuation(self, casing_string_id):
        casing_string = self.project.casing_strings[casing_string_id]
       # calcular = FullEvacuationCalculator(project=self.project, casing_string=casing_string, production=None,
                                        #    calculate_parameters=True)
        attributes = FullEvacuationAttributes(perforation_base_depth=4657,
                                              packer_fluid=9.9)
        internal_pressure_load = FullEvacuation(project=self.project, casing_string=casing_string,
                                                attributes=attributes)
        backup = FluidGradientBackup(project=self.project, casing_string=casing_string)
        result = LoadScenario(internal_pressure_load=internal_pressure_load, external_pressure_load=backup).solve()
        return CasingDesign(string_sections=casing_string.string_sections,
                            load_result=result, design_standard=N2752Y2014SimpleConnectionTriaxialDesignStandard,
                            tipo_carregamento=str('full_evacuation'), tipo_carga='Sobrevivência')

    def solve_partial_evacuation(self, casing_string_id):
        casing_string = self.project.casing_strings[casing_string_id]
        calcular = PartialEvacuationCalculator(project=self.project, casing_string=casing_string, production=None,
                                            calculate_parameters=True)
        attributes = PartialEvacuationAttributes(evacuation_md=561.06,
                                                 perforation_base_depth=4657,
                                                 packer_fluid=9.9, fluid_gradient=calcular.fluid_gradient)
        internal_pressure_load = PartialEvacuation(project=self.project, casing_string=casing_string,
                                                attributes=attributes)
        backup = FluidGradientBackup(project=self.project, casing_string=casing_string)
        result = LoadScenario(internal_pressure_load=internal_pressure_load, external_pressure_load=backup).solve()
        return CasingDesign(string_sections=casing_string.string_sections,
                            load_result=result, design_standard=N2752Y2014SimpleConnectionTriaxialDesignStandard,
                            tipo_carregamento=str('partial_evacuation'), tipo_carga='Serviço')

    def solve_influx(self, casing_string_id):
        casing_string = self.project.casing_strings[casing_string_id]
        calcular = InfluxCalculator(project=self.project, casing_string=casing_string, production=None,
                                            calculate_parameters=True)
        attributes = InfluxAttributes(influx_depth=calcular.influx_depth,
                                      influx_pore_gradient=calcular.influx_pore_gradient,
                                      next_mud_weight=calcular.next_mud_weight, influx_is_hc=calcular.influx_is_hc,
                                      influx_gradient=calcular.influx_gradient, influx_gas_gravity=calcular.influx_gas_gravity,
                                      influx_api_density=calcular.influx_api_density,
                                      fracture_margin=calcular.fracture_margin, fluid_percentage=calcular.fluid_percentage)
        internal_pressure_load = Influx(project=self.project, casing_string=casing_string,
                                                   attributes=attributes)
        #backup = FluidGradientBackup(project=self.project, casing_string=casing_string)
        calcular_backup = FluidGradientPorePressureCalculator(project=self.project, casing_string=casing_string,
                                                              calculate_parameters=True)

        attributes_backup = FluidGradientPorePressureAttributes(toc_md=calcular_backup.toc_md,
                                                   previous_shoe_md=calcular_backup.previous_shoe_md,
                                                   fluid_gradient_above_toc=calcular_backup.fluid_gradient_above_toc,
                                                   fluid_gradient_below_toc=calcular_backup.fluid_gradient_below_toc,
                                                   enable_pore_pressure=calcular_backup.enable_pore_pressure)
        backup = FluidGradientPorePressure(project=self.project, casing_string=casing_string,
                                           attributes=attributes_backup)
        result = LoadScenario(internal_pressure_load=internal_pressure_load, external_pressure_load=backup).solve()
        return CasingDesign(string_sections=casing_string.string_sections,
                            load_result=result, design_standard=N2752Y2014SimpleConnectionTriaxialDesignStandard,
                            tipo_carregamento=str('influx'), tipo_carga='Sobrevivência')
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
                            load_result=result, design_standard=N2752Y2014SimpleConnectionTriaxialDesignStandard,
                            tipo_carregamento=str('WellFullOfGas'), tipo_carga='Sobrevivência')

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
                            load_result=result, design_standard=N2752Y2014SimpleConnectionTriaxialDesignStandard,
                            tipo_carregamento='WCD_colapse')
    def solve_tubing_leak(self, casing_string_id):
        casing_string = self.project.casing_strings[casing_string_id]
        #calcular = TubingLeakCalculator(project=self.project, casing_string=casing_string, production=1,
                           #             calculate_parameters=True)
        attributes = TubingLeakAttributes(wellhead_pressure=2921.48, perforation_base_depth=4657,
                                          perforation_pressure=6863.36, fluid_gradient=1.24,
                                          packer_depth=3982, packer_fluid=9.9)
        internal_pressure_load = TubingLeak(project=self.project, casing_string=casing_string,
                                                   attributes=attributes)
       # backup = FluidGradientBackup(project=self.project, casing_string=casing_string)
        calcular_backup = FluidGradientPorePressureCalculator(project=self.project, casing_string=casing_string,
                                                              calculate_parameters=True)

        attributes_backup = FluidGradientPorePressureAttributes(toc_md=calcular_backup.toc_md,
                                                                previous_shoe_md=calcular_backup.previous_shoe_md,
                                                                fluid_gradient_above_toc=calcular_backup.fluid_gradient_above_toc,
                                                                fluid_gradient_below_toc=calcular_backup.fluid_gradient_below_toc,
                                                                enable_pore_pressure=calcular_backup.enable_pore_pressure)
        backup = FluidGradientPorePressure(project=self.project, casing_string=casing_string,
                                           attributes=attributes_backup,)
        result = LoadScenario(internal_pressure_load=internal_pressure_load, external_pressure_load=backup).solve()
        return CasingDesign(string_sections=casing_string.string_sections,
                            load_result=result, design_standard=N2752Y2014SimpleConnectionTriaxialDesignStandard,
                            tipo_carregamento=str('Tubing_leak'), tipo_carga='Sobrevivência')
    def solve_injection(self, casing_string_id):
        casing_string = self.project.casing_strings[casing_string_id]
        attributes = InjectionAttributes(wellhead_pressure=2500, perforation_base_depth=4657,
                                         perforation_pressure=7118.97, fluid_gradient=1.46, packer_depth=3982,
                                         packer_fluid=9.9)
        internal_pressure_load = Injection(project=self.project, casing_string=casing_string, attributes=attributes)
       # backup = FluidGradientBackup(project=self.project, casing_string=casing_string)
        calcular_backup = FluidGradientPorePressureCalculator(project=self.project, casing_string=casing_string,
                                                              calculate_parameters=True)

        attributes_backup = FluidGradientPorePressureAttributes(toc_md=calcular_backup.toc_md,
                                                                previous_shoe_md=calcular_backup.previous_shoe_md,
                                                                fluid_gradient_above_toc=calcular_backup.fluid_gradient_above_toc,
                                                                fluid_gradient_below_toc=calcular_backup.fluid_gradient_below_toc,
                                                                enable_pore_pressure=calcular_backup.enable_pore_pressure)
        backup = FluidGradientPorePressure(project=self.project, casing_string=casing_string,
                                           attributes=attributes_backup)
        result = LoadScenario(internal_pressure_load=internal_pressure_load, external_pressure_load=backup).solve()
        return CasingDesign(string_sections=casing_string.string_sections,
                            load_result=result, design_standard=N2752Y2014SimpleConnectionTriaxialDesignStandard,
                            tipo_carregamento=str('injection'), tipo_carga='Sobrevivência')


class Carregamentos:
    def __init__(self, project):
        self.project = project

    def revestimento_superior(self, casing_string_id):
        cs_id = casing_string_id
        pressure_test_result =ScoreSolver(project=self.project).solve_pressure_test(casing_string_id=cs_id)
        influx_result = ScoreSolver(project=self.project).solve_influx(casing_string_id=cs_id)
        cementing_result = ScoreSolver(project=self.project).solve_cementing_load(casing_string_id=cs_id)
        lost_returns_result = ScoreSolver(project=self.project).solve_lost_returns(casing_string_id=cs_id)

        return pressure_test_result, cementing_result, influx_result, lost_returns_result

    def revestimento_intermediario(self, casing_string_id):
        cs_id = casing_string_id
        pressure_test_result =ScoreSolver(project=self.project).solve_pressure_test(casing_string_id=cs_id)
        influx_result = ScoreSolver(project=self.project).solve_influx(casing_string_id=cs_id)
        cementing_result = ScoreSolver(project=self.project).solve_cementing_load(casing_string_id=cs_id)
        lost_returns_result = ScoreSolver(project=self.project).solve_lost_returns(casing_string_id=cs_id)

        return cementing_result,  influx_result, lost_returns_result, pressure_test_result

    def revestimento_intermediario2(self, casing_string_id):
        cs_id = casing_string_id
        pressure_test_result = ScoreSolver(project=self.project).solve_pressure_test(casing_string_id=cs_id)
        influx_result = ScoreSolver(project=self.project).solve_influx(casing_string_id=cs_id)
        cementing_result = ScoreSolver(project=self.project).solve_cementing_load(casing_string_id=cs_id)
        partial_evacuation_result = ScoreSolver(project=self.project).solve_partial_evacuation(casing_string_id=cs_id)
        injection_result = ScoreSolver(project=self.project).solve_injection(casing_string_id=cs_id)
        tubing_leak_result = ScoreSolver(project=self.project).solve_tubing_leak(casing_string_id=cs_id)
        lost_returns_result = ScoreSolver(project=self.project).solve_lost_returns(casing_string_id=cs_id)
        full_evacuation_result = ScoreSolver(project=self.project).solve_full_evacuation(casing_string_id=cs_id)
        return cementing_result,   pressure_test_result, influx_result, partial_evacuation_result, injection_result, \
               tubing_leak_result, lost_returns_result


    def revestimento_produção(self, casing_string_id):
        cs_id = casing_string_id

        pressure_test_result =ScoreSolver(project=self.project).solve_pressure_test(casing_string_id=cs_id)
        cementing_result = ScoreSolver(project=self.project).solve_cementing_load(casing_string_id=cs_id)
        partial_evacuation_result = ScoreSolver(project=self.project).solve_partial_evacuation(casing_string_id=cs_id)
        injection_result = ScoreSolver(project=self.project).solve_injection(casing_string_id=cs_id)
        tubing_leak_result = ScoreSolver(project=self.project).solve_tubing_leak(casing_string_id=cs_id)

        return injection_result, tubing_leak_result, pressure_test_result, cementing_result, partial_evacuation_result