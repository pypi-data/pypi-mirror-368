import os
from os import getenv

import requests
from dotenv import load_dotenv
from rich import print

WEATHER_CODES = {
    0: "Unknown",
    1000: "Clear, Sunny",
    1100: "Mostly Clear",
    1101: "Partly Cloudy",
    1102: "Mostly Cloudy",
    1001: "Cloudy",
    2000: "Fog",
    2100: "Light Fog",
    4000: "Drizzle",
    4001: "Rain",
    4200: "Light Rain",
    4201: "Heavy Rain",
    5000: "Snow",
    5001: "Flurries",
    5100: "Light Snow",
    5101: "Heavy Snow",
    6000: "Freezing Drizzle",
    6001: "Freezing Rain",
    6200: "Light Freezing Rain",
    6201: "Heavy Freezing Rain",
    7000: "Ice Pellets",
    7101: "Heavy Ice Pellets",
    7102: "Light Ice Pellets",
    8000: "Thunderstorm",
}


def clear_screen():
    # For Windows
    if os.name == "nt":
        _ = os.system("cls")
    # For macOS and Linux
    else:
        _ = os.system("clear")


def display_weather_art(condition):
    if condition == WEATHER_CODES[1000] or condition == WEATHER_CODES[1100]:
        print(
            r"""[yellow]
  \   /  
   .-.   
― (   ) ―
   `-’   
  /   \  

[/yellow]"""
        )
    elif (
        condition == WEATHER_CODES[1001]
        or condition == WEATHER_CODES[1101]
        or condition == WEATHER_CODES[1102]
    ):
        print(
            r"""[grey]

                                
        +++++++                 
      +        +++++++          
     +                 +       
     +                 ++      
   +++                 +++   
 ++                       ++ 
 +                         + 
 ++                      ++ 
   ++++++++++++++++++++++   
                                

[/grey]"""
        )
    else:
        print("No ascii art.")


def main():
    # api key
    load_dotenv()
    TOMORROW_IO_KEY = getenv("TOMORROW_IO_API") or input(
        "Enter your Tomorrow.io API Key: "
    )

    # location
    location = input("Enter a location: ").lower()

    # api call
    url = f"https://api.tomorrow.io/v4/weather/realtime?location={location}"
    headers = {
        "content-type": "application/json",
        "apikey": TOMORROW_IO_KEY,
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        clear_screen()

        content = response.json()
        values = content["data"]["values"]

        print(f"Location:  {content['location']['name']}")

        print(f"Current temperature: {values['temperature']}\u00b0C")

        condition = WEATHER_CODES[values["weatherCode"]]
        print(f"Current conditions: {condition.lower()}.")
        display_weather_art(condition)
    elif response.status_code == 400:
        print("Invalid Location.")
    else:
        print(f"Error: {response}")


if __name__ == "__main__":
    main()
