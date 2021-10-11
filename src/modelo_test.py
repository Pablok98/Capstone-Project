from os import read
import numpy as np
from gurobipy import *
from optimization.parametros import *
from optimization.parametros import conseguir_cal
from files import read_lot_data
import pickle
from os.path import join, isfile
from os import remove
import json
###############RELLENAR DIA EN EL QUE SE ESTA ACA PARA LA CALIDAD DE CADA LOTE########## 
cal = conseguir_cal(80)


m = Model()
# m.Params.OutputFlag = 0
# m.Params.LogToConsole = 0

#Variables Cosecha
c_cosecha = m.addVars(len(L),len(T),vtype=GRB.BINARY, name='cosecha')
c_auto = m.addVars(len(L),len(T), vtype=GRB.INTEGER, name ='auto')
c_manual = m.addVars(len(L),len(T), vtype=GRB.INTEGER, name='manual')
c_tolva = m.addVars(len(L),len(T), vtype=GRB.INTEGER, name='numtolva')
c_bines = m.addVars(len(L),len(T), vtype=GRB.INTEGER, name='bines')
c_cuad = m.addVars(len(K),len(L),len(T), vtype=GRB.BINARY, name='cuadrillas')
c_man_bin = m.addVars(len(K),len(L),len(T), vtype=GRB.BINARY, name='asigbin')
c_man_tolva = m.addVars(len(K),len(L),len(T), vtype=GRB.BINARY, name='asigtolva')
c_cant_uva = m.addVars(len(L),len(T), vtype=GRB.CONTINUOUS, name='cantidad')
c_monta = m.addVars(len(L),len(T), vtype=GRB.INTEGER, name='montacargas')
c_disponibilidad = m.addVars(len(L),len(T), vtype=GRB.CONTINUOUS, name='disponibilidad')
#c_cajones

#Variables Transporte
t_ruta = m.addVars(len(L),len(P),len(T), vtype=GRB.BINARY, name='ruta')
t_camion = m.addVars(len(C),len(L),len(T), vtype=GRB.BINARY, name='camion')
t_camion_bin = m.addVars(len(C),len(L),len(T), vtype=GRB.BINARY, name='cambin')
t_camion_tolva = m.addVars(len(C),len(L),len(T), vtype=GRB.BINARY, name='camtolva')
camion_tercero_b = m.addVars(len(L),len(T), vtype=GRB.INTEGER, name='ctercerob')
camion_tercero_t = m.addVars(len(L),len(T), vtype=GRB.INTEGER, name='ctercerot')

#Variables Planta
p_proc = m.addVars(len(P),len(T), vtype=GRB.CONTINUOUS, name='procesado')
p_fermentando = m.addVars(len(P),len(T), vtype=GRB.CONTINUOUS, name='fermentando')
p_disp = m.addVars(len(P),len(T), vtype=GRB.CONTINUOUS, name='disp')
p_rec = m.addVars(len(P),len(T), vtype=GRB.CONTINUOUS, name='recepcionado')
p_terceros = m.addVars(len(P),len(T), vtype=GRB.CONTINUOUS, name='terceros')

#Variable Auxiliar
auxiliar = m.addVar(vtype=GRB.CONTINUOUS, name='auxiliar')

m.update()


