import matplotlib.pyplot as plt
from .utilities import *

# -- Estas funciones obtienen recursivamente el valor esperado de la calidad --
def E_quality(t, p_rain, f_optimal_q, f_mu):
  if t == 0:
    return f_optimal_q(0) - E_cumulative_mu(0, p_rain, f_optimal_q, f_mu)
    
  return f_optimal_q(t) * (1 - E_cumulative_mu(t, p_rain, f_optimal_q, f_mu))

def E_cumulative_mu(t, p_rain, f_optimal_q, f_mu):
  if t == 0:
    return f_mu(f_optimal_q(0)) * p_rain
    
  return (f_mu(E_quality(t - 1, p_rain, f_optimal_q, f_mu)) * p_rain 
          + E_cumulative_mu(t - 1, p_rain, f_optimal_q, f_mu))
# -----------------------------------------------------------------------------

if __name__ == "__main__":

  for p_rain in (0.1, 0.25, 0.5, 0.75, 1):
    print(f'p = {p_rain}')

    valores_esperados = []
    for i in range(14):
      valor_esperado = E_quality(i, p_rain)
      valores_esperados.append(valor_esperado)
      print(f'dia={i}, q={valor_esperado}')
    print()

    plt.plot(range(14), valores_esperados)
  plt.show()