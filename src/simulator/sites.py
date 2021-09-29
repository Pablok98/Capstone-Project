from datetime import datetime, timedelta
from time import sleep
from entities import Laborer, Bin, Truck
from sim import SimulationObject


class Lot(SimulationObject):
    def __init__(self, nombre, uva, ctd_uva, dia):
        self.nombre = nombre
        self.tipo_uva = uva
        self.cantidad = ctd_uva
        self.dia_optimo = dia

        self.lloviendo = False

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
        self.tiempo_proximo_cajon = SimulationObject.tiempo_actual + timedelta(minutes=tiempo)

    @property
    def proximo_evento(self):
        """
        Retorna el proximo evento a ocurrir (segun fecha)
        """
        tiempos = [
            self.tiempo_proximo_cajon,
            self.tiempo_proximo_bin
        ]
        tiempo_prox_evento = min(tiempos)
        eventos = ['llenar_cajon', 'descargar_bin']
        return self.nombre, eventos[tiempos.index(tiempo_prox_evento)], tiempo_prox_evento

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
            # Si es que no hemos definido aun un tiempo de descarga
            if not self.bines[0].tiempo_carga:
                # En el caso de que se cumpla lo anterior, pero no hay camion, entonces no se puede
                if not self.proximo_camion_vacio:
                    print("Hay un bin que no tiene a donde cargarse!")
                    return datetime(3000, 1, 1, hour=6, minute=0, second=0)
                # En caso contrario, se define el tiempo de descarga
                else:
                    self.bines[0].tiempo_carga = SimulationObject.tiempo_actual + timedelta(minutes=10)
            # Retornamos el tiempo determinado
            return self.bines[0].tiempo_carga
        return datetime(3000, 1, 1, hour=6, minute=0, second=0)

    @property
    def proximo_camion_vacio(self):
        for camion in self.camiones:
            if not camion.lleno:
                return camion
        print("No hay camiones con espacio disponible!")
        return None

    def cajon_lleno(self):
        """
        Se ocupa al llenar un cajon, se genera el próximo tiempo de cajon y se carga el bin
        """
        SimulationObject.tiempo_actual = self.tiempo_proximo_cajon
        self.generar_tiempo_cajon()

        _bin = self.proximo_bin_vacio
        _bin.carga_actual += 1

        print(f"{self.nombre} - Se lleno un nuevo cajon a la hora {SimulationObject.tiempo_actual}")

    def descarga_bin(self):
        """
        Se carga el bin al camión y se elimina de la lista de bines. Se actualiza el tiempo.
        """
        SimulationObject.tiempo_actual = self.tiempo_proximo_bin
        self.bines.pop(0)

        print(f"{self.nombre} -Se descargó un bin a la hora {SimulationObject.tiempo_actual}")

    def instanciar(self):
        self.generar_tiempo_cajon()

    def resolver_evento(self, evento):
        metodos = {
            'llenar_cajon': self.cajon_lleno,
            'descargar_bin': self.descarga_bin
        }
        metodos[evento]()


class Plant:
    def __init__(self):
        pass



