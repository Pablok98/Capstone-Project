from ..sim import SimulationObject


class Crate(SimulationObject):  # (cajon)
    _id = 0

    def __init__(self, uva: int, calidad: float):
        Crate._id += 1
        self.id = Crate._id
        self.tipo_uva = uva
        self.hora_cosechada = SimulationObject.tiempo_actual
        self.calidad = calidad
