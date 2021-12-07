import sys
from PyQt5.QtWidgets import QMainWindow,QDockWidget, QWidget, QLineEdit, QPushButton, QLabel, QDesktopWidget, QApplication
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt5.QtCore import pyqtSignal, QTimer, QObject, Qt
from PyQt5.QtGui import QFont, QColor

from .components import *


def hook(type, value, traceback):
    print(type)
    print(traceback)


sys.__excepthook__ = hook


class GUI(QMainWindow):
    status_signal = pyqtSignal(dict)
    command_signal = pyqtSignal(str, dict)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status_signal.connect(self.actualizar_estado)
        self.command_signal.connect(self.parse_command)

        self.lot_grid = LotGrid(self)

        self.init_gui()

    def init_gui(self):
        self.setCentralWidget(self.lot_grid)

        self.showMaximized()

    def parse_command(self, command, data):
        if command == 'lotes_inicial':
            self.inicializar_lotes(data)

    def inicializar_lotes(self, info):
        self.lot_grid.set_lots(info)

    def actualizar_estado(self, data):
        self.lot_grid.actualizar(data)

    def restart(self):
        self.lot_grid.reset()



