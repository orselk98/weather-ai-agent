import requests

WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Drizzle: Light",
    53: "Drizzle: Moderate",
    55: "Drizzle: Dense intensity",
    56: "Freezing Drizzle: Light",
    57: "Freezing Drizzle: Dense intensity",
    61: "Rain: Slight",
    63: "Rain: Moderate",
    65: "Rain: Heavy intensity",
    66: "Freezing Rain: Light",
    67: "Freezing Rain: Heavy intensity",
    71: "Snow fall: Slight",
    73: "Snow fall: Moderate",
    75: "Snow fall: Heavy intensity",
    77: "Snow grains",
    80: "Rain showers: Slight",
    81: "Rain showers: Moderate",
    82: "Rain showers: Violent",
    85: "Snow showers slight",
    86: "Snow showers heavy",
    95: "Thunderstorm: Slight or moderate",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",

}
def get_weather(city, country_code):
    response = requests.get(
    "https://geocoding-api.open-meteo.com/v1/search",
    params={"name": city, "count": 5, "countryCode": country_code},
)
    data = response.json()

    place = None
    for result in data.get("results", []):
        if result.get("feature_code", "").startswith("PPL"):
            place = result
            break

    if place is None:
        return {"error": "City not found"}
    else:
        weather_response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": place["latitude"],
                "longitude": place["longitude"],
                "timezone": place["timezone"],
                "current": "temperature_2m,weather_code"
            },
            timeout=10,
        )
        weather_data = weather_response.json()
        return {
            "city": place["name"],
            "temperature": weather_data.get("current", {}).get("temperature_2m"),
            "unit": weather_data.get("current_units", {}).get("temperature_2m"),
            "condition": WEATHER_CODES.get(weather_data.get("current", {}).get("weather_code")),
            "time": weather_data.get("current", {}).get("time"),
        }


print(get_weather("Durres", "AL"))
print(get_weather("Tirana", "AL"))
print(get_weather("Tirane", "AL"))

