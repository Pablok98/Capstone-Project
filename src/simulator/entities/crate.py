from sim import SimulationObject


class Crate(SimulationObject):  # (cajon)
    _id = 0

    def __init__(self, uva, dif_optimo):
        Crate._id += 1
        self.tipo_uva = uva
        self.hora_cosechada = SimulationObject.tiempo_actual
        self.dif_optimo = dif_optimo.days


