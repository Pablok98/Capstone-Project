from datetime import datetime, timedelta
from time import sleep
from entities import Laborer, Bin

class Lot:
    def __init__(self, nombre, uva, ctd_uva, dia, precio_uva):
        self.nombre = nombre
        self.tipo_uva = uva
        # self.precio_uva = precio_uva
        self.cantidad = ctd_uva
        self.dia_optimo = dia

        self.tiempo_actual = datetime(2021, 1, 1, hour=6, minute=0, second=0)

        self.tiempo_proximo_cajon = None

        self.jornaleros = []
        self.bines = []

    def generar_tiempo_cajon(self):
        tasa = 0
        for jornalere in self.jornaleros:
            tasa += jornalere.velocidad_cosecha
        tiempo = 60*24*18 / tasa
        self.tiempo_proximo_cajon = self.tiempo_actual + timedelta(minutes = tiempo)

    @property
    def proximo_evento(self):
        tiempos = [
            self.tiempo_proximo_cajon
        ]
        tiempo_prox_evento = min(tiempos)
        eventos = ['llenar_cajon']
        return eventos[tiempos.index(tiempo_prox_evento)]

    @property
    def proximo_bin_vacio(self):
        if not self.bines:
            self.bines.append(Bin())
        _bin = self.bines[-1]
        if _bin.lleno:
            self.bines.append(Bin())
        return _bin

    def cajon_lleno(self):
        self.tiempo_actual = self.tiempo_proximo_cajon
        self.generar_tiempo_cajon()

        _bin = self.proximo_bin_vacio
        _bin.carga_actual += 1

        print(f"Se lleno un nuevo cajon a la hora {self.tiempo_actual}")
        print(self.bines)

    def run(self):
        self.generar_tiempo_cajon()

        metodos = {
            'llenar_cajon': self.cajon_lleno
        }

        while True:
            evento = self.proximo_evento
            metodos[evento]()
            sleep(0.5)





class Plant:
    def __init__(self):
        pass


if __name__ == "__main__":
    lote = Lot('u_1_8', 8, 58000, 118, 231)
    lote.jornaleros.append(Laborer())
    lote.run()
