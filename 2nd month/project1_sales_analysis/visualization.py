import matplotlib.pyplot as plt
import seaborn as sns


# ----------------------------------------
# 1. Daily Sales Trend
# ----------------------------------------
def plot_daily_sales(df):
    if "date" not in df.columns or "total" not in df.columns:
        print("Required columns not found for daily sales plot.")
        return

    daily_sales = df.groupby("date")["total"].sum()

    plt.figure(figsize=(12,6))
    daily_sales.plot()
    plt.title("Daily Sales Trend")
    plt.xlabel("Date")
    plt.ylabel("Total Sales")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("../visualizations/sales/daily_sales.png")
    plt.show()


# ----------------------------------------
# 2. Sales by Product Line
# ----------------------------------------
def plot_product_line_sales(df):
    if "product_line" not in df.columns or "total" not in df.columns:
        print("Required columns not found for product line plot.")
        return

    product_sales = (
        df.groupby("product_line")["total"]
        .sum()
        .sort_values(ascending=False)
    )

    plt.figure(figsize=(10,6))
    sns.barplot(x=product_sales.values, y=product_sales.index)
    plt.title("Total Sales by Product Line")
    plt.xlabel("Total Sales")
    plt.ylabel("Product Line")
    plt.tight_layout()
    plt.savefig("../visualizations/sales/product_line_sales.png")
    plt.show()


# ----------------------------------------
# 3. Sales by Branch
# ----------------------------------------
def plot_branch_sales(df):
    if "branch" not in df.columns or "total" not in df.columns:
        print("Required columns not found for branch plot.")
        return

    branch_sales = df.groupby("branch")["total"].sum()

    plt.figure(figsize=(8,5))
    branch_sales.plot(kind="bar")
    plt.title("Total Sales by Branch")
    plt.xlabel("Branch")
    plt.ylabel("Total Sales")
    plt.tight_layout()
    plt.savefig("../visualizations/sales/branch_sales.png")
    plt.show()


# ----------------------------------------
# 4. Hourly Sales Pattern
# ----------------------------------------
def plot_hourly_sales(df):
    if "hour" not in df.columns or "total" not in df.columns:
        print("Hour feature not found. Run feature_engineering first.")
        return

    hourly_sales = df.groupby("hour")["total"].sum()

    plt.figure(figsize=(10,6))
    hourly_sales.plot()
    plt.title("Hourly Sales Trend")
    plt.xlabel("Hour of Day")
    plt.ylabel("Total Sales")
    plt.tight_layout()
    plt.savefig("../visualizations/sales/hourly_sales.png")
    plt.show()


# ----------------------------------------
# 5. Correlation Heatmap
# ----------------------------------------
def plot_correlation_heatmap(df):
    numeric_df = df.select_dtypes(include=["number"])

    if numeric_df.empty:
        print("No numeric columns found for correlation.")
        return

    plt.figure(figsize=(10,6))
    sns.heatmap(numeric_df.corr(), annot=True, fmt=".2f")
    plt.title("Correlation Heatmap")
    plt.tight_layout()
    plt.savefig("../visualizations/sales/correlation_heatmap.png")
    plt.show()