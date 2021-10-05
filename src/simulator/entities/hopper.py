from ..entities import *
from typing import Union
from datetime import datetime
from src.params import TASA_DEPRECIACION_TOLVA, COSTO_POR_TONELADA_TOLVA


class Hopper:  # (tolva)
    _id = 0

    def __init__(self):
        Hopper._id += 1
        self.id = Hopper._id
        self.capacidad_maxima = 5  # cajones
        self.cajones: list[Crate] = []
        self.tiempo_transporte: Union[datetime, None] = None
        self.tasa_depreciacion = TASA_DEPRECIACION_TOLVA
        self.costo_por_tonelada = COSTO_POR_TONELADA_TOLVA

    @property
    def lleno(self) -> bool:
        return len(self.cajones) == self.capacidad_maxima

    @property
    def tiene_contenido(self) -> bool:
        return len(self.cajones) != 0

    def cargar_cajon(self, cajon: Crate) -> None:
        if self.lleno:
            print(f"El tolva {self._id} esta lleno!")
            return
        self.cajones.append(cajon)

    def descargar(self) -> Union[tuple[int, float], None]:
        if not self.cajones:
            return
        cajon = self.cajones.pop(0)
        calidad = cajon.calidad
        kg = 18
        if not self.cajones:
            self.tiempo_transporte = None
        return kg, calidad
