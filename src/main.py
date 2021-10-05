from files import load_initial_data, write_excel_listed, read_lot_data
from simulator import simulate_rain
import params as p
from simulator.motor import Wine
from simulator.ui.ui import GUI
import threading
import sys

"""
dfs = load_initial_data()
rain_data = simulate_rain(dfs[0], p.TIME_RANGE)
write_excel_listed(rain_data, p.RAIN_DATA_PATH)
"""

ui = False

winifera = Wine(ui)
winifera.test()


lot_data = read_lot_data()
winifera.instanciar_lotes(lot_data)


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
