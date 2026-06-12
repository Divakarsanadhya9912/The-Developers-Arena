def validate_weather(data):
    """
    Returns (True, "") if valid.
    Otherwise returns (False, error_message)
    """

    if data is None:
        return False, "No data received"

    required_fields = [
        "temperature",
        "humidity",
        "pressure",
        "wind_speed",
        "condition"
    ]

    for field in required_fields:
        if field not in data or data[field] is None:
            return False, f"Missing field: {field}"

    # Temperature check
    if not (-50 <= data["temperature"] <= 60):
        return False, "Invalid temperature"

    # Humidity check
    if not (0 <= data["humidity"] <= 100):
        return False, "Invalid humidity"

    # Pressure check
    if data["pressure"] <= 0:
        return False, "Invalid pressure"

    # Wind speed check
    if data["wind_speed"] < 0:
        return False, "Invalid wind speed"

    return True, ""

if __name__ == "__main__":
    sample = {
        "temperature": 35,
        "humidity": 80,
        "pressure": 1008,
        "wind_speed": 2.5,
        "condition": "clear sky"
    }

    print(validate_weather(sample))