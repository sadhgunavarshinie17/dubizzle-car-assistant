import pandas as pd

DATA_PATH = "data/cars.xlsx"

def load_inventory():
    df = pd.read_excel(
        DATA_PATH, 
        sheet_name = "cleaned dataset"
        )

    return df


def search_inventory(
        make=None,
        model=None,
        min_year=None,
        max_year=None
):
    df = load_inventory()

    if make:
        df = df[df["make"].str.lower() == make.lower()]

    if model:
        df = df[df["model"].str.lower() == model.lower()]

    if min_year:
        df = df[df["year"] >= min_year]

    if max_year:
        df = df[df["year"] <= max_year]


    return df
    