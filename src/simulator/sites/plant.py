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
        self.name = name
        self.ferm_cap = ferm_cap
        self.prod_cap = prod_cap
        self.hopper_cap = hopper_cap
        self.bin_cap = bin_cap

        # grapes contains tuples, each with values(quantity, quality, date). When grape is unloaded
        # from trucks, the quantity and quality is stored in the list, as well as the date unloaded.
        self.grapes: list[Batch] = []
        # Current state variables
        self.total_wine = 0
        self.total_grape = 0
        self.trucks: list[Truck, None] = []

        self.unload_time: Union[datetime, None] = None

        self.daily_grapes = 0

    @property
    def week_recieved(self):
        load = 0
        for batch in self.grapes:
            time_ = (SimulationObject.current_time - batch.date).days < 7
            if not time_:
                break
            load += batch.kilograms
        return load

    @property
    def current_load(self) -> int:
        """
        Iterates through the batches (tuples) of grape and counts the total grape currently
        inside the plant.

        :return: Current grape load
        """
        load = 0
        for batch in self.grapes:
            load += batch.kilograms
        return load

    @property
    def daily_grape_percentage(self) -> float:
        """
        :return: Current percentage of total capacity loaded in the day
        """
        return round(self.daily_grapes / self.ferm_cap, 3)

    def truck_arrival(self, truck) -> None:
        """
        Method to call when a truck gets to the plant.

        :param truck: truck to add to the plant
        """
        self.trucks.append(truck)

    @property
    def next_event(self) -> tuple[str, str, datetime]:
        """
        Calculates all the events in the plant, and returns the data of the closest event.

        :return: A tuple with the following format (site Name, event name, event time)
        """
        if not self.trucks or self.daily_grape_percentage >= SimulationObject.MAX_DAILY_UNLOAD:
            return self.name, 'unload', SimulationObject.never_date
        if not self.unload_time:
            self.unload_time = SimulationObject.current_time + timedelta(minutes=60)
        return self.name, 'unload', self.unload_time

    def unload_constraint(self) -> bool:
        """
        Checks if the plant can currently can unload grapes from a truck to the local storage

        :return: True if the plant can still unload grapes, False in other case.
        """
        # We can only unload a percentage of the max capacity (per day)
        max_daily = self.daily_grape_percentage <= SimulationObject.MAX_DAILY_UNLOAD
        # We can't unload more than the plant's capacity
        max_cap = self.current_load < self.ferm_cap
        # We only unload if there's still trucks on the site
        truck = self.trucks != []
        return max_daily and max_cap and truck

    def unload_trucks(self) -> None:
        """
        Unloads grape from the current truck queue. Simulates an hour of unloading.
        """
        # We set the new global time, and reset the next unload event time.
        SimulationObject.current_time = self.unload_time
        self.unload_time = None

        unloaded = 0  # For storing current unloaded grape
        # We only can unload while we comply certain restrictions
        while self.unload_constraint():
            truck = self.trucks[0]  # Truck to unload
            rate = self.bin_cap if truck.loading_bins else self.hopper_cap  # Maximum hourly rate

            print(f"Descargando camion {truck.id} en la planta {self.name}")
            # While we still can unload grapes, we take grape batched from the truck and store them
            # in the plant's storage
            while unloaded < rate and truck.has_content:
                kg, quality = truck.unload()
                batch = Batch(kg, quality, SimulationObject.current_time)

                self.grapes.append(batch)
                self.daily_grapes += kg
                unloaded += kg
            # If the truck doesn't have contents, we remove it from the plant
            if not truck.has_content:
                self.trucks.pop(0)

    def process_day(self) -> None:
        """
        Processes the grape currently in the plant (given by the max rate of processing by
        the plant)
        """
        print(f"Procesando uva en la planta {self.name}")

        processed = 0
        # We process grape until we reach the maximum daily capacity or grape is exhausted
        while processed < self.prod_cap and self.grapes:
            # We must check if the next grape in the queue has been fermented
            fermented = (SimulationObject.current_time - self.grapes[0].date).days >= 7
            if not fermented:
                break
            batch = self.grapes.pop(0)
            processed += batch.kilograms
            self.total_grape += batch.kilograms
            self.total_wine += (batch.kilograms * batch.quality) * 0.55
        print(self)

    def resolve_event(self, event: str) -> None:
        """
        Resolves the given event.

        :param event: Name of the event
        """
        if event == 'unload':
            self.unload_trucks()

    def __str__(self) -> str:
        string = f"""
        Planta: {self.name}
        Uva procesada: {self.total_grape}
        Vino procesado: {self.total_wine}
        Uva dentro: {self.current_load}
        """
        return string
