from .machine import Machine
from params import TASA_DEPRECIACION_TRACTOR, COSTO_POR_TONELADA_TRACTOR


class Tractor(Machine):  # Tractor xd
    _id = 0

    def __init__(self):
        self._id = Tractor._id
        Tractor._id += 1
        self.nombre = 'tractor'
        super().__init__(TASA_DEPRECIACION_TRACTOR, COSTO_POR_TONELADA_TRACTOR)

