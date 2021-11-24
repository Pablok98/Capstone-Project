import gurobipy as gb
from optimization.parametros import *
from optimization.parametros import conseguir_cal
from optimization.parametros import recepcionado
from optimization.parametros import DI
from statistics import mean
import json

dic_neutro = {
    -7: 0,
    -6: 0,
    -5: 0,
    -4: 0,
    -3: 0,
    -2: 0,
    -1: 0
}

def Disponible_dic_a_lista(disponible_planta):
    lista = [0 for _ in range(5)]
    for i in disponible_planta.keys():
        aux = int(i[1])
        lista[aux - 1] = disponible_planta[i]
    return lista

def f_disponible(disp):
    lista = [0 for l in L]
    for n in disp.keys():#el diccionario tiene a todos los lotes?
        aux = n.split("_")[1]
        lista[int(aux)-1] = disp[n]
    return lista

def recepcionado_dic_a_lista(rec):
    lista = [0 for _ in range(5)]
    for i in rec.keys():
        aux = int(i[1])
        dic = {
        -7: rec[i][0],
        -6: rec[i][1],
        -5: rec[i][2],
        -4: rec[i][3],
        -3: rec[i][4],
        -2: rec[i][5],
        -1: rec[i][6]
        }
        lista[aux - 1] = dic
    print("Este es el parametro recepcionado: ")
    print(lista)
    return lista

