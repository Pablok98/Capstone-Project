class TruckDriver:
    _id = 0

    def __init__(self):
        TruckDriver._id += 1
        self.id = TruckDriver._id
        self.truck = None
        self.available = True
        self.dias_trabajo_semanales = 0
        self.dias_trabajo_totales = 0

    def assign_truck(self, truck):
        self.truck = truck

