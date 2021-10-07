import numpy as np
from gurobipy import *
from parametros import *
from parametros import conseguir_cal

###############RELLENAR DIA EN EL QUE SE ESTA ACA PARA LA CALIDAD DE CADA LOTE########## 
cal = conseguir_cal(80)


m = Model()
# m.Params.OutputFlag = 0


#Variables Cosecha
c_cosecha = m.addVars(len(L),len(T),vtype=GRB.BINARY, name='cosecha')
c_auto = m.addVars(len(L),len(T), vtype=GRB.INTEGER, name ='auto')
c_manual = m.addVars(len(L),len(T), vtype=GRB.INTEGER, name='manual')
c_tolva = m.addVars(len(L),len(T), vtype=GRB.INTEGER, name='tolva')
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
t_camion_bin = m.addVars(len(C),len(L),len(T), vtype=GRB.BINARY, name='camionbin')
t_camion_tolva = m.addVars(len(C),len(L),len(T), vtype=GRB.BINARY, name='camiontolva')
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
print(m.objVal)
for v in m.getVars():
    if 'cosecha' in v.varName:
        print('%s %g' % (v.varName, v.x))
    if 'cantidad' in v.varName or 'aux' in v.varName:
        print('%s %g' % (v.varName, v.x))
print(cal)