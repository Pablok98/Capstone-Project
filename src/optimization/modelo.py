import numpy as np
from gurobipy import *



m = Model()
m.Params.OutputFlag = 0

#
L = [0,1,2,3,4,5,6]
T = [0,1,2,3,4,5,6,]
K = 0
C = 0
P = 5
M = 1000
cap_bin = 486
cap_tolva = 10000
cantidad_tolvas = 100
cap_montacargas = 22
CFD = 10 #costo fijo diario
penalizacion = 10

#Variables Cosecha
c_cosecha = m.addVars(L,T,vtype=GRB.BINARY)
c_auto = m.addVars(L,T, vtype=GRB.INTEGER)
c_manual = m.addVars(L,T, vtype=GRB.INTEGER)
c_tolva = m.addVars(L,T, vtype=GRB.INTEGER)
c_bines = m.addVars(L,T, vtype=GRB.INTEGER)
c_cuad = m.addVars(K,L,T, vtype=GRB.BINARY)
c_man_bin = m.addVars(K,L,T, vtype=GRB.BINARY)
c_man_tolva = m.addVars(K,L,T, vtype=GRB.BINARY)
c_cant_uva = m.addVars(L,T, vtype=GRB.CONTINUOUS)
c_monta = m.addVars(L,T, vtype=GRB.INTEGER)
c_disponibilidad = m.addVars(L,T, vtype=GRB.CONTINUOUS)
#c_cajones

#Variables Transporte
t_ruta = m.addVars(L,P,T, vtype=GRB.BINARY)
t_camion = m.addVars(C,L,T, vtype=GRB.BINARY)
t_camion_bin = m.addVars(C,L,T, vtype=GRB.BINARY)
t_camion_tolva = m.addVars(C,L,T, vtype=GRB.BINARY)
camion_tercero_b = m.addVars(L,T vtype=GRB.CONTINUOUS)
camion_tercero_t = m.addVars(L,T vtype=GRB.CONTINUOUS)

#Variables Planta
p_proc = m.addVars(P,T, vtype=GRB.CONTINUOUS)
p_fermentando = m.addVars(P,T, vtype=GRB.CONTINUOUS)
p_disp = m.addVars(P,T, vtype=GRB.CONTINUOUS)
p_rec = m.addVars(P,T, vtype=GRB.CONTINUOUS)
p_terceros = m.addVars(P,T, vtype=GRB.CONTINUOUS)


#Restricciones Cosecha
m.addConstrs((c_cant_uva = ef_cos[l,t] * c_auto[l,t] + ef_cuad[l,t] * c_manual[l,t] for l in L for t in T))
m.addConstrs((c_cosecha[l,t] <= c_disponible[l,t] for l in L for t in T))
m.addConstrs((c_cosecha[l,t] <= c_auto[l,t] + c_manual[l,t] for l in L for t in T))
m.addConstrs((c_auto[l,t] <=c_cosecha[l,t] * M)) #aca talvez para mejorar rendimiento se puede poner distintos M
m.addConstrs((c_manual[l,t] <=c_cosecha[l,t] * M))
m.addConstrs((sum(c_manual[l,t] for l in L) <= 5 for t in T))
m.addConstrs((sum(c_cuad[k,l,t] for k in K) = c_manual[l,t]))
m.addConstrs((c_bines[l,t] >= ((ef_cos[l,t] * c_auto[l,t] + ef_cuad * sum(c_man_bin[k,l,t] for k in K))/cap_bin) for l in L for t in T))
m.addConstrs((c_tolva[l,t] >= ((ef_cuad * sum(c_man_tolva[k,l,t] for k in K))/cap_tolva) for l in L for t in T))
m.addConstrs((sum(c_bines[l,t] for l in L) <= 800 for t in T))
m.addConstrs((sum(c_tolva[l,t] for l in L) <= cantidad_tolvas for t in T))
m.addConstrs((sum(c_monta[l,t] for l in L)  <= cap_montacargas for t in T))
m.addConstrs((c_monta[l,t] >= sum(t_camion_bin[c,l,t] for c in C) for l in L for t in T))
m.addConstrs((c_disponibilidad[l,t] == c_disponibilidad[l,t-1] - c_cant_uva[l,t-1] for l in L for t in T if t >= 1))
m.addConstrs((c_disponibilidad[l,0] == DI[l] for l in L))
#restriccion carros tolva 17
#restriccion cajones??

#Restricciones Transporte
m.addConstrs((sum(t_ruta[l,p,t] for p in P) == c_cosecha[l,t]))
m.addConstrs((sum(t_ruta[l,p,t] for p in P) == 1 for l in L for t in T))
m.addConstrs((camion_tercero_b[l,t] + sum(t_camion_bin[c,l,t] * cap_bines[c] for c in C) >= c_bines[l,t] for l in L for t in T))
m.addConstrs((camion_tercero_t[l,t] + sum(t_camion_tolva[c,l,t] * cap_tolva[c] for c in C) >= c_tolva[l,t] for l in L for t in T))
m.addConstrs((t_camion_tolva[c,l,t] + t_camion_bin[c,l,t] == t_camion[c,l,t] for c in C for l in L for t in T))

#Restricciones Planta
m.addConstrs((p_fermentando[p,t] == p_rec[p,t] + p_fermentando[p,t-1] - p_proc[p,t-1] for p in P for t in T if t >=1))
m.addConstrs((p_fermentando[p,0] == 0 for p in P))
m.addConstrs((p_proc[p,t] <= cap_proc[p] for p in P for t in T))
m.addConstrs((p_proc[p,t] <= p_disp[p,t] for p in P for t in T))
m.addConstrs((p_disp[p,t] == p_disp[p,t-1] + p_rec[p,t-7] - p_proc[p,t-1] for p in P for t in T if t >= 7))
m.addConstrs((p_disp[p,t] == 0 for p in P for t in T if t < 7))
m.addConstrs((p_terceros[p,t] + p_rec[p,t] == sum(c_cant_uva[l,t]*t_ruta[l,p] for l in L) for p in P for t in T))
m.addConstrs((sum(p_terceros[p,t] + p_rec[p,t] for p in P) == sum(c_cant_uva[l,t] for l in L) for p in P for t in T))
m.addConstrs((p_rec[p,t] <= cap_fermentacion[p]*0.3 for p in P for t in T))
m.addConstrs((p_rec[p,t] <= cap_fermentacion[p] - p_fermentando[p,t] for p in P for t in T))
m.addConstrs((p_fermentando[p,t] <= cap_fermentacion[p] for p in P for t in T))


m.addConstrs((sum(t_camion[c,l,t] for l in L) == 1 for c in C for t in T))

#Funcion Objetivo
costo_terceros = quicksum(1.12*80*p_terceros[p,t] for p in P for t in T) + 
quicksum((camion_tercero_t[l,t] + camion_tercero_b[l,t])*1.15*100 for t in T for l in L)
sobrecosto_ocupacion = quicksum(CFD * (1 - (p_fermentando[p,t]/cap_fermentacion[p])) for p in P for t in T)
# sobrecosto_ocupacion = quicksum(CFD * (1 - (p_fermentando[p,t]/cap_fermentacion[p])) for p in P for t in T)
promedio = (quicksum(c_cosecha[l,t] * cal[l,t] for l in L for t in T)) / quicksum(c_cosecha[l,t] for l in L for t in T)
sobrecosto_cal = quicksum(penalizacion*(1 - promedio))
m.setObjective(costo_terceros + sobrecosto_ocupacion + sobrecosto_cal + quicksum(cost_proc[p]*p_proc[p,t] for p in P for t in T))
