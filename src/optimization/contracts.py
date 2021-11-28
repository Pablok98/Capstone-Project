import statistics
import params as p
import json


# Genera una función de respuesta que
# retorna la proporción de uva extra
# que compra la bodega según la calidad
# de uva del lote el día esperado de compra
def response_function_generator(max_q, min_q, var):
    def inner(q):
        if q >= max_q:
            return 1
        if q < (min_q + var):
            return 0

        m = (1 - (0.1 - (min_q + var) / max_q) / (1 - (min_q + var) / max_q)) / max_q
        n = (0.1 - (min_q + var) / max_q) / (1 - (min_q + var) / max_q)

        return m * q + n
    
    return inner


# Función que mide la calidad de cada contrato dadas
# las condiciones del lote al cual se enfrenta
def q_per_unit_cost(a_j, max_q, c_j, cs_j, ps_j):
    q = min(1 - a_j + max_q, 1)
    cost = c_j + (1 - c_j) * cs_j * ps_j
    return (q / cost)


# Función que obtiene el mejor contrato a partir de
# las condiciones del lote
def get_optimum_contract(expected_q: list):
    max_q = max(expected_q)
    avg_q = sum(expected_q) / len(expected_q)
    min_q = min(expected_q)
    var = statistics.variance(expected_q)
    # std = statistics.stdev(expected_q) se puede cambiar la métrica
    cs_j = response_function_generator(max_q, min_q, var)(avg_q)

    kpi_contracts = {}

    for c, info in p.CONTRACTS_DATA.items():
        kpi = q_per_unit_cost(**info, max_q=max_q, cs_j=cs_j)
        kpi_contracts[c] = kpi
    
    return max(kpi_contracts.items(), key=lambda x: x[1])[0]


if __name__ == "__main__":
    with open("analitic_expected_q.json", 'r') as lotes:
        lotes_prueba = json.load(lotes)

    dict_optimum_contracts = {lote: get_optimum_contract(info) for lote, info in lotes_prueba.items()}

    with open("optimum_contracts.json", 'w') as file:
        json.dump(dict_optimum_contracts, file)
    
