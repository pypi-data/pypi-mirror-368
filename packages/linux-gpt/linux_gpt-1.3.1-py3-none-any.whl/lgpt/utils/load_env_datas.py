from dotenv import load_dotenv
import os

load_dotenv()

def load_datas() -> tuple:
    model_saved = os.getenv("DEFAULT_MODEL") or ''
    api_key_saved = os.getenv("APIKEY") or ''

    return (model_saved, api_key_saved)
