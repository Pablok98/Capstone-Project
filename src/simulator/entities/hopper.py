class Hopper:  # (tolva)
    _id = 0

    def __init__(self):
        Hopper._id += 1
        self.capacidad_maxima = 5  # cajones
        self.cajones = []

        self.tiempo_transporte = None

    @property
    def lleno(self):
        return len(self.cajones) == self.capacidad_maxima

    @property
    def tiene_contenido(self):
        return len(self.cajones) != 0

    def cargar_cajon(self, cajon):
        if self.lleno:
            print(f"El tolva {self._id} esta lleno!")
            return
        self.cajones.append(cajon)

    def descargar(self):
        if not self.cajones:
            return
        cajon = self.cajones.pop(0)
        calidad = cajon.calidad
        kg = 18
        if not self.cajones:
            self.tiempo_transporte = None
        return kg, calidad
