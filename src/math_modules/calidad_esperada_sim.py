import random
from .utilities import *


# -- Simula muchas iteraciones de semanas y obtiene la calidad promedio por día de la semana --
def run_sim(iteraciones, len_simulacion, m_transicion, funcion_mu, funcion_q, lluvia_inicial=False):
    simulaciones = []
    for _ in range(iteraciones):
        simulacion = []
        mu_acumulado = []
        p_actual = funcion_q(0)
        llovio = lluvia_inicial
        for t in range(len_simulacion):

            if llovio:
                llovio = True if random.random() <= m_transicion[0][0] else False
            else:
                llovio = True if random.random() <= m_transicion[1][0] else False

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

    p_11, p_01 = 0.6, 0.2
    m_transicion = [[p_11, (1 - p_11)], [p_01, (1 - p_01)]]
    resultados = run_sim(iteraciones=100000, len_simulacion=14, m_transicion=m_transicion, 
                        funcion_mu=mu, funcion_q=optimal_q_generator(0.85, 0.95))

    for i, res in enumerate(resultados):
        print(f'dia={i}, q={res}')
