import json

# get json file from score web interface
from matplotlib import pyplot
from scorelib.converter import Converter
from pandas import read_excel
from scorelib.models.string_section import StringSectionBuilder, StringSection

from parsers.score_project_json import JSONTest, convert_json
from scripts.score_solver import ScoreSolver, Carregamentos
from scripts.tubulars_catalog.roque_catalog_to_df import new_casing_catalog
from scripts.tubulars_catalog.Chilingarian_catalog_to_df import *
from scorelib.proj_poco.rev_tubos_lib import *
#from scripts.conf import *
from scorelib.design.casing_design import MinimumAllowableSafetyFactorsBuilder

with open("C:/casing_selection-master/scripts/score_projects/project454.json", 'r', encoding="latin-1") as f:
#with open("C:/casing_selection-master/scripts/score_projects/project495.json", 'r', encoding="latin-1") as f:
    data = json.load(f)
arquivo = open("C:/Users/luis_/Desktop/casing_selection-master/scripts/arquivo_teste.txt", 'w')
instance = JSONTest()
instance.input = convert_json(data)
project = Converter.to_lccv_project(instance)

# acesso aos resultados de FS e Pf para o revestimento produtor cs_id=3
cs_id = 1
ss = ScoreSolver(project=project)
pressure_test_result = ss.solve_pressure_test(casing_string_id=cs_id)
cementing_result = ss.solve_cementing_load(casing_string_id=cs_id)
lost_returns_result = ss.solve_lost_returns(casing_string_id=cs_id)
gas_kick_result = ss.solve_gas_kick(casing_string_id=cs_id)
full_evacuation_result = ss.solve_full_evacuation(casing_string_id=cs_id)
partial_evacuation_result = ss.solve_partial_evacuation(casing_string_id=cs_id)
tubing_leak_result = ss.solve_tubing_leak(casing_string_id=cs_id)
injection_result = ss.solve_injection(casing_string_id=cs_id)
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

#pyplot.plot(fs_original, depths, label='original tubular, $fs_{min}$=%.2f' %(min(fs_original)))
#Caso de perda de circulação
fs_original = []
depths = []
for fs_result in lost_returns_fs:
    depths.append(fs_result[0])
    fs_original.append(fs_result[1])

#pyplot.plot(fs_original, depths, label='original tubular_lost_returns, $fs_{min}$=%.2f' %(min(fs_original)))
#caso de  teste de pressão
fs_original = []
depths = []
for fs_result in pressure_test_fs:
    depths.append(fs_result[0])
    fs_original.append(fs_result[1])

#pyplot.plot(fs_original, depths, label='original tubular_teste_de_pressão, $fs_{min}$=%.2f' %(min(fs_original)))
# working on production string (id=3), we want to change the current tubular of the project to the first one in the dataframe
burst = 2
collapse = 1
triaxial = 1.25
axial = 1.3

numero_secoes = len(data['well_strings'][cs_id]['string_sections'])

