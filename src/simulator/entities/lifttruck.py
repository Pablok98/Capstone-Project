from .machine import Machine
from params import TASA_DEPRECIACION_MONTACARGAS, COSTO_POR_TONELADA_MONTACARGAS


class LiftTruck(Machine):
    _id = 0

    def __init__(self):
        super().__init__(TASA_DEPRECIACION_MONTACARGAS, COSTO_POR_TONELADA_MONTACARGAS)
        LiftTruck._id += 1
        self.id = LiftTruck._id
        self.nombre = 'montacargas'
