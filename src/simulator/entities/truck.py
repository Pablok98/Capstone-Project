import logging

import params as p
from typing import Union
from ..entities import *
from ..sites import *
from .machine import Machine
from ..sim import SimulationObject

Load = Union[tuple[int, float], None]


class Truck(Machine):
    _id = -1

    def __init__(self, type_: str, hopper: int, bins: int):
        super().__init__(p.TASA_DEPRECIACION_TRACTOR, p.COSTO_POR_TONELADA_TRACTOR)
        Truck._id += 1
        self.id = Truck._id

        self.name = 'Truck'
        self.t_type = type_
        self.hopper_cap = hopper
        self.bin_cap = bins

        self.hoppers: list[Hopper] = []
        self.bins: list[Bin] = []

        self.driver: Union[TruckDriver, None] = None  # Current driver assigned to the truck
        self.assigned_plant: Union[str, None] = None  # Current plant assigned to the truck
        self.current_lot: Union[Lot, None] = None  # Lot where the truck is located

        self.distance_travelled = 0
        self.loading_bins = True  # True if the truck currently is loading bins (and not hopper)

    def clean(self) -> None:
        """
        Clears the Truck of any events or assignments it had during a day. Used when reassigned.
        """
        self.hoppers = []
        self.loading_bins = True
        self.driver = None
        self.current_lot = None
        self.assigned_plant = None

    def assign_driver(self, driver: 'TruckDriver') -> None:
        """
        Assigns a driver to this truck. The truck can only function if it has a driver.

        :param driver: Driver to be assigned (can ONLY be a truck driver)
        """
        msg = f'{SimulationObject.current_time} -> '
        if driver.weekly_days < p.MAX_DIAS_TRABAJO_CONDUCTORES or self.driver:
            self.driver = driver
            driver.assign_truck(self)
            msg += f'El conductor {driver.id} fue asignado al camion {self.id}'
            logging.info(msg)
        else:
            msg +=f"El conductor {driver.id} no pudo ser asignado al camion {self.id}" + \
                  "porque excede los dias maximos de trabajo"
            logging.warning(msg)

    @property
    def full(self) -> bool:
        """
        :return: True if the truck cannot load more bins or attach more hoppers, depending on the
                current load type.
        """
        if self.loading_bins:
            return not len(self.bins) < self.bin_cap
        return not len(self.hoppers) < self.hopper_cap

    @property
    def has_content(self) -> bool:
        """
        Checks if either has any bins loaded, or current attached hoppers have content.

        :return: True if there's any grapes to unload, False otherwise
        """
        # Check for bin load
        if self.loading_bins:
            return self.bins != []

        # Check for hopper load
        for hopper in self.hoppers:
            if hopper.has_content:
                return True

        # If neither condition is met, then there's no load
        return False

    @property
    def can_attach(self) -> bool:
        """
        :return: True if the truck can attach a new hopper, False otherwise.
        """
        return len(self.hoppers) < self.hopper_cap

    def unload(self) -> Load:
        """
        :return: Batch of unloaded contents from the truck (if there's no content, then None
                is returned)
        """
        if not self.has_content:
            return

        # Bin unload process
        if self.loading_bins:
            bin_ = self.bins.pop()
            return bin_.unload()

        # Hopper unload process
        for hopper in self.hoppers:
            if hopper.has_content:
                return hopper.unload()

    def travel(self) -> None:
        """
        Must be called when the truck travels to his assigned plant. This method will calculate
        the distance traveled and stores it.
        """
        distance = self.current_lot.plant_distances[self.assigned_plant]
        self.distance_travelled += distance

    def state(self) -> dict:
        """
        Used for visualizing the current state of the truck.

        :return: Dictionary with structured info.
        """
        type_ = 'Bines' if self.loading_bins else 'Tolva'
        capacity = self.bin_cap if self.loading_bins else self.hopper_cap
        load = len(self.bins) if self.loading_bins else len(self.hoppers)
        return {
            'id': self.id,
            'tipo': type_,
            'capacidad': capacity,
            'ocupacion': load
        }
