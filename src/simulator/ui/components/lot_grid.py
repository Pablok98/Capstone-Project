import sys
from PyQt5.QtWidgets import QMainWindow,QDockWidget, QWidget, QLineEdit, QPushButton, QLabel, QDesktopWidget, QApplication
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt5.QtCore import pyqtSignal, QTimer, QObject, Qt
from PyQt5.QtGui import QFont, QColor

from .lot_square import LotSquare


class LotGrid(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.lots = {}

        self.max_fila = 10

        self.init_gui()

    def set_lots(self, data):
        i, j = 0, 0
        for lot_name in data.keys():
            lot = LotSquare()
            self.lots[lot_name] = lot
            self.grid.addWidget(lot, i, j)

            i += 1
            if i == self.max_fila:
                i = 0
                j += 1

    def init_gui(self):
        self.grid = QGridLayout(self)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(10)

    def actualizar(self, data):
        for name, info in data.items():
            try:
                self.lots[name].update_info(info)
            except KeyError as error:
                continue
