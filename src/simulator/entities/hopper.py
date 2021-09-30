class Hopper:  # (tolva)
    _id = 0

    def __init__(self):
        Hopper._id += 1
        self.capacidad_maxima = 5  # cajones
        self.cajones = []

        self.tiempo_transporte = None

    @property
    def lleno(self):
        return len(self.cajones) == self.capacidad_maxima

    def cargar_cajon(self, cajon):
        if self.lleno:
            print(f"El tolva {self._id} esta lleno!")
            return
        self.cajones.append(cajon)