from datetime import datetime
from .. import params as p


class SimulationObject:
    tiempo_actual = datetime(2021, 1, 1, hour=6, minute=0, second=0)
    neverdate = datetime(3000, 1, 1, hour=6, minute=0, second=0)
    MAX_DAILY_UNLOAD = p.MAX_DAILY_UNLOAD
