from .crate import Crate


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

    def cargar_cajon(self, cajon):
        self.cajones.append(cajon)

    def descargar(self):
        """
        Retorna los kilos y la calidad promedio del bin
        """
        calidad = 0
        kg = 0
        ctd_cajones = 0
        for cajon in self.cajones:
            kg += 18
            # TODO cambiar calidad a cajon mismo
            calidad += self.calc_calidad(cajon)
            ctd_cajones += 1
        calidad /= ctd_cajones
        self.cajones = []
        self.tiempo_carga = None
        return kg, calidad

    def llenar(self, tipo_uva, delta_optimo):
        for _ in range(self.carga_maxima):
            self.cajones.append(Crate(tipo_uva, delta_optimo))

    def calc_calidad(self, cajon):
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
        a = (calidades[cajon.tipo_uva][0] + calidades[cajon.tipo_uva][1] - 2)/98
        b = (calidades[cajon.tipo_uva][1] - calidades[cajon.tipo_uva][0])/14

        calidad = a*(cajon.dif_optimo**2) + b*cajon.dif_optimo + 1
        if calidad > 1:
            calidad = 1
        return calidad



