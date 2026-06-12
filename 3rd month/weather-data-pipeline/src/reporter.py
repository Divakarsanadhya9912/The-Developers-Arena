from database import get_connection


def generate_report():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT c.city_name,
               w.temperature_c,
               w.humidity,
               w.weather_condition,
               w.timestamp
        FROM weather_data w
        JOIN cities c
        ON w.city_id = c.city_id
        ORDER BY w.timestamp DESC
        LIMIT 10
    """)

    rows = cursor.fetchall()

    report = "CURRENT WEATHER REPORT\n"
    report += "=" * 30 + "\n\n"

    for row in rows:
        report += (
            f"{row[0]}: "
            f"{row[1]}°C, "
            f"{row[2]}% humidity, "
            f"{row[3]}\n"
        )

    with open("reports/daily_report.txt", "w") as f:
        f.write(report)

    cursor.close()
    conn.close()

    print("Report generated.")
    
def generate_alerts():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT c.city_name,
               w.temperature_c,
               w.humidity
        FROM weather_data w
        JOIN cities c
        ON w.city_id = c.city_id
        ORDER BY w.timestamp DESC
        LIMIT 20
    """)

    alerts = []

    for city, temp, humidity in cursor.fetchall():

        if temp > 35:
            alerts.append(
                f"High Temperature Alert: {city} ({temp}°C)"
            )

        if humidity > 85:
            alerts.append(
                f"High Humidity Alert: {city} ({humidity}%)"
            )

    with open("reports/alerts.txt", "w") as f:
        if alerts:
            f.write("\n".join(alerts))
        else:
            f.write("No alerts.")

    cursor.close()
    conn.close()

    print("Alerts generated.")
    
if __name__ == "__main__":
    generate_report()
    generate_alerts()