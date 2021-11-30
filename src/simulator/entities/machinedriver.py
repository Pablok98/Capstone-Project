from ..entities import *
from typing import Union


class MachineDriver:
    _id = 0

    def __init__(self):
        MachineDriver._id += 1
        self.id = MachineDriver._id

        self.machine: Union['Machine', None] = None

        self.available = True
        self.weekly_days = 0
        self.total_days = 0
        self.harvested = 0

    def assign_machine(self, machine: 'Machine') -> None:
        self.machine = machine
