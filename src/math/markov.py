import numpy as np


# -- Obtiene la distribución estacionaria dada la matriz de transición --
def stationary_distribution(p_matrix, accuracy=100):
    pi = np.linalg.matrix_power(np.array(p_matrix), accuracy)[0]
    return pi
# -----------------------------------------------------------------------


if __name__ == '__main__':
    p_matrix = [[0.4, 0.6], 
                [0.2, 0.8]]
    p_matrix = np.array(p_matrix)
    pi_obtenido = stationary_distribution(p_matrix)
    print(pi_obtenido)