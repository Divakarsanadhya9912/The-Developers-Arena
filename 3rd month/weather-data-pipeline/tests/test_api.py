from src.api_client import fetch_weather

def test_fetch_weather():
    data = fetch_weather("Mumbai")

    assert data is not None
    assert "temperature" in data
    assert "humidity" in data