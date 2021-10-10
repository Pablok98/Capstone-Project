class Laborer:
    _id = 0

    def __init__(self):
        Laborer._id += 1
        self.id = Laborer._id

        self.harvest_rate = 700 * 5  # Todo: esto es cuadrilla
        self.harvested = 0
        self.time_working = 0
        self.days_working = 0
