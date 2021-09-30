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
        self.plantas['P1'] = Plant('P1', 2500000, 150000, 50000, 40000)

        self.lotes['u_1_8'] = Lot('u_1_8', '1', 58000, 1)
        self.lotes['u_1_8'].jornaleros.append(Laborer())
        self.lotes['u_1_8'].jornaleros.append(Laborer())
        self.lotes['u_1_8'].jornaleros.append(Laborer())
        self.lotes['u_1_8'].jornaleros.append(Laborer())
        self.lotes['u_1_8'].jornaleros.append(Laborer())
        self.lotes['u_1_8'].jornaleros.append(Laborer())
        self.lotes['u_1_8'].jornaleros.append(Laborer())
        self.lotes['u_1_8'].jornaleros.append(Laborer())
        self.lotes['u_1_8'].jornaleros.append(Laborer())
        camion = Truck("A", 2, 2)
        camion.de_bin = False
        self.lotes['u_1_8'].tolvas.append(Hopper())
        camion.planta_asignada = 'P1'
        self.lotes['u_1_8'].camiones.append(camion)
        self.lotes['u_1_8'].cosechadoras.append(Harvester())
        self.lotes['u_1_8'].instanciar()
        """
        self.lotes['u_1_9'] = Lot('u_1_9', '3', 58000, 4)
        self.lotes['u_1_9'].jornaleros.append(Laborer())
        self.lotes['u_1_9'].jornaleros.append(Laborer())
        self.lotes['u_1_9'].jornaleros.append(Laborer())
        self.lotes['u_1_9'].jornaleros.append(Laborer())
        self.lotes['u_1_9'].jornaleros.append(Laborer())
        self.lotes['u_1_9'].jornaleros.append(Laborer())
        camion = Truck("A", 2, 2)
        camion.planta_asignada = 'P1'
        self.lotes['u_1_9'].camiones.append(camion)
        self.lotes['u_1_9'].instanciar()
        """
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
            retorno = self.lotes[prox_lote].resolver_evento(eventos[prox_lote]['event'])
            if retorno:
                self.plantas[retorno.planta_asignada].descargar_camion(retorno)
            sleep(1)
        for planta in self.plantas.values():
            planta.procesar_dia()


if __name__ == "__main__":
    winifera = Wine()
    winifera.poblar()
    winifera.run()