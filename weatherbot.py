import requests
import telebot
from telebot import types

OWM_API_KEY = "6f6c7160b5e6b7016b200cf7ba25fa10"
BOT_TOKEN = "8384257308:AAEmN76X7cUGdSrfAsd0hEubX2l6xEoYqjw"

# TeleBot instance .
bot = telebot.TeleBot(BOT_TOKEN)
print("bot started")

# Nested dictionary used to map city names to their latitude/longitude.
CITIES = {"Barcelona": {"lat": 41.3851, "lon": 2.1734},"Madrid": {"lat": 40.4168, "lon": -3.7038},"Valencia": {"lat": 39.4699, "lon": -0.3763},"Seville": {"lat": 37.3891, "lon": -5.9845},}

# When the user sends /start, build an inline keyboard with a button for each city
@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id
    # Build an inline keyboard object
    keyboard = types.InlineKeyboardMarkup()
    # Add one InlineKeyboardButton per city (label = city name, callback_data = city name)
    for city in CITIES:
        button = types.InlineKeyboardButton(city, callback_data=city)
        keyboard.add(button)

    # Send the prompt message with the inline keyboard attached
    bot.send_message(chat_id, "Choose a city:", reply_markup=keyboard)

# Function to fetch weather from OpenWeatherMap
#   Calls requests.get to retrieve JSON data and extracts main fields
#   Returns a formatted string with description, temperature, feels-like, and humidity
def get_weather(city_name):
    # Input validation: if the city_name is not in CITIES, return a clear message
    if city_name not in CITIES:
        return "City not found"

    # Access the stored coordinates for the selected city
    lat = CITIES[city_name]["lat"]
    lon = CITIES[city_name]["lon"]

    # Build the request URL. Using string concatenation here; for user-supplied text prefer requests params.
    url = "https://api.openweathermap.org/data/2.5/weather"
    url = url + "?lat=" + str(lat) + "&lon=" + str(lon) + "&appid=" + OWM_API_KEY + "&units=metric"

    try:
        # Perform the HTTP GET request to OpenWeather
        r = requests.get(url, timeout=10)
        # stores the response data in a json
        data = r.json()

        # gets the main data from the json 
        main = data["main"]
        weather = data["weather"][0]

        # Read values (may raise KeyError if response is unexpectedly formatted)
        temp = main["temp"]
        feels_like = main["feels_like"]
        humidity = main["humidity"]
        description = weather["description"]

        # sends several lines of strings to the user
        text = "Weather: " + str(description) + "\n"
        text = text + "Temperature: " + str(temp) + "°C\n"
        text = text + "Feels like: " + str(feels_like) + "°C\n"
        text = text + "Humidity: " + str(humidity) + "%"
        
        # - Returns a formatted string with description, temperature, feels-like, and humidity
        return text
    except requests.RequestException:
        # Network or HTTP-related error (timeout, connection error, non-2xx status)
        return "Error getting weather"
    except (ValueError, KeyError):
        # JSON parse error or unexpected response structure
        return "Error parsing weather data"

# telebot expects a function that receives a call and returns True/False.
def callback_all(call):
    return True

# Callback query handler: called when the user clicks a city button.
# - Reads the city name from call.data (callback_data)
# - Calls get_weather to fetch weather text
# - Rebuilds the keyboard so the user can pick another city
# - Edits the original message to show the weather and the keyboard again
@bot.callback_query_handler(func=callback_all)
def handle_city_choice(call):
    city_name = call.data
    # Fetch weather synchronously (this will block this thread briefly)
    weather_text = get_weather(city_name)

    # Rebuild the inline keyboard so the user can choose another cityp
    keyboard = types.InlineKeyboardMarkup()
    for city in CITIES:
        button = types.InlineKeyboardButton(city, callback_data=city)
        keyboard.add(button)

    # Compose the new message text showing the weather and prompting to choose again
    new_text = "Weather in " + city_name + ":\n" + weather_text + "\n\nChoose another city:"

    # Edit the existing message (replace text and attach the keyboard)
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=new_text,
        reply_markup=keyboard
    )

# infinity_polling() runs forever 
bot.infinity_polling()
