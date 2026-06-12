import logging
from datetime import datetime

from validators import validate_weather
from api_client import fetch_weather
from database import get_connection


# Configure logging
logging.basicConfig(
    filename="logs/pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def extract(city):
    """
    Extract weather data from the API.
    """
    return fetch_weather(city)


def transform(data):
    """
    Transform and clean the extracted data.
    """
    if not data:
        return None

    # Standardize weather condition text
    data["condition"] = data["condition"].title()

    return data


def load(data):
    """
    Load transformed data into MySQL database.
    Returns True if successful, otherwise False.
    """
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Check if city already exists
        cursor.execute(
            "SELECT city_id FROM cities WHERE city_name = %s",
            (data["city"],)
        )

        city = cursor.fetchone()

        if city:
            city_id = city[0]

        else:
            cursor.execute(
                """
                INSERT INTO cities
                (city_name, country, latitude, longitude)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    data["city"],
                    data["country"],
                    data["latitude"],
                    data["longitude"]
                )
            )

            city_id = cursor.lastrowid

        # Insert weather record
        cursor.execute(
            """
            INSERT INTO weather_data
            (
                city_id,
                timestamp,
                temperature_c,
                humidity,
                pressure_hpa,
                wind_speed_mps,
                weather_condition
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                city_id,
                datetime.now(),
                data["temperature"],
                data["humidity"],
                data["pressure"],
                data["wind_speed"],
                data["condition"]
            )
        )

        # Insert success log into pipeline_logs table
        cursor.execute(
            """
            INSERT INTO pipeline_logs
            (
                run_time,
                status,
                records_processed,
                message
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                datetime.now(),
                "SUCCESS",
                1,
                f"{data['city']} processed successfully"
            )
        )

        conn.commit()

        logging.info(
            f"{data['city']} data inserted successfully."
        )

        return True

    except Exception as e:

        if conn:
            conn.rollback()

        logging.error(f"Database Error: {e}")

        # Try to save failure log
        try:
            if conn and conn.is_connected():

                if cursor is None:
                    cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO pipeline_logs
                    (
                        run_time,
                        status,
                        records_processed,
                        message
                    )
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        datetime.now(),
                        "FAILED",
                        0,
                        str(e)
                    )
                )

                conn.commit()

        except Exception as log_error:
            logging.error(
                f"Failed to insert pipeline log: {log_error}"
            )

        return False

    finally:

        if cursor:
            cursor.close()

        if conn and conn.is_connected():
            conn.close()


def run_pipeline(city):
    """
    Run the complete ETL pipeline.
    """

    logging.info(f"Pipeline started for {city}")

    # Extract
    data = extract(city)

    # Validate
    is_valid, message = validate_weather(data)

    if not is_valid:
        logging.error(
            f"Validation failed for {city}: {message}"
        )

        print(f"Validation failed: {message}")

        return False

    # Transform
    transformed = transform(data)

    if transformed is None:
        logging.error(
            f"Transformation failed for {city}"
        )

        return False

    # Load
    success = load(transformed)

    if success:

        logging.info(
            f"Pipeline completed successfully for {city}"
        )

        print(f"{city} processed successfully.")

        return True

    else:

        logging.error(
            f"Pipeline failed for {city}"
        )

        print(f"{city} processing failed.")

        return False


if __name__ == "__main__":

    cities = [
        "Mumbai",
        "Delhi",
        "Bangalore"
    ]

    for city in cities:
        run_pipeline(city)
