import json

# get json file from score web interface
import numpy
from matplotlib import pyplot

from scipy.optimize import fsolve
from scorelib.converter import Converter

from parsers.score_project_json import JSONTest, convert_json
from source.constraint_functions import constraint_fs_cementing
from source.cost_functions import cost_from_catalog, cost_linear_fitted

from source.tubulars_catalog.roque_catalog_to_df import new_casing_catalog

od = 7
od_catalog = new_casing_catalog.loc[new_casing_catalog['OD'] == od, :]

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

burst = 1.1
collapse = 1.0
triaxial = 1.25

# WT VS. CONSTRAINT
wts = numpy.linspace(od_catalog['wt'].min(), od_catalog['wt'].max())
fys = numpy.linspace(od_catalog['fy'].min(), od_catalog['fy'].max(), 7)
for fy in fys:
    pyplot.plot(wts, [constraint_fs_cementing(parameters=[wt, fy], project=project,
                                              casing_string_id=cs_id,
                                              min_collapse_sf=collapse) for wt in wts],
                label='fy='+str(fy))
pyplot.legend()
pyplot.gca().set_xlabel('wt')
pyplot.gca().set_ylabel('constraint')

# FY VS. CONSTRAINT
pyplot.figure()
wts = numpy.linspace(od_catalog['wt'].min(), od_catalog['wt'].max(), 7)
fys = numpy.linspace(od_catalog['fy'].min(), od_catalog['fy'].max())
for wt in wts:
    pyplot.plot(fys, [constraint_fs_cementing(parameters=[wt, fy], project=project,
                                              casing_string_id=cs_id,
                                              min_collapse_sf=collapse) for fy in fys],
                label='wt='+str(wt))
pyplot.legend()
pyplot.gca().set_xlabel('fy')
pyplot.gca().set_ylabel('constraint')

# 3D: SCATTER COST
wts = od_catalog['wt']
fys = od_catalog['fy']
prices = od_catalog.apply(lambda row: cost_from_catalog([row['wt'], row['fy']],
                                                        catalog=new_casing_catalog),
                          axis=1)

fig = pyplot.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(wts, fys, prices)

# 3D: SCATTER CONSTRAINT
wts = od_catalog['wt']
fys = od_catalog['fy']
constraints = od_catalog.apply(lambda row: constraint_fs_cementing([row['wt'], row['fy']],
                                                                   project=project,
                                                                   casing_string_id=cs_id,
                                                                   min_collapse_sf=collapse),
                               axis=1)

# fig = pyplot.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(wts, fys, constraints)

# 3D: FITTED COST ISO CURVES + CONSTRAINT
pyplot.figure()
wts = numpy.linspace(od_catalog['wt'].min(), od_catalog['wt'].max())
fys = numpy.linspace(od_catalog['fy'].min(), od_catalog['fy'].max())
WTS, FYS = numpy.meshgrid(wts, fys)

PRICES = numpy.array(cost_linear_fitted([WTS, FYS]))

cost_contour = pyplot.contour(WTS, FYS, PRICES)
pyplot.clabel(cost_contour, inline=1)

wts = numpy.linspace(od_catalog['wt'].min(), od_catalog['wt'].max(), 50)

fy_of_constraint = numpy.array([fsolve(lambda fy: constraint_fs_cementing(parameters=[wt, fy[0]],
                                                                          project=project,
                                                                          casing_string_id=cs_id,
                                                                          min_collapse_sf=collapse),
                                       x0=numpy.array(1e5))[0] for wt in wts])
constraint = []
for wt, fy in zip(wts, fy_of_constraint):
    constraint.append(constraint_fs_cementing(parameters=[wt, fy], project=project,
                                              casing_string_id=cs_id, min_collapse_sf=collapse))

constraint = numpy.array(constraint)
# constraint_ids = numpy.where(abs(constraint) < 1e-2)
# pyplot.plot(wts[constraint_ids[0]], fy_of_constraint[constraint_ids[0]], label='fs constraint')

pyplot.plot(wts, fy_of_constraint, label='fs constraint')

pyplot.legend()
pyplot.gca().set_ylim(od_catalog['fy'].min(), od_catalog['fy'].max())
