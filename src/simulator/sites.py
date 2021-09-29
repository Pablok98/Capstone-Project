from datetime import datetime, timedelta
from time import sleep
from entities import Laborer, Bin, Truck


class Lot:
    def __init__(self, nombre, uva, ctd_uva, dia):
        self.nombre = nombre
        self.tipo_uva = uva
        self.cantidad = ctd_uva
        self.dia_optimo = dia

        self.tiempo_actual = datetime(2021, 1, 1, hour=8, minute=0, second=0)
        self.fin_jornada = datetime(2021, 1, 1, hour=18, minute=0, second=0)

        self.tiempo_proximo_cajon = None

        self.jornaleros = []
        self.bines = []
        self.camiones = []

    def generar_tiempo_cajon(self):
        tasa = 0
        for jornalere in self.jornaleros:
            tasa += jornalere.velocidad_cosecha
        tiempo = 60*24*18 / tasa
        self.tiempo_proximo_cajon = self.tiempo_actual + timedelta(minutes=tiempo)

    @property
    def proximo_evento(self):
        tiempos = [
            self.tiempo_proximo_cajon,
            self.tiempo_proximo_bin
        ]
        tiempo_prox_evento = min(tiempos)
        eventos = ['llenar_cajon', 'descargar_bin']
        return eventos[tiempos.index(tiempo_prox_evento)]

    @property
    def proximo_bin_vacio(self):
        if not self.bines:
            self.bines.append(Bin())
        _bin = self.bines[-1]
        if _bin.lleno:
            _bin = Bin()
            self.bines.append(_bin)
        return _bin

    @property
    def tiempo_proximo_bin(self):
        if self.bines and self.bines[0].lleno:
            if not self.bines[0].tiempo_descarga:
                if not self.proximo_camion_vacio:
                    print("Hay un bin que no tiene a donde cargarse!")
                    return datetime(3000, 1, 1, hour=6, minute=0, second=0)
                else:
                    self.bines[0].tiempo_descarga = self.tiempo_actual + timedelta(minutes=10)
            return self.bines[0].tiempo_descarga
        return datetime(3000, 1, 1, hour=6, minute=0, second=0)

    @property
    def proximo_camion_vacio(self):
        for camion in self.camiones:
            if not camion.lleno:
                return camion
        print("No hay camiones con espacio disponible!")
        return None

    def cajon_lleno(self):
        self.tiempo_actual = self.tiempo_proximo_cajon
        self.generar_tiempo_cajon()

        _bin = self.proximo_bin_vacio
        _bin.carga_actual += 1

        print(f"Se lleno un nuevo cajon a la hora {self.tiempo_actual}")

    def descarga_bin(self):
        self.tiempo_actual = self.tiempo_proximo_bin
        self.bines.pop(0)

        print(f"Se descargó un bin a la hora {self.tiempo_actual}")

    def run(self):
        self.generar_tiempo_cajon()

        metodos = {
            'llenar_cajon': self.cajon_lleno,
            'descargar_bin': self.descarga_bin
        }

        while self.tiempo_actual < self.fin_jornada:
            evento = self.proximo_evento
            metodos[evento]()
            print(self.bines)
            sleep(0.15)


class Plant:
    def __init__(self):
        pass


if __name__ == "__main__":
    lote = Lot('u_1_8', 8, 58000, 118)
    lote.jornaleros.append(Laborer())
    lote.jornaleros.append(Laborer())
    lote.jornaleros.append(Laborer())
    lote.jornaleros.append(Laborer())

    lote.camiones.append(Truck("A", 2, 36))

    lote.run()
