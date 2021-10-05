import numpy as np
import matplotlib.pyplot as plt


# -- Obtiene una función optimal_q(t) dadas las calidades inicial y final --
def optimal_q_generator(init_q, final_q):
    A = np.array([[0, 0, 1], [169, 13, 1], [36, 6, 1]])
    b = np.array([init_q, final_q, 1])
    alpha, beta, gamma = np.linalg.solve(A, b)

    def optimal_q(t):
        return min(alpha * (t ** 2) + beta * t + gamma, 1)
    
    return optimal_q
# --------------------------------------------------------------------------

# -- la función mu(q) del enunciado --
def mu(q):
    if 0 <= q < 0.9:
        return 0.03

    elif 0.9 <= q < 0.95:
        return 0.05

    elif 0.95 <= q < 0.98:
        return 0.07

    else:
        return 0.1
# ------------------------------------

if __name__ == '__main__':
    funcion = optimal_q_generator(0.01, 0.99)
    plt.plot(range(14), [funcion(i) for i in range(14)])
    plt.show()