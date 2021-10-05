import matplotlib.pyplot as plt
import numpy as np
from calidad_esperada import *
from calidad_esperada_sim import *
from markov import stationary_distribution

# Aquí probamos todos los archivos de /math
for p_11, p_01 in ((0.3, 0.2), (0.4, 0.3), (0.6, 0.3), (0.9, 0.1), (0.9, 0.9)):
    m_transicion = np.array([[p_11, (1 - p_11)], [p_01, (1 - p_01)]])
    p_lluvia = stationary_distribution(m_transicion)[0]
    f_optimal_q = optimal_q_generator(0.85, 0.95)
    resultados_analiticos = [E_quality(t, p_lluvia, f_optimal_q, mu) for t in range(14)]
    resultados_simulacion = run_sim(100000, 14, m_transicion, mu, f_optimal_q)

    print(f'probabilidad lluvia: {p_lluvia}')
    print(*[f'dia {i}: {resultados_analiticos[i] - resultados_simulacion[i]}' for i in range(14)], sep='\n')
    print()

    plt.plot(range(14), resultados_analiticos, 'g')
    plt.plot(range(14), resultados_simulacion, 'r')
    plt.show()
