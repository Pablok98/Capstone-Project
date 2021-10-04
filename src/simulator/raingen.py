import pandas as pd
from random import randint

from os.path import join


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


def read_data():
    df = pd.read_excel(join('data', 'lluvia_generada.xlsx'))
    return df
