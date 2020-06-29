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
from scorelib.conf.form import FORM
from scorelib.estat.va import RV
from scorelib.design.standards.n_2752_y_2014_design_standard import *
from scorelib.proj_poco.rev_tubos_lib import *
from scorelib.estat.param import method_of_moments
from scorelib.design.casing_design import MinimumAllowableSafetyFactorsBuilder

with open("C:/casing_selection-master/scripts/score_projects/project454.json", 'r', encoding="latin-1") as f:
    data = json.load(f)
arquivo = open("C:/Users/luis_/Desktop/casing_selection-master/scripts/arquivo_teste_confiabilidade.txt", 'w')
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

    Resistencia_conf3 = ISO_Collapse(Pint=Pi, Fa=Fa,
                 fymn=u1[3],
                 D=u1[0], t=u1[1],
                 ov=u1[5],
                 ec=u1[6],
                 rs=rs,
                 hn=hn,
                 E=u1[2],
                 nu=0.3,
                 kedes=kedes,
                 kydes=kydes,
                 Htdes=Htdes)

    return (u1[4]*Resistencia_conf3) - abs(Pe - Pi)

def von_mises_1 (u1):
    mises = vonMisesCritical(Pint=Pi,
                                      Pout=Pe,
                                      Fa=Fa,
                                      D=u1[0],
                                      t=u1[1],
                                      tmin=(u1[1] -
                                            (1. - kwall_mises) * u1[1]),
                                      E=u1[2],
                                      # DL=0,
                                      DL=dl,
                                      TQ=TQ)
    return u1[3]-mises[0]