#Restricciones Cosecha
m.addConstrs((c_cant_uva[l,t] <= ef_cos[l][t] * c_auto[l,t] + ef_cuad[l][t] * c_manual[l,t] for l in L for t in T))
m.addConstrs((c_cosecha[l,t] * M >= c_cant_uva[l,t] for l in L for t in T))
m.addConstrs((c_cosecha[l,t] <= cal[l][t] * M for l in L for t in T))
m.addConstrs((c_cant_uva[l,t] <= c_disponibilidad[l,t] for l in L for t in T))
m.addConstrs((c_cosecha[l,t] <= c_disponibilidad[l,t] for l in L for t in T))
m.addConstrs((c_cosecha[l,t] <= c_auto[l,t] + c_manual[l,t] for l in L for t in T))
m.addConstrs((c_auto[l,t] <=c_cosecha[l,t] * M for l in L for t in T)) #aca talvez para mejorar rendimiento se puede poner distintos M
m.addConstrs((c_manual[l,t] <=c_cosecha[l,t] * M for l in L for t in T))
m.addConstrs((sum(c_auto[l,t] for l in L) <= 5 for t in T))
m.addConstrs((quicksum(c_manual[l,t] for l in L) <= 200 for t in T))
m.addConstrs((sum(c_cuad[k,l,t] for k in K) == c_manual[l,t] for l in L for t in T))
m.addConstrs((c_bines[l,t] >= ((ef_cos[l][t] * c_auto[l,t] + ef_cuad[l][t] * sum(c_man_bin[k,l,t] for k in K))/kg_bin) for l in L for t in T))
m.addConstrs((c_tolva[l,t] >= ((ef_cuad[l][t] * sum(c_man_tolva[k,l,t] for k in K))/kg_tolva) for l in L for t in T))
m.addConstrs((sum(c_bines[l,t] for l in L) <= 800 for t in T))
m.addConstrs((sum(c_tolva[l,t] for l in L) <= cantidad_tolvas for t in T))
m.addConstrs((sum(c_monta[l,t] for l in L)  <= cap_montacargas for t in T))
m.addConstrs((c_monta[l,t] >= sum(t_camion_bin[c,l,t] for c in C) for l in L for t in T))
m.addConstrs((c_disponibilidad[l,t] == c_disponibilidad[l,t-1] - c_cant_uva[l,t-1] for l in L for t in T if t >= 1))
m.addConstrs((c_disponibilidad[l,0] == DI[l] for l in L))
#restriccion carros tolva 17
#restriccion cajones??

#Restricciones Transporte
m.addConstrs((sum(t_ruta[l,p,t] for p in P) == c_cosecha[l,t] for l in L for t in T))
m.addConstrs((camion_tercero_b[l,t] + sum(t_camion_bin[c,l,t] * cap_bines[c] for c in C) >= c_bines[l,t] for l in L for t in T))
m.addConstrs((camion_tercero_t[l,t] + sum(t_camion_tolva[c,l,t] * cap_tolva[c] for c in C) >= c_tolva[l,t] for l in L for t in T))
m.addConstrs((t_camion_tolva[c,l,t] + t_camion_bin[c,l,t] == t_camion[c,l,t] for c in C for l in L for t in T))
m.addConstrs((quicksum(t_camion[c,l,t] for c in C for l in L) <= 25 for t in T))

#Restricciones Planta
m.addConstrs((p_fermentando[p,t] == p_rec[p,t] + p_fermentando[p,t-1] - p_proc[p,t-1] for p in P for t in T if t >=1))
m.addConstrs((p_fermentando[p,0] == 0 for p in P))
m.addConstrs((p_proc[p,t] <= cap_proc[p] for p in P for t in T))
m.addConstrs((p_proc[p,t] <= p_disp[p,t] for p in P for t in T))
m.addConstrs((p_disp[p,t] == p_disp[p,t-1] + p_rec[p,t-7] - p_proc[p,t-1] for p in P for t in T if t >= 7))
m.addConstrs((p_disp[p,t] == 0 for p in P for t in T if t < 7))
m.addConstrs((p_terceros[p,t] + p_rec[p,t] == sum(c_cant_uva[l,t]*t_ruta[l,p,t] for l in L) for p in P for t in T))
m.addConstrs((sum(p_terceros[p,t] + p_rec[p,t] for p in P) >= sum(c_cant_uva[l,t] for l in L) for p in P for t in T))
m.addConstrs((p_rec[p,t] <= cap_fermentacion[p]*0.3 for p in P for t in T))
m.addConstrs((p_rec[p,t] <= cap_fermentacion[p] - p_fermentando[p,t] for p in P for t in T))
m.addConstrs((p_fermentando[p,t] <= cap_fermentacion[p] for p in P for t in T))



#Auxiliar
m.addConstr((auxiliar * quicksum(c_cosecha[l,t] for l in L for t in T) == quicksum(c_cosecha[l,t] * cal[l][t] for l in L for t in T)))
a = 0.9
m.update()

#Funcion Objetivo
costo_terceros = quicksum(1.12*80*p_terceros[p,t] for p in P for t in T) \
                 + quicksum((camion_tercero_t[l,t] + camion_tercero_b[l,t])*1.15*100 for t in T for l in L)
sobrecosto_ocupacion = quicksum(CFD * (1 - (p_fermentando[p,t]/cap_fermentacion[p])) for p in P for t in T)
promedio = quicksum(c_cosecha[l,t] * cal[l][t] for l in L for t in T)

