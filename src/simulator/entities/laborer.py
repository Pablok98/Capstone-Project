class Laborer:
    _id = 0

    def __init__(self):
        Laborer._id += 1
        self.velocidad_cosecha = 700
        self.cantidad_cosechada = 0
        self.tiempo_cosechando = 0
        self.dias_trabajando = 0
