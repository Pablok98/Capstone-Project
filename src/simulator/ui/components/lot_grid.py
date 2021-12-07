import sys
from PyQt5.QtWidgets import QMainWindow,QDockWidget, QWidget, QLineEdit, QPushButton, QLabel, QDesktopWidget, QApplication
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt5.QtCore import pyqtSignal, QTimer, QObject, Qt, QMutex
from PyQt5.QtGui import QFont, QColor

from .lot_square import LotSquare


class LotGrid(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.lots = {}

        self.mutex = QMutex()

        self.max_fila = 10
        self.ending_coords = (0, 0)  # This is aborrent


        self.init_gui()

    def set_lots(self, data):
        self.mutex.lock()
        i, j = self.ending_coords
        for lot_name in data.keys():
            if lot_name in self.lots.keys():
                continue
            lot = LotSquare()
            self.lots[lot_name] = lot
            self.grid.addWidget(lot, i, j)

            i += 1
            if i == self.max_fila:
                i = 0
                j += 1
        self.ending_coords = (i, j)
        self.mutex.unlock()

    def init_gui(self):
        self.grid = QGridLayout(self)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(10)

    def reset(self):
        self.mutex.lock()
        for name, lot in self.lots.items():
            self.grid.removeWidget(lot)
            lot.setParent(None)
            self.lots[name] = None
        self.lots = {}
        self.ending_coords = (0, 0)
        self.mutex.unlock()

    def actualizar(self, data):
        for name, info in data.items():
            try:
                self.lots[name].update_info(info)
            except KeyError as error:
                continue
