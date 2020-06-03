import numpy

from score_solver import ScoreSolver


def constraint_func_builder(parameters, project, casing_string_id, min_collapse_sf):
    wt = parameters[0]
    fy = parameters[1]
    ss = ScoreSolver(project=project)
    for section in ss.project.casing_strings[casing_string_id].string_sections:
        section.wt = wt
        section.nominal_wt = wt
        section.material.minimum_yield_strength = fy

        section.material.young_modulus = 30E6
        section.material.poisson_ratio = 0.28
    return ss


def constraint_fs_cementing(parameters, project, casing_string_id, min_collapse_sf):
    ss = constraint_func_builder(parameters=parameters,
                                 project=project,
                                 casing_string_id=casing_string_id,
                                 min_collapse_sf=min_collapse_sf)

    cementing_result = ss.solve_cementing_load(casing_string_id=casing_string_id)
    cementing_fs = cementing_result.get_api_collapse_safety_factor()
    cementing_fs = numpy.array(cementing_fs)

    return cementing_fs[:, 1].min() - min_collapse_sf


def constraint_fs_pressure_test(parameters, project, casing_string_id, min_collapse_sf):
    ss = constraint_func_builder(parameters=parameters,
                                 project=project,
                                 casing_string_id=casing_string_id,
                                 min_collapse_sf=min_collapse_sf)

    pressure_test_result = ss.solve_pressure_test(casing_string_id=casing_string_id)
    pressure_test_fs = pressure_test_result.get_api_collapse_safety_factor()
    pressure_test_fs = numpy.array(pressure_test_fs)

    return pressure_test_fs[:, 1].min() - min_collapse_sf