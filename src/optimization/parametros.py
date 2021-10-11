import numpy as np
import os
import json
import pandas as pd

L = [i for i in range(100)]
T = [i for i in range(7)]
K = [i for i in range(100)]
C = [i for i in range(20)]  #Camiones desde 0 hasta 25 -> 7A, 3B, 8C, 7D
P = [0,1,2,3,4]
M = 1000000

###############################################################################
ef_cos = [[4000 * 10 for t in T] for l in L]  #10 hras  ->  #kg/día                       #lt
ef_jorn = 700 #kg/dia                                           #lt
ef_cuad = [[5 * ef_jorn for t in T] for l in L]  #Cuadrillas de 5 personas                #lt
###############################################################################


###############################################################################
cap_cuadrillas = 200 # cuantas cuadrillas podremos ocupar
###############################################################################


def load_km():
    curr_dir = os.path.dirname(__file__)
    parent = os.path.split(curr_dir)[0]
    file = pd.read_excel(os.path.join(parent, 'data', 'datos_entregados.xlsx'), engine='openpyxl')
    lista = []
    for i in range (290):
        lista.append([file.iloc[i]['km a P1'], file.iloc[i]['km a P2'], file.iloc[i]['km a P3'], 
        file.iloc[i]['km a P4'], file.iloc[i]['km a P5']])
    return lista

def dic_lote():
    curr_dir = os.path.dirname(__file__)
    #print(curr_dir)
    parent = os.path.split(curr_dir)[0]
    file = pd.read_excel(os.path.join(parent, 'data', 'datos_entregados.xlsx'), engine='openpyxl')
    lots = {}
    for i in range (290):
        lots[i] = file.iloc[i]['Lote COD']
    return lots

def load_DI():
    curr_dir = os.path.dirname(__file__)
    #print(curr_dir)
    parent = os.path.split(curr_dir)[0]
    file = pd.read_excel(os.path.join(parent, 'data', 'datos_entregados.xlsx'), engine='openpyxl')
    lista = []
    for i in range (290):
        lista.append(1000*file.iloc[i]['Tn  '])
    return lista


###############################################################################
km = load_km() #lp
###############################################################################
#l
DI = load_DI() #tn


#p
cap_proc = [150, 65, 100, 90, 120]  #[P1, P2, P3, P4, P5] tn/dia
cap_fermentacion = [2500, 1250, 3500, 950, 900]  #[P1, P2, P3, P4, P5] tn
costo_fijo = [27000, 18000, 18700, 22500, 31500]  #UTM
costo_procesado = [20.0, 30.8, 20.8, 27.8, 29.2]  #Ch$ /kg



#c

cap_bines = [36, 36, 36, 36, 36, 36, 36, 32, 32, 32, 36, 36, 36, 36, 36, 36, 36, 36, 12, 
12, 12, 12, 12, 12, 12] 
cap_tolva = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1]
costo_camion = [0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.025, 0.025, 0.025, 0.018, 0.018, 
0.018, 0.018, 0.018, 0.018, 0.018, 0.018, 0.032, 0.032, 0.032, 0.032, 0.032, 0.032, 0.032]  #UTM/TKM


cap_montacargas = 22
kg_bin = 486
kg_tolva = 10000
cantidad_tolvas = 100
CFD = 10  #costo fijo diario
penalizacion = 10




def conseguir_cal(actual):
    curr_dir = os.path.dirname(__file__)
    #print(curr_dir)
    parent = os.path.split(curr_dir)[0]
    with open(os.path.join(parent, 'data', 'simulated_expected_q.json')) as jsonFile:
        jsonObject = json.load(jsonFile)
        jsonFile.close()

    #print(jsonObject)
    calidades = list(jsonObject.values())
    #calidades = calidades[:7]
    #print(calidades)
    #print(len(calidades))
    #print(len(calidades[0]))

    file = pd.read_excel(os.path.join(parent, 'data', 'datos_entregados.xlsx'), engine='openpyxl')
# print(file.head())

    aux = []
    for i in range(len(calidades)):
        fila = []
        # fila.append(i)
        dia = 0
        while dia != 181:
            num = dia - file.iloc[i]['Dia optimo cosecha']
            if num == -7:
                for dato in calidades[i]:
                    fila.append(dato)
                dia += 14
            else:
                fila.append(0)
            dia += 1
        aux.append(fila)
    calfinal = []
    for i in aux:
        aux1 = []
        for j in range(actual, actual+7):
            aux1.append(i[j])
        calfinal.append(aux1)

    return calfinal
    #print(aux)
    #print(len(aux))
    #print(len(aux[0]))


#print(km)
#print(DI_l)
#cal = conseguir_cal(80)
#print(cal)