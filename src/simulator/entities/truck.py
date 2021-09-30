class Truck:
    _id = 0

    def __init__(self, tipo, tolva, bines):
        Truck._id += 1
        self.tipo = tipo
        self.cap_tolva = tolva
        self.cap_bines = bines

        self.planta_asignada = None

        self.carros = []
        self.bines = []

    @property
    def lleno(self):
        return not len(self.bines) < self.cap_bines

    @property
    def tiene_contenido(self):
        return self.bines != []

    def descargar(self):
        if self.tiene_contenido:
            bin_ = self.bines.pop(0)
            return bin_.descargar()
