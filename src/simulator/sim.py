from datetime import datetime


class SimulationObject:
    tiempo_actual = datetime(2021, 1, 1, hour=6, minute=0, second=0)
    neverdate = datetime(3000, 1, 1, hour=6, minute=0, second=0)
    current_day = 1
    MAX_DAILY_UNLOAD = 0.3
