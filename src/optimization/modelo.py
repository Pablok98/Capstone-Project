import numpy as np
from gurobipy import *



m = Model()
m.Params.OutputFlag = 0

#
L = 0
T = 7
K = 0
C = 0
P = 5
M = 1000
cap_bin = 486
cap_tolva = 10000
cantidad_tolvas = 100
cap_montacargas = 22


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
c_disponible = m.addVars(L,T, vtype=GRB.CONTINUOUS)
#c_cajones

#Variables Transporte
t_ruta = m.addVars(L,P,T, vtype=GRB.BINARY)
t_camion = m.addVars(C,L,T, vtype=GRB.BINARY)
t_camion_bin = m.addVars(C,L,T, vtype=GRB.BINARY)
t_camion_tolva = m.addVars(C,L,T, vtype=GRB.BINARY)

#Variables Planta
p_proc = m.addVars(P,T, vtype=GRB.CONTINUOUS)
p_fermentando = m.addVars(P,T, vtype=GRB.CONTINUOUS)
p_disp = m.addVars(P,T, vtype=GRB.CONTINUOUS)
p_rec = m.addVars(P,T, vtype=GRB.CONTINUOUS)


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
#restriccion cajones??

