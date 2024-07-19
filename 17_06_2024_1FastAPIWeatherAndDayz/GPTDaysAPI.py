# -*- coding: utf-8 -*-

import requests
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv
import os
import streamlit as st

# Загружаем переменные окружения
load_dotenv()

# Получаем ключ API из переменных окружения
openai_api_key = os.getenv('OPENAI_API_KEY')
if not openai_api_key:
    st.error("API ключ для OpenAI не найден. Убедитесь, что переменная окружения OPENAI_API_KEY установлена.")
    st.stop()

# Инициализация клиента OpenAI
client = OpenAI(api_key=openai_api_key)

url = 'http://127.0.0.1:8002/date-check/'


def check_business_type_similarity(context):
    prompt = f'please answer user query: {context}'
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        response = response.choices[0].message.content.strip().lower()
        return response
    except OpenAIError as e:
        st.error(f"Ошибка при запросе к OpenAI API: {e}")
        return None


st.title("Дата и пользовательский запрос")

# Используем календарь для выбора даты
user_input_date = st.date_input('Выберите дату')

# Преобразуем дату в нужный формат
user_input_date = user_input_date.strftime('%d/%m/%Y')

# Создаем поле для ввода пользовательского запроса
user_query = st.text_area('Введите ваш запрос:')

if st.button('Отправить запрос'):
    if user_input_date and user_query:
        json_data = {"user_input_date": user_input_date}
        response = requests.post(url, json=json_data)

        if response.status_code == 200:
            response_data = response.json()
            context = f'{user_query}. Date info: {response_data}'
            AI_response = check_business_type_similarity(context)
            if AI_response:
                st.success("Запрос выполнен успешно!")
                st.write("Ответ AI:", AI_response)
        else:
            st.error(f"Ошибка! Код ответа: {response.status_code}")
            st.error(f"Сообщение об ошибке: {response.text}")
    else:
        st.error("Пожалуйста, заполните оба поля.")
