"""
Selecionar dentre os geradores 1, 2, 3 e 4 aqueles que minimizam o custo de operação
+--------+-----+-----+-----+------+
GERADOR  |  1  |  2  |  3  |   4  |
+--------+-----+-----+-----+------+
Custo    |  7  |  12 |  5  |  14  |
+--------+-----+-----+-----+------+
Potência | 300 | 600 | 500 | 1600 |
+--------+-----+-----+-----+------+
O mínimo de potência necessário para que haja a produção é 700.

Utilizando Branch and Bound, onde a problemática é limitar os bounds após cada Solve
do minimize de modo que em um determinado ponto o Solve chegue a um resultado discreto
para o problema proposto.

Para iniciar, chame a função verifica_solucao(solution.x, solution.fun).
"""

from math import inf
from numpy import transpose, dot

from numpy.matlib import zeros
from scipy.optimize import minimize


def objective(x):
    return x.dot(transpose([7, 12, 5, 14]))


    #return 7 * x1 + 12 * x2 + 5 * x3 + 14 * x4


def constraint1(x):

    return 300 * x[0] + 600 * x[1] + 500 * x[2] + 1600 * x[3] - 700

#Define constraints
cons1 = {'type': 'ineq', 'fun': constraint1}
cons2 = {'type': 'ineq', 'fun': lambda x: x.dot(transpose([300,600,500,1600])) -700}
constraints = [cons2]

# initial guess
x0 = zeros(4)

# Bounds
b = (0, 1)
bnds = [[[b, (1,1), (1,1), (0,0)]]]

j = 0

armazena_solucao = [14]  # Store possible solutions, but always keeping the best configuration with the lower cost
                          # +inf to start the Optimization
counter = [1]
generation = [0]

solution = minimize(objective, x0, bounds=bnds[generation[0]][j], method='SLSQP', constraints=constraints)
print(solution)
'''
def verifica_solucao(solution, custo):
    for i in range(4):
        if solution[i] == 0 or solution[i] == 1:
            if i == 3:
                compara_custo(custo, solution)


        else:
            return solution
            # subproblema1(i)     # Este subproblema torna subdivide o problema anterior para um lado
            # subproblema0(i)   # e este para o outro, dando origem a novos nós.
    return custo, solution


def compara_custo(custo, solution):
    c = armazena_solucao[0]
    if custo < c:
        c = custo
        armazena_solucao[0] = solution
        print(f'O custo atual é {c}, cuja configuração é {solution}')
    return c


def subproblema0(i):
    node = counter[0]
    gen = generation[0]
    bnds.append(bnds[gen][len(bnds) - node])
    bnds[gen][node][i] = [0, 0]
    solution = minimize(objective, x0, bounds=bnds[gen][node], method='SLSQP', constraints=constraints)
    node += 1
    counter[0] = node
    return solution


def subproblema1(i):
    node = counter[0]
    bnds.append(bnds[gen][node])
    bnds[gen][node][i] = [1, 1]
    solution = minimize(objective, x0, bounds=bnds[gen][node], method='SLSQP', constraints=constraints)
    return solution


def cria_geracao(gen, node):
    if gen >= 1:
        if len(bnds[gen]) < 2 * len(bnds[gen - 1]):
            bnds[gen].append(bnds[gen][node - 1])
        else:
            bnds.append(bnds[gen][node])    # Dá origem a uma nova geração
            generation[0] += 1
    else:
        bnds.append(bnds[gen][node])
    return gen
#print(verifica_solucao(solution.x, solution.fun))
'''