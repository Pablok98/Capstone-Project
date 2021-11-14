import logging
from abc import ABC
from src.params import MAX_DIAS_TRABAJO_CONDUCTORES
from ..entities import *
from typing import Union
from ..sim import SimulationObject


class Machine(ABC):

    def __init__(self, tasa_depreciacion: int, costo_por_tonelada: float):
        self.tasa_depreciacion = tasa_depreciacion
        self.costo_por_tonelada = costo_por_tonelada
        self.days_used = 0
        self.depreciacion_acumulada = 0
        self.driver: Union[MachineDriver, None] = None
        self.working = False
        self.nombre = ''
        self.id = -2

    def assign_driver(self, driver: 'MachineDriver') -> None:
        msg = f'{SimulationObject.current_time} -> '
        if driver.weekly_days < MAX_DIAS_TRABAJO_CONDUCTORES:
            self.driver = driver
            driver.assign_machine(self)
            msg += f'El conductor {driver.id} fue asignado al {self.nombre} con {self.id}'
            logging.info(msg)
        else:
            msg += f"El conductor {driver.id} no pudo ser asignado al {self.nombre} con {self.id}" + \
                  "porque excede los dias maximos de trabajo"
            logging.warning(msg)


    def depreciar(self) -> None:
        if self.days_used == 30:
            self.days_used = 0
            self.depreciacion_acumulada += self.tasa_depreciacion

    @property
    def available(self):
        if not self.driver or self.working:
            return False
        return True
