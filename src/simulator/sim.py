from datetime import datetime
from random import randint


class SimulationObject:
    current_time = datetime(2021, 1, 1, hour=6, minute=0, second=0)
    never_date = datetime(3000, 1, 1, hour=6, minute=0, second=0)
    current_day = 1
    MAX_DAILY_UNLOAD = 0.3


class Interface(SimulationObject):
    def __init__(self):
        self.laborers = None
        self.trucks = None
        self.hoppers = None
        self.harvesters = None
        self.lift_trucks = None
        self.truck_drivers = None
        self.machine_drivers = None

    def load_data(self, name, data):
        setattr(self, name, data)


def event(time_var, func=None):
    def event_decorator(event_func):
        def event_wrapper(self, *args, **kwargs):
            time = getattr(self, time_var)
            SimulationObject.current_time = time
            setattr(self, time_var, None)
            if func:
                getattr(self, func)()
            res = event_func(self, *args, **kwargs)
            return res
        return event_wrapper
    return event_decorator


def simulate_rain(lot_frame, time_range):
    rain_data = []
    for day in range(time_range):
        for index in range(lot_frame.shape[0]):
            if day != 0:
                ocurrence = rain_data[index][f'day {day}']
            else:
                ocurrence = 0
                rain_data.append({'Lote COD': lot_frame.iloc[index]['Lote COD']})
            rain_prob = lot_frame.iloc[index][f'p_{ocurrence}1']
            resultado = 1 if (randint(0, 100)/100 < rain_prob) else 0
            rain_data[index][f'day {day + 1}'] = resultado
    return rain_data
