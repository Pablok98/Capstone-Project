class TruckDriver:
    _id = 0

    def __init__(self):
        TruckDriver._id += 1
        self.truck = None
        self.available = True

    def assign_truck(self, truck):
        self.truck = truck

