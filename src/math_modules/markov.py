import numpy as np


# -- Obtiene la distribución estacionaria dada la matriz de transición --
def stationary_distribution(p_matrix, accuracy=1000):
    pi = np.linalg.matrix_power(np.array(p_matrix), accuracy)[0]
    return pi
# -----------------------------------------------------------------------


if __name__ == '__main__':
    p_11, p_01 = 0.39, 0.43
    p_matrix = [[p_11, (1 - p_11)], 
                [p_01, (1 - p_01)]]
    p_matrix = np.array(p_matrix)
    pi_obtenido = stationary_distribution(p_matrix)
    print(pi_obtenido)