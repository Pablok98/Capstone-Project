from optimization.initial_model import get_optimum_contracts
from files import read_lot_data
import json
import params as p

data = read_lot_data()
with open('data/analitic_expected_q.json', 'r') as file:
    expected_q = json.load(file)

demand = sum(v['prod_cap'] for v in p.PLANTS_DATA.values()) * p.TOTAL_DAYS * p.DEMAND_WEIGHT
opt_contracts = get_optimum_contracts(data, expected_q, demand)

with open('data/initial_contracts.json', 'w') as file:
    json.dump(opt_contracts, file)

