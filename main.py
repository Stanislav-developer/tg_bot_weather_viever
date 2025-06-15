import json
import telebot
from telebot import types
from datetime import datetime
import datetime as dt
import requests

#Функція для визначення привітання користувача в залежності від часу доби
def greetingText():
    
    hour = current_time.hour
    
    if hour >= 6 and hour <= 12:
        greeting_text = 'Доброго ранку'
    elif hour > 12 and hour <= 18:
        greeting_text = 'Доброго дня'
    elif hour > 18 and hour <= 23:
        greeting_text = 'Доброго вечора'
    else:
        greeting_text = 'Доброї ночі'
        
    return greeting_text

#Відкриваємо ключі від зовнішніх API
with open("data/config.json", 'r') as file:
    config = json.load(file)

#Універсальна функція для відкриття текстових файлів
def openTxt(file_corner):
    with open(file_corner, 'r', encoding = 'utf-8') as file:
        info_text = file.read()
    return info_text

# Завантажити місто з JSON
def load_city():
    try:
        with open("data/city.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("city", "")
    except (FileNotFoundError, json.JSONDecodeError):
        return ""

# Зберегти місто в JSON
def save_city(city_name):
    with open("data/city.json", 'w', encoding='utf-8') as f:
        json.dump({"city": city_name}, f, ensure_ascii=False, indent=4)

# Функція конвертації градусів        
def kelvin_to_celsius_fahrenheit(kelvin):
    celsius = kelvin - 273.15
    fahrenheit = celsius * (9/5) + 32
    return celsius, fahrenheit

#Отримуємо json з url
def get_weather_json():
    global response
    url = base_url + 'appid=' + weather_key + '&q=' + city
    response = requests.get(url).json()

#Змінна чи чекаємо ми на вибір міста
select_location_flag = False

#Змінна у якій зберігається json з openweather
response = None

current_time = datetime.now()
full_time = current_time.strftime("%H:%M")

base_url = "https://api.openweathermap.org/data/2.5/weather?"

telegram_key = config['telegram_token']
weather_key = config["openweather_key"]

bot = telebot.TeleBot(telegram_key)

city = load_city()
        
start_text = openTxt("data/start_info.txt")
help_text = openTxt("data/help_info.txt")
info_text = openTxt('data/info_text.txt')

greeting_text = greetingText()

#Обробка команди /start
@bot.message_handler(commands=['start','hello','hi'])
def get_start(message):
    bot.send_message(message.chat.id, f'{greeting_text}, {message.from_user.first_name}!')
    bot.send_message(message.chat.id, start_text)
    
#Обробка команди /help    
@bot.message_handler(commands=['help','support'])
def get_help(message):
    
    markup = types.InlineKeyboardMarkup(row_width=2)

    markup.add(
        types.InlineKeyboardButton("🌆 Вибрати місто", callback_data='select_region'),
        types.InlineKeyboardButton("🌡 Температура", callback_data='temp'),
        types.InlineKeyboardButton("🤔 Відчувається як", callback_data='feels_like'),
        types.InlineKeyboardButton("💨 Вітер", callback_data='wind'),
        types.InlineKeyboardButton("💧 Вологість", callback_data='humidity'),
        types.InlineKeyboardButton("🌅 Схід/Захід сонця", callback_data='sun_time'),
        types.InlineKeyboardButton("🌥 Опис погоди", callback_data='description'),
        types.InlineKeyboardButton("📋 Вся погода", callback_data='weather'),
        types.InlineKeyboardButton("ℹ️ Про бота", callback_data='info')
    )

    help_text = "Ось список доступних команд. Натисни кнопку:"

    bot.send_message(message.chat.id, help_text, reply_markup=markup)

#Обробка команди /info
@bot.message_handler(commands=['info','about'])
def get_info(message):
    bot.send_message(message.chat.id, info_text)

#Обробка команди /select_region
@bot.message_handler(commands=['select_region'])
def select_region(message):
    global select_location_flag
    select_location_flag = True
    bot.send_message(message.chat.id, 'Ок тепер напиши назву свого міста(кирилецею або латинецею) де ти проживаєш👇')

#Отримуємо поточну температуру /temp
@bot.message_handler(commands=['temp'])
def get_temp(message):
    get_weather_json()
    temp_kelvin = response['main']['temp']
    temp_celsius, temp_fahrenheit = kelvin_to_celsius_fahrenheit(temp_kelvin)
    emoji = ''
    if temp_celsius > 20.0:
        image = 'sun.png'
        emoji = '☀️'
    elif temp_celsius <= 20.0 or temp_celsius >= 10.0:
        image = 'cloudy.png'
        emoji = '⛅️'
    elif temp_celsius < 10.0 or temp_celsius >= 1.0:
        image = 'cloud.png'
        emoji = '☁️'
    elif temp_celsius < 1.0 :
        image = 'snow.png'
        emoji = '❄️'
        
    bot.send_message(message.chat.id, f'Поточна температура на вулиці у місті {city}: {temp_celsius:.2f}°С {emoji}')
    bot.send_message(message.chat.id, f'Поточна температура на вулиці у місті {city}: {temp_celsius:.2f}°F {emoji}')

#Отримуємо поточну швидкість вітру /wind
@bot.message_handler(commands=['wind'])
def get_wind_speed(message):
    get_weather_json()
    wind_speed = response['wind']['speed']
    bot.send_message(message.chat.id, f'Швидкість вітру у місті {city}: {wind_speed}м/с 💨')

#Отримуємо поточну відчутну температуру /feels_like
@bot.message_handler(commands=['feels_like'])
def get_wind_speed(message):
    get_weather_json()
    feels_like_kelvin = response['main']['feels_like']
    feels_like_celsius, feels_like_fahrenheit = kelvin_to_celsius_fahrenheit(feels_like_kelvin)
    emoji = ''
    if feels_like_celsius > 20.0:
        image = 'sun.png'
        emoji = '☀️'
    elif feels_like_celsius <= 20.0 or feels_like_celsius >= 10.0:
        image = 'cloudy.png'
        emoji = '⛅️'
    elif feels_like_celsius < 10.0 or feels_like_celsius >= 1.0:
        image = 'cloud.png'
        emoji = '☁️'
    elif feels_like_celsius < 1.0 :
        image = 'snow.png'
        emoji = '❄️'
    bot.send_message(message.chat.id, f'Як відчувається температура на вулиці у місті {city}: {feels_like_celsius:.2f}°С {emoji}')
    bot.send_message(message.chat.id, f'Як відчувається температура на вулиці у місті {city}: {feels_like_fahrenheit:.2f}°F {emoji}')

#Отримуємо поточну вологість повітря /humidity
@bot.message_handler(commands=['humidity'])
def get_humidity(message):
    get_weather_json()
    humidity = response['main']['humidity']
    bot.send_message(message.chat.id, f'Вологість повітря у місті {city}: {humidity}% 💦')

#Отримуємо час сходу та заходу сонця /sun_time
@bot.message_handler(commands=['sun_time'])
def get_sun(message):
    get_weather_json()
    sunrise_time = dt.datetime.utcfromtimestamp(response['sys']['sunrise'] + response['timezone']) 
    sunset_time = dt.datetime.utcfromtimestamp(response['sys']['sunset'] + response['timezone'])
    
    bot.send_message(message.chat.id, f'У місті {city} сонце сходить о: {sunrise_time} годині 🌅')
    bot.send_message(message.chat.id, f'У місті {city} сонце заходить о: {sunset_time} годині 🌅')

#Отримуємо загальний опис погоди /description
@bot.message_handler(commands=['description'])
def get_description(message):
    get_weather_json()
    description = response['weather'][0]['description']
    bot.send_message(message.chat.id, f'Загальний опис погоди у місті {city}: {description} ')

#Отримуємо всі данні по погоді /weather
@bot.message_handler(commands=['weather'])
def weather(message):
    get_weather_json()
    temp_kelvin = response['main']['temp']
    temp_celsius, temp_fahrenheit = kelvin_to_celsius_fahrenheit(temp_kelvin)
    feels_like_kelvin = response['main']['feels_like']
    feels_like_celsius, feels_like_fahrenheit = kelvin_to_celsius_fahrenheit(feels_like_kelvin)
    wind = response['wind']['speed']
    humidity = response['main']['humidity']
    description = response['weather'][0]['description']
    sunrise_time = dt.datetime.utcfromtimestamp(response['sys']['sunrise'] + response['timezone']) 
    sunset_time = dt.datetime.utcfromtimestamp(response['sys']['sunset'] + response['timezone']) 
    
    weather_text = (
    f"📍 Місто: {city.capitalize()}\n"
    f"🌡 Температура: {temp_celsius:.1f}°C (відчувається як {feels_like_celsius:.1f}°C)\n"
    f"🌥 Опис: {description.capitalize()}\n"
    f"💧 Вологість: {humidity}%\n"
    f"💨 Вітер: {wind} м/с\n"
    f"🌅 Схід сонця: {sunrise_time.strftime('%H:%M')}\n"
    f"🌇 Захід сонця: {sunset_time.strftime('%H:%M')}\n"
    f"🕒 Оновлено на: {current_time.strftime('%H:%M')}"
    )
    
    bot.send_message(message.chat.id, weather_text)

#Обробник довільного тексту
@bot.message_handler(content_types=['text'])
def handle_text(message):
    global select_location_flag, city

    text = message.text.strip().lower()

    # Якщо користувач вводить місто
    if select_location_flag:
        res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={text}&appid={weather_key}&units=metric')
        if res.status_code == 200:
            city = text
            save_city(city)
            bot.send_message(message.chat.id, f'Місто збережено: {city.capitalize()}')
            select_location_flag = False
            return  
        else:
            bot.send_message(message.chat.id, f'Місто вказано не правильно...')
            return

    # Звичайні відповіді
    if text in ['привіт','салам','hello','hi','здоров']:
        bot.send_message(message.chat.id, f'{greetingText()}, {message.from_user.first_name}!')
        bot.send_message(message.chat.id, start_text)

    elif text in ['як справи?', 'як ти?','how are you?']:
        bot.send_message(message.chat.id, 'Я у повній готовності, звертайся!')

    elif text in ['який час?', 'яка година?', 'який зараз час?', 'яка зараз година?']:
        now = datetime.now()
        bot.send_message(message.chat.id, f'Зараз: {now.strftime("%H:%M")}')

    elif text in ['дякую', 'дякую!', 'спасибі', 'спасибі!']:
        bot.send_message(message.chat.id, 'Завжди будь ласка)')

    else:
        bot.send_message(message.chat.id, "такої команди не існує... використай /help")
        
#Обробник Каллбеків
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == 'select_region':
        select_region(call.message)
    elif call.data == 'temp':
        get_temp(call.message)
    elif call.data == 'feels_like':
        get_wind_speed(call.message)  # у тебе два однакові імені функції!
    elif call.data == 'wind':
        get_wind_speed(call.message)
    elif call.data == 'humidity':
        get_humidity(call.message)
    elif call.data == 'sun_time':
        get_sun(call.message)
    elif call.data == 'description':
        get_description(call.message)
    elif call.data == 'weather':
        weather(call.message)
    elif call.data == 'info':
        get_info(call.message)

#Пишемо цю команду щоб код виконувався цілий час
bot.polling(none_stop=True)