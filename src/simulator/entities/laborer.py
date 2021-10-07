class Laborer:
    _id = 0

    def __init__(self):
        Laborer._id += 1
        self.id = Laborer._id
        self.velocidad_cosecha = 700 * 5  # Todo: esto es cuadrilla
        self.cantidad_cosechada = 0
        self.tiempo_cosechando = 0
        self.dias_trabajando = 0
