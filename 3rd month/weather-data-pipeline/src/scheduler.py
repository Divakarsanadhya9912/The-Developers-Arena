import schedule
import time
from etl_pipeline import run_pipeline

CITIES = [
    "Mumbai",
    "Delhi",
    "Bangalore"
]


def collect_weather():
    print("\nStarting scheduled weather collection...")

    for city in CITIES:
        run_pipeline(city)

    print("Weather collection completed.\n")


# Run every hour
schedule.every(1).hours.do(collect_weather)

print("Scheduler started...")
print("Press CTRL + C to stop.")

# Optional: Run immediately when the program starts
collect_weather()

while True:
    schedule.run_pending()
    time.sleep(1)