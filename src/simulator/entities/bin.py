from __future__ import annotations
from .crate import Crate
from datetime import datetime
from typing import Union



class Bin:
    _id = 0

    def __init__(self):
        """
        Represents a bin for storing and transporting grape. Can either store crates or be loaded
        with grapes directly (by a harvester).
        """

        Bin._id += 1
        self.id = Bin._id

        self.load_time: Union[datetime, None] = None  # Time which the bin will be loaded to a truck
        self.crates: list[Crate] = []  # List of current content
        self.capacity = 27  # Max crate capacity

    @property
    def full(self) -> bool:
        """
        :return: True if the Bin cannot load more grape, False in other case
        """
        return len(self.crates) == self.capacity

    def load_crate(self, crate: Crate) -> None:
        """
        Receives a crate to store it inside the bin.

        :param crate: Crate to load into the bin.
        """
        self.crates.append(crate)

    def auto_load(self, grape_type: int, quality: float) -> None:
        """
        Auxiliary method to call when a bin is loaded by a automatic harvester, which doesn't use
        crates, but loads directly into the bin. For simplicity reasons, the program will create
        crates until the bin is full, all with the same quality and date.

        :param grape_type: Type of the grape loaded.
        :param quality: Quality of the grape loaded.
        """
        for _ in range(self.capacity):
            self.crates.append(Crate(grape_type, quality))

    def unload(self) -> tuple[int, float]:
        """
        Method to call when a bin is being unloaded into a Plant. It pops all the crates from the
        bin, calculates total grape extracted and it's average quality. It then returns said values

        :return: Tuple with format (quantity, quality)
        """
        # TODO cambiar calidad a cajon mismo

        quality, kg, crates = 0, 0, 0
        for cajon in self.crates:
            kg += 18
            quality += cajon.quality
            crates += 1
        quality /= crates
        self.reset()
        return kg, quality

    def reset(self) -> None:
        self.crates = []
        self.load_time = None

