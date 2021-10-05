import pandas as pd
import params as p


def load_initial_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Reads excel file with initial data for the optimization problem, loading it to a dataframe.

    :return: Tuple of dataframes, first lot info then miscellaneous
    """
    lot_df = pd.read_excel(p.GIVEN_DATA_PATH, sheet_name=p.LOT_SHEET)
    misc_df = pd.read_excel(p.GIVEN_DATA_PATH, sheet_name=p.MISC_SHEET)

    return lot_df, misc_df


def read_lot_data():
    lot, misc = load_initial_data()
    info = {}
    cal_uvas = {}
    for index, row in misc.iterrows():
        info_tipo = {}
        for categoria in row.keys():
            if categoria == "Uva tipo":
                tipo = row[categoria]
            else:
                info_tipo[categoria.replace(" ", "_")] = row[categoria]
        cal_uvas[tipo] = info_tipo
        if index == 7:
            break
    for index, row in lot.iterrows():
        info_lot = {}
        for categoria in row.keys():
            if categoria == "Lote COD":
                pass
            elif categoria == "$ Ch Compra Futuro/ kg uva":
                info_lot["Costo_kg_uva"] = row[categoria]
            else:
                info_lot[categoria.strip().replace(" ", "_")] = row[categoria]
        for tipo, cal in cal_uvas.items():
            if tipo == info_lot["Tipo_UVA"]:
                info_lot["rango_calidad"] = [cal["q[t-7]"], cal["q[t+7]"]]
        info[row["Lote COD"]] = info_lot
    return info

def write_excel_listed(data, target):
    df = pd.DataFrame(data)
    df.to_excel(target, index=False)


if __name__ == "__main__":
    for name, info in read_lot_data().items():
        print(name)
        print(info)
        break
    print(read_lot_data())