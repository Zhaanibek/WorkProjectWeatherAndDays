# openai_utils.py

from openai import OpenAI
import config

# Инициализация истории чата
chat_history = []


def create_client(model_name):
    api_key = config.get_api_key(model_name)
    base_url = config.get_base_url(model_name)
    return OpenAI(api_key=api_key, base_url=base_url)


def check_business_type_similarity(context, model_name):
    global chat_history  # Используем глобальную переменную для хранения истории чата
    client = create_client(model_name)
    prompt = f'please answer user query: {context}'
    response = None

    if model_name == "gpt-3.5-turbo":
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
    elif model_name == "TheBloke/phi-2-GGUF":
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "Always answer in rhymes."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )

    if response:
        response_content = response.choices[0].message['content'].strip().lower()
    else:
        response_content = "No response from the model"

    # Добавляем текущее сообщение пользователя и ответ модели в историю чата
    chat_history.append((prompt, response_content))

    return response_content
