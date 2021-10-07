"""
camiones = {
  camion1: {
    dia1: loteX,
    dia2: loteY
    ...
  },
  camion: {
    dia1: loteX,
    dia2: loteY
    ...
  }
}
"""
from sim import SimulationObject


class Assignations(SimulationObject):
    def __init__(self):
        self.laborers = None
        self.trucks = None
        self.hoppers = None
        self.harvesters = None
        self.lift_trucks = None
        self.truck_drivers = None
        self.machine_drivers = None

