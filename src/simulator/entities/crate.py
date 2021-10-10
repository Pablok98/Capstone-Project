from ..sim import SimulationObject


class Crate(SimulationObject):
    _id = 0

    def __init__(self, grape: int, quality: float):
        """

        :param grape: Type of grape which the crate contains.
        :param quality: Quality of the grape at the moment of harvest.
        """
        Crate._id += 1
        self.id = Crate._id

        self.type = grape
        self.time_harvested = SimulationObject.tiempo_actual
        self.quality = quality
