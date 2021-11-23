import json

from files import load_initial_data, write_excel_listed, read_lot_data
import params as p
from simulator.motor import Wine
from simulator.ui.ui import GUI
import threading
import sys
from os.path import join
from simulator.sim import SimulationObject
import logging

logging.basicConfig(filename='simulation.log', filemode='w', format='%(levelname)s - %(message)s', level=logging.INFO)
# from modelo_test import modelo_principal

ui = True
lot_data = read_lot_data()
winifera = Wine(lot_data, ui)


for path, name in p.PATHS_DUMP.items():
    with open(path, 'r') as file:
        data = json.load(file)
        winifera.assign_data.load_data(name, data)

# -----------------------------

if ui:
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)

    ventana = GUI()
    winifera.status_signal = ventana.status_signal
    winifera.command_signal = ventana.command_signal
    motor_thread = threading.Thread(target=winifera.run, daemon=True)
    motor_thread.start()
    sys.exit(app.exec())
else:
    winifera.run()


# modelo_principal(winifera.current_day, winifera.grape_disp(), winifera.plant_recv(), winifera.fermented_unprocessed())