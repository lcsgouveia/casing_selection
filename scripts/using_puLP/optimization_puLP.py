from pulp import *
import pandas as pd

df = pd.read_excel("diet_medium.xls", nrows=17)

prob = LpProblem("SimpleDietProblem", LpMinimize)

food_items = list(df['Foods'])
costs = dict(zip(food_items, df['PriceServing']))
calories = dict(zip(food_items, df['Calories']))
fat = dict(zip(food_items, df['TotalFat']))
carbs = dict(zip(food_items,  df['Carbohydrates']))
fiber = dict(zip(food_items, df['DietaryFiber']))
protein = dict(zip(food_items, df['Protein']))

food_vars = LpVariable.dicts("Food",food_items,0,cat='Continuous')
#Objective
prob += lpSum([costs[i] * food_vars[i] for i in food_items])

#Constraints
prob += lpSum([calories[f] * food_vars[f] for f in food_items]) >= 800
prob += lpSum([calories[f] * food_vars[f] for f in food_items]) <= 1300

prob += lpSum([fat[f] * food_vars[f] for f in food_items]) >= 20
prob += lpSum([fat[f] * food_vars[f] for f in food_items]) <= 50

prob += lpSum([carbs[f] * food_vars[f] for f in food_items]) >= 130
prob += lpSum([carbs[f] * food_vars[f] for f in food_items]) <= 200

prob += lpSum([fiber[f] * food_vars[f] for f in food_items]) >= 60
prob += lpSum([fiber[f] * food_vars[f] for f in food_items]) <= 125

prob += lpSum([protein[f] * food_vars[f] for f in food_items]) >= 100
prob += lpSum([protein[f] * food_vars[f] for f in food_items]) <= 150

#Solving the Problem

prob.solve()
print('Status:', LpStatus[prob.status])
print("Therefore, the optimal (least cost) balanced diet consists of\n"+"-"*110)
for v in prob.variables():
    if v.varValue>0:
        print(v.name, "=", v.varValue)

print("The total cost of this balanced diet is: ${}".format(round(value(prob.cost_linear_fitted), 2)))