from sim import SimulationObject


class Crate(SimulationObject):  # (cajon)
    _id = 0

    def __init__(self, uva, dif_optimo):
        Crate._id += 1
        self.tipo_uva = uva
        self.hora_cosechada = SimulationObject.tiempo_actual
        self.dif_optimo = dif_optimo.days

    @property
    def calidad(self):
        """
        Retorna calidad de uva del cajon
        """
        calidades = {
            '1': [0.85, 0.95],
            '2': [0.92, 0.93],
            '3': [0.90, 0.92],
            '4': [0.88, 0.93],
            '5': [0.95, 0.95],
            '6': [0.89, 0.85],
            '7': [0.93, 0.91],
            '8': [0.94, 0.89],
        }
        a = (calidades[self.tipo_uva][0] + calidades[self.tipo_uva][1] - 2)/98
        b = (calidades[self.tipo_uva][1] - calidades[self.tipo_uva][0])/14

        calidad = a*(self.dif_optimo**2) + b*self.dif_optimo + 1
        if calidad > 1:
            calidad = 1
        return calidad
