from lgpt.utils.markdown_handler import RESET, GREEN, BOLD
import lgpt.utils.load_env_datas as env_datas

def api_key_exists(api_key: str) -> str:
    return bool(api_key)

def save_env_data(api_key: str, default_model: str, available_models: list) -> str:

    from lgpt.utils.utils import error_string_styled

    model_exists = default_model in available_models

    if default_model and not model_exists:
        return error_string_styled("This model doesn't exists at once :(")

    import lgpt.utils.get_path as gph

    env_path = gph.get_path('.env')

    model_to_save = default_model or env_datas.load_datas()[0]
    api_key_to_save = api_key or env_datas.load_datas()[1]

    output_message: str = (
        "✔ Your api key was successful saved."
        if api_key
        else "✔ Your default model was successful saved."
    )

    with open(env_path, "w") as f:
        f.write(f"APIKEY = '{api_key_to_save}'\nDEFAULT_MODEL = '{model_to_save}'")

    return f"{GREEN}{BOLD}{output_message}{RESET}"
