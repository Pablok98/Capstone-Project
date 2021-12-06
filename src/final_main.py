import json
from PyQt5.QtWidgets import QApplication
from files import load_initial_data, write_excel_listed, read_lot_data
import params as p
from simulator.motor import Wine
from simulator.ui.ui import GUI
import threading
import sys
from os.path import join
from simulator.sim import SimulationObject, reset_sim
from modelo_test import modelo_principal
from initial_data import write_rain
from custom_log import setup_logger
import time
from datetime import datetime
from simulator.entities import *

# Cargamos la información de la optimizacion
def cargar_data_semana(motor):
    for path, name in p.PATHS_FINAL.items():
        with open(path, 'r') as file:
            data = json.load(file)
            motor.assign_data.load_data(name, data)
    write_rain()


def obtener_kpis(motor, n_it):
    simulation_kpis = {}

    simulation_kpis["calidad_promedio"] = motor.obtener_info("calidad_promedio")
    simulation_kpis["ocupacion_promedio_ferm"] = motor.obtener_info("ocupacion_promedio_ferm")
    simulation_kpis["procesado_planta"] = motor.obtener_info("procesado_planta")
    simulation_kpis["porcentaje_camiones_tercero"] = motor.obtener_info("porcentaje_camiones_tercero")
    simulation_kpis["porcentaje_uva_terceros"] = motor.obtener_info("porcentaje_uva_terceros")

    costos_procesamiento = motor.obtener_info("costos_procesamiento")
    costos_transporte = motor.obtener_info("costos_transporte")
    costos_jornaleros = motor.obtener_info("costos_jornaleros")
    costos_asignacion = motor.obtener_info("costos_asignacion")

    simulation_kpis["costos_procesamiento"] = costos_procesamiento
    simulation_kpis["costos_transporte"] = costos_transporte
    simulation_kpis["costos_jornaleros"] = costos_jornaleros
    simulation_kpis["costos_asignacion"] = costos_asignacion
    simulation_kpis["costos_totales"] = costos_procesamiento + costos_transporte + costos_jornaleros + costos_asignacion

    i = 1  # iteration number

    kpis = {f"iter_{i}": simulation_kpis}

    path_kpi = join('results', 'kpi', f'results_{n_it}.json')

    with open(path_kpi) as file:
        data = json.load(file)

    data.update(kpis)

    with open(path_kpi, "w") as file:
        json.dump(data, file, indent=4)


def loop_semanal(motor, n_it, window):
    path_logger = join('results', 'logs', f'simulation_{n_it}.log')
    print(("*" * 10 + "INICIANDO LOOP SEMANAL" + "*" * 10).center(60))
    while SimulationObject.current_day <= (p.TOTAL_DAYS - 7):
        print(SimulationObject.current_day)
        if p.UI:
            window.restart()
        print(("*" * 10 + f"OPTIMIZANDO SEMANA {motor.week_number}" + "*" * 10).center(60))
        print()
        cargar_data_semana(motor)
        # motor_thread = threading.Thread(target=motor.run_week, daemon=True)
        # motor_thread.start()
        # motor_thread.join()
        motor.run_week()
        if motor.lotes_veraison and not (SimulationObject.current_day == p.TOTAL_DAYS):
            modelo_principal(SimulationObject.current_day, motor.grape_disp(), motor.plant_recv(),
                         motor.fermented_unprocessed(), paths=True, path_logger=path_logger)

    obtener_kpis(motor, n_it)


def run_process(ctd):
    lot_data = read_lot_data()
    ui = p.UI
    ventana = None

    if ui:
        app = QApplication(sys.argv)
        ventana = GUI()

    dmn = True
    if not ui:
        dmn = False

    thrd = threading.Thread(target=iterate_opt, daemon=dmn, args=(ctd, lot_data, ui, ventana))
    thrd.start()

    if ui:
        sys.exit(app.exec())


def iterate_opt(ctd, lot_data, ui, ventana):
    inicio = time.time()

    print(("=" * 60).center(60))
    print(("*"*20 + "INICIANDO PROGRAMA" + "*"*20).center(60))
    print(("=" * 60).center(60))
    print()
    for it in range(ctd):
        inicio_local = time.time()
        print()
        msg = "="*15 + ' ' * 2 + f"EJECUTANDO ITERACIÓN NÚMERO: {it}" + ' ' * 2 + "="*15
        print(msg.center(60))
        optimizar(it, lot_data, ui, ventana)

        print()
        print("="*60)
        print("Iteración terminada")
        print()
        final = round(time.time() - inicio, 3)
        final_local = round(time.time() - inicio_local, 3)
        print("\nTiempo de ejecucion iteracion: {}[s]".format(final_local))
        print("\nTiempo de ejecucion total: {}[s]".format(final))

        reset_sim()
        # Nose donde mas dejar esto
        Crate._id = 0
        Hopper._id = 0
        Laborer._id = 0
        LiftTruck._id = 0
        MachineDriver._id = 0
        Truck._id = -1
        Tractor._id = 0
        TruckDriver._id = 0
        Bin._id = 0
        Harvester._id = 0

        if p.UI:
            ventana.restart()

    print("Simulación terminada")
    sys.exit()


def optimizar(n_it, lot_data, ui, window=None):
    path_logger = join('results', 'logs', f'simulation_{n_it}.log')
    logger = setup_logger(f'logger_{n_it}', path_logger)
    SimulationObject.logger = logger

    dia_inicial = p.INITIAL_DAY
    # Primera optimización
    print(("*"*10 + "REALIZANDO PRIMERA OPTIMIZACIÓN" + "*"*10).center(60))
    print()

    motor = Wine(lot_data, ui, logger)
    modelo_principal(dia_inicial, paths=True, path_logger=path_logger)

    if ui:
        motor.status_signal = window.status_signal
        motor.command_signal = window.command_signal

    motor.initialize(dia_inicial)

    # Create empty kpi json
    path_kpi = join('results', 'kpi', f'results_{n_it}.json')
    data = {}
    with open(path_kpi, "w") as file:
        json.dump(data, file)

    loop_semanal(motor, n_it, window)

    # thrd = threading.Thread(target=loop_semanal, daemon=dmn, args=(motor, logger, n_it))
    # thrd.start()


if __name__ == "__main__":
    run_process(10)


