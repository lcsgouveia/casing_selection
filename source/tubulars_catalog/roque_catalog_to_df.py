import pandas
from pandas import read_excel
from scorelib.proj_poco.rev_tubos_lib import API_Burst, API_Collapse, API_Axial

casing_properties = read_excel('./rep/roque1996b.xlsx').copy()


grade_fy_passer = {'K55': 55000, 'N80': 80000, 'C95': 95000, 'S95': 95000, 'C75': 75000, 'P110': 110000, 'H40': 40000,
                   'V150': 150000}
grade_fu_passer = {'K55': 95000, 'N80': 100000, 'C95': 110000, 'S95': 110000, 'C75': 95000, 'P110': 125000,
                   'H40': 60000, 'V150': 175000}

casing_properties['Burst SCORE'] = None
casing_properties['Collapse SCORE'] = None
casing_properties['Axial SCORE'] = None
for row in range(casing_properties.shape[0]):
    grade = casing_properties.loc[row, 'Grade']
    od = casing_properties.loc[row, 'OD']
    wt = casing_properties.loc[row, 'wt']
    kwall = 0.875
    young = 3E8
    poisson = 0.3

    casing_properties.loc[row, 'Burst SCORE'] = API_Burst(Yp=grade_fy_passer[grade], D=od, t=wt, kwall=kwall)
    casing_properties.loc[row, 'Collapse SCORE'] = API_Collapse(Yp=grade_fy_passer[grade], D=od, t=wt, E=young, nu=poisson)
    casing_properties.loc[row, 'Axial SCORE'] = API_Axial(Yp=grade_fy_passer[grade], D=od, t=wt)

# casing_properties.to_clipboard()

# new casing catalog table
new_casing_catalog = pandas.DataFrame(columns=['OD', 'Weight', 'Grade', 'wt', 'fy', 'old_ids'])

aux_i = []
for row_i in casing_properties.iterrows():
    tubular_id_i = row_i[0]
    tubular_properties_i = row_i[1]

    # verifica se o tubular já foi computado
    row_done = False
    for row_j in new_casing_catalog.iterrows():
        if tubular_id_i in new_casing_catalog.loc[row_j[0], 'old_ids']:
            row_done = True
            break

    if row_done:
        continue
    aux_i = [tubular_id_i]

    for row_j in casing_properties.iterrows():
        tubular_id_j = row_j[0]
        tubular_properties_j = row_j[1]
        if tubular_id_j > tubular_id_i and \
                tubular_properties_i['OD'] == tubular_properties_j['OD'] and \
                tubular_properties_i['Weight'] == tubular_properties_j['Weight'] and \
                tubular_properties_i['Grade'] == tubular_properties_j['Grade']:

            aux_i.append(tubular_id_j)
    # print(tubular_id_i, aux_i, min(casing_properties.loc[aux_i, 'Price']))

    new_casing_catalog = new_casing_catalog.append({'OD': tubular_properties_i['OD'],
                                                    'Weight': tubular_properties_i['Weight'],
                                                    'Grade': tubular_properties_i['Grade'],
                                                    'wt': tubular_properties_i['wt'],
                                                    'fy': grade_fy_passer[tubular_properties_i['Grade']],
                                                    'old_ids': aux_i, 'Price': tubular_properties_i['Price'],
                                                    'fu': grade_fu_passer[tubular_properties_i['Grade']]},
                                                   ignore_index=True)
aux_ii = 1

#excel = pandas.ExcelWriter('new_casing_catalog.xlsx', engine='xlsxwriter')
#new_casing_catalog.to_excel(excel, sheet_name='Dados de um ANO específico')
#excel.save()