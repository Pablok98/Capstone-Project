from collections import deque
from random import expovariate, randint, uniform, seed
from datetime import datetime, timedelta
from time import sleep

from entities import *
from sites import *

from sim import SimulationObject


class Wine(SimulationObject):
    def __init__(self):
        # Entities
        self.lotes = {}
        self.plantas = {}
        self.fin_jornada = datetime(2021, 1, 1, hour=18, minute=0, second=0)

    def asignar_jornalero(self, jornalero, lote):
        print(f"El jornalero {jornalero._id} fue asignado al lote {lote}")
        self.lotes[lote].jornaleros.append(jornalero)

    def poblar(self):
        """
        Asigna jornaleros y camiones a los lotes
        """
        self.lotes['u_1_8'] = Lot('u_1_8', 8, 58000, 118)
        self.lotes['u_1_8'].jornaleros.append(Laborer())
        self.lotes['u_1_8'].jornaleros.append(Laborer())
        self.lotes['u_1_8'].jornaleros.append(Laborer())
        self.lotes['u_1_8'].camiones.append(Truck("A", 2, 36))
        self.lotes['u_1_8'].instanciar()

        self.lotes['u_1_9'] = Lot('u_1_9', 8, 58000, 118)
        self.lotes['u_1_9'].jornaleros.append(Laborer())
        self.lotes['u_1_9'].jornaleros.append(Laborer())
        self.lotes['u_1_9'].camiones.append(Truck("A", 2, 36))
        self.lotes['u_1_9'].instanciar()

    def run(self):
        # Placeholder lluvia
        for lote in self.lotes.values():
            lote.lloviendo = randint(0, 1)

        while SimulationObject.tiempo_actual < self.fin_jornada:
            eventos = {}
            for lote in self.lotes.values():
                lot, evento, tiempo = lote.proximo_evento
                eventos[lot] = {'event': evento, 'tiempo': tiempo}
            prox_lote = min(eventos, key=lambda x: eventos[x]['tiempo'])
            self.lotes[prox_lote].resolver_evento(eventos[prox_lote]['event'])
            sleep(0.1)



if __name__ == "__main__":
    winifera = Wine()
    winifera.poblar()
    winifera.run()