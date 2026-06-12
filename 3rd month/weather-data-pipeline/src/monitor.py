from database import get_connection


def system_status():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM weather_data"
    )
    total_records = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM cities"
    )
    total_cities = cursor.fetchone()[0]

    print("\nSYSTEM STATUS")
    print("=" * 20)
    print("Database Status: Connected")
    print("Total Records:", total_records)
    print("Cities Tracked:", total_cities)

    cursor.close()
    conn.close()
    
if __name__ == "__main__":
    system_status()