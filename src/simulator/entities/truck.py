class Truck:
    _id = 0

    def __init__(self, tipo, tolva, bines):
        Truck._id += 1
        self.id = Truck._id
        self.tipo = tipo
        self.cap_tolva = tolva
        self.cap_bines = bines

        self.planta_asignada = None

        self.de_bin = True

        self.tolvas = []
        self.bines = []

        self.driver = None

        self.distance_travelled = 0

        self.current_lot = None

    @property
    def lleno(self):
        if self.de_bin:
            return not len(self.bines) < self.cap_bines
        return not len(self.tolvas) < self.cap_tolva

    @property
    def tiene_contenido(self):
        if self.de_bin:
            return self.bines != []
        for tolva in self.tolvas:
            if tolva.tiene_contenido:
                return True
        return False

    @property
    def espacio_tolva(self):
        return len(self.tolvas) < self.cap_tolva

    def descargar(self):
        if self.tiene_contenido:
            if self.de_bin:
                bin_ = self.bines.pop(0)
                return bin_.descargar()
            else:
                for tolva in self.tolvas:
                    if tolva.tiene_contenido:
                        return tolva.descargar()

    def assign_driver(self, driver):
        if self.driver:
            print(f'Truck {self._id} already has a driver')

        else:
            self.driver = driver

    def travel(self):
        distance = self.current_lot.plant_distances[self.planta_asignada.nombre]
        self.distance_travelled += distance

    def estado(self):
        tipo = 'Bines' if self.de_bin else 'Tolva'
        capacidad = self.cap_bines if self.de_bin else self.cap_tolva
        ocupacion = len(self.bines) if self.de_bin else len(self.tolvas)
        return {
            'id': self.id,
            'tipo': tipo,
            'capacidad': capacidad,
            'ocupacion': ocupacion
        }
