# import params as p
from datetime import datetime, timedelta
from ..sim import SimulationObject
from collections import namedtuple

from ..entities import *
from typing import Union

Batch = namedtuple("Grape_batch", ["kilos", "calidad", "fecha_in"])


class Plant(SimulationObject):
    MAX_DAILY_UNLOAD = 0.3

    def __init__(self, name: str, ferm_cap: int, prod_cap: int, hopper_cap: int, bin_cap: int):
        """
        Represents a plant site, which can store and process grape daily. Trucks bring grapes from
        lots to unload them for processing.

        :param name: MUST be unique. Name of the plant, which will used by the simulator to both
                    display and reference.
        :param ferm_cap: Maximum capacity of grapes that the plant can contain at once.
        :param prod_cap: Maximum capacity of grapes that the plant can process in one day.
        :param hopper_cap: Maximum rate of grapes that can be unloaded to the plant from a truck
                        with hopper(s)
        :param bin_cap: Maximum rate of grapes that can be unloaded to the plant from a truck
                        loaded with bin(s)
        """
        self.nombre = name
        self.cap_ferm = ferm_cap
        self.cap_prod = prod_cap
        self.cap_tolva = hopper_cap
        self.cap_bin = bin_cap

        # uva_actual contains tuples, each with the pair (quantity, quality). When grape is unloaded
        # from trucks, the quanity and quality is stored in the list. todo add date
        self.uva_actual: list[Batch] = []
        # State variables
        self.vino_total_producido = 0
        self.uva_procesada = 0
        self.camiones = []

        self.tiempo_descarga: Union[datetime, None] = None

        self.daily_grapes = 0

    @property
    def carga_actual(self) -> int:
        """
        Iterates through the batches (touples) of grape and counts the total grape currently
        inside the plant.

        :return: Current grape load

        """
        carga = 0
        for batch in self.uva_actual:
            carga += batch.kilos
        return carga

    @property
    def daily_grape_percentage(self) -> float:
        return round(self.daily_grapes / self.cap_ferm, 3)

    def llegada_camion(self, camion: Truck) -> None:
        self.camiones.append(camion)

    def descargar_camiones(self) -> None:
        SimulationObject.tiempo_actual = self.tiempo_descarga
        self.tiempo_descarga = None

        while self.daily_grape_percentage <= Plant.MAX_DAILY_UNLOAD and self.carga_actual < self.cap_ferm and self.camiones:
            camion = self.camiones[0]
            tasa = self.cap_bin if camion.de_bin else self.cap_tolva
            print(f"Descargando camion {camion.id} en la planta {self.nombre}")
            descargado = 0
            while descargado < tasa and camion.tiene_contenido:
                kilos, calidad = camion.descargar()
                uva = Batch(kilos, calidad, SimulationObject.tiempo_actual)
                self.uva_actual.append(uva)
                self.daily_grapes += kilos
                descargado += kilos
            if not camion.tiene_contenido:
                self.camiones.pop(0)

    def procesar_dia(self) -> None:
        print(f"Procesando uva en la planta {self.nombre}")
        procesado = 0
        while procesado < self.cap_prod:
            if not self.uva_actual:
                break
            if not (SimulationObject.tiempo_actual - self.uva_actual[0].fecha_in).days >= 7:
                break
            batch = self.uva_actual.pop(0)
            procesado += batch.kilos
            self.uva_procesada += batch.kilos
            self.vino_total_producido += (batch.kilos * batch.calidad) * 0.55
        print(self)

    @property
    def proximo_evento(self) -> tuple[str, str, datetime]:
        if not self.camiones or self.daily_grape_percentage >= Plant.MAX_DAILY_UNLOAD:
            return self.nombre, 'descarga', datetime(3000, 1, 1, hour=6, minute=0, second=0)
        if not self.tiempo_descarga:
            self.tiempo_descarga = SimulationObject.tiempo_actual + timedelta(minutes=60)
        return self.nombre, 'descarga', self.tiempo_descarga

    def resolver_evento(self, evento: str) -> None:
        if evento == 'descarga':
            self.descargar_camiones()

    def __str__(self):
        return f"Planta: {self.nombre}. Uva procesada: {self.uva_procesada}. Vino procesado: {self.vino_total_producido}. Uva dentro: {self.carga_actual}"
