import random
from utilities import *


# -- Simula muchas iteraciones de semanas y obtiene la calidad promedio por día de la semana --
def run_sim(iteraciones, len_simulacion, p_lluvia, funcion_mu, funcion_q):
    simulaciones = []
    for _ in range(iteraciones):
        simulacion = []
        mu_acumulado = []
        p_actual = funcion_q(0)
        for t in range(len_simulacion):
            llovio = True if random.random() <= p_lluvia else False
            if llovio:
                mu_acumulado.append(funcion_mu(p_actual))
            p_actual = funcion_q(t) * (1 - sum(mu_acumulado))
            simulacion.append(p_actual)
        simulaciones.append(simulacion)
    avg_results = [(sum(simulaciones[i][t] for i in range(
        iteraciones))) / iteraciones for t in range(len_simulacion)]
    return avg_results
# ---------------------------------------------------------------------------------------------


if __name__ == "__main__":

    resultados = run_sim(iteraciones=1000, len_simulacion=14,
                         p_lluvia=0.1, funcion_mu=mu, funcion_q=optimal_q_generator(0.85, 0.95))

    for i, res in enumerate(resultados):
        print(f'dia={i}, q={res}')
