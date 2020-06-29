# coding: utf-8
from scorelib.conf.form import FORM
from scorelib.estat.va import RV
from scorelib.estat.param import method_of_moments

# Definição da distribuição das v.a.
R = RV(dist_name='lognormal_2p')
S = RV(dist_name='norm')

# Calculando os parâmetros para a distribuição lognormal
param = method_of_moments(R, [50., (50*0.05)**4])

# Setando os parâmetros das v.a.
R.set_param(param)

S.set_param([5.0, 2.0])

# Definiação da função de falha
G = lambda x: x[0] - x[1]

# Vetor de variáveis aleatórias
X = [R, S]

model_reliability = FORM(RV=X, G=G)

print(model_reliability)