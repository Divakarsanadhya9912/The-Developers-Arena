
from scheduler import collect_weather


def main():
    print("=" * 50)
    print("WEATHER DATA PIPELINE SYSTEM")
    print("=" * 50)

    collect_weather()

    print("\nPipeline execution completed.")


main()