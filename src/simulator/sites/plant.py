class Plant:
    def __init__(self, name: str, ferm_cap: int, prod_cap: int, hopper_cap: int, bin_cap: int):
        """
        Represents a plant site, which can store and process grape daily. Trucks bring grapes from
        lots to unload them for processing.

        :param name: MUST be unique. Name of the plant, which will used by the simulator to both
                    display and reference.
        :param ferm_cap: Maximum capacity of grapes that the plant can contain at once.
        :param prod_cap: Maximum capacity of grapes that the plant can process in one day.
        :param hopper_cap: Maximum rate of grapes that can be unloaded to the plant from a truck
                        with hopper(s)
        :param bin_cap: Maximum rate of grapes that can be unloaded to the plant from a truck
                        loaded with bin(s)
        """
        self.nombre = name
        self.cap_ferm = ferm_cap
        self.cap_prod = prod_cap
        self.cap_tolva = hopper_cap
        self.cap_bin = bin_cap

        # uva_actual contains tuples, each with the pair (quantity, quality). When grape is unloaded
        # from trucks, the quanity and quality is stored in the list.
        self.uva_actual: list[tuple[int, float]] = []

        # State variables
        self.vino_total_producido = 0
        self.uva_procesada = 0
        self.camiones = []

    @property
    def carga_actual(self) -> int:
        """
        Iterates through the batches (touples) of grape and counts the total grape currently
        inside the plant.

        :return: Current grape load

        """
        carga = 0
        for batch in self.uva_actual:
            carga += batch[0]
        return carga

    def descargar_camion(self, camion):
        """
        Recibe un camion y calcula el proceso de llenar la planta
        """
        self.camiones.append(camion)
        print(f"Descargando camion {camion.id} en la planta {self.nombre}")
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
