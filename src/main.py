import json

from files import load_initial_data, write_excel_listed, read_lot_data
import params as p
from simulator.motor import Wine
from simulator.ui.ui import GUI
import threading
import sys
from os.path import join
from simulator.sim import SimulationObject
"""
dfs = load_initial_data()
rain_data = simulate_rain(dfs[0], p.TIME_RANGE)
write_excel_listed(rain_data, p.RAIN_DATA_PATH)
"""

ui = True
lot_data = read_lot_data()
winifera = Wine(lot_data, ui)

# TODO: get out of here

paths = {
    join('data', 'results', 'lots.json'): 'harvesters',
    join('data', 'results', 'trucks.json'): 'trucks',
    join('data', 'results', 'cuads.json'): 'laborers',
    join('data', 'results', 'hoppers.json'): 'hoppers',
    join('data', 'results', 'harvesters.json'): 'harvesters',
    join('data', 'results', 'lift.json'): 'lift_trucks',
}

for path, name in paths.items():
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
