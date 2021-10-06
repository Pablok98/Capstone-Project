from os.path import join


# General
TOTAL_DAYS = 180

# Modelo inicial
DEMAND_WEIGHT = 0.2

# Currencies
CLP = 1
UTM = 52842 * CLP

# Paths and excel
GIVEN_DATA_PATH = join('src', "data", "datos_entregados.xlsx")
RAIN_DATA_PATH = join("data", "lluvia_generada.xlsx")

LOT_SHEET = "lotes"
MISC_SHEET = "otros"

# Plantas
MAX_DAILY_UNLOAD = 0.3
TIME_RANGE = 7
PLANTS_DATA = {
    'P1': {'ferm_cap': 2500, 'prod_cap': 150, 'hopper_cap': 50, 'bin_cap': 40, 'fixed_cost': 27000 * UTM, 'var_cost': 20}, 
    'P2': {'ferm_cap': 1250, 'prod_cap': 65, 'hopper_cap': 30, 'bin_cap': 30, 'fixed_cost': 18000 * UTM, 'var_cost': 30.8}, 
    'P3': {'ferm_cap': 3500, 'prod_cap': 100, 'hopper_cap': 75, 'bin_cap': 50, 'fixed_cost': 18700 * UTM, 'var_cost': 20.8}, 
    'P4': {'ferm_cap': 950, 'prod_cap': 90, 'hopper_cap': 40, 'bin_cap': 25, 'fixed_cost': 22500 * UTM, 'var_cost': 27.8}, 
    'P5': {'ferm_cap': 900, 'prod_cap': 120, 'hopper_cap': 50, 'bin_cap': 30, 'fixed_cost': 31500 * UTM, 'var_cost': 29.2}
}


# Camiones

TRUCK_DATA = {
    'A': {'avail_units': 7, 'hopper_cap': 2, 'bin_cap': 36, 'cost_per_km': 0.02 * UTM}, 
    'B': {'avail_units': 3, 'hopper_cap': 2, 'bin_cap': 32, 'cost_per_km': 0.025 * UTM}, 
    'C': {'avail_units': 8, 'hopper_cap': 2, 'bin_cap': 36, 'cost_per_km': 0.018 * UTM}, 
    'D': {'avail_units': 7, 'hopper_cap': 1, 'bin_cap': 12, 'cost_per_km': 0.032 * UTM}
}

# Jornaleros
MAX_DIAS_TRABAJO_JORNALERO = 6

# Conductores
MAX_DIAS_TRABAJO_CONDUCTORES = 5

# Tractores
TASA_DEPRECIACION_TRACTOR = 5
COSTO_POR_TONELADA_TRACTOR = 0.1

# Montacargas
TASA_DEPRECIACION_MONTACARGAS = 0
COSTO_POR_TONELADA_MONTACARGAS = 0

# Carro Tolva
TASA_DEPRECIACION_TOLVA = 1.5
COSTO_POR_TONELADA_TOLVA = 0.01

# Cosechadora
TASA_DEPRECIACION_COSECHADORA = 10
COSTO_POR_TONELADA_COSECHADORA = 0.1
VELOCIDAD_COSECHADORA = 4000   # por hora
