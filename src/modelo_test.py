from os import read
import numpy as np
#Tratar de cambiar aca la importacion usando el *
import gurobipy as gb
from optimization.parametros import *
from optimization.parametros import conseguir_cal
from optimization.parametros import recepcionado
from optimization.parametros import DI
from files import read_lot_data
import pickle
from os.path import join, isfile
from os import remove
import json

###############RELLENAR DIA EN EL QUE SE ESTA ACA PARA LA CALIDAD DE CADA LOTE##########
#dia = 77
#cal = conseguir_cal(dia)
#SimDisponible = 100  # Uva disponible para procesar en planta
#hola
dic_neutro = {
    -7: 0,
    -6: 0,
    -5: 0,
    -4: 0,
    -3: 0,
    -2: 0,
    -1: 0
}


def modelo_principal(dia, disponible_cosecha = None, rec = None, disponible_planta = None, paths=None, path_logger=None):


    cal = conseguir_cal2(dia)

    if not disponible_planta:
        SimDisponible = [0 for _ in range(5)]
    else:
        SimDisponible = Disponible_dic_a_lista(disponible_planta)
    if not rec:
        recepcionado = [ dic_neutro for i in P]
    else:
        recepcionado = recepcionado_dic_a_lista(rec)

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
    
    m1.addConstrs((c_cant_uva[l,t] <= ef_cos[l][t] * c_auto[l,t] + ef_cuad[l][t] * c_manual[l,t] for l in L for t in T)) #POR QUE NO IGUALAMOS?
    m1.addConstrs((c_cosecha[l,t] * M >= c_cant_uva[l,t] for l in L for t in T))
    m1.addConstrs((c_cosecha[l,t] <= cal[l][t] * M for l in L for t in T))
    m1.addConstrs((c_cant_uva[l,t] <= c_disponibilidad[l,t] for l in L for t in T))
    m1.addConstrs((c_cosecha[l,t] <= c_disponibilidad[l,t] for l in L for t in T))
    m1.addConstrs((c_cosecha[l,t] <= c_auto[l,t] + c_manual[l,t] for l in L for t in T))
    m1.addConstrs((c_auto[l,t] <=c_cosecha[l,t] * M for l in L for t in T)) #aca talvez para mejorar rendimiento se puede poner distintos M
    m1.addConstrs((c_manual[l,t] <=c_cosecha[l,t] * M for l in L for t in T))
    m1.addConstrs((sum(c_auto[l,t] for l in L) <= 5 for t in T))
    m1.addConstrs((gb.quicksum(c_manual[l, t] for l in L) <= cap_cuadrillas for t in T)) #aca es el limite de cuadrillas, podria no necesitarse    
    m1.addConstrs((sum(c_cuad[k,l,t] for k in K) == c_manual[l,t] for l in L for t in T)) 
    m1.addConstrs((c_bines[l,t] >= ((ef_cos[l][t] * c_auto[l,t] + ef_cuad[l][t] * sum(c_man_bin[k,l,t] for k in K))/kg_bin) for l in L for t in T)) 
    m1.addConstrs((c_tolva[l,t] >= ((ef_cuad[l][t] * sum(c_man_tolva[k,l,t] for k in K))/kg_tolva) for l in L for t in T))    
    m1.addConstrs((sum(c_bines[l,t] for l in L) <= 800 for t in T))
    m1.addConstrs((sum(c_tolva[l,t] for l in L) <= cantidad_tolvas for t in T))
    m1.addConstrs((sum(c_monta[l,t] for l in L)  == cap_montacargas for t in T))
    m1.addConstrs((c_monta[l,t] >= c_cosecha[l,t] for l in L for t in T))
    m1.addConstrs((c_disponibilidad[l,t] == c_disponibilidad[l,t-1] - c_cant_uva[l,t-1] for l in L for t in T if t >= 1))
    m1.addConstrs((c_disponibilidad[l,0] == actual_DI[l] for l in L))#esta en toneladas?

    # m1.addConstr((auxiliar * quicksum(c_cosecha[l,t] for l in L for t in T) == quicksum(c_cosecha[l,t] * cal[l][t] for l in L for t in T)))
    #restriccion carros tolva 17
    #restriccion cajones??

    ###################

    m2 = gb.Model()

    # Variables Transporte
    # t_ruta = m2.addVars(len(L), len(P), len(T), vtype=gb.GRB.BINARY, name='ruta')
    # t_camion = m2.addVars(len(C), len(L), len(T), vtype=gb.GRB.BINARY, name='camion')
    # t_camion_bin = m2.addVars(len(C), len(L), len(T), vtype=gb.GRB.BINARY, name='cambin')
    # t_camion_tolva = m2.addVars(len(C), len(L), len(T), vtype=gb.GRB.BINARY, name='camtolva')
    # camion_tercero_b = m2.addVars(len(L), len(T), vtype=gb.GRB.INTEGER, name='ctercerob')
    # camion_tercero_t = m2.addVars(len(L), len(T), vtype=gb.GRB.INTEGER, name='ctercerot')
    t_ruta = m2.addVars(len(L),len(P),len(T), vtype=gb.GRB.BINARY, name='ruta')
    t_camion = m2.addVars(len(C),len(L), len(P),len(T), vtype=gb.GRB.BINARY, name='camion')
    t_camion_bin = m2.addVars(len(C),len(L), len(P), len(T), vtype=gb.GRB.BINARY, name='cambin')
    t_camion_tolva = m2.addVars(len(C),len(L), len(P), len(T), vtype=gb.GRB.BINARY, name='camtolva')
    camion_tercero_b = m2.addVars(len(L), len(P),len(T), vtype=gb.GRB.INTEGER, name='ctercerob')
    camion_tercero_t = m2.addVars(len(L), len(P),len(T), vtype=gb.GRB.INTEGER, name='ctercerot')


    #######################

    m3 = gb.Model()

    # #Variables Planta

    p_proc = m2.addVars(len(P), len(T), vtype=gb.GRB.CONTINUOUS, name='procesado')
    p_fermentando = m2.addVars(len(P), len(T), vtype=gb.GRB.CONTINUOUS, name='fermentando')
    p_disp = m2.addVars(len(P), len(T), vtype=gb.GRB.CONTINUOUS, name='disp')
    p_rec = m2.addVars(len(P), len(T), vtype=gb.GRB.CONTINUOUS, name='recepcionado')
    p_terceros = m2.addVars(len(P), len(T), vtype=gb.GRB.CONTINUOUS, name='terceros')


    ########################
    VarJornaleros= gb.quicksum((c_cuad[k, l, t] * tam_cuadrillas[k] * ef_jorn) / 1000 for k in K for l in L for t in T)

    VarConductores= gb.quicksum((c_cant_uva[l, t]) / 15000 for l in L for t in T)

    VarTractores= gb.quicksum(((c_cant_uva[l, t]) / 1000) * 0.1 for l in L for t in T)

    VarTolva= gb.quicksum(((gb.quicksum(c_man_tolva[k, l, t] * tam_cuadrillas[k] * ef_jorn for k in K)) / 1000) * 0.01 for l in L for t in T)

    VarCosechadora= gb.quicksum(((ef_cos[l][t]  * c_auto[l, t]) / 1000) * 0.1 for l in L for t in T)

    RepBines= gb.quicksum(c_bines[l, t] for l in L for t in T) / 100

    PerdidaCalidad = gb.quicksum(c_cant_uva[l,t] * (1-cal[l][t])* 0.004 for l in L for t in T) #el 0.004 es el costo promedio en utm por kg de uva

    m1.setObjective(PerdidaCalidad + gb.quicksum((c_disponibilidad[l, t] - c_cant_uva[l, t]) * cal[l][t] * 0.004 for l in L for t in T) + VarJornaleros + VarConductores + VarTractores + VarTolva + VarCosechadora + RepBines)

    m1.Params.MIPGap = 0.02

    m1.setParam("LogFile", path_logger)
    m1.setParam("LogToConsole", 0)
    m2.setParam("LogFile", path_logger)
    m2.setParam("LogToConsole", 0)
    m3.setParam("LogFile", path_logger)
    m3.setParam("LogToConsole", 0)

    m1.update()
    m1.optimize()


    cosecha = [[0 for t in T] for l in L]
    bines = [[0 for t in T] for l in L]
    tolva = [[0 for t in T] for l in L]
    cantidad = [[0 for t in T] for l in L]
    for v in m1.getVars():

        if 'cosecha' in v.varName:
            _, i = v.varName.split('[')
            i = i[:-1]
            l, t = [int(n) for n in i.split(',')]

            try:
                cosecha[l][t] = v.x

            except KeyError:
                print("Hubo un error")

        elif 'bines' in v.varName:
            _, i = v.varName.split('[')
            i = i[:-1]
            l, t = [int(n) for n in i.split(',')]

            try:
                bines[l][t] = v.x

            except KeyError:
                print("Hubo un error")

        elif 'numtolva' in v.varName:

            _, i = v.varName.split('[')
            i = i[:-1]
            l, t = [int(n) for n in i.split(',')]
            try:
                tolva[l][t] = v.x

            except KeyError:
                print("Hubo un error")

        elif 'cantidad' in v.varName:
            _, i = v.varName.split('[')
            i = i[:-1]
            l, t = [int(n) for n in i.split(',')]

            try:
                cantidad[l][t] = v.x

            except KeyError:
                print("Hubo un error")
    
    print("\n")
    print("La calidad promedio es: ")
    total_lotes_cosechados = sum(cosecha[l][t] for l in L for t in T)
    if total_lotes_cosechados == 0:
        calidad_promedio = 0
    else:
        calidad_promedio = gb.quicksum(cal[l][t] * cosecha[l][t] for l in L for t in T) / total_lotes_cosechados
    print(calidad_promedio)



    #Restricciones Transporte
    # m2.addConstrs((gb.quicksum(t_ruta[l, p, t] for p in P) == cosecha[l][t] for l in L for t in T))
    # m2.addConstrs((camion_tercero_b[l,t] + gb.quicksum(t_camion_bin[c, l, t] * cap_bines[c] for c in C) >= bines[l][t] for l in L for t in T))
    # m2.addConstrs((camion_tercero_t[l,t] + gb.quicksum(t_camion_tolva[c, l, t] * cap_tolva[c] for c in C) >= tolva[l][t] for l in L for t in T))
    # m2.addConstrs((t_camion_tolva[c,l,t] + t_camion_bin[c,l,t] == t_camion[c,l,t] for c in C for l in L for t in T))
    # m2.addConstrs((gb.quicksum(t_camion[c, l, t] for c in C for l in L) <= 25 for t in T))


    # VarCamion = gb.quicksum((t_camion_bin[c,l,t] * cap_bines[c] *kg_bin * 30*costo_camion[c] + t_camion_tolva[c,l,t] * cap_tolva[c] *kg_tolva * 30*costo_camion[c]) for c in C for l in L for t in T)
    # TerCamion = gb.quicksum((camion_tercero_b[l,t]* 36 * kg_bin * 30 *1.15 * 0.02 / 1000 + camion_tercero_t[l,t] * 2* kg_tolva * 30 * 1.15*0.02 / 1000) for l in L for t in T)

    m2.addConstrs((gb.quicksum(t_ruta[l,p,t] for p in P) == cosecha[l][t] for l in L for t in T))
    m2.addConstrs((gb.quicksum(camion_tercero_b[l,p,t] for p in P) + gb.quicksum(t_camion_bin[c,l,p,t] * cap_bines[c] for c in C for p in P) >= bines[l][t] for l in L for t in T))
    m2.addConstrs((gb.quicksum(camion_tercero_t[l,p,t] for p in P) + gb.quicksum(t_camion_tolva[c,l,p,t] * cap_tolva[c] for c in C for p in P) >= tolva[l][t] for l in L for t in T))
    m2.addConstrs((t_camion_tolva[c,l,p,t] + t_camion_bin[c,l,p,t] == t_camion[c,l,p,t] for c in C for l in L for t in T for p in P))
    m2.addConstrs((gb.quicksum(t_camion[c,l,p,t] for c in C for l in L for p in P) <= 25 for t in T))
    #posibles agreggb.aciones
    m2.addConstrs((gb.quicksum(t_camion[c,l,p,t] for p in P) <= 1 for c in C for t in T for l in L))
    m2.addConstrs((gb.quicksum(t_camion[c,l,p,t] for l in L) <= 1 for c in C for t in T for p in P))
    m2.addConstrs((gb.quicksum(t_camion_tolva[c,l,p,t] for l in L) <= 1 for c in C for t in T for p in P))
    m2.addConstrs((gb.quicksum(t_camion_bin[c,l,p,t] for l in L) <= 1 for c in C for t in T for p in P))
    m2.addConstrs((gb.quicksum(t_camion[c,l,p,t] for c in C) >= t_ruta[l,p,t] for l in L for p in P for t in T)) #si hay ruta se tiene q asignar por lo menos uno
    m2.addConstrs((gb.quicksum(t_camion[c,l,p,t] for c in C) <= 1000 * t_ruta[l,p,t] for l in L for p in P for t in T)) #si no hay ruta no se puede asignar

    VarCamion = gb.quicksum(t_camion_bin[c,l,p,t] * cap_bines[c] *kg_bin * km[l][p]*costo_camion[c] + t_camion_tolva[c,l,p,t] * cap_tolva[c] *kg_tolva * km[l][p]*costo_camion[c] for c in C for l in L for t in T for p in P)
    TerCamion = gb.quicksum(camion_tercero_b[l,p,t] * kg_bin * km[l][p] * 100 + camion_tercero_t[l,p,t] * kg_tolva * km[l][p] * 100 for l in L for t in T for p in P)

    # m2.setObjective(TerCamion + VarCamion)
    # m2.setObjective(TerCamion+VarCamion)
    # m2.Params.MIPGap = 0.02
    # m2.update()
    # m2.optimize()

    ruta = [[[0 for t in T] for p in P] for l in L]
    for v in m2.getVars():

        if 'ruta' in v.varName:
            _, i = v.varName.split('[')
            i = i[:-1]
            l, p, t = [int(n) for n in i.split(',')]

            try:
                ruta[l][p][t] = v.x

            except KeyError:
                print("Hubo un error")
    # print(ruta)


    # # #Restricciones Planta
    m2.addConstrs((p_fermentando[p,t] == p_rec[p,t] + p_fermentando[p,t-1] - p_proc[p,t-1] for p in P for t in T if t >=1))
    m2.addConstrs((p_fermentando[p,0] == 0 for p in P))
    m2.addConstrs((p_proc[p,t] <= cap_proc[p]*1000 for p in P for t in T))
    m2.addConstrs((p_proc[p,t] <= p_disp[p,t] for p in P for t in T))

    if dia >= 7:
        m2.addConstrs((p_disp[p,t] == p_disp[p,t-1] + recepcionado[p][t - 7] - p_proc[p,t-1] for p in P for t in T if t >= 1))
    else:
        m2.addConstrs((p_disp[p,t] == 0 for p in P for t in T))
    m2.addConstrs((p_disp[p,t] == SimDisponible[p] for p in P for t in T if t == 0))

    m2.addConstrs((p_terceros[p,t] + p_rec[p,t] == sum(cantidad[l][t]*t_ruta[l,p,t] for l in L) for p in P for t in T))
    m2.addConstrs((sum(p_terceros[p,t] + p_rec[p,t] for p in P) >= sum(cantidad[l][t] for l in L) for p in P for t in T))
    m2.addConstrs((p_rec[p,t] <= cap_fermentacion[p]*0.3*1000 for p in P for t in T))
    m2.addConstrs((p_rec[p,t] <= cap_fermentacion[p]*1000 - p_fermentando[p,t] for p in P for t in T))
    m2.addConstrs((p_fermentando[p,t] <= cap_fermentacion[p]*1000 for p in P for t in T))

    VarPlanta = gb.quicksum((p_proc[p, t] * utm_kg[p]) for p in P for t in T)

    TercerizacionPlanta = gb.quicksum((p_terceros[p, t] * 1.12 * utm_kg[p]*100) for p in P for t in T)

    m2.setObjective(VarCamion+TerCamion+gb.quicksum(CFD * (1 - (p_fermentando[p, t] / (cap_fermentacion[p]*1000))) for p in P for t in T) + VarPlanta + TercerizacionPlanta)
    m2.Params.MIPGap = 0.02
    m2.update()
    m2.optimize()





    # with open('archivo.obj', 'w') as file:
    #     pickle.dump(m, file)
    # print(m.objVal)
    numtolot = {}
    lot_names = list(read_lot_data().keys())
    contador = 0
    for i in lot_names:
        numtolot[contador] = i
        contador += 1
    # lot_names = lot_names[:100]#pq esta en 100?
    truck_names = [i for i in range (25)]
    cuad_names = [i for i in range(100)]


    dict_traduccion = {
        0: 'P1',
        1: 'P2',
        2: 'P3',
        3: 'P4',
        4: 'P5'
    }
    monta = {}

    lot_harvest = {lot_names[i]: {} for i in range(len(lot_names))}
    lot_trucks = {truck_names[i]: {} for i in range(len(truck_names))}
    lot_cuad = {cuad_names[i]: {} for i in range(len(cuad_names))}
    lot_tolvas = {lot_names[i]: {} for i in range(len(lot_names))}
    lot_cosechadoras = {lot_names[i]: {} for i in range(len(lot_names))}
    lot_montas = {lot_names[i]: {} for i in range(len(lot_names))}
    truck_type = {truck_names[i]: {} for i in range(len(truck_names))}
    routes = {lot_names[i]: {} for i in range(len(lot_names))}
    plants = {f'P{i+1}': {} for i in range(5)}


    # v = m.getVarByName('cosecha')
    # lot_harvest = {lot_names[i]: {f'dia {t}': bool(m.getVarByName(f'cosecha[{i},{t}]').x) for t in range(7)} for i in range(len(lot_names))}
    # cosecha[95,0]

    for v in m1.getVars():
        if 'cosecha' in v.varName:
            _, i = v.varName.split('[')
            i = i[:-1]
            l, t = [int(n) for n in i.split(',')]

            try:
                lot_harvest[lot_names[l]]

            except KeyError:
                lot_harvest[lot_names[l]] = {}

            lot_harvest[lot_names[l]][f'dia {t}'] = bool(v.x)

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
                pass

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
                pass

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
                pass

            try:
                lot_montas[lot_names[l]]

            except KeyError:
                lot_montas[lot_names[l]] = {}

            lot_montas[lot_names[l]][f'dia {t}'] = v.x

            
    for v in m2.getVars():

        if 'ruta' in v.varName:
            _, i = v.varName.split('[')
            i = i[:-1]
            l, p, t = [int(n) for n in i.split(',')]
            nom_plant = dict_traduccion[int(p)]

            try:
                routes[lot_names[l]]

            except KeyError:
                routes[lot_names[l]] = {}
            
            if bool(v.x):
                routes[lot_names[l]][f'dia {t}'] = p

        if 'camion' in v.varName:
            _, i = v.varName.split('[')
            i = i[:-1]
            c, l, p, t = [int(n) for n in i.split(',')]
            try:
                lot_trucks[truck_names[c]]

            except KeyError:
                lot_trucks[truck_names[c]] = {}

            if bool(v.x):
                lot_trucks[truck_names[c]][f'dia {t}'] = numtolot[l]
        if 'cambin' in v.varName:
            _, i = v.varName.split('[')
            i = i[:-1]
            c, l, p, t = [int(n) for n in i.split(',')]
            try:
                lot_trucks[truck_names[c]]

            except KeyError:
                lot_trucks[truck_names[c]] = {}

            if bool(v.x):
                truck_type[truck_names[c]][f'dia {t}'] = True

        if 'camtolva' in v.varName:
            _, i = v.varName.split('[')
            i = i[:-1]
            c, l, p, t = [int(n) for n in i.split(',')]
            try:
                lot_trucks[truck_names[c]]

            except KeyError:
                lot_trucks[truck_names[c]] = {}

            if bool(v.x):
                truck_type[truck_names[c]][f'dia {t}'] = False

        if 'recepcionado' in v.varName:
            _, i = v.varName.split('[')
            i = i[:-1]
            p, t = [int(n) for n in i.split(',')]

            try:
                if v.x != 0 or v.x != -0:
                    nom_plant = dict_traduccion[int(p)]
                    plants[nom_plant][dia + t] = v.x
            except:
                print(v.varName, 'no tiene valor')
    if not paths:
        dict_paths = {
            join('data', 'results', 'lots.json'): lot_harvest,
            join('data', 'results', 'trucks.json'): lot_trucks,
            join('data', 'results', 'cuads.json'): lot_cuad,
            join('data', 'results', 'hoppers.json'): lot_tolvas,
            join('data', 'results', 'harvesters.json'): lot_cosechadoras,
            join('data', 'results', 'lift.json'): lot_montas,
            join('data', 'results', 'plants.json'): plants,
            join('data', 'results', 'truck_type.json'): truck_type,
            join('data', 'results', 'routes.json'): routes,
        }
    else:
        dict_paths = {
            join('results', 'lots.json'): lot_harvest,
            join('results', 'trucks.json'): lot_trucks,
            join('results', 'cuads.json'): lot_cuad,
            join('results', 'hoppers.json'): lot_tolvas,
            join('results', 'harvesters.json'): lot_cosechadoras,
            join('results', 'lift.json'): lot_montas,
            join('results', 'plants.json'): plants,
            join('results', 'truck_type.json'): truck_type,
            join('results', 'routes.json'): routes,
        }
    for path, data in dict_paths.items():
        if isfile(path):
            remove(path)
        with open(path, 'w') as archivo:
            json.dump(data, archivo, indent=4)

    print("Operación realizada con éxito")

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

def Disponible_dic_a_lista(disponible_planta):
    lista = [0 for _ in range(5)]
    for i in disponible_planta.keys():
        aux = int(i[1])
        lista[aux - 1] = disponible_planta[i]
    return lista

if __name__ == "__main__":
    modelo_principal(91)


