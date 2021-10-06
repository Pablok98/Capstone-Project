from optimization.initial_model import get_optimum_contracts
from files import read_lot_data
import json
import params as p

data = read_lot_data()
with open('src/analitic_expected_q.json', 'r') as file:
    expected_q = json.load(file)

demand = sum(v['prod_cap'] for v in p.PLANTS_DATA.values()) * p.TOTAL_DAYS * p.DEMAND_WEIGHT
# demand = 25696
x = get_optimum_contracts(data, expected_q, demand)
print()
comprados = sum(i for i in x.values() if i)
print(f"comprados: {comprados}")
print(f"proporcion: {comprados / 290}")
