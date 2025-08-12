import os
from os import getenv

import requests
from dotenv import load_dotenv
from rich import print

WEATHER_CODES = {
    1000: "clear",
    1100: "mostly clear",
    1101: "partly cloudy",
    1102: "mostly cloudy",
}


def clear_screen():
    # For Windows
    if os.name == "nt":
        _ = os.system("cls")
    # For macOS and Linux
    else:
        _ = os.system("clear")


def display_weather_art():
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
    elif condition == WEATHER_CODES[1101] or condition == WEATHER_CODES[1102]:
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
        print(f"It is {condition}.")
        display_weather_art()
    elif response.status_code == 400:
        print("Invalid Location.")
    else:
        print(f"Error: {response}")


if __name__ == "__main__":
    main()