for secao in range(numero_secoes):
    for new_cs in range(102):
        if (project.casing_strings[cs_id].interval == 'PRODUCTION'
            and 'PRODUCTION' == new_casing_catalog_Chilingarian.loc[new_cs, 'Fase'])\
            or (project.casing_strings[cs_id].interval == 'SURFACE'
            and 'SURFACE' == new_casing_catalog_Chilingarian.loc[new_cs, 'Fase'])\
            or (project.casing_strings[cs_id].interval == 'INTERMEDIATE'
            and 'INTERMEDIATE' == new_casing_catalog_Chilingarian.loc[new_cs, 'Fase'])\
            or (project.casing_strings[cs_id].interval == 'INTERMEDIATE'
            and 'INTERMEDIATE' == new_casing_catalog_Chilingarian.loc[new_cs, 'Fase']):

            data['well_strings'][cs_id]['string_sections'][secao]['pipe']['weight'] = new_casing_catalog_Chilingarian.loc[new_cs, 'Weight']
            data['well_strings'][cs_id]['string_sections'][secao]['pipe']['wt'] = new_casing_catalog_Chilingarian.loc[new_cs, 'wt']
            data['well_strings'][cs_id]['string_sections'][secao]['pipe']['grade']['name'] = new_casing_catalog_Chilingarian.loc[new_cs, 'Grade']
            data['well_strings'][cs_id]['string_sections'][secao]['pipe']['grade']['fymn'] = new_casing_catalog_Chilingarian.loc[new_cs, 'fy']
            data['well_strings'][cs_id]['string_sections'][secao]['pipe']['grade']['fumn'] = new_casing_catalog_Chilingarian.loc[new_cs, 'fu']
            data['well_strings'][cs_id]['string_sections'][secao]['pipe']['Price'] = new_casing_catalog_Chilingarian.loc[new_cs, 'Price']
            data['well_strings'][cs_id]['string_sections'][secao]['pipe']['od'] = new_casing_catalog_Chilingarian.loc[new_cs, 'OD']

        # other parameters must be also changed to work with ULS

            instance.input = convert_json(data)
            project = Converter.to_lccv_project(instance)
            ss = ScoreSolver(project=project)
            #Verificação dos fatores de segurança
            aa = Carregamentos(project=project)

            fu = new_casing_catalog_Chilingarian.loc[new_cs, 'fu']
            od = new_casing_catalog_Chilingarian.loc[new_cs, 'OD']
            wt = new_casing_catalog_Chilingarian.loc[new_cs, 'wt']
            kwall_mises = project.casing_strings[cs_id].string_sections[secao].kwall_mises

            if project.casing_strings[cs_id].interval == 'CONDUCTOR':
                selecao_carregamento = aa.revestimento_superior(casing_string_id=cs_id)
            if project.casing_strings[cs_id].interval == 'SURFACE':
                selecao_carregamento = aa.revestimento_superior(casing_string_id=cs_id)
            if project.casing_strings[cs_id].interval == 'INTERMEDIATE' and cs_id == 2:
                selecao_carregamento = aa.revestimento_intermediario(casing_string_id=cs_id)
            if project.casing_strings[cs_id].interval == 'INTERMEDIATE'and cs_id == 3:
                selecao_carregamento = aa.revestimento_intermediario2(casing_string_id=cs_id)
            if project.casing_strings[cs_id].interval == 'PRODUCTION':
                selecao_carregamento = aa.revestimento_produção(casing_string_id=cs_id)

            tamanho = len(depths)
            numero_carregamentos = len(selecao_carregamento)
            passou = True
            fator_s = None
            depths1 = None
            fator_s_triaxial = None
            for k in range(numero_carregamentos):
               # arquivo.write('\nDeslocamentos e forcas nos nos do contorno:\n')

                profundidade_carregamento = len(selecao_carregamento[k].load_result.internal_profile)
                fator_s = []
                depths1 = []
                fator_s_triaxial = []
                base = data['well_strings'][cs_id]['string_sections'][secao]['base_md']
                topo = data['well_strings'][cs_id]['string_sections'][secao]['top_md']
                for j in range(profundidade_carregamento):
                    base_j = selecao_carregamento[k].load_result.internal_profile[j][0]
                    if base_j <= base and base_j >= topo:
                        pe = selecao_carregamento[k].load_result.external_profile[j][1]
                        pi = selecao_carregamento[k].load_result.internal_profile[j][1]
                        Fa = selecao_carregamento[k].load_result.axial_profile[j][1]
                        dl = selecao_carregamento[k].load_result.axial_profile[j][2]
                        TQ = selecao_carregamento[k].load_result.axial_profile[j][3]
                        if (pe > pi): #collapso
                            fator_seguranca = selecao_carregamento[k].get_api_collapse_safety_factor()
                            if fator_seguranca[j][1] < collapse:
                                passou = False
                        if (pi > pe): #collapso: #ruptura
                            fator_seguranca = selecao_carregamento[k].get_api_burst_safety_factor()
                            if fator_seguranca[j][1] < burst:
                                passou = False
                        if passou is False:
                            break
                      #  fator_seguranca_mises = selecao_carregamento[k].get_api_von_mises_safety_factor()
                      #  if (fator_seguranca_mises[j][1] < triaxial):
                      #      passou = False
                      #     break
                     #   fator_axial =selecao_carregamento[k].get_api_axial_safety_factor()
                     #   if fator_axial[j][1] < axial: #Critério axial
                     #       passou = False
                     #       break
                        fator_s.append(fator_seguranca[j][1])
                      #  fator_s_triaxial.append(fator_seguranca_mises[j][1])
                        depths1.append(selecao_carregamento[k].load_result.internal_profile[j][0])
                if passou is False:
                    break
                arquivo.write('%f\n' % k)
                for jj in range(len(depths1)):
                    arquivo.write('%f\t' % (fator_s[jj]))
                    arquivo.write('%f\n' % (depths1[jj]))
        #            a = 1
                pyplot.plot(fator_s, depths1, label=k)
                #pyplot.plot(fator_s_triaxial, depths1, label=k)
                #pyplot.plot(fs_original, depths, label='our selection tubular_lost_returns, $fs_{min}$=%.2f' % (min(fs_original)))

            if passou:
                print('secao', secao+1)
                print('Tubo ótimo escolhido')
                print('fase', cs_id)
                print('od:', data['well_strings'][cs_id]['string_sections'][secao]['pipe']['od'])
                print('Weight:', data['well_strings'][cs_id]['string_sections'][secao]['pipe']['weight'])
                print('wt:', data['well_strings'][cs_id]['string_sections'][secao]['pipe']['wt'])
                print('grade:', data['well_strings'][cs_id]['string_sections'][secao]['pipe']['grade']['name'])
                print('Price:', data['well_strings'][cs_id]['string_sections'][secao]['pipe']['Price'])

                pyplot.legend()
                pyplot.title(cs_id)
                pyplot.show()
                break


#   for i in range(tamanho-3):
# Cenários de Collapso
#      if cementing_fs[i][1] < collapse or lost_returns_fs[i][1] < collapse:
#         passou = False
#        break
# Cenários de Burst
#   if pressure_test_fs[i][1] < burst or gas_kick_fs[i][1] < burst or influx_fs[i][1] < burst or \
#                                                           well_full_of_gas_fs[i][1] < burst:
#      passou = False
#     break
# Cenário triaxial
# if cementing_fs_mises[i][1] < triaxial or lost_returns_fs_mises[i][1] < triaxial or \
#     pressure_test__fs_mises[i][1] < triaxial or gas_kick_fs_mises[i][1] < triaxial or \
#         influx_fs_mises[i][1] < triaxial or well_full_of_gas_fs_mises[i][1] < triaxial:
#    passou = False
#    break