m.setObjective(costo_terceros + sobrecosto_ocupacion + penalizacion*(1 - auxiliar) + quicksum(costo_procesado[p]*p_proc[p,t] for p in P for t in T))

m.update()
m.optimize()

# with open('archivo.obj', 'w') as file:
#     pickle.dump(m, file)
# print(m.objVal)
numtolot = {}
lot_names = list(read_lot_data().keys())
contador = 0
for i in lot_names:
    numtolot[contador] = i
    contador += 1
lot_names = lot_names[:100]
truck_names = [i for i in range (25)]
cuad_names = [i for i in range(100)]



monta = {}

lot_harvest = {lot_names[i]: {} for i in range(len(lot_names))}
lot_trucks = {truck_names[i]: {} for i in range(len(truck_names))}
lot_cuad = {cuad_names[i]: {} for i in range(len(cuad_names))}
lot_tolvas = {lot_names[i]: {} for i in range(len(lot_names))}
lot_cosechadoras = {lot_names[i]: {} for i in range(len(lot_names))}
lot_montas = {lot_names[i]: {} for i in range(len(lot_names))}


# v = m.getVarByName('cosecha')
# lot_harvest = {lot_names[i]: {f'dia {t}': bool(m.getVarByName(f'cosecha[{i},{t}]').x) for t in range(7)} for i in range(len(lot_names))}
# cosecha[95,0]

for v in m.getVars():

    if 'cosecha' in v.varName:
        _, i = v.varName.split('[')
        i = i[:-1]
        l, t = [int(n) for n in i.split(',')]

        try:
            lot_harvest[lot_names[l]]

        except KeyError:
            lot_harvest[lot_names[l]] = {}

        lot_harvest[lot_names[l]][f'dia {t}'] = bool(v.x)

    if 'camion' in v.varName:
        _, i = v.varName.split('[')
        i = i[:-1]
        c, l, t = [int(n) for n in i.split(',')]
        try:
            lot_trucks[truck_names[c]]

        except KeyError:
            lot_trucks[truck_names[c]] = {}

        if bool(v.x):
            lot_trucks[truck_names[c]][f'dia {t}'] = numtolot[l]

    if 'cuadrillas' in v.varName:
        _, i = v.varName.split('[')
        i = i[:-1]
        k, l, t = [int(n) for n in i.split(',')]
        try:
            lot_cuad[cuad_names[k]]

        except KeyError:
            lot_cuad[cuad_names[k]] = {}

        if bool(v.x):
            lot_cuad[cuad_names[k]][f'dia {t}'] = numtolot[l]

    if 'numtolva' in v.varName:
        _, i = v.varName.split('[')
        i = i[:-1]
        l, t = [int(n) for n in i.split(',')]
        if v.x != 0 or v.x != -0:
            print(l, t, v.x)

        try:
            lot_tolvas[lot_names[l]]

        except KeyError:
            lot_tolvas[lot_names[l]] = {}

        lot_tolvas[lot_names[l]][f'dia {t}'] = v.x

    if 'auto' in v.varName:
        _, i = v.varName.split('[')
        i = i[:-1]
        l, t = [int(n) for n in i.split(',')]
        if v.x != 0 or v.x != -0:
            print(l, t, v.x)

        try:
            lot_cosechadoras[lot_names[l]]

        except KeyError:
            lot_cosechadoras[lot_names[l]] = {}

        lot_cosechadoras[lot_names[l]][f'dia {t}'] = v.x

    if 'montacargas' in v.varName:
        _, i = v.varName.split('[')
        i = i[:-1]
        l, t = [int(n) for n in i.split(',')]
        if v.x != 0 or v.x != -0:
            print(l, t, v.x)

        try:
            lot_montas[lot_names[l]]

        except KeyError:
            lot_montas[lot_names[l]] = {}

        lot_montas[lot_names[l]][f'dia {t}'] = v.x

dict_paths = {
    join('data', 'results', 'lots.json'): lot_harvest,
    join('data', 'results', 'trucks.json'): lot_trucks,
    join('data', 'results', 'cuads.json'): lot_cuad,
    join('data', 'results', 'hoppers.json'): lot_tolvas,
    join('data', 'results', 'harvesters.json'): lot_cosechadoras,
    join('data', 'results', 'lift.json'): lot_montas,
}
for path, data in dict_paths.items():
    if isfile(path):
        remove(path)
    with open(path, 'w') as archivo:
        json.dump(data, archivo, indent=4)



#print(lot_montas)