import pandas as pd


def clean_data(df):
    """
    Clean supermarket sales dataset:
    - Standardize column names
    - Remove duplicates
    - Handle missing values
    - Convert date and time columns
    - Fix numeric types
    """

    # ---------------------------
    # 1. Standardize column names
    # ---------------------------
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("%", "percent")
    )

    # ---------------------------
    # 2. Remove duplicates
    # ---------------------------
    df = df.drop_duplicates()

    # ---------------------------
    # 3. Handle missing values
    # ---------------------------
    df = df.dropna()

    # ---------------------------
    # 4. Convert Date column
    # ---------------------------
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # ---------------------------
    # 5. Convert Time column
    # ---------------------------
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"], errors="coerce").dt.time

    # ---------------------------
    # 6. Ensure numeric columns are correct
    # ---------------------------
    numeric_columns = [
        "unit_price",
        "quantity",
        "tax_5percent",
        "total",
        "cogs",
        "gross_income",
        "rating"
    ]

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def feature_engineering(df):
    """
    Create new useful features:
    - Year, Month, Day
    - Day name
    - Hour of purchase
    - Revenue per unit
    """

    # Date-based features
    if "date" in df.columns:
        df["year"] = df["date"].dt.year
        df["month"] = df["date"].dt.month
        df["day"] = df["date"].dt.day
        df["day_name"] = df["date"].dt.day_name()

    # Hour feature from time
    if "time" in df.columns:
        df["hour"] = pd.to_datetime(df["time"], format="%H:%M:%S", errors="coerce").dt.hour

    # Revenue per unit
    if "total" in df.columns and "quantity" in df.columns:
        df["revenue_per_unit"] = df["total"] / df["quantity"]

    return df


def validate_data(df):
    """
    Basic data validation checks
    """

    if "total" in df.columns:
        if (df["total"] < 0).any():
            print("⚠ Warning: Negative total values detected")

    if "quantity" in df.columns:
        if (df["quantity"] <= 0).any():
            print("⚠ Warning: Zero or negative quantity detected")

    print("✅ Data validation complete.")

    return df

def load_and_clean_data(file_path):
    """
    Load dataset and apply full cleaning pipeline
    """
    df = pd.read_csv(file_path)

    df = clean_data(df)
    df = feature_engineering(df)
    df = validate_data(df)

    return df