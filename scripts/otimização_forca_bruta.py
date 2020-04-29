import json

# get json file from score web interface
from matplotlib import pyplot
from scorelib.converter import Converter
from pandas import read_excel
from scorelib.models.string_section import StringSectionBuilder, StringSection

from parsers.score_project_json import JSONTest, convert_json
from scripts.score_solver import ScoreSolver
from scripts.tubulars_catalog.roque_catalog_to_df import new_casing_catalog
from scripts.conf import *
from scorelib.design.casing_design import MinimumAllowableSafetyFactorsBuilder

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

def Klever_Tamano1 (u1):
    Resistencia_conf = ISO_CollapseUniaxial(fymn=u1[3],
                                     D=u1[0], t=u1[1],
                                     ov=0.217,
                                     ec=3.924,
                                     rs=-0.138,
                                     hn=0,
                                     E=u1[2],
                                     nu=0.3,
                                     kedes=0.825,
                                     kydes=0.825,
                                     Htdes='calculate')

    return (u1[4]*Resistencia_conf)-(abs(u1[5]-u1[6]))

def von_mises_1 (u1):
    mises = vonMisesCritical(Pint=u1[5],
                                      Pout=u1[4],
                                      Fa=u1[6],
                                      D=u1[0],
                                      t=u1[1],
                                      tmin=(u1[1] -
                                            (1. - kwall_mises) * u1[1]),
                                      E=u1[2],
                                      # DL=0,
                                      DL=dl,
                                      TQ=TQ)
    return u1[3]-mises[0]

def k_S_1 (u1):
    Resistencia_conf = (
        ISO_DuctileRuptureUniaxial(u1[2], u1[0], u1[1], n,
                                   kwall_burst, ka, an))

    return (u1[3]*Resistencia_conf)-abs(u1[4]-u1[5])

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
burst = 1.1
collapse = 1.0
triaxial = 1.25
for new_cs in range(44):
    data['well_strings'][cs_id]['string_sections'][0]['pipe']['weight'] = new_casing_catalog.loc[new_cs, 'Weight']
    data['well_strings'][cs_id]['string_sections'][0]['pipe']['wt'] = new_casing_catalog.loc[new_cs, 'wt']
    data['well_strings'][cs_id]['string_sections'][0]['pipe']['grade']['name'] = new_casing_catalog.loc[new_cs, 'Grade']
    data['well_strings'][cs_id]['string_sections'][0]['pipe']['grade']['fymn'] = new_casing_catalog.loc[new_cs, 'fy']
    data['well_strings'][cs_id]['string_sections'][0]['pipe']['Price'] = new_casing_catalog.loc[new_cs, 'Price']
    data['well_strings'][cs_id]['string_sections'][0]['pipe']['od'] = new_casing_catalog.loc[new_cs, 'OD']

# other parameters must be also changed to work with ULS
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
    tamanho = len(depths)
    passou = True
    for i in range(tamanho-3):
        cementing_collapso = cementing_fs[i][1]
        #Cenários de Collapso
        if cementing_fs[i][1] < collapse or lost_returns_fs[i][1] < collapse:
            passou = False
            break

        #Cenários de Burst
        if pressure_test_fs[i][1] < burst or gas_kick_fs[i][1] < burst or influx_fs[i][1] < burst or \
                                                                        well_full_of_gas_fs[i][1] < burst:
            passou = False
            break
        #Cenário triaxial
        if cementing_fs_mises[i][1] < triaxial or lost_returns_fs_mises[i][1] < triaxial or \
            pressure_test__fs_mises[i][1] < triaxial or gas_kick_fs_mises[i][1] < triaxial or \
                influx_fs_mises[i][1] < triaxial or well_full_of_gas_fs_mises[i][1] < triaxial:
            passou = False
            break
        #Restrição de confiabilidade
        # Função de falha
        Pe0 = gas_kick_result.load_result.external_profile[i][1]
        Pi0 = gas_kick_result.load_result.internal_profile[i][1]
        Fa0 = gas_kick_result.load_result.axial_profile[i][1]
        dl = gas_kick_result.load_result.axial_profile[i][2]
        TQ = gas_kick_result.load_result.axial_profile[i][3]
        #Caracterização das variáveis estatísticas
        Pe = RV("normal", Pe0, Pe0*0)
        Pi = RV("normal", Pi0, Pi0*0)
        Fa = RV("normal", Fa0, Fa0*0)
        D = RV("normal", new_casing_catalog.loc[new_cs, 'OD']*1.0059, (new_casing_catalog.loc[new_cs, 'OD']*1.0059)*0.00181)
        t = RV("normal", new_casing_catalog.loc[new_cs, 'wt']*1.0069, (new_casing_catalog.loc[new_cs, 'wt']*1.0069)*0.259)
        E = RV("normal", 30e6, 30e6*0.035)
        fymn = RV("normal", new_casing_catalog.loc[new_cs, 'fy']*1.10, (new_casing_catalog.loc[new_cs, 'fy']*1.10)*0.036)
        kwall_mises = project.casing_strings[cs_id].string_sections[0].kwall_mises
        kwall_burst = project.casing_strings[cs_id].string_sections[0].kwall_burst
        n = project.casing_strings[cs_id].string_sections[0].material.n
        ka = project.casing_strings[cs_id].string_sections[0].material.ka
        an = project.casing_strings[cs_id].string_sections[0].material.an
        errokt = RV("normal", 0.9991, 0.0670)
        erroks = RV("normal", 1.004, 0.0470)
        X1 = [D, t, E, fymn, errokt, Pe, Pi] #KT
        X2 = [D, t, E, fymn, Pe, Pi, Fa] #vonmises
        X3 = [D, t, fymn, erroks, Pi, Pe] #KS
        #result1 = FORM(X2, von_mises_1)
        if Pe0 < Pi0:
            result2 = FORM(X3, k_S_1)
        if Pe0 > Pi0:
            result2 = FORM(X1, Klever_Tamano1)
        if result2.pf > 0.001:
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



a = 1