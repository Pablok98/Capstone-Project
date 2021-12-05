from math_modules.markov import stationary_distribution
import params as p
import numpy as np
import json
from files import read_lot_data


def obtener_productividad_esperada(p_matrix):
    pi = stationary_distribution(p_matrix)
    eficiencia_esperada_cuadrilla = (pi[0] * p.TASA_COSECHA_JORNALERO * p.PRODUCTIVIDAD_CON_LLUVIA_JORNALERO
                                    * p.TAMANO_CUADRILLAS + pi[1] * p.TASA_COSECHA_JORNALERO * p.TAMANO_CUADRILLAS)
    
    eficiencia_esperada_cosechadora = (pi[0] * p.VELOCIDAD_COSECHADORA * p.PRODUCTIVIDAD_CON_LLUVIA_COSECHADORA
                                     + pi[1] * p.VELOCIDAD_COSECHADORA)
    
    return {'cuadrilla': eficiencia_esperada_cuadrilla, 'cosechadora': eficiencia_esperada_cosechadora}

if __name__ == '__main__':

    results = {}

    for name, info in read_lot_data().items():
        p_01 = info['p_01']
        p_11 = info['p_11']

        p_matrix = np.array([[p_11, (1 - p_11)], [p_01, (1 - p_01)]])

        results[name] = obtener_productividad_esperada(p_matrix)

    with open('data/expected_productivity.json', 'w') as file:
        json.dump(results, file)