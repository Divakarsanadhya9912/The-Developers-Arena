import matplotlib.pyplot as plt


def price_distribution(df):

    plt.figure()

    plt.hist(df["Price"], bins=30)

    plt.title("House Price Distribution")

    plt.xlabel("Price")

    plt.ylabel("Frequency")

    plt.savefig("../visualizations/finance/price_distribution.png")

    plt.close()


def area_vs_price(df):

    plt.figure()

    plt.scatter(df["Area"], df["Price"])

    plt.title("Area vs Price")

    plt.xlabel("Area")

    plt.ylabel("Price")

    plt.savefig("../visualizations/finance/area_vs_price.png")

    plt.close()


def property_type_price(df):

    avg_price = df.groupby("Property_Type")["Price"].mean()

    plt.figure()

    avg_price.plot(kind="bar")

    plt.title("Average Price by Property Type")

    plt.xlabel("Property Type")

    plt.ylabel("Average Price")

    plt.savefig("../visualizations/finance/property_type_price.png")

    plt.close()


def location_price(df):

    avg_price = df.groupby("Location")["Price"].mean()

    plt.figure()

    avg_price.plot(kind="bar")

    plt.title("Average Price by Location")

    plt.xlabel("Location")

    plt.ylabel("Average Price")

    plt.savefig("../visualizations/finance/location_price.png")

    plt.close()