def modelo_cosecha(dia, jornaleros_list, disponible_cosecha = None, rec = None, disponible_planta = None, paths=None):
    
    tam_cuadrillas = [5 for i in range(len(jornaleros_list))]
    ef_cuad = [[tam_cuadrillas[0] * ef_jorn for t in T] for l in L]  #Cuadrillas de 5 personas  

    K = jornaleros_list

    cal = conseguir_cal(dia)

    if dia == 0 or not disponible_cosecha:
        actual_DI = DI
    else:
        actual_DI = f_disponible(disponible_cosecha)

    m1 = gb.Model()
    # m.Params.OutputFlag = 0
    # m.Params.LogToConsole = 0

    #Variables Cosecha
    c_cosecha = m1.addVars(len(L), len(T), vtype=gb.GRB.BINARY, name='cosecha')
    c_auto = m1.addVars(len(L), len(T), vtype=gb.GRB.INTEGER, name ='auto')
    c_manual = m1.addVars(len(L), len(T), vtype=gb.GRB.INTEGER, name='manual')
    c_tolva = m1.addVars(len(L), len(T), vtype=gb.GRB.INTEGER, name='numtolva')
    c_bines = m1.addVars(len(L), len(T), vtype=gb.GRB.INTEGER, name='bines')
    c_cuad = m1.addVars(len(K), len(L), len(T), vtype=gb.GRB.BINARY, name='cuadrillas')
    c_man_bin = m1.addVars(len(K), len(L), len(T), vtype=gb.GRB.BINARY, name='asigbin')
    c_man_tolva = m1.addVars(len(K), len(L), len(T), vtype=gb.GRB.BINARY, name='asigtolva')
    c_cant_uva = m1.addVars(len(L), len(T), vtype=gb.GRB.CONTINUOUS, name='cantidad')
    c_monta = m1.addVars(len(L), len(T), vtype=gb.GRB.INTEGER, name='montacargas')
    c_disponibilidad = m1.addVars(len(L), len(T), vtype=gb.GRB.CONTINUOUS, name='disponibilidad')
    #c_cajones

    # #Variable Auxiliar
    # auxiliar = m1.addVar(vtype=GRB.CONTINUOUS, name='auxiliar')

    m1.update()


    #Restricciones Cosecha
    m1.addConstrs((c_cant_uva[l,t] <= ef_cos[l][t] * c_auto[l,t] + ef_cuad[l][t] * c_manual[l,t] for l in L for t in T))
    m1.addConstrs((c_cosecha[l,t] * M >= c_cant_uva[l,t] for l in L for t in T))
    m1.addConstrs((c_cosecha[l,t] <= cal[l][t] * M for l in L for t in T))
    m1.addConstrs((c_cant_uva[l,t] <= c_disponibilidad[l,t] for l in L for t in T))
    m1.addConstrs((c_cosecha[l,t] <= c_disponibilidad[l,t] for l in L for t in T))
    m1.addConstrs((c_cosecha[l,t] <= c_auto[l,t] + c_manual[l,t] for l in L for t in T))
    m1.addConstrs((c_auto[l,t] <=c_cosecha[l,t] * M for l in L for t in T)) #aca talvez para mejorar rendimiento se puede poner distintos M
    m1.addConstrs((c_manual[l,t] <=c_cosecha[l,t] * M for l in L for t in T))
    m1.addConstrs((sum(c_auto[l,t] for l in L) <= 5 for t in T))
    m1.addConstrs((gb.quicksum(c_manual[l, t] for l in L) <= 100 for t in T)) #aca es el limite de cuadrillas, podria no necesitarse
    m1.addConstrs((sum(c_cuad[k,l,t] for k in K) == c_manual[l,t] for l in L for t in T))
    m1.addConstrs((c_bines[l,t] >= ((ef_cos[l][t] * c_auto[l,t] + ef_cuad[l][t] * sum(c_man_bin[k,l,t] for k in K))/kg_bin) for l in L for t in T))
    m1.addConstrs((c_tolva[l,t] >= ((ef_cuad[l][t] * sum(c_man_tolva[k,l,t] for k in K))/kg_tolva) for l in L for t in T))
    m1.addConstrs((sum(c_bines[l,t] for l in L) <= 800 for t in T))
    m1.addConstrs((sum(c_tolva[l,t] for l in L) <= cantidad_tolvas for t in T))
    m1.addConstrs((sum(c_monta[l,t] for l in L)  <= cap_montacargas for t in T))
    m1.addConstrs((c_monta[l,t] >= c_cosecha[l,t] for l in L for t in T))
    m1.addConstrs((c_disponibilidad[l,t] == c_disponibilidad[l,t-1] - c_cant_uva[l,t-1] for l in L for t in T if t >= 1))
    m1.addConstrs((c_disponibilidad[l,0] == actual_DI[l] for l in L))#esta en toneladas?
    # m1.addConstr((auxiliar * quicksum(c_cosecha[l,t] for l in L for t in T) == quicksum(c_cosecha[l,t] * cal[l][t] for l in L for t in T)))
    #restriccion carros tolva 17
    #restriccion cajones??

    ########################

    VarJornaleros= gb.quicksum((c_cuad[k, l, t] * tam_cuadrillas[k] * ef_jorn) / 1000 for k in K for l in L for t in T)

    VarConductores= gb.quicksum((c_cant_uva[l, t]) / 15000 for l in L for t in T)

    VarTractores= gb.quicksum(((c_cant_uva[l, t]) / 1000) * 0.1 for l in L for t in T)

    VarTolva= gb.quicksum(((gb.quicksum(c_man_tolva[k, l, t] * tam_cuadrillas[k] * ef_jorn for k in K)) / 1000) * 0.1 for l in L for t in T)

    VarCosechadora= gb.quicksum(((ef_jorn * 4000 * 8 * c_auto[l, t]) / 1000) * 0.1 for l in L for t in T)

    RepBines= gb.quicksum(c_bines[l, t] for l in L for t in T) / 100

    PerdidaCalidad = gb.quicksum(c_cant_uva[l,t] * (1-cal[l][t])* 216.13 for l in L for t in T)

    m1.setObjective(PerdidaCalidad + gb.quicksum(c_disponibilidad[l, t] - c_cant_uva[l, t] for l in L for t in T) * 10 + VarJornaleros + VarConductores + VarTractores + VarTolva + VarCosechadora + RepBines)

    m1.update()
    m1.optimize()

    return m1


UTM = 52842

laborer_cost = 8 * UTM

jornaleros_obj = {}

for j in range(1, 20):

    objs = []
    jornaleros_list = [i for i in range(j)]
    cost = laborer_cost * j * tam_cuadrillas[0]

    for dia in [77, 84, 91, 98]:

        model = modelo_cosecha(dia, jornaleros_list)

        obj = model.getObjective().getValue()

        objs.append(obj + cost)

    jornaleros_obj[j] = mean(objs)

print(jornaleros_obj)

with open('data/initial_laborers.json', 'w') as file:
    json.dump(jornaleros_obj, file)
