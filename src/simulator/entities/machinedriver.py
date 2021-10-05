class MachineDriver:
    _id = 0

    def __init__(self):
        MachineDriver._id += 1
        self.id = MachineDriver._id
        self.machine = None
        self.available = True
        self.dias_trabajo_semanales = 0
        self.dias_trabajo_totales = 0

    def assign_machine(self, machine):
        self.machine = machine
