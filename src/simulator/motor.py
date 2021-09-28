from collections import deque
from random import expovariate, randint, uniform, seed
from datetime import datetime, timedelta
import time

from entities import Laborer, MotorDriver, TruckDriver, Truck, Hopper, Bin, Harvester
from sites import Lot, Plant


class Wine:
    def __init__(self):
        # Time definition
        self.tiempo_actual = datetime(2021, 1, 1, hour=6, minute=0, second=0)

        # Entities
        self.lotes = {}
        self.plantas = {}

    def asignar_jornalero(self, jornalero, lote):
        """
        Assign laborer to Lot. Done daily.
        """
        print(f"El jornalero {jornalero._id} fue asignado al lote {lote}")
        self.lotes[lote].jornaleros.append(jornalero)


    def run(self):
        pass


    def poblar(self):
        self.lotes['u_1_8'] = Lot('u_1_8', 8, 58000, 118, 231)



if __name__ == "__main__":
    winifera = Wine()
    winifera.poblar()
    winifera.run()