class Laborer:
    _id = 0

    def __init__(self):
        Laborer._id += 1
        self.velocidad_cosecha = 700
        self.cantidad_cosechada = None
        self.tiempo_cosechando = None
        self.dias_trabajando = None
