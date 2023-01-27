import pytest
import app as main

@pytest.fixture
def client():
    main.app.config["TESTING"] = True
    client = main.app.test_client()
    with main.app.app_context():
        main.db.drop_all()
        main.db.create_all()
        weather_data = main.WeatherRecord(
            station="station_name",
            date="19850101",
            maximum_temperature=1,
            minimum_temperature=1,
            precipitation=10,
        )
        main.db.session.add(weather_data)
        main.db.session.commit()

    yield client


def test_weather_reports(client):
    response = client.get("/api/weather/")
    assert response.status_code == 200
    assert response.json == [
        {
            "date": "19850101",
            "maximum_temperature": 1,
            "minimum_temperature": 1,
            "precipitation": 10,
            "station": "station_name",
        }
    ]
