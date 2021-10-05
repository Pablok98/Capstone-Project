from collections import deque
from random import expovariate, randint, uniform, seed
from datetime import datetime, timedelta
from time import sleep

from .entities import *
from .sites import *

from .sim import SimulationObject
from . import raingen

import os


class Wine(SimulationObject):
    def __init__(self, ui=False):
        self.lotes = {}
        self.plantas = {}
        self.rain_data = None
        self.dia = 1
        self.fin_jornada = datetime(2021, 1, 1, hour=18, minute=0, second=0)

        self.ui = ui
        self.status_signal = None
        self.command_signal = None

    def set_rain_data(self):
        self.rain_data = raingen.read_data()

    def set_daily_rain(self):
        for lot in self.lotes.values():
            mask = self.rain_data['Lote COD'] == lot.nombre
            lluvia = int(self.rain_data[mask][f'day {self.dia}'])
            lot.llover(lluvia)

    def asignar_jornalero(self, jornalero, lote):
        print(f"El jornalero {jornalero._id} fue asignado al lote {lote}")
        self.lotes[lote].jornaleros.append(jornalero)

    def assign_truck(self, truck, lot):
        print(f"El camion {truck._id} fue asignado al lote {lot}")
        self.lotes[lot].camiones.append(truck)

    def assign_driver(self, driver, truck):
        print(f'El conductor {driver._id} fue asignado al camion {truck._id}')
        driver.assign_truck(truck)

    def poblar(self):
        pass

    def run(self):
        for lote in self.lotes.values():
            lote.iniciar_dia()

        if self.ui:
            self.command_signal.emit('lotes_inicial', self.lotes)

        self.set_rain_data()
        self.set_daily_rain()

        while SimulationObject.tiempo_actual < self.fin_jornada:
            eventos = {}
            for lote in self.lotes.values():
                lot, evento, tiempo = lote.proximo_evento
                eventos[lot] = {'event': evento, 'tiempo': tiempo}
            prox_lote = min(eventos, key=lambda x: eventos[x]['tiempo'])
            retorno = self.lotes[prox_lote].resolver_evento(eventos[prox_lote]['event'])
            if retorno:
                self.plantas[retorno.planta_asignada].descargar_camion(retorno)

            if self.ui:
                self.status_signal.emit(self.estado_lotes_ui())
            else:
                print(self.estado_lotes_noui())
            sleep(1)

        for lote in self.lotes.values():
            for camion in lote.camiones:
                self.plantas[camion.planta_asignada].descargar_camion(camion)

        for planta in self.plantas.values():
            planta.procesar_dia()

    def estado_lotes_ui(self):
        data = {}
        for lote in self.lotes.values():
            data[lote.nombre] = lote.estado
        return data

    def estado_lotes_noui(self):
        string = ""
        for lote in self.lotes.values():
            string += lote.estado_string
        return string

    def instanciar_lotes(self, info):
        for name, info_lote in info.items():
            self.lotes[name] = Lot(name, info_lote["Tipo_UVA"], info_lote["Tn"],
                                   info_lote["Dia_optimo_cosecha"], info_lote["rango_calidad"])
        print()

    def test(self):
        self.plantas['P1'] = Plant('P1', 2500000, 150000, 50000, 40000)

        self.lotes['U_1_8_58_118'] = Lot('U_1_8_58_118', '1', 58000, 1, [0.9, 0.85])
        for _ in range(5):
            self._tasignar_jornalero('U_1_8_58_118')
        camion = Truck("A", 1, 2)
        camion.de_bin = False
        self.lotes['U_1_8_58_118'].tolvas.append(Hopper())
        camion.planta_asignada = 'P1'
        self.lotes['U_1_8_58_118'].camiones.append(camion)
        camion = Truck("B", 1, 200)
        camion.planta_asignada = 'P1'
        self.lotes['U_1_8_58_118'].camiones.append(camion)
        self.lotes['U_1_8_58_118'].cosechadoras.append(Harvester())

        self.lotes['U_2_6_138_123'] = Lot('U_2_6_138_123', '3', 58000, 4, [0.9, 0.85])
        for _ in range(5):
            self._tasignar_jornalero('U_2_6_138_123')
        camion = Truck("A", 2, 2)
        camion.planta_asignada = 'P1'
        self.lotes['U_2_6_138_123'].camiones.append(camion)

    def _tasignar_jornalero(self, lote):
        self.lotes[lote].jornaleros.append(Laborer())