def von_mises_uls (u1):
    mises = vonMisesCritical(Pint=Pi,
                                      Pout=Pe,
                                      Fa=Fa,
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
    Resistencia_conf3 = iso_ductilerupture(pext=Pe, fa=Fa, fumn=u1[2],
                                           od=u1[0], wt=u1[1], n=n,
                                           kwall=kwall_burst, ka=ka, an=an)

    return (u1[3]*Resistencia_conf3) - abs(Pe - Pi)



def API_collapse (u1):
    Resistencia_conf = API_Collapse(u1[3], u1[0], u1[1], u1[2], 0.3)

    return Resistencia_conf - abs(Pe - Pi)

def API_burst (u1):
    Resistencia_conf = API_Burst(u1[2], u1[0], u1[1], kwall_burst)

    return Resistencia_conf - abs(Pe-Pi)

def API_axial (u1):
    Resistencia_conf = API_Axial(u1[2], u1[0], u1[1])

    return Resistencia_conf - abs(Fa)

def uls_axial(u1):
    Resistencia_conf = API_Axial(u1[2], u1[0], u1[1])

    return Resistencia_conf - abs(Fa)

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
burst = 1.1
collapse = 1.0
triaxial = 1.25
numero_secoes = len(data['well_strings'][cs_id]['string_sections'])
#if project.casing_strings[cs_id].interval is 'PRODUCTION':
# Entrada da seleção de diâmetros por fase
#Producao = project.casing_strings[4].interval
#Surface = project.casing_strings[1].interval
#intermediario = project.casing_strings[2].interval
#intermediario2 = project.casing_strings[3].interval
#condutor = project.casing_strings[0].interval

for secao in range(numero_secoes):
    for new_cs in range(102):
        #Escolha  do diâmetro a ser usado por revestimento (Produção 7, Superficie : 13.375, Intermediario : 9.675)
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

            #data['well_strings'][cs_id]['string_sections'][secao]['pipe']['weight'] = 29
            #strings_sections = data['well_strings'][cs_id]['string_sections'][secao]
            # other parameters must be also changed to work with ULS
            #ov = project.casing_strings[cs_id].string_sections[secao].geometric_statistics.ov_mean
            #ec = project.casing_strings[cs_id].string_sections[secao].geometric_statistics.ec_mean
            rs = project.casing_strings[cs_id].string_sections[secao].material.statistics.rs_mean
            hn = project.casing_strings[cs_id].string_sections[secao].material.hn
            kedes = project.casing_strings[cs_id].string_sections[secao].material.kedes
            kydes = project.casing_strings[cs_id].string_sections[secao].material.kydes
            Htdes = project.casing_strings[cs_id].string_sections[secao].material.Htdes
            instance.input = convert_json(data)
            project = Converter.to_lccv_project(instance)
            ss = ScoreSolver(project=project)
            # Verificação dos fatores de segurança
            aa = Carregamentos(project=project)


            if project.casing_strings[cs_id].interval == 'CONDUCTOR':
                selecao_carregamento = aa.revestimento_superior(casing_string_id=cs_id)
            if project.casing_strings[cs_id].interval == 'SURFACE':
                selecao_carregamento = aa.revestimento_superior(casing_string_id=cs_id)
            if project.casing_strings[cs_id].interval == 'INTERMEDIATE' and cs_id == 2:
                selecao_carregamento = aa.revestimento_intermediario(casing_string_id=cs_id)
            if project.casing_strings[cs_id].interval == 'INTERMEDIATE' and cs_id == 3:
                selecao_carregamento = aa.revestimento_intermediario2(casing_string_id=cs_id)
            if project.casing_strings[cs_id].interval == 'PRODUCTION':
                selecao_carregamento = aa.revestimento_produção(casing_string_id=cs_id)

            #dados estatísticos
            # Definição da distribuição das v.a.

            D = RV(dist_name='norm')
            t = RV(dist_name='norm')
            E = RV(dist_name='norm')
            ov = RV(dist_name='weibull_2p')
            ec = RV(dist_name='weibull_2p')
            errokt = RV(dist_name='norm')
            erroks = RV(dist_name='norm')
            fymn = RV(dist_name='norm')
            fumn = RV(dist_name='norm')

            D.set_param([new_casing_catalog_Chilingarian.loc[new_cs, 'OD'] * 1.0059,
                         (new_casing_catalog_Chilingarian.loc[new_cs, 'OD'] * 1.0059) * 0.00181])
            #D.set_param([15 * 1.0059, (13 * 1.0059) * 0.00181])
            t.set_param([new_casing_catalog_Chilingarian.loc[new_cs, 'wt'] * 1.0069,
                         (new_casing_catalog_Chilingarian.loc[new_cs, 'wt']*1.0069) * 0.0259])
            #t.set_param([0.625 * 1.0069, (0.595 * 1.0069) * 0.259])
            fymn.set_param([new_casing_catalog_Chilingarian.loc[new_cs, 'fy'] * 1.10,
                            (new_casing_catalog_Chilingarian.loc[new_cs, 'fy'] * 1.10) * 0.036])
            fumn.set_param([new_casing_catalog_Chilingarian.loc[new_cs, 'fu'] * 1.1180,
                            (new_casing_catalog_Chilingarian.loc[new_cs, 'fu'] * 1.1180) * 0.098])

            E.set_param([30e6, 30e6*0.035])
            errokt.set_param([0.9991, 0.9991*0.0670])
            erroks.set_param([1.004, 1.004*0.0470])
            # Calculando os parâmetros para a distribuição weibull
            param_ov = method_of_moments(ov, [0.217, (0.217*0.541)**2])
            param_ec = method_of_moments(ec, [3.924, (3.924*0.661)**2])
            ov.set_param(param_ov)
            ec.set_param(param_ec)
            #fymn.set_param([new_casing_catalog.loc[new_cs, 'fy'] * 1.10,
                   #         (new_casing_catalog.loc[new_cs, 'fy'] * 1.10) * 0.036])


            #D = RV("normal", new_casing_catalog.loc[new_cs, 'OD'] * 1.0059,
            #       (new_casing_catalog.loc[new_cs, 'OD'] * 1.0059) * 0.00181)
            #t = RV("normal", new_casing_catalog.loc[new_cs, 'wt'] * 1.0069,
            #       (new_casing_catalog.loc[new_cs, 'wt'] * 1.0069) * 0.259)
            #E = RV("normal", 30e6, 30e6 * 0.035)

            kwall_mises = project.casing_strings[cs_id].string_sections[secao].kwall_mises
            kwall_burst = project.casing_strings[cs_id].string_sections[secao].kwall_burst
            n = project.casing_strings[cs_id].string_sections[secao].material.n
            ka = project.casing_strings[cs_id].string_sections[secao].material.ka
            an = project.casing_strings[cs_id].string_sections[secao].material.an
            #errokt = RV("normal", 0.9991, 0.0670)
            #erroks = RV("normal", 1.004, 0.0470)

            tamanho = len(depths)
            numero_carregamentos = len(selecao_carregamento)
            passou = True
            aux_beta=None
            depths1=None
            for k in range(numero_carregamentos):
                aux_beta = []
                depths1 = []
                profundidade_carregamento = len(selecao_carregamento[k].load_result.internal_profile)
                base = data['well_strings'][cs_id]['string_sections'][secao]['base_md']
                topo = data['well_strings'][cs_id]['string_sections'][secao]['top_md']
                for j in range(profundidade_carregamento):
                    base_j = selecao_carregamento[k].load_result.internal_profile[j][0]
                    if base_j <= base and base_j >= topo:
                        Pe = selecao_carregamento[k].load_result.external_profile[j][1]
                        Pi = selecao_carregamento[k].load_result.internal_profile[j][1]
                        Fa = selecao_carregamento[k].load_result.axial_profile[j][1]
                        dl = selecao_carregamento[k].load_result.axial_profile[j][2]
                        TQ = selecao_carregamento[k].load_result.axial_profile[j][3]
                        # Caracterização das variáveis estatísticas
                        #Pe = RV("normal", pe0, pe0 * 0)
                        #Pi = RV("normal", pi0, pi0 * 0)
                        #Fa = RV("normal", fa0, fa0 * 0)
                        X1 = [D, t, E, fymn, errokt, ov, ec]  # KT
                        X2 = [D, t, E, fymn]  # vonmises
                        X3 = [D, t, fumn, erroks]  # KS
                        X4 = [D, t, E, fymn] #API collapse
                        X5 = [D, t, fymn] #API Burst
                        X6 = [D, t, fymn] #API AXIAL
                        X7 = [D, t, fumn] #uls AXIAL
                        X8 = [D, t, E, fumn] #von mises uls
                        # Apenas Limite elástico !!!!!!
                        if (Pe < Pi):
                            result2 = FORM(RV=X5, G=API_burst) #API_burst
                        if (Pe > Pi):
                            result2 = FORM(RV=X4, G=API_collapse) #API_collapse
                        result3 = FORM(RV=X6, G=API_axial)  # API_axial
                        result1 = FORM(RV=X2, G=von_mises_1) #von mises els

                        if Pe > Pi and result2.pf > 0.001: #Colapso
                            passou = False
                            break
                        if Pe < Pi and result2.pf > 0.00001: #Ruptura
                            passou = False
                            break
                        if result3.pf > 0.001: #Axial
                            passou = False
                            break
                        if result1.pf > 0.001: #von mises
                            passou = False
                            break
                        aux_beta.append(result2.beta)
                        depths1.append(selecao_carregamento[k].load_result.internal_profile[j][0])
                    #depths.append(fs_result[0])
                if passou is False:
                    break
                arquivo.write('%f\n' % k)
                for jj in range(len(depths1)):
                    arquivo.write('%f\t' % (aux_beta[jj]))
                    arquivo.write('%f\n' % (depths1[jj]))
                pyplot.plot(aux_beta, depths1, label=k)
            if passou:
                print('secao', secao + 1)
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
#depths2 = []
#beta1 = []
#for i in range(37):
#    depths2.append(depths1[i])
#    beta1.append(aux_beta[i])

#pyplot.plot(aux_beta, depths1, label=k)

a = 1

#pyplot.plot(fs_original, depths, label='our selection tubular_lost_returns, $fs_{min}$=%.2f' %(min(fs_original)))
#pyplot.legend()
#pyplot.show()