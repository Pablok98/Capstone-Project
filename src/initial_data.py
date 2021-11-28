import pandas as pd

from files import load_initial_data, write_excel_listed
from simulator.sim import simulate_rain
from os.path import join


def write_rain():
    df, _ = load_initial_data()
    write_excel_listed(simulate_rain(df, 7), join('data', 'lluvia_generada.xlsx'))
