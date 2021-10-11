from ..entities import *
from typing import Union


class TruckDriver:
    _id = 0

    def __init__(self):
        TruckDriver._id += 1
        self.id = TruckDriver._id

        self.truck: Union[Truck, None] = None

        self.available = True
        self.weekly_days = 0
        self.total_days = 0

    def assign_truck(self, truck: Truck) -> None:
        self.truck = truck

