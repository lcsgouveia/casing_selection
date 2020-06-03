import json
import numpy
from scipy.optimize import minimize
from scorelib.converter import Converter

from parsers.score_project_json import JSONTest, convert_json
from source.constraint_functions import constraint_fs_cementing
from source.cost_functions import cost_from_catalog

from source.tubulars_catalog.roque_catalog_to_df import new_casing_catalog

od = 7
od_catalog = new_casing_catalog.loc[new_casing_catalog['OD'] == od, :]

with open("source/score_projects/project476.json", 'r', encoding="latin-1") as f:
    data = json.load(f)

cs_id = 3
burst = 1.1
collapse = 1.0
triaxial = 1.25

instance = JSONTest()
instance.input = convert_json(data)
project = Converter.to_lccv_project(instance)

constraintfscementing = {'type': 'ineq', 'fun': constraint_fs_cementing,
                         'args': (project, cs_id, collapse)}

catalog_bounds = [(od_catalog['wt'].min(), od_catalog['wt'].max()),
                  (od_catalog['fy'].min(), od_catalog['fy'].max())]

x0 = numpy.array([od_catalog.iloc[-1, 3], od_catalog.iloc[-1, 4]])

minsolve = minimize(cost_from_catalog, x0, args=(od_catalog,),
                    constraints=constraintfscementing,
                    bounds=catalog_bounds,
                    method='COBYLA')
print(minsolve)


# fy_of_constraint = numpy.array([fsolve(lambda fy: fscementing([wt, fy[0]], data_=data), x0=numpy.array(1e5))[0] for wt in wts])
# constraint = []
# for wt, fy in zip(wts, fy_of_constraint):
#     constraint.append(fscementing([wt, fy], data_=data))
#
# constraint = numpy.array(constraint)
# constraint_ids = numpy.where(abs(constraint) < 1e-2)
#
# pyplot.plot(wts[constraint_ids[0]], fy_of_constraint[constraint_ids[0]], label='fs constraint')
#
# pyplot.legend()
# pyplot.gca().set_ylim(0, 150000)