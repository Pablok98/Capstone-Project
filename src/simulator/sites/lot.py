from datetime import datetime, timedelta
from time import sleep
from entities import *
from sim import SimulationObject


class Lot(SimulationObject):
    def __init__(self, nombre, uva, ctd_uva, dia):
        self.nombre = nombre
        self.tipo_uva = uva
        self.cantidad = ctd_uva
        self.dia_optimo = SimulationObject.tiempo_actual + timedelta(days=dia-1)

        self.lloviendo = 0

        self.fin_jornada = datetime(2021, 1, 1, hour=18, minute=0, second=0)

        self.tiempo_proximo_cajon = None
        self.tiempo_proximo_binlleno = None

        self.jornaleros = []
        self.cosechadoras = []
        self.bines = []
        self.camiones = []

    def generar_tiempo_cajon(self):
        """
        Calcula el tiempo en que se llenará el próximo cajon (fecha)
        """
        if not self.jornaleros:
            self.tiempo_proximo_cajon = datetime(3000, 1, 1, hour=6, minute=0, second=0)
            return
        tasa = 0
        for jornalere in self.jornaleros:
            tasa += jornalere.velocidad_cosecha
        tiempo = 60*24*18 / (tasa - (tasa * 0.3 * self.lloviendo))
        self.tiempo_proximo_cajon = SimulationObject.tiempo_actual + timedelta(minutes=tiempo)

    def generar_tiempo_bin(self):
        if not self.cosechadoras:
            self.tiempo_proximo_binlleno = datetime(3000, 1, 1, hour=6, minute=0, second=0)
            return
        tasa = 0
        for cosechadore in self.cosechadoras:
            tasa += cosechadore.velocidad_cosecha
        tiempo = 60*486 / (tasa - (tasa * 0.6 * self.lloviendo))
        self.tiempo_proximo_binlleno = SimulationObject.tiempo_actual + timedelta(minutes=tiempo)

    @property
    def proximo_evento(self):
        """
        Retorna el proximo evento a ocurrir (segun fecha)
        """
        tiempos = [
            self.tiempo_proximo_cajon,
            self.tiempo_proximo_bin,
            self.tiempo_proximo_camion,
            self.tiempo_proximo_binlleno
        ]
        tiempo_prox_evento = min(tiempos)
        eventos = ['llenar_cajon', 'cargar_bin', 'salida_camion', 'bin_lleno']
        return self.nombre, eventos[tiempos.index(tiempo_prox_evento)], tiempo_prox_evento

    @property
    def proximo_bin_vacio(self):
        """
        Retorna el proximo bin vacío para ocupar
        """
        if not self.bines:
            self.bines.append(Bin())  # agregar restriccion de bines(?)
        _bin = self.bines[-1]
        if _bin.lleno:
            print(
                f"{self.nombre} -Se llenó (manual) un bin a la hora {SimulationObject.tiempo_actual}")
            _bin = Bin()
            self.bines.append(_bin)
        return _bin

    @property
    def tiempo_proximo_bin(self):
        """
        Retorna el tiempo en que se carga el próximo bin (fecha)
        """
        # Si es que hay bines y el último está lleno (si no, nada se va a descargar)
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
    def tiempo_proximo_camion(self):
        for camion in self.camiones:
            if camion.lleno:
                return SimulationObject.tiempo_actual
        return datetime(3000, 1, 1, hour=6, minute=0, second=0)

    @property
    def proximo_camion_vacio(self):
        """
        Retorna el proximo camión vacío
        """
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

        delta_optimo = SimulationObject.tiempo_actual - self.dia_optimo
        _bin.cajones.append(Crate(self.tipo_uva, delta_optimo))

        print(f"{self.nombre} - Se lleno un nuevo cajon a la hora {SimulationObject.tiempo_actual}")

    def carga_bin(self):
        """
        Se carga el bin al camión y se elimina de la lista de bines. Se actualiza el tiempo.
        """
        SimulationObject.tiempo_actual = self.tiempo_proximo_bin
        _bin = self.bines.pop(0)
        camion = self.proximo_camion_vacio
        camion.bines.append(_bin)

        print(f"{self.nombre} -Se cargó un bin a la hora {SimulationObject.tiempo_actual}")

    def instanciar(self):
        self.generar_tiempo_cajon()
        self.generar_tiempo_bin()

    def salida_camion(self):
        """
        Se despacha camión y se eliminca de la lista de camiones disp.
        """
        for i, camion in enumerate(self.camiones):
            if camion.lleno:
                print(
                    f"{self.nombre} - Se despachó un camión a la hora {SimulationObject.tiempo_actual}")
                return self.camiones.pop(i)

    def llenar_bin(self):
        self.generar_tiempo_bin()
        delta_optimo = SimulationObject.tiempo_actual - self.dia_optimo
        _bin = Bin()
        _bin.llenar(self.tipo_uva, delta_optimo)
        self.bines.insert(0, _bin)

        print(f"{self.nombre} -Se llenó (automatico) un bin a la hora {SimulationObject.tiempo_actual}")

    def resolver_evento(self, evento):
        metodos = {
            'llenar_cajon': self.cajon_lleno,
            'cargar_bin': self.carga_bin,
            'salida_camion': self.salida_camion,
            'bin_lleno': self.llenar_bin
        }
        return metodos[evento]()

