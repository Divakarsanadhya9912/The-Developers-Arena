from src.validators import validate_weather

def test_valid_data():
    data = {
        "temperature": 25,
        "humidity": 50,
        "pressure": 1013,
        "wind_speed": 2,
        "condition": "Clear"
    }

    valid, _ = validate_weather(data)
    assert valid is True


def test_invalid_humidity():
    data = {
        "temperature": 25,
        "humidity": 150,
        "pressure": 1013,
        "wind_speed": 2,
        "condition": "Clear"
    }

    valid, _ = validate_weather(data)
    assert valid is False