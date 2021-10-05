import matplotlib.pyplot as plt
from calidad_esperada import *
from calidad_esperada_sim import *

# Aquí probamos todos los archivos de /math
for p_lluvia in (0.1, 0.25, 0.5, 0.75):
    f_optimal_q = optimal_q_generator(0.85, 0.95)
    resultados_analiticos = [E_quality(t, p_lluvia, f_optimal_q, mu) for t in range(14)]
    resultados_simulacion = run_sim(100000, 14, p_lluvia, mu, f_optimal_q)

    print(f'probabilidad lluvia: {p_lluvia}')
    print(*[f'dia {i}: {resultados_analiticos[i] - resultados_simulacion[i]}' for i in range(14)], sep='\n')
    print()

    plt.plot(range(14), resultados_analiticos, 'g')
    plt.plot(range(14), resultados_simulacion, 'r')
    plt.show()
