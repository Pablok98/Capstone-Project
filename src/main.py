from files import load_initial_data, write_excel_listed
from simulator import simulate_rain
import params as p

dfs = load_initial_data()
rain_data = simulate_rain(dfs[0], p.TIME_RANGE)
write_excel_listed(rain_data, p.RAIN_DATA_PATH)
