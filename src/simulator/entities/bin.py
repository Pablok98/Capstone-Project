class Bin:
    _id = 0

    def __init__(self):
        Bin._id += 1

        self.cajones = []
        self.carga_maxima = 27
        self.tiempo_carga = None

    @property
    def lleno(self):
        return len(self.cajones) == self.carga_maxima
