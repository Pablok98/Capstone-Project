import json
from PyQt5.QtWidgets import QApplication
from files import load_initial_data, write_excel_listed, read_lot_data
import params as p
from simulator.motor import Wine
from simulator.ui.ui import GUI
import threading
import sys
from os.path import join
from simulator.sim import SimulationObject
import logging
from modelo_test import modelo_principal
from initial_data import write_rain

logging.basicConfig(filename='simulation.log', filemode='w', format='%(levelname)s - %(message)s', level=logging.INFO)

dia_inicial = p.INITIAL_DAY
# Primera optimización
modelo_principal(dia_inicial, paths=True)

# Inicializacion del simulador
# Leemos excel de lotes
lot_data = read_lot_data()
# Instanciamos el motor
winifera = Wine(lot_data, True)


# Cargamos la información de la optimizacion
def cargar_data_semana():
    global winifera
    for path, name in p.PATHS_FINAL.items():
        with open(path, 'r') as file:
            data = json.load(file)
            winifera.assign_data.load_data(name, data)
    write_rain()


cargar_data_semana()
# Iniciación ui
app = QApplication(sys.argv)
ventana = GUI()
winifera.status_signal = ventana.status_signal
winifera.command_signal = ventana.command_signal
winifera.initialize(dia_inicial)


def loop_semanal():
    global winifera
    while SimulationObject.current_day <= p.TOTAL_DAYS: # cambiar p.TOTAL_DAYS
        cargar_data_semana()
        motor_thread = threading.Thread(target=winifera.run_week, daemon=True)
        motor_thread.start()
        motor_thread.join()
        if winifera.lotes_veraison:
            modelo_principal(SimulationObject.current_day, winifera.grape_disp(), winifera.plant_recv(),
                         winifera.fermented_unprocessed(), True)

    print(winifera.obtener_info("calidad_promedio"))
    print("\n")
    print(winifera.obtener_info("ocupacion_promedio_ferm"))
    print("\n")
    print(winifera.obtener_info("procesado_planta"))
    print("\n")
    print(winifera.obtener_info("porcentaje_camiones_tercero"))
    print("\n")
    print(winifera.obtener_info("porcentaje_uva_terceros"))
    print("\n")
    print(winifera.obtener_info("costos_procesamiento"))
    print("\n")
    print(winifera.obtener_info("costos_transporte"))


thrd = threading.Thread(target=loop_semanal, daemon=True)
thrd.start()
sys.exit(app.exec())



