import params as p
from typing import Union
from ..entities import *
from ..sites import *
from machine import Machine


class Truck(Machine):
    _id = 0

    def __init__(self, tipo: str, tolva: int, bines: int):
        super().__init__(p.TASA_DEPRECIACION_TRACTOR, p.COSTO_POR_TONELADA_TRACTOR)
        Truck._id += 1
        self.id = Truck._id
        self.nombre = 'camion'
        self.tipo = tipo
        self.cap_tolva = tolva
        self.cap_bines = bines

        self.planta_asignada: Union[str, None] = None

        self.de_bin = True

        self.tolvas: list[Hopper] = []
        self.bines: list[Bin] = []

        self.driver: Union[TruckDriver, None] = None

        self.distance_travelled = 0

        self.current_lot: Union[Lot, None] = None

    def clean(self):
        self.tolvas = []
        self.de_bin = True
        self.driver = None
        self.current_lot = None
        self.planta_asignada = None

    def assign_driver(self, driver: TruckDriver) -> None:
        if driver.dias_trabajando < p.MAX_DIAS_TRABAJO_CONDUCTORES:
            self.driver = driver
            driver.assign_truck(self)
            print(f'El conductor {driver._id} fue asignado al camion {self._id}')

        else:
            print(f"El conductor {driver._id} no pudo ser asignado al camion {self.id}" +
                  "porque excede los dias maximos de trabajo")

    @property
    def lleno(self) -> bool:
        if self.de_bin:
            return not len(self.bines) < self.cap_bines
        return not len(self.tolvas) < self.cap_tolva

    @property
    def tiene_contenido(self) -> bool:
        if self.de_bin:
            return self.bines != []
        for tolva in self.tolvas:
            if tolva.tiene_contenido:
                return True
        return False

    @property
    def espacio_tolva(self) -> bool:
        return len(self.tolvas) < self.cap_tolva

    def descargar(self) -> Union[tuple[int, float], None]:
        if self.tiene_contenido:
            if self.de_bin:
                bin_ = self.bines.pop(0)
                return bin_.descargar()
            else:
                for tolva in self.tolvas:
                    if tolva.tiene_contenido:
                        return tolva.descargar()

    def assign_driver(self, driver: TruckDriver) -> None:
        if self.driver:
            print(f'Truck {self._id} already has a driver')

        else:
            self.driver = driver

    def travel(self) -> None:
        distance = self.current_lot.plant_distances[self.planta_asignada]
        self.distance_travelled += distance

    def estado(self) -> dict:
        tipo = 'Bines' if self.de_bin else 'Tolva'
        capacidad = self.cap_bines if self.de_bin else self.cap_tolva
        ocupacion = len(self.bines) if self.de_bin else len(self.tolvas)
        return {
            'id': self.id,
            'tipo': tipo,
            'capacidad': capacidad,
            'ocupacion': ocupacion
        }
