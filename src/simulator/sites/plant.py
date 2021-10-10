from ..sim import SimulationObject
from ..datastruct import Batch
from ..entities import *
from datetime import datetime, timedelta
from typing import Union


class Plant(SimulationObject):
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
        # Current state variables
        self.vino_total_producido = 0
        self.uva_procesada = 0
        self.camiones: list[Truck, None] = []

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
            carga += batch.kilograms
        return carga

    @property
    def daily_grape_percentage(self) -> float:
        """
        :return: Current percentage of total capacity loaded in the day
        """
        return round(self.daily_grapes / self.cap_ferm, 3)

    def llegada_camion(self, truck):# -> None:
        """
        Method to call when a truck gets to the plant.

        :param truck: truck to add to the plant
        """
        self.camiones.append(truck)

    @property
    def proximo_evento(self) -> tuple[str, str, datetime]:
        """
        Calculates all the events in the plant, and returns the data of the closest event.

        :return: A tuple with the following format (site Name, event name, event time)
        """
        if not self.camiones or self.daily_grape_percentage >= SimulationObject.MAX_DAILY_UNLOAD:
            return self.nombre, 'descarga', SimulationObject.neverdate
        if not self.tiempo_descarga:
            self.tiempo_descarga = SimulationObject.tiempo_actual + timedelta(minutes=60)
        return self.nombre, 'descarga', self.tiempo_descarga

    def unload_constraint(self) -> bool:
        """
        Checks if the plant can currently can unload grapes from a truck to the local storage

        :return: True if the plant can still unload grapes, False in other case.
        """
        # We can only unload a percentage of the max capacity (per day)
        max_daily = self.daily_grape_percentage <= SimulationObject.MAX_DAILY_UNLOAD
        # We can't unload more than the plant's capacity
        max_cap = self.carga_actual < self.cap_ferm
        # We only unload if there's still trucks on the site
        truck = self.camiones != []
        return max_daily and max_cap and truck

    def descargar_camiones(self) -> None:
        """
        Unloads grape from the current truck queue. Simulates an hour of unloading.
        """
        # We set the new global time, and reset the next unload event time.
        SimulationObject.tiempo_actual = self.tiempo_descarga
        self.tiempo_descarga = None

        unloaded = 0  # For storing current unloaded grape
        # We only can unload while we comply certain restrictions
        while self.unload_constraint():
            truck = self.camiones[0]  # Truck to unload
            rate = self.cap_bin if truck.de_bin else self.cap_tolva  # Maximum hourly rate

            print(f"Descargando camion {truck.id} en la planta {self.nombre}")
            # While we still can unload grapes, we take grape batched from the truck and store them
            # in the plant's storage
            while unloaded < rate and truck.tiene_contenido:
                kg, quality = truck.descargar()
                batch = Batch(kg, quality, SimulationObject.tiempo_actual)

                self.uva_actual.append(batch)
                self.daily_grapes += kg
                unloaded += kg
            # If the truck doesn't have contents, we remove it from the plant
            if not truck.tiene_contenido:
                self.camiones.pop(0)

    def procesar_dia(self) -> None:
        """
        Procesess the grape currently in the plant (given by the max rate of processing by
        the plant)
        """
        print(f"Procesando uva en la planta {self.nombre}")

        processed = 0
        # We process grape until we reach the maximum daily capacity or grape is exhausted
        while processed < self.cap_prod:
            # We must check if the next grape in the queue has been fermented
            fermented = (SimulationObject.tiempo_actual - self.uva_actual[0].date).days >= 7
            if not self.uva_actual or not fermented:
                break
            batch = self.uva_actual.pop(0)
            processed += batch.kilograms
            self.uva_procesada += batch.kilograms
            self.vino_total_producido += (batch.kilograms * batch.quality) * 0.55
        print(self)

    def resolver_evento(self, event: str) -> None:
        """
        Resolves the given event.

        :param event: Name of the event
        """
        if event == 'descarga':
            self.descargar_camiones()

    def __str__(self) -> str:
        string = f"""
        Planta: {self.nombre}
        Uva procesada: {self.uva_procesada}
        Vino procesado: {self.vino_total_producido}
        Uva dentro: {self.carga_actual}
        """
        return string
