

class Laborer:
    _id = 0

    def __init__(self):
        Laborer._id += 1
        self.velocidad_cosecha = 700
        self.cantidad_cosechada = None
        self.tiempo_cosechando = None
        self.dias_trabajando = None


class Bin:
    _id = 0

    def __init__(self):
        Bin._id += 1
        self.carga_maxima = 27

        self.carga_actual = 0

    @property
    def lleno(self):
        return self.carga_actual == self.carga_maxima


class MotorDriver:
    def __init__(self):
        pass


class TruckDriver:
    def __init__(self):
        pass


class Truck:
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