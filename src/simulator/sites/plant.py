

class Plant:
    def __init__(self, nombre, cap_ferm, cap_prod, cap_tolva, cap_bin):
        self.nombre = nombre
        self.cap_ferm = cap_ferm
        self.cap_prod = cap_prod
        self.cap_tolva = cap_tolva
        self.cap_bin = cap_bin

        self.uva_actual = []
        self.vino_total_producido = 0
        self.uva_procesada = 0

        self.camiones = []

    @property
    def carga_actual(self):
        carga = 0
        for batch in self.uva_actual:
            carga += batch[0]
        return carga

    def descargar_camion(self, camion):
        """
        Recibe un camion y calcula el proceso de llenar la planta
        """
        self.camiones.append(camion)
        print(f"Descargando camion {camion._id} en la planta {self.nombre}")
        while self.carga_actual < self.cap_ferm and camion.tiene_contenido:
            kilos, calidad = camion.descargar()
            self.uva_actual.append((kilos, calidad))

    def procesar_dia(self):
        print(f"Procesando uva en la planta {self.nombre}")
        procesado = 0
        while procesado < self.cap_prod:
            if not self.uva_actual:
                break
            batch = self.uva_actual.pop(0)
            procesado += batch[0]
            self.uva_procesada += batch[0]
            self.vino_total_producido += batch[0] * batch[1]
        print(self)

    def __str__(self):
        return f"Planta: {self.nombre}. Uva procesada: {self.uva_procesada}. Vino procesado: {self.vino_total_producido}"


