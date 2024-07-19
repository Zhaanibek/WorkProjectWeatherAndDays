# config.py
from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "http://localhost:1234/v1")
API_KEY = os.getenv("API_KEY", "lm-studio")

SUPPORTED_MODELS = ["TheBloke/phi-2-GGUF", "gpt-3.5-turbo"]


def get_api_key(model_name):
    if model_name == "gpt-3.5-turbo":
        return os.getenv('OPENAI_API_KEY')
    elif model_name == "TheBloke/phi-2-GGUF":
        return os.getenv("API_KEY", "lm-studio")
    else:
        raise ValueError(f"Unsupported model: {model_name}")


def get_base_url(model_name):
    if model_name == "TheBloke/phi-2-GGUF":
        return os.getenv("BASE_URL", "http://localhost:1234/v1")
    elif model_name == "gpt-3.5-turbo":
        return "https://api.openai.com/v1"
    else:
        raise ValueError(f"Unsupported model: {model_name}")
