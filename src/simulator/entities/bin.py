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
            calidad += cajon.calidad
            ctd_cajones += 1
        calidad /= ctd_cajones
        self.cajones = []
        self.tiempo_carga = None
        return kg, calidad

    def llenar(self, tipo_uva, delta_optimo):
        for _ in range(self.carga_maxima):
            self.cajones.append(Crate(tipo_uva, delta_optimo))





