class Truck:
    _id = 0

    def __init__(self, tipo, tolva, bines):
        Truck._id += 1
        self.tipo = tipo
        self.cap_tolva = tolva
        self.cap_bines = bines

        self.carros = []
        self.bines = []

    @property
    def lleno(self):
        return not len(self.bines) < self.cap_bines
