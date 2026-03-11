import matplotlib.pyplot as plt


def temperature_trend(df):

    plt.figure(figsize=(10,5))

    plt.plot(df["Date"], df["Avg_Temperature"])

    plt.title("Temperature Trend Over Time")

    plt.xlabel("Date")
    plt.ylabel("Average Temperature")

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.savefig("../visualizations/weather/temperature_trend.png")

    plt.close()


def rainfall_distribution(df):

    plt.figure()

    plt.hist(df["Rainfall_mm"], bins=30)

    plt.title("Rainfall Distribution")

    plt.xlabel("Rainfall (mm)")
    plt.ylabel("Frequency")

    plt.tight_layout()

    plt.savefig("../visualizations/weather/rainfall_distribution.png")

    plt.close()


def seasonal_temperature(df):

    seasonal_avg = df.groupby("month")["Avg_Temperature"].mean()

    plt.figure()

    seasonal_avg.plot(kind="bar")

    plt.title("Monthly Average Temperature")

    plt.xlabel("Month")
    plt.ylabel("Temperature")

    plt.tight_layout()

    plt.savefig("../visualizations/weather/monthly_temperature.png")

    plt.close()


def extreme_weather(df):

    extreme = df[df["Extreme_Event"] == 1]

    plt.figure()

    plt.scatter(extreme["Date"], extreme["Max_Temperature"])

    plt.title("Extreme Weather Events")

    plt.xlabel("Date")
    plt.ylabel("Max Temperature")

    plt.tight_layout()

    plt.savefig("../visualizations/weather/extreme_weather_events.png")

    plt.close()