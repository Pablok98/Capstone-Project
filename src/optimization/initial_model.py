import gurobipy as gp
from gurobipy import GRB
import random

# -- IMPORTANTE: Asumimos que lot_data esta en el mismo orden que expected_q y --
# lot_data está ordenado por lote del 1 al final --

def get_optimum_contracts(lot_data: dict, expected_q: dict, demand: float) -> dict:
    lot_quantity = len(lot_data)
    grape_quantity_by_lot = [info['Tn'] for info in lot_data.values()]
    average_qualities = [sum(qualities) / len(qualities) for qualities in expected_q.values()]

    model = gp.Model()
    model.Params.LogToConsole = 0
    l_i = model.addVars(lot_quantity, name='compra de lote i', vtype=GRB.BINARY)
    obj_func = gp.LinExpr()
    obj_func += sum((1 - average_qualities[i]) * l_i[i] for i in range(lot_quantity))
    model.setObjective(obj_func, GRB.MINIMIZE)

    model.addConstr(sum(l_i[i] * grape_quantity_by_lot[i] for i in range(lot_quantity)) >= demand)

    model.optimize()

    optimum_contracts = {list(lot_data.keys())[i]: bool(v.x) for i, v in enumerate(model.getVars())}
    return optimum_contracts


if __name__ == '__main__':
    
    random.seed(69420)

    cant_lotes = 20
    calidades_promedio = [random.random() for _ in range(cant_lotes)]
    demanda = 1000
    lot_data = {f'lot {i}': {'Tn': random.randint(50, 100)} for i in range(cant_lotes)}
    expected_q = {f'lot {i}': [calidades_promedio[i]] * 14 for i in range(cant_lotes)}

    print(get_optimum_contracts(lot_data, expected_q, demanda))

    # initial_model = gp.Model('Initial Contracts Model')
    # l_i = initial_model.addVars(cant_lotes, name='compra de lote i', vtype=GRB.BINARY)

    # obj_func = gp.LinExpr()
    # obj_func += sum((1 - calidades_promedio[i]) * l_i[i] for i in range(cant_lotes))
    # initial_model.setObjective(obj_func, GRB.MINIMIZE)

    # initial_model.addConstr(sum(l_i[i] * cant_uva_por_lote[i] for i in range(cant_lotes)) >= demanda)

    # initial_model.optimize()
    # for i, v in enumerate(initial_model.getVars()):
    #     print(f'{v.varName}: {v.x}, avg: {calidades_promedio[i]}, cant: {cant_uva_por_lote[i]}')

