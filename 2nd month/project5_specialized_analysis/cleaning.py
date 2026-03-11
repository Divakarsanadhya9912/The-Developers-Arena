import pandas as pd

def load_data(filepath):

    df = pd.read_csv(filepath)

    return df


def basic_inspection(df):

    print("Shape:", df.shape)

    print("\nColumns:\n", df.columns)

    print("\nMissing Values:\n", df.isnull().sum())

    print("\nData Types:\n", df.dtypes)