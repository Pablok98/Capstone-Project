from collections import deque
from random import expovariate, randint, uniform, seed
from datetime import datetime, timedelta
from time import sleep

from .entities import *
from .sites import *

from .sim import SimulationObject
from . import raingen


class Wine(SimulationObject):
    def __init__(self, lot_data, ui=False):
        self.lot_data = lot_data
        self.ui = ui

        self.lotes: dict[str, Lot] = {}
        self.plantas: dict[str, Plant] = {}
        self.camiones: dict[str, Truck] = {}

        self.cosechadoras: list[Harvester] = []
        self.tolvas: list[Hopper] = []
        self.jornaleros: list[Laborer] = []
        self.monta_cargas: list[LiftTruck] = []
        self.conductores: list[MachineDriver] = []
        self.camioneros: list[TruckDriver] = []
        self.tractores: list[Tractor] = []

        self.rain_data = None

        self.status_signal = None
        self.command_signal = None

    @property
    def fin_jornada(self) -> datetime:
        return SimulationObject.tiempo_actual.replace(hour=18, minute=0, second=0)

    @property
    def termino_dia(self) -> datetime:
        return SimulationObject.tiempo_actual.replace(hour=22, minute=0, second=0)

    @property
    def dia(self) -> int:
        return SimulationObject.tiempo_actual.day

    def set_rain_data(self):
        self.rain_data = raingen.read_data()

    def set_daily_rain(self):
        for lot in self.lotes.values():
            mask = self.rain_data['Lote COD'] == lot.nombre
            lluvia = int(self.rain_data[mask][f'day {self.dia}'])
            lot.llover(lluvia)

    def asignar_jornalero(self, jornalero, lote):
        self.lotes[lote].asignar_jornalero(jornalero)

    def assign_truck(self, truck, lot):
        self.lotes[lot].assign_truck(truck)

    @staticmethod
    def assign_truck_driver(driver, truck):
        truck.assign_driver(driver)

    @staticmethod
    def assign_machine_driver(driver, machine):
        machine.assign_driver(driver)

    @property
    def lotes_veraison(self):
        results = {}
        for llabe, lote in self.lotes.items():
            dia_optimo = lote.dia_optimo
            if abs((dia_optimo - SimulationObject.tiempo_actual).days) <= 7:
                results[llabe] = lote
        return results

    def run(self):
        self.instanciar_lotes(self.lot_data)
        self._test_instancing()
        self.set_rain_data()
        self.set_daily_rain()

        while SimulationObject.tiempo_actual.day <= 7:
            self._test_assing()
            self.simular_dia()

    def simular_dia(self):
        for lote in self.lotes.values():
            lote.iniciar_dia()

        if self.ui:
            self.command_signal.emit('lotes_inicial', self.lotes_veraison)

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

            if self.ui:
                self.status_signal.emit(self.estado_lotes_ui())
            else:
                print(self.estado_lotes_noui())
            sleep(0.02)

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

        new_day = SimulationObject.tiempo_actual.day + 1
        new_time = SimulationObject.tiempo_actual.replace(day=new_day, hour=6, minute=0, second=0)
        SimulationObject.tiempo_actual = new_time

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
            self.lotes[name] = Lot(name, info_lote["Tipo_UVA"], info_lote["Tn"]*1000,
                                   info_lote["Dia_optimo_cosecha"], info_lote["rango_calidad"],
                                   dist_plantas)

    def _test_instancing(self):
        test_d = {
            "P1": 1,
            "P2": 2,
            "P3": 3,
            "P4": 4,
            "P5": 5
        }
        # Overwrite test lots
        self.lotes['U_1_8_58_118'] = Lot('U_1_8_58_118', '1', 58000, 1, [0.9, 0.85], test_d)
        self.lotes['U_2_6_138_123'] = Lot('U_2_6_138_123', '3', 58000, 4, [0.9, 0.85], test_d)
        # Plant instancing
        self.plantas['P1'] = Plant('P1', 2500000, 150000, 50000, 40000)

        # Laborer instancing
        for _ in range(10):
            self.jornaleros.append(Laborer())

        # Truck instancing
        camion = Truck("A", 1, 2)
        self.camiones[camion.id] = camion
        camion = Truck("B", 1, 200)
        self.camiones[camion.id] = camion
        camion = Truck("A", 2, 2)
        self.camiones[camion.id] = camion

        # Hopper instancing
        self.tolvas.append(Hopper)

        # Harvester instancing
        self.cosechadoras.append(Harvester())

    def _test_assing(self):
        for i, jornalero in enumerate(self.jornaleros):
            if i < 5:
                self.asignar_jornalero(jornalero, 'U_1_8_58_118')
            else:
                self.asignar_jornalero(jornalero, 'U_2_6_138_123')

        for camion in self.camiones.values():
            if not camion.tiene_contenido:
                camion.clean()
                if camion.id == 1:
                    self.assign_truck(camion, 'U_1_8_58_118')
                    camion.planta_asignada = 'P1'
                    camion.de_bin = False
                elif camion.id == 2:
                    camion.planta_asignada = 'P1'
                    self.assign_truck(camion, 'U_1_8_58_118')
                elif camion.id == 3:
                    camion.planta_asignada = 'P1'
                    self.assign_truck(camion, 'U_2_6_138_123')

        for tolva in self.tolvas:
            if not tolva.tiene_contenido:
                if tolva.id == 1:
                    self.lotes['U_1_8_58_118'].tolvas.append(Hopper())

        for cosechadora in self.cosechadoras:
            self.lotes['U_1_8_58_118'].cosechadoras.append(cosechadora)

