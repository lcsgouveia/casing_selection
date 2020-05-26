# coding: utf-8
from scorelib.conf.form import *
from scorelib.estat.va import *
from scorelib.estat.param import *
from scorelib.design.standards.n_2752_y_2014_design_standard import *

l = 20.

# Função de falha - flexão
def viga_flexao(u):
    return u[1] - (1/8.) * u[0] * l ** 2


# Variáveis aleatórias
w = RV("normal", 6.0, 1.5)
mo = RV("normal", 470.0, 47.0)
X = [w, mo]
result = FORM(X, viga_flexao)


