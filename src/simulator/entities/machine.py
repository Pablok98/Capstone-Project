from abc import ABC
from src.params import MAX_DIAS_TRABAJO_CONDUCTORES
from ..entities import *
from typing import Union


class Machine(ABC):

    def __init__(self, tasa_depreciacion: int, costo_por_tonelada: float):
        self.tasa_depreciacion = tasa_depreciacion
        self.costo_por_tonelada = costo_por_tonelada
        self.days_used = 0
        self.depreciacion_acumulada = 0
        self.driver: Union[MachineDriver, None] = None
        self.working = False


    def assign_driver(self, driver: MachineDriver) -> None:
        if driver.dias_trabajando < MAX_DIAS_TRABAJO_CONDUCTORES:
            self.driver = driver
            driver.assign_machine(self)
            print(f'El conductor {driver._id} fue asignado al {self.nombre} con {self._id}')

        else:
            print(f"El conductor {driver._id} no pudo ser asignado al {self.nombre} con {self.id}" +
                  "porque excede los dias maximos de trabajo")

    def depreciar(self) -> None:
        if self.days_used == 30:
            self.days_used = 0
            self.depreciacion_acumulada += self.tasa_depreciacion

    @property
    def available(self):
        if not self.driver or self.working:
            return False
        return True
