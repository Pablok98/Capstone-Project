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


def write_excel_listed(data, target):
    df = pd.DataFrame(data)
    df.to_excel(target, index=False)
