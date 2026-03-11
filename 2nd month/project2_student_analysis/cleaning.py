import pandas as pd

def load_data(filepath):
    df = pd.read_csv(filepath)
    return df

def basic_inspection(df):
    print("Shape:", df.shape)
    print("\nColumns:\n", df.columns)
    print("\nMissing Values:\n", df.isnull().sum())
    print("\nData Types:\n", df.dtypes)

def clean_data(df):
    # Remove duplicates
    df = df.drop_duplicates()

    # Ensure numeric columns are correct type
    numeric_cols = [
        "attendance_percentage",
        "math_score",
        "science_score",
        "english_score",
        "total_score",
        "average_score"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop rows with missing numeric values
    df = df.dropna()

    return df