import time
from collections import deque
from datetime import datetime, timedelta
from time import sleep
from typing import Union
import logging
import pandas as pd

from .entities import *
from .sites import *

from .sim import SimulationObject, Interface

from files import read_rain_data

from params import (EXTERNAL_PLANT, TRUCK_DATA, PLANTS_DATA, INITIAL_DAY, CAMIONEROS, CONDUCTORES,
                    COSECHADORAS, MONTACARGAS)
import logging


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

        self.week_number = INITIAL_DAY // 7

        self.assign_data = Interface()

        self.camiones_originales = 0
        self.camiones_extra = 0

    def run(self):
        self.instanciar_lotes(self.lot_data)
        self.set_initial_day(INITIAL_DAY)
        self.initial_instancing()
        self.set_rain_data()

        last_day = SimulationObject.current_day + 6
        while SimulationObject.current_day <= last_day:
            self.assign()
            self.set_daily_rain()
            self.simular_dia()

    def initialize(self, day):
        self.instanciar_lotes(self.lot_data)
        self.set_initial_day(day)
        self.initial_instancing()

    def run_week(self):
        # There's no variance per week yet
        self.set_rain_data()
        last_day = SimulationObject.current_day + 6
        while SimulationObject.current_day <= last_day:
            self.assign()
            self.set_daily_rain()
            self.simular_dia()


    # ==== INSTANCIAR =========================================================
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

    def set_initial_day(self, day):
        if day % 7 != 0:
            print("No es el inicio de la semana!")
            return
        SimulationObject.current_day = day
        SimulationObject.current_time += timedelta(days=day)
        self.week_number = int(day//7)

    def initial_instancing(self):
        # Plant instancing
        for p_name, plant in PLANTS_DATA.items():
            self.plantas[p_name] = Plant(
                p_name,
                plant['ferm_cap']*1000,
                plant['prod_cap']*1000,
                plant['hopper_cap']*1000,
                plant['bin_cap']*1000
            )
        # Special plant

        self.plantas["P6"] = Plant(
            "P6",
            99999999999999 * 1000,
            9999999999 * 1000,
            9999999999 * 1000,
            9999999999 * 1000
        )

        for c_type, truck in TRUCK_DATA.items():
            for _ in range(truck['avail_units']):
                truck_i = Truck(c_type, truck['hopper_cap'], truck['bin_cap'])
                self.camiones[truck_i.id] = truck_i

        for _ in range(CAMIONEROS):
            self.camioneros.append(TruckDriver())
        for _ in range(CONDUCTORES):
            self.conductores.append(MachineDriver())
        for _ in range(COSECHADORAS):
            self.cosechadoras.append(Harvester())
        for _ in range(MONTACARGAS):
            self.monta_cargas.append(LiftTruck())

        # TODO: Special day set

    def set_rain_data(self) -> None:
        self.rain_data = read_rain_data()

    # =========================================================================
    # Week assigments
    # =========================================================================
    def set_daily_rain(self) -> None:
        for lot in self.lotes.values():
            mask = self.rain_data['Lote COD'] == lot.name
            lluvia = int(self.rain_data[mask][f'day {self.week_day}'])
            lot.rain(lluvia)

    def assign(self):
        day_str = f'dia {self.week_day}'
        for laborer, assignation in self.assign_data.laborers.items():
            if day_str in assignation:
                # TODO: jornaleros totales iniciales
                self.asignar_jornalero(Laborer(), assignation[day_str])

        # Los camiones se sacan de las plantas si quedan a las 10
        for camion in self.camiones.values():
            camion.clean()

        for id_, camion in self.camiones.items():
            if day_str in self.assign_data.trucks[str(id_)]:
                if not (day_str in self.assign_data.truck_type[str(id_)]):
                    logging.warning(f"El camion con id {id_} está asignado a un lote pero no su tipo")
                    camion.loading_bins = True
                else:
                    camion.loading_bins = self.assign_data.truck_type[str(id_)][day_str]

                for camionero in self.camioneros:
                    if camion.assign_driver(camionero):
                        break
                else:
                    logging.warning("No hay camioneros para camionar")
                    continue
                self.camiones_originales += 1
                self.assign_truck(camion, self.assign_data.trucks[str(id_)][day_str])

        for name, lot in self.lotes.items():
            if day_str in self.assign_data.routes[name]:
                plant = self.assign_data.routes[name][day_str]
                lot.assigned_plant = f"P{plant + 1}"
            else:
                lot.assigned_plant = "P6"

        for lot, assignation in self.assign_data.hoppers.items():
            for _ in range(int(assignation[day_str])):
                to_assign = self.lotes[lot]
                if not self.assign_hopper(to_assign):
                    logging.warning('Se intentó asignar un tolva pero no quedan disponibles')
                    break
            else:
                continue
            break

        for lot, assignation in self.assign_data.harvesters.items():
            for _ in range(int(assignation[day_str])):
                to_assign = self.lotes[lot]
                if not self.assign_harvester(to_assign):
                    logging.warning('Se intentó asignar una cosechadora pero no quedan disponibles')
                    break
            else:
                continue
            break

        for lot, assignation in self.assign_data.lift_trucks.items():
            for _ in range(int(assignation[day_str])):
                to_assign = self.lotes[lot]
                if not self.assign_lift_truck(to_assign):
                    logging.warning('Se intentó asignar un montacarga pero no quedan disponibles')
                    break
            else:
                continue
            break

        self.special_assignations()

    def special_assignations(self):
        for lote in self.lotes.values():
            if not lote.trucks:
                cond = (lote.laborers) or (lote.harvesters) or (lote.bins)
                if cond:
                    camion = Truck('A', 2, 36)
                    camion.assign_driver(TruckDriver())
                    self.assign_truck(camion, lote.name)
                    self.camiones_extra += 1

                    if not lote.lift_trucks:
                        lt = LiftTruck()
                        lote.lift_trucks.append(lt)
                        lt.assign_driver(MachineDriver())

    # ========= SIMULATION CYCLE ==============================================
    def simular_dia(self) -> None:
        for lote in self.lotes.values():
            lote.start_day()

        if self.ui:
            self.command_signal.emit('lotes_inicial', self.lotes_veraison)
        sleep(0.5)
        logging.info(f'{SimulationObject.current_time} - Inicia el dia')
        ui_counter = 0
        while SimulationObject.current_time < self.fin_jornada:
            eventos = {}
            for lote in self.lotes.values():
                lot, evento, tiempo = lote.next_event
                eventos[lot] = {'event': evento, 'tiempo': tiempo}
            for plant in self.plantas.values():
                planta, evento, tiempo = plant.next_event
                eventos[planta] = {'event': evento, 'tiempo': tiempo}
            prox_lote = min(eventos, key=lambda x: eventos[x]['tiempo'])
            if eventos[prox_lote]['tiempo'] == SimulationObject.never_date:
                break
            if prox_lote in ['P1', 'P2', 'P3', 'P4', 'P5', 'P6']:
                retorno = self.plantas[prox_lote].resolve_event(eventos[prox_lote]['event'])
            else:
                retorno = self.lotes[prox_lote].resolve_event(
                    eventos[prox_lote]['event'])
            if retorno:
                if type(retorno) == Truck:
                    planta = self.plantas[retorno.assigned_plant]
                    retorno.travel()
                    planta.truck_arrival(retorno)
            if self.ui:
                # ui delay
                if ui_counter == 100:
                    self.status_signal.emit(self.estado_lotes_ui())
                    ui_counter = 0
                else:
                    ui_counter += 1
            else:
                # print(self.estado_lotes_noui())
                pass

        for lote in self.lotes.values():
            lote.end_day()
            for camion in lote.trucks:
                planta = self.plantas[camion.assigned_plant]
                camion.travel()
                planta.truck_arrival(camion)
            lote.truck_clean()

        while SimulationObject.current_time < self.termino_dia:
            eventos = {}
            for plant in self.plantas.values():
                planta, evento, tiempo = plant.next_event
                eventos[planta] = {'event': evento, 'tiempo': tiempo}
            prox_planta = min(eventos, key=lambda x: eventos[x]['tiempo'])
            if eventos[prox_planta]['tiempo'] == datetime(3000, 1, 1, hour=6,
                                                          minute=0, second=0):
                break
            self.plantas[prox_planta].resolve_event(
                eventos[prox_planta]['event'])

        for planta in self.plantas.values():
            planta.process_day()
            planta.end_day()

        self.pass_day()

    @property
    def fin_jornada(self) -> datetime:
        return SimulationObject.current_time.replace(hour=18, minute=0, second=0)

    @property
    def termino_dia(self) -> datetime:
        return SimulationObject.current_time.replace(hour=22, minute=0, second=0)

    @property
    def week_day(self) -> int:
        day = SimulationObject.current_day - self.week_number * 7
        return day

    def pass_day(self):
        SimulationObject.current_time += timedelta(days=1)
        SimulationObject.current_day += 1
        if SimulationObject.current_day % 7 == 0:
            self.week_number += 1
        SimulationObject.current_time = SimulationObject.current_time.replace(hour=6, minute=0, second=0)

    # =======================================================================
    def asignar_jornalero(self, jornalero: Laborer, lote: str) -> None:
        self.lotes[lote].assign_laborer(jornalero)

    def assign_truck(self, truck: Truck, lot: str) -> None:
        self.lotes[lot].assign_truck(truck)
        truck.assigned_plant = self.lotes[lot].assigned_plant

    def assign_hopper(self, lot: Lot):
        for hopper in self.tolvas:
            if not hopper.assigned:
                hopper.assigned = True
                lot.hoppers.append(hopper)
                return True
        return False

    def assign_harvester(self, lot: Lot):
        for harvester in self.cosechadoras:
            if not harvester.assigned:
                harvester.assigned = True
                lot.harvesters.append(harvester)
                # TODO: necesita drivers?
                return True
        return False

    def assign_lift_truck(self, lot: Lot):
        for lift_truck in self.monta_cargas:
            if not lift_truck.assigned:
                lift_truck.assigned = True
                lot.lift_trucks.append(lift_truck)

                lift_truck.assign_driver(MachineDriver())

                return True
        return False

    @staticmethod
    def assign_truck_driver(driver: TruckDriver, truck: Truck) -> None:
        truck.assign_driver(driver)

    @staticmethod
    def assign_machine_driver(driver: MachineDriver, machine: Union[LiftTruck, Tractor]) -> None:
        machine.assign_driver(driver)

    @property
    def lotes_veraison(self) -> "dict[str, Lot]":
        results = {}
        for llabe, lote in self.lotes.items():
            dia_optimo = lote.optimal_day
            dia1 = dia_optimo.replace(hour=10, minute=10, second=10, microsecond=10)
            dia2 = SimulationObject.current_time.replace(hour=10, minute=10, second=10, microsecond=10)
            if abs((dia1 - dia2).days) <= 7:
                results[llabe] = lote
        return results

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

    # ---------------  Optimization functions --------------------------------
    def grape_disp(self):
        info = {}
        for name, lot in self.lotes.items():
            info[name] = lot.grape_quantity
        return info

    def plant_recv(self):
        info = {}
        for name, plant in self.plantas.items():
            if name == "P6":
                continue
            info[name] = plant.recv_grapes
        return info

    def fermented_unprocessed(self):
        info = {}
        for name, plant in self.plantas.items():
            if name == "P6":
                continue
            info[name] = plant.fermented
        return info

    def obtener_info(self, comando):  # entrega la prop de cada planta por la qty
        
        comando_print = comando.replace("_", " ").upper()
        print(comando_print)

        if comando == "calidad_promedio":
            kilo_por_calidad = 0
            total_kilos = 0
            list_kilos_plantas = []
            list_calidad_plantas = []
            for planta in self.plantas:  # agregar plantas de terceros
                calidad_planta = 0
                kilos_planta = 0
                if len(self.plantas[planta].historical_grapes) != 0:
                    lenght = len(self.plantas[planta].historical_grapes)
                    for batch in self.plantas[planta].historical_grapes:
                        if batch.quality != 0:  # eliminar calidad 0
                            kilos_planta += batch.kilograms
                            calidad_planta += batch.quality
                        else:
                            lenght -= 1
                    list_kilos_plantas.append(kilos_planta)
                    list_calidad_plantas.append(calidad_planta/lenght)
                    total_kilos += kilos_planta
                else:
                    list_kilos_plantas.append(0)
                    list_calidad_plantas.append(0)
            print(f"kilos:{list_kilos_plantas}", f"calidad:{list_calidad_plantas}")
            for _ in range(len(self.plantas)):
                kilo_por_calidad += list_kilos_plantas.pop(0)*list_calidad_plantas.pop(0)
            if total_kilos == 0:
                total_kilos = 1
            return kilo_por_calidad / total_kilos

        elif comando == "ocupacion_promedio_ferm":
            ocupacion = []
            for planta in self.plantas:
                historial_util = [0]
                for dia in self.plantas[planta].historical_ferm:
                    if dia != 0:
                        index = self.plantas[planta].historical_ferm.index(dia)
                        historial_util = self.plantas[planta].historical_ferm[index:]
                        break
                print(f"ferm_x_dia: {historial_util}")
                promedio = sum(historial_util)/len(historial_util)
                maximo = max(historial_util)/self.plantas[planta].ferm_cap
                ocupacion.append([self.plantas[planta].name, promedio/self.plantas[planta].ferm_cap, maximo])
            return ocupacion

        elif comando == "procesado_planta":
            ocupacion = []
            for planta in self.plantas.values():
                ocupacion.append(planta.total_grape)
            return ocupacion

        elif comando == "porcentaje_camiones_tercero":
            print(f"camiones originales: {self.camiones_originales}")
            print(f"camiones extra: {self.camiones_extra}")
            return (self.camiones_extra/(self.camiones_originales + self.camiones_extra))
        
        elif comando == "porcentaje_uva_terceros":
            
            kilos_planta_terceros = 0
            kilos_totales = 0
            i = 0

            for planta in self.plantas.values():
                kilos_totales += planta.total_grape

                if i == 5:
                    kilos_planta_terceros += planta.total_grape

                i += 1

            return kilos_planta_terceros / kilos_totales

        
        elif comando == "costos_procesamiento":
            
            costo_total = 0
    
            i = 1

            for planta in self.plantas.values():

                if i < 6:
                    costos_por_kg = PLANTS_DATA[f"P{i}"]["var_cost"]

                else:
                    costos_por_kg = EXTERNAL_PLANT["var_cost"]

                costos_planta = costos_por_kg * planta.total_grape
                costo_total += costos_planta

                i += 1


            return costo_total

        elif comando == "costos_transporte":

            costo_total = 0
            
            for camion in self.camiones.values():
                ton = camion.total_kgs / 1000
                unit = ton * camion.distance_travelled
                costo_por_unidad = TRUCK_DATA[camion.t_type]
                costo = costo_por_unidad * unit
                costo_total += costo

            return costo_total



    # ---------------  Now unused  --------------------------------------------
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