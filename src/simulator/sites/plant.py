# import params as p
from datetime import datetime, timedelta
from ..sim import SimulationObject


class Plant(SimulationObject):
    MAX_DAILY_UNLOAD = 0.3
    def __init__(self, name: str, ferm_cap: int, prod_cap: int, hopper_cap: int, bin_cap: int):
        """

        :param name: MUST be unique. Name of the plant, which will used by the simulator to both
                    display and reference.
        :param ferm_cap: Maximum capacity of grapes (in kg) that the plant can contain at once.
        :param prod_cap: Maximum capacity of grapes (in kg) that the plant can contain at once.
        :param hopper_cap:
        :param bin_cap:
        """
        self.nombre = name
        self.cap_ferm = ferm_cap
        self.cap_prod = prod_cap
        self.cap_tolva = hopper_cap
        self.cap_bin = bin_cap
        self.uva_actual = []
        self.vino_total_producido = 0
        self.uva_procesada = 0

        self.camiones = []

        self.tiempo_proximo_procesamiento = None

        self.daily_grapes = 0



    @property
    def carga_actual(self):
        carga = 0
        for batch in self.uva_actual:
            carga += batch[0]
        return carga

    @property
    def daily_grape_percentage(self):
        return round(self.daily_grapes / self.cap_ferm, 3)

    def descargar_camion(self, camion):
        """
        Recibe un camion y calcula el proceso de llenar la planta
        """
        self.camiones.append(camion)
        print(f"Descargando camion {camion.id} en la planta {self.nombre}")
        while self.carga_actual < self.cap_ferm and camion.tiene_contenido:
            kilos, calidad = camion.descargar()
            self.uva_actual.append((kilos, calidad))
            self.daily_grapes += kilos

    def procesar_dia(self):
        print(f"Procesando uva en la planta {self.nombre}")
        procesado = 0
        while procesado < self.cap_prod:
            if not self.uva_actual:
                break
            batch = self.uva_actual.pop(0)
            procesado += batch[0]
            self.uva_procesada += batch[0]
            self.vino_total_producido += batch[0] * batch[1]
        print(self)

    @property
    def proximo_evento(self):
        if not self.camiones or self.daily_grape_percentage >= Plant.MAX_DAILY_UNLOAD:
            return datetime(3000, 1, 1, hour=6, minute=0, second=0)
        if not self.tiempo_proximo_procesamiento:
            self.tiempo_proximo_procesamiento = SimulationObject.tiempo_actual + timedelta(minutes=60)
        return self.nombre, 'descarga', self.tiempo_proximo_procesamiento

    def resolver_evento(self, evento):
        if evento == 'descarga':



    def __str__(self):
        return f"Planta: {self.nombre}. Uva procesada: {self.uva_procesada}. Vino procesado: {self.vino_total_producido}"
