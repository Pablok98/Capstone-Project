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
        self.termino_dia = datetime(2021, 1, 1, hour=22, minute=0, second=0)

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
        truck.current_lot = self.lotes[lot]

    def assign_driver(self, driver, truck):
        print(f'El conductor {driver._id} fue asignado al camion {truck._id}')
        driver.assign_truck(truck)

    def poblar(self):
        pass

    @property
    def lotes_veraison(self):
        results = {}
        for llabe, lote in self.lotes.items():
            dia_optimo = lote.dia_optimo
            if abs((dia_optimo - SimulationObject.tiempo_actual).days) <= 7:
                results[llabe] = lote
        return results

    def run(self):
        for lote in self.lotes.values():
            lote.iniciar_dia()

        if self.ui:
            self.command_signal.emit('lotes_inicial', self.lotes_veraison)

        self.set_rain_data()
        self.set_daily_rain()

        while SimulationObject.tiempo_actual < self.fin_jornada:
            eventos = {}
            for lote in self.lotes.values():
                lot, evento, tiempo = lote.proximo_evento
                eventos[lot] = {'event': evento, 'tiempo': tiempo}

            for plant in self.plantas.values():
                planta, evento, tiempo = plant.proximo_evento
                eventos[planta] = {'event': evento, 'tiempo': tiempo}
            prox_lote = min(eventos, key=lambda x: eventos[x]['tiempo'])
            if prox_lote in ['P1', 'P2', 'P3', 'P4', 'P5']:
                retorno = self.plantas[prox_lote].resolver_evento(eventos[prox_lote]['event'])
            else:
                retorno = self.lotes[prox_lote].resolver_evento(eventos[prox_lote]['event'])

            if retorno:
                if type(retorno) == Truck:
                    planta = self.plantas[retorno.planta_asignada]
                    retorno.travel()
                    planta.llegada_camion(retorno)
                    print(retorno.estado())

            if self.ui:
                self.status_signal.emit(self.estado_lotes_ui())
            else:
                print(self.estado_lotes_noui())
            sleep(0.0)

        for lote in self.lotes.values():
            for camion in lote.camiones:
                planta = self.plantas[camion.planta_asignada]
                camion.travel()
                planta.llegada_camion(camion)
        while SimulationObject.tiempo_actual < self.termino_dia:
            eventos = {}
            for plant in self.plantas.values():
                planta, evento, tiempo = plant.proximo_evento
                eventos[planta] = {'event': evento, 'tiempo': tiempo}
            prox_planta = min(eventos, key=lambda x: eventos[x]['tiempo'])
            if eventos[prox_planta]['tiempo'] == datetime(3000, 1, 1, hour=6, minute=0, second=0):
                break
            self.plantas[prox_planta].resolver_evento(eventos[prox_planta]['event'])

        for planta in self.plantas.values():
            planta.procesar_dia()

    def estado_lotes_ui(self):
        data = {}
        for lote in self.lotes_veraison.values():
            data[lote.nombre] = lote.estado
        return data

    def estado_lotes_noui(self):
        string = ""
        for lote in self.lotes.values():
            string += lote.estado_string
        return string

    def instanciar_lotes(self, info):
        for name, info_lote in info.items():
            dist_plantas = {
                "P1": info_lote["km_a_P1"],
                "P2": info_lote["km_a_P2"],
                "P3": info_lote["km_a_P3"],
                "P4": info_lote["km_a_P4"],
                "P5": info_lote["km_a_P5"]
            }
            self.lotes[name] = Lot(name, info_lote["Tipo_UVA"], info_lote["Tn"],
                                   info_lote["Dia_optimo_cosecha"], info_lote["rango_calidad"], dist_plantas)

    def test(self):
        test_d = {
            "P1": 1,
            "P2": 2,
            "P3": 3,
            "P4": 4,
            "P5": 5
        }
        self.plantas['P1'] = Plant('P1', 2500000, 150000, 50000, 40000)
        self.lotes['U_1_8_58_118'] = Lot('U_1_8_58_118', '1', 58000, 1, [0.9, 0.85], test_d)
        for _ in range(5):
            self._tasignar_jornalero('U_1_8_58_118')
        camion = Truck("A", 1, 2)
        self.assign_truck(camion, 'U_1_8_58_118')
        camion.planta_asignada = 'P1'
        camion.de_bin = False
        self.lotes['U_1_8_58_118'].tolvas.append(Hopper())
        camion = Truck("B", 1, 200)
        camion.planta_asignada = 'P1'
        self.assign_truck(camion, 'U_1_8_58_118')
        self.lotes['U_1_8_58_118'].cosechadoras.append(Harvester())
        self.lotes['U_2_6_138_123'] = Lot('U_2_6_138_123', '3', 58000, 4, [0.9, 0.85], test_d)
        for _ in range(5):
            self._tasignar_jornalero('U_2_6_138_123')
        camion = Truck("A", 2, 2)
        camion.planta_asignada = 'P1'
        self.assign_truck(camion, 'U_2_6_138_123')

    def _tasignar_jornalero(self, lote):
        self.lotes[lote].jornaleros.append(Laborer())
