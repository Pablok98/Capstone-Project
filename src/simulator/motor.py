from collections import deque
from random import expovariate, randint, uniform, seed
from datetime import datetime, timedelta
from time import sleep
from typing import Union

import pandas as pd

from .entities import *
from .sites import *

from .sim import SimulationObject, Interface

from files import read_rain_data

from params import TRUCK_DATA, PLANTS_DATA


class Wine(SimulationObject):
    def __init__(self, lot_data: dict, ui=False):
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

        self.rain_data: Union[pd.DataFrame, None] = None

        self.status_signal = None
        self.command_signal = None

        self.week_number = 0

        self.assign_data = Interface()

    @property
    def fin_jornada(self) -> datetime:
        return SimulationObject.current_time.replace(hour=18, minute=0, second=0)

    @property
    def termino_dia(self) -> datetime:
        return SimulationObject.current_time.replace(hour=22, minute=0, second=0)

    def set_rain_data(self) -> None:
        self.rain_data = read_rain_data()

    def set_daily_rain(self) -> None:
        for lot in self.lotes.values():
            mask = self.rain_data['Lote COD'] == lot.name
            lluvia = int(self.rain_data[mask][f'day {self.week_day}'])
            lot.rain(lluvia)

    @property
    def week_day(self) -> int:
        day = SimulationObject.current_day - self.week_number * 7
        return day

    def pass_day(self):
        SimulationObject.current_time += timedelta(days=1)
        SimulationObject.current_day += 1
        if (SimulationObject.current_day + 1) % 7 == 0:
            self.week_number += 1
        SimulationObject.current_time.replace(hour=6, minute=0, second=0)

    def set_initial_day(self, day):
        if day % 7 != 0:
            print("No es el inicio de la semana!")
            return
        SimulationObject.current_day = day
        SimulationObject.current_time += timedelta(days=day)
        self.week_number = int(day/7)
        print(SimulationObject.current_time)

    def asignar_jornalero(self, jornalero: Laborer, lote: str) -> None:
        self.lotes[lote].assign_laborer(jornalero)

    def assign_truck(self, truck: Truck, lot: str) -> None:
        self.lotes[lot].assign_truck(truck)

    @staticmethod
    def assign_truck_driver(driver: TruckDriver, truck: Truck) -> None:
        truck.assign_driver(driver)

    @staticmethod
    def assign_machine_driver(driver: MachineDriver, machine: Union[LiftTruck, Tractor]) -> None:
        machine.assign_driver(driver)

    @property
    def lotes_veraison(self) -> dict[str, Lot]:
        results = {}
        for llabe, lote in self.lotes.items():
            dia_optimo = lote.optimal_day
            dia1 = dia_optimo.replace(hour=10, minute=10, second=10, microsecond=10)
            dia2 = SimulationObject.current_time.replace(hour=10, minute=10, second=10, microsecond=10)
            if abs((dia1 - dia2).days) <= 7:
                results[llabe] = lote
        return results

    def run(self):
        self.instanciar_lotes(self.lot_data)
        self.set_initial_day(77)
        #self._test_instancing()
        self.initial_instancing()
        self.set_rain_data()

        while SimulationObject.current_day <= 86:
            #self._test_assing()
            self.assign()
            self.set_daily_rain()
            self.simular_dia()

    def simular_dia(self) -> None:
        for lote in self.lotes.values():
            lote.start_day()

        if self.ui:
            self.command_signal.emit('lotes_inicial', self.lotes_veraison)

        while SimulationObject.current_time < self.fin_jornada:
            print(len(self.lotes_veraison))
            eventos = {}
            for lote in self.lotes.values():
                lot, evento, tiempo = lote.next_event
                eventos[lot] = {'event': evento, 'tiempo': tiempo}
            for plant in self.plantas.values():
                planta, evento, tiempo = plant.next_event
                eventos[planta] = {'event': evento, 'tiempo': tiempo}
            prox_lote = min(eventos, key=lambda x: eventos[x]['tiempo'])
            if prox_lote in ['P1', 'P2', 'P3', 'P4', 'P5']:
                retorno = self.plantas[prox_lote].resolve_event(eventos[prox_lote]['event'])
            else:
                retorno = self.lotes[prox_lote].resolve_event(eventos[prox_lote]['event'])
            print(len(self.lotes_veraison))
            if retorno:
                if type(retorno) == Truck:
                    planta = self.plantas[retorno.planta_asignada]
                    retorno.travel()
                    planta.truck_arrival(retorno)
            sleep(0.5)
            if self.ui:
                self.status_signal.emit(self.estado_lotes_ui())
            else:
                print(self.estado_lotes_noui())

        for lote in self.lotes.values():
            for camion in lote.trucks:
                planta = self.plantas[camion.assigned_plant]
                camion.travel()
                planta.truck_arrival(camion)
        while SimulationObject.current_time < self.termino_dia:
            eventos = {}
            for plant in self.plantas.values():
                planta, evento, tiempo = plant.next_event
                eventos[planta] = {'event': evento, 'tiempo': tiempo}
            prox_planta = min(eventos, key=lambda x: eventos[x]['tiempo'])
            if eventos[prox_planta]['tiempo'] == datetime(3000, 1, 1, hour=6, minute=0, second=0):
                break
            self.plantas[prox_planta].resolve_event(eventos[prox_planta]['event'])

        for planta in self.plantas.values():
            planta.process_day()

        self.pass_day()

    def estado_lotes_ui(self):
        data = {}
        for lote in self.lotes_veraison.values():
            data[lote.name] = lote.estado
        return data

    def estado_lotes_noui(self) -> str:
        string = ""
        for lote in self.lotes.values():
            string += lote.estado_string
        return string

    def instanciar_lotes(self, info: dict) -> None:
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

    def initial_instancing(self):
        # Plant instancing
        # TODO: use keyword arguments
        for p_name, plant in PLANTS_DATA.items():
            self.plantas[p_name] = Plant(
                p_name,
                plant['ferm_cap']*1000,
                plant['prod_cap']*1000,
                plant['hopper_cap']*1000,
                plant['bin_cap']*1000
            )
        for c_type, truck in TRUCK_DATA.items():
            for _ in range(truck['avail_units']):
                truck_i = Truck(c_type, truck['hopper_cap'], truck['bin_cap'])
                self.camiones[truck_i.id] = truck_i

        # TODO: Special day set

    def week_assignments(self):
        # Clean state
        for truck in self.camiones.values():
            truck.clean()

    def _test_instancing(self) -> None:
        test_d = {
            "P1": 1,
            "P2": 2,
            "P3": 3,
            "P4": 4,
            "P5": 5
        }
        # Overwrite test lots
        self.lotes['U_1_8_58_118'] = Lot('U_1_8_58_118', 1, 58000, 1, [0.9, 0.85], test_d)
        self.lotes['U_2_6_138_123'] = Lot('U_2_6_138_123', 3, 58000, 4, [0.9, 0.85], test_d)
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
        self.tolvas.append(Hopper())

        # Harvester instancing
        self.cosechadoras.append(Harvester())

    def assign(self):
        day_str = f'dia {self.week_day}'
        for laborer, assignation in self.assign_data.laborers.items():
            if day_str in assignation:
                self.lotes[assignation[day_str]].laborers.append(Laborer())

        for id_, camion in self.camiones.items():
            camion.clean()
            if day_str in self.assign_data.trucks[str(id_)]:
                self.assign_truck(camion, self.assign_data.trucks[str(id_)][day_str])
                camion.assigned_plant = 'P1'

        for lot, assignation in self.assign_data.hoppers.items():
            for _ in range(int(assignation[day_str])):
                self.lotes[lot].hoppers.append(Hopper())

        for lot, assignation in self.assign_data.harvesters.items():
            for _ in range(int(assignation[day_str])):
                self.lotes[lot].hoppers.append(Hopper())

        for lot, assignation in self.assign_data.lift_trucks.items():
            for _ in range(int(assignation[day_str])):
                self.lotes[lot].hoppers.append(Hopper())

    def _test_assing(self) -> None:
        for i, jornalero in enumerate(self.jornaleros):
            if i < 5:
                self.asignar_jornalero(jornalero, 'U_1_8_58_118')
            else:
                self.asignar_jornalero(jornalero, 'U_2_6_138_123')

        for camion in self.camiones.values():
            if not camion.has_content:
                camion.clean()
                if camion.id == 1:
                    self.assign_truck(camion, 'U_1_8_58_118')
                    camion.assigned_plant = 'P1'
                    camion.loading_bins = False
                elif camion.id == 2:
                    camion.assigned_plant = 'P1'
                    self.assign_truck(camion, 'U_1_8_58_118')
                elif camion.id == 3:
                    camion.assigned_plant = 'P1'
                    self.assign_truck(camion, 'U_2_6_138_123')

        for tolva in self.tolvas:
            if not tolva.has_content:
                if tolva.id == 1:
                    self.lotes['U_1_8_58_118'].hoppers.append(Hopper())

        for cosechadora in self.cosechadoras:
            self.lotes['U_1_8_58_118'].harvesters.append(cosechadora)

