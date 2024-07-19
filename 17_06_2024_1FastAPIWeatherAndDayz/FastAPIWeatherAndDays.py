import os
import requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

app = FastAPI()

# Retrieve API token from environment variables
token = os.getenv('API_TOKEN')
url_api = f'https://calendarific.com/api/v2/holidays?&api_key={token}&country=kz&year=2024'

# Fetch holiday data from the API
response = requests.get(url_api)
data = response.json()

# Extract the list of holidays
holidays = data['response']['holidays']

# Create a DataFrame for the holidays
df = pd.DataFrame([{
    'Название': holiday['name'],
    'Описание': holiday['description'],
    'Страна': holiday['country']['name'],
    'Дата': holiday['date']['iso'],
    'Тип': ', '.join(holiday['type']),
    'Выходной день': 'Да' if holiday['primary_type'] == 'Public holiday' else 'Нет',
    'Ссылка': holiday['canonical_url']
} for holiday in holidays])

# Placeholder for the weather URL
weather_url = os.getenv('WEATHER_URL')

# Headers for the HTTP request to mimic a real browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/58.0.3029.110 Safari/537.3"
}

# Fetch weather data from the website
response = requests.get(weather_url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# Parse weather data
days = soup.find_all("time", class_="time forecast-briefly__date")
max_temps = soup.find_all("div", class_="temp forecast-briefly__temp forecast-briefly__temp_day")
min_temps = soup.find_all("div", class_="temp forecast-briefly__temp forecast-briefly__temp_night")
fb_conditions = soup.find_all("div", class_="forecast-briefly__condition")


# Function to replace Russian month names with English names
def replace_russian_month(date_str):
    months = {
        "января": "January", "февраля": "February", "марта": "March", "апреля": "April",
        "мая": "May", "июня": "June", "июля": "July", "августа": "August",
        "сентября": "September", "октября": "October", "ноября": "November", "декабря": "December"
    }
    for ru, en in months.items():
        date_str = date_str.replace(ru, en)
    return date_str


# Model for the input date
class UserInputDate(BaseModel):
    user_input_date: str


# Endpoint to find holiday and weather information by date
@app.post("/date-check/")
def find_holiday_by_date(user_input: UserInputDate):
    input_date = user_input.user_input_date
    try:
        # Convert the input date to YYYY-MM-DD format
        date_obj = datetime.strptime(input_date, '%d/%m/%Y').date()
        date_str = date_obj.strftime('%Y-%m-%d')

        # Find holidays for the input date
        result = df[df['Дата'] == date_str]

        weather_info = {
            "Дата": input_date,
            "Максимальная температура": "Нет данных",
            "Минимальная температура": "Нет данных",
            "Прогноз погоды": "Нет данных"
        }

        # Find weather information for the input date
        for i in range(min(len(max_temps), len(min_temps), len(days))):
            day_str = days[i].text.strip()
            try:
                # Replace Russian months with English and parse the date
                day_date = datetime.strptime(replace_russian_month(day_str) + " " + str(date_obj.year),
                                             "%d %B %Y").date()
            except ValueError:
                print(f"Неподдерживаемый формат даты: {day_str}")
                continue

            if day_date == date_obj:
                max_temp = max_temps[i].text.strip()
                min_temp = min_temps[i].text.strip()
                fb_condition = fb_conditions[i].text.strip()

                weather_info = {
                    "Дата": input_date,
                    "Максимальная температура": max_temp,
                    "Минимальная температура": min_temp,
                    "Прогноз погоды": fb_condition
                }
                break

        holiday_info = []
        if not result.empty:
            for _, row in result.iterrows():
                holiday_info.append({
                    "Название": row['Название'],
                    "Описание": row['Описание'],
                    "Страна": row['Страна'],
                    "Дата": row['Дата'],
                    "Тип": row['Тип'],
                    "Выходной день": row['Выходной день'],
                    "Ссылка": row['Ссылка']
                })
        else:
            if date_obj.weekday() in [5, 6]:  # Check if the day is a weekend (Saturday or Sunday)
                holiday_info.append({
                    "Сообщение": f"Выходной день: {date_obj.strftime('%A')} {input_date}"
                })
            else:
                holiday_info.append({
                    "Сообщение": f"Рабочий день: {date_obj.strftime('%A')} {input_date}"
                })

        return {
            "Погода": weather_info,
            "Праздники": holiday_info
        }

    except ValueError:
        return {"Ошибка": "Неверный формат даты. Пожалуйста, введите дату в формате dd/mm/yyyy."}


# Run the FastAPI application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)
