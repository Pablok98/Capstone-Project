from datetime import datetime, timedelta
from sim import SimulationObject


class Laborer:
    _id = 0

    def __init__(self):
        Laborer._id += 1
        self.velocidad_cosecha = 700
        self.cantidad_cosechada = None
        self.tiempo_cosechando = None
        self.dias_trabajando = None


class Crate(SimulationObject):  # (cajon)
    _id = 0

    def __init__(self, uva):
        Crate._id += 1
        self.tipo_uva = uva
        self.hora_cosechada = SimulationObject.tiempo_actual


class Bin:
    _id = 0

    def __init__(self):
        Bin._id += 1

        self.cajones = []
        self.carga_maxima = 27
        self.tiempo_carga = None

    @property
    def lleno(self):
        return len(self.cajones) == self.carga_maxima


class Truck:
    _id = 0

    def __init__(self, tipo, tolva, bines):
        Truck._id += 1
        self.tipo = tipo
        self.cap_tolva = tolva
        self.cap_bines = bines

        self.carros = []
        self.bines = []

    @property
    def lleno(self):
        return not len(self.bines) < self.cap_bines


class MotorDriver:
    def __init__(self):
        pass


class TruckDriver:
    def __init__(self):
        pass


class Hopper:
    def __init__(self):
        pass


class Harvester:
    def __init__(self):
        pass


class LiftTruck:
    def __init__(self):
        pass