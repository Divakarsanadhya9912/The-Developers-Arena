import pandas as pd


def load_data(filepath):
    df = pd.read_csv(filepath)

    df["Date"] = pd.to_datetime(df["Date"])

    df["year"] = df["Date"].dt.year
    df["month"] = df["Date"].dt.month
    df["day"] = df["Date"].dt.day

    return df


def basic_inspection(df):

    print("Shape:", df.shape)

    print("\nColumns:\n", df.columns)

    print("\nMissing Values:\n", df.isnull().sum())

    print("\nData Types:\n", df.dtypes)