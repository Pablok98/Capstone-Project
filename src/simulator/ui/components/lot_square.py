import sys
from PyQt5.QtWidgets import QMainWindow,QDockWidget, QWidget, QLineEdit, QPushButton, QLabel, QDesktopWidget, QApplication
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt5.QtCore import pyqtSignal, QTimer, QObject, Qt
from PyQt5.QtGui import QFont, QColor


class LotSqare(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.init_gui()

    def init_gui(self):
        self.vbox = QVBoxLayout(self)


        self.lnombre_lote = QLabel("Lote: ", self)
        self.lnombre_lote.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(self.lnombre_lote)

        hbox = QHBoxLayout()

        self.lctd_jornaleros = QLabel("J: 999999", self)
        hbox.addWidget(self.lctd_jornaleros)

        self.ltasa_jornaleros = QLabel("TC-J: 999999", self)
        hbox.addWidget(self.ltasa_jornaleros)

        self.vbox.addLayout(hbox)

        hbox = QHBoxLayout()

        self.lctd_cosechadoras = QLabel("CA: 999999", self)
        hbox.addWidget(self.lctd_cosechadoras)

        self.ltasa_cosechadoras = QLabel("TC-CA: 999999", self)
        hbox.addWidget(self.ltasa_cosechadoras)

        self.vbox.addLayout(hbox)

        hbox = QHBoxLayout()

        self.lctd_bines = QLabel("B: 999999", self)
        hbox.addWidget(self.lctd_bines)

        self.lctd_tolvas = QLabel("T: 999999", self)
        hbox.addWidget(self.lctd_tolvas)

        self.vbox.addLayout(hbox)

        self.lctd_camiones = QLabel("C: 999999", self)
        self.vbox.addWidget(self.lctd_camiones)

        self.dict_labels = {
            'nombre_lote': self.lnombre_lote,
            'ctd_jornaleros': self.lctd_jornaleros,
            'tasa_jornaleros': self.ltasa_jornaleros,
            'ctd_cosechadoras': self.lctd_cosechadoras,
            'tasa_cosechadoras': self.ltasa_cosechadoras,
            'ctd_bines': self.lctd_bines,
            'ctd_tolvas': self.lctd_tolvas,
            'ctd_camiones': self.lctd_camiones
        }

    def update_info(self, info):
        for entry, data in info.items():
            if entry in self.dict_labels.keys():
                label = self.dict_labels[entry]
                new_text = label.text().split(":")[0] + f": {data}"
                label.setText(new_text)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    ventana = LotSqare()
    ventana.show()
    sys.exit(app.exec())