import numpy as np
from gurobipy import *
from parametros import *
from parametros import conseguir_cal

print(ef_cos)
print(type(ef_cos[2][2]))
cal = conseguir_cal()
print("Esto es DI")
print(DI)

m = Model()
# m.Params.OutputFlag = 0


#Variables Cosecha
c_cosecha = m.addVars(len(L),len(T),vtype=GRB.BINARY)
c_auto = m.addVars(len(L),len(T), vtype=GRB.INTEGER)
c_manual = m.addVars(len(L),len(T), vtype=GRB.INTEGER)
c_tolva = m.addVars(len(L),len(T), vtype=GRB.INTEGER)
c_bines = m.addVars(len(L),len(T), vtype=GRB.INTEGER)
c_cuad = m.addVars(len(K),len(L),len(T), vtype=GRB.BINARY)
c_man_bin = m.addVars(len(K),len(L),len(T), vtype=GRB.BINARY)
c_man_tolva = m.addVars(len(K),len(L),len(T), vtype=GRB.BINARY)
c_cant_uva = m.addVars(len(L),len(T), vtype=GRB.CONTINUOUS)
c_monta = m.addVars(len(L),len(T), vtype=GRB.INTEGER)
c_disponibilidad = m.addVars(len(L),len(T), vtype=GRB.CONTINUOUS)
#c_cajones

#Variables Transporte
t_ruta = m.addVars(len(L),len(P),len(T), vtype=GRB.BINARY)
t_camion = m.addVars(len(C),len(L),len(T), vtype=GRB.BINARY)
t_camion_bin = m.addVars(len(C),len(L),len(T), vtype=GRB.BINARY)
t_camion_tolva = m.addVars(len(C),len(L),len(T), vtype=GRB.BINARY)
camion_tercero_b = m.addVars(len(L),len(T), vtype=GRB.CONTINUOUS)
camion_tercero_t = m.addVars(len(L),len(T), vtype=GRB.CONTINUOUS)

#Variables Planta
p_proc = m.addVars(len(P),len(T), vtype=GRB.CONTINUOUS)
p_fermentando = m.addVars(len(P),len(T), vtype=GRB.CONTINUOUS)
p_disp = m.addVars(len(P),len(T), vtype=GRB.CONTINUOUS)
p_rec = m.addVars(len(P),len(T), vtype=GRB.CONTINUOUS)
p_terceros = m.addVars(len(P),len(T), vtype=GRB.CONTINUOUS)

m.update()


#Restricciones Cosecha
m.addConstrs((c_cant_uva[l,t] <= ef_cos[l][t] * c_auto[l,t] + ef_cuad[l][t] * c_manual[l,t] for l in L for t in T))
m.addConstrs((c_cant_uva[l,t] <= c_disponibilidad[l,t] for l in L for t in T))
m.addConstrs((c_cosecha[l,t] <= c_disponibilidad[l,t] for l in L for t in T))
m.addConstrs((c_cosecha[l,t] <= c_auto[l,t] + c_manual[l,t] for l in L for t in T))
m.addConstrs((c_auto[l,t] <=c_cosecha[l,t] * M for l in L for t in T)) #aca talvez para mejorar rendimiento se puede poner distintos M
m.addConstrs((c_manual[l,t] <=c_cosecha[l,t] * M for l in L for t in T))
m.addConstrs((sum(c_manual[l,t] for l in L) <= 5 for t in T))
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
m.addConstrs((p_terceros[p,t] + p_rec[p,t] >= sum(c_cant_uva[l,t]*t_ruta[l,p,t] for l in L) for p in P for t in T))
m.addConstrs((sum(p_terceros[p,t] + p_rec[p,t] for p in P) >= sum(c_cant_uva[l,t] for l in L) for p in P for t in T))
m.addConstrs((p_rec[p,t] <= cap_fermentacion[p]*0.3 for p in P for t in T))
m.addConstrs((p_rec[p,t] <= cap_fermentacion[p] - p_fermentando[p,t] for p in P for t in T))
m.addConstrs((p_fermentando[p,t] <= cap_fermentacion[p] for p in P for t in T))


m.addConstrs((sum(t_camion[c,l,t] for l in L) == 1 for c in C for t in T))

m.update()

#Funcion Objetivo
costo_terceros = quicksum(1.12*80*p_terceros[p,t] for p in P for t in T) \
                 + quicksum((camion_tercero_t[l,t] + camion_tercero_b[l,t])*1.15*100 for t in T for l in L)
sobrecosto_ocupacion = quicksum(CFD * (1 - (p_fermentando[p,t]/cap_fermentacion[p])) for p in P for t in T)
# sobrecosto_ocupacion = quicksum(CFD * (1 - (p_fermentando[p,t]/cap_fermentacion[p])) for p in P for t in T)
# auxiliar = quicksum(c_cosecha[l,t] for l in L for t in T)
promedio = quicksum(c_cosecha[l,t] * cal[l][t] for l in L for t in T)
# sobrecosto_cal = quicksum(penalizacion*(1 - (promedio / auxiliar)))
m.setObjective(costo_terceros + sobrecosto_ocupacion + penalizacion*(1 - promedio) + quicksum(costo_procesado[p]*p_proc[p,t] for p in P for t in T))

m.update()
m.optimize()
# print(m.objVal)
#print(m.getVars())
