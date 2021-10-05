import matplotlib.pyplot as plt
import numpy as np
from math_modules.calidad_esperada import *
from math_modules.calidad_esperada_sim import *
from math_modules.markov import stationary_distribution
from files import read_lot_data
import json

# -- Calcula los valores esperados de la calidad por lote y por dia de la semana --
def get_expected_q(analitic: bool):

    results = {}

    for name, info in read_lot_data().items():
        p_01 = info['p_01']
        p_11 = info['p_11']
        lower_bound, upper_bound = info['rango_calidad']

        p_matrix = np.array([[p_11, (1 - p_11)], [p_01, (1 - p_01)]])
        f_optimal_q = optimal_q_generator(lower_bound, upper_bound)

        if analitic:
            p_rain = stationary_distribution(p_matrix)[0]
            lot_results = [E_quality(t, p_rain, f_optimal_q, mu) for t in range(14)]

        else:
            lot_results = run_sim(100000, 14, p_matrix, mu, f_optimal_q)

        results[name] = lot_results
        
    return results
# ---------------------------------------------------------------------------------

if __name__ == '__main__':
    # results_anal = get_expected_q(True)
    results_sim = get_expected_q(False)

    # with open('analitic_expected_q.json', 'w') as file:
    #     json.dump(results_anal, file)

    with open('simulated_expected_q.json') as file:
        json.dump(results_sim, file)

    