from .machine import Machine
from src.params import TASA_DEPRECIACION_COSECHADORA, COSTO_POR_TONELADA_COSECHADORA, VELOCIDAD_COSECHADORA


class Harvester(Machine):  # (cosechadora)
    _id = 0

    def __init__(self):
        self.nombre = 'cosechadora'
        super().__init__(TASA_DEPRECIACION_COSECHADORA, COSTO_POR_TONELADA_COSECHADORA)
        Harvester._id += 1
        self.id = Harvester._id
        self.velocidad_cosecha = VELOCIDAD_COSECHADORA  # por hora
