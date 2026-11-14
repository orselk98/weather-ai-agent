import os
from groq import Groq
import json
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

client = Groq(
    api_key=os.environ["GROQ_API_KEY"]
)

def get_weather(city, country_code):
    params = {"name": city, "count": 5}
    if country_code:
        params["countryCode"] = country_code

    response = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params=params,
        timeout=10,
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




#SF=get_weather("San Francisco")
#print(f"The weather in {SF['city']} is {SF['temperature']}°{SF['unit']} and {SF['condition']}.")

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather information for a given city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The name of the city to get weather information for"
                    },
                    "country_code": {
                        "type": "string",
                        "description": "The country code of the city"
                    }
                },
                "required": ["city", "country_code"]
            }
        }
    }
]
messages=[
        {
            "role": "system",
            "content": "You are a weather agent that can provide weather information for cities around the world. "
            "When you report the weather, only state the temperature,the city, the weather condition and the time, and do not include any other information. "
            # Rule 2: always use the tool for CURRENT weather, and always send a country code
            "When the user asks about the current weather in a place, always call get_weather, "
            "even if the place name seems unusual or made up. "
            "Always provide a country code: if the user does not name the country, "
            "use the two-letter ISO code of the country where that place is most likely located "
            "(for example, US for San Francisco, AL for Durrës). "
            "Never send an empty country code. "
            # Rule 3: what the tool can't do, named specifically
            "You can only provide current weather conditions. "
            "If the user asks for a forecast, past weather, humidity, wind, or any other weather detail "
            "you do not have, do not call get_weather; reply that you can only provide current weather. "
            # Rule 4: greetings and small talk
            "If the user greets you or makes small talk, reply briefly and politely, "
            "and mention that you can tell them the current weather for any city. "
            "If get_weather returns an error, ignore the rule about reporting the weather: "
            "do not mention temperature, condition or time. "
            "Instead, say 'City not found'. "
        },
        {
            "role": "user",
            "content": "What's the weather in lnlnlnljn?"
        }
    ]

MAX_STEPS = 5 #safety limit 
final_answer = None

for step in range(MAX_STEPS):
    completion = client.chat.completions.create(
        messages=messages,
        tools=tools,
        temperature=0, #low temperature for consistent tool decisions
        model="openai/gpt-oss-120b",
    )
    message = completion.choices[0].message
    #Case A: a text answer with no tool calls, we are done
    if not message.tool_calls:
        final_answer = message.content
        break
    # Case B: the model wants tools , so run every one it asked for 
    messages.append(message)
    for tool_call in message.tool_calls:
        arguments_dict = json.loads(tool_call.function.arguments)
        print(arguments_dict)           #debug
        result = get_weather(arguments_dict["city"], arguments_dict["country_code"])
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": "get_weather",
            "content": json.dumps(result)
        })
#after the loop: answer, or explain that the limit was reached
if final_answer is None:
    print("Sorry, I could not complete your request.")
else:
    print(final_answer)








