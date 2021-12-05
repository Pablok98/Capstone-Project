from ..entities import *
from typing import Union
from datetime import datetime
from params import TASA_DEPRECIACION_TOLVA, COSTO_POR_TONELADA_TOLVA
from ..sim import SimulationObject
Load = Union["tuple[int, float]", None]


class Hopper:
    _id = 0

    def __init__(self):
        """
        Represents hoppers used to load crates with grapes. Hoppers have to be mounted to a truck
        for transport.
        """
        Hopper._id += 1
        self.id = Hopper._id

        self.max_load = 5

        self.crates: list[Crate] = []
        self.transport_time: Union[datetime, None] = None

        self.depreciation_rate = TASA_DEPRECIACION_TOLVA
        self.ton_cost = COSTO_POR_TONELADA_TOLVA

        self.assigned = False

    @property
    def full(self) -> bool:
        """
        :return: True if the Hopper cannot load more grape, False in other case.
        """
        return len(self.crates) == self.max_load

    @property
    def has_content(self) -> bool:
        """
        :return: True if the Hopper has any crates, False in other case.
        """
        return len(self.crates) != 0

    def load_crate(self, crate: Crate) -> None:
        """
        Loads a crate into the Hopper, only if the hopper has capacity.

        :param crate: Crate to load into the hopper
        """
        if self.full:
            SimulationObject.logger.warning(f"{SimulationObject.current_time} - El tolva {self._id} esta lleno!")
            return
        self.crates.append(crate)

    def unload(self) -> Load:
        """
        Unloads from the hopper the next crate stored (only if it has any contents). The is returned

        :return: Tuple with the attributes of the grape unloaded, in the format (quantity, quality)
        """
        if not self.crates:
            return
        crate = self.crates.pop(0)
        quality = self.real_quality(crate)
        kg = 18
        # If there's no more content, then we're ready for reset.
        if not self.crates:
            self.reset()
        return kg, quality

    def real_quality(self, crate):
        harvest = crate.time_harvested
        current = SimulationObject.current_time
        days = (harvest - current).days
        if days > 3:
            return 0
        q = {
            1: 0.95,
            2: 0.85,
            3: 0.8,
        }
        return crate.quality * q[days]


    def reset(self) -> None:
        self.transport_time = None
