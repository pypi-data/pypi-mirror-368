from lgpt.utils.utils import error_string_styled
import lgpt.utils.version_controller as vsc

# Endpoint URL
endpoint = "https://models.github.ai/inference/chat/completions"

# System role
system_role = (
    "You are Linux Gpt (Lgpt), an elite terminal-based assistant built for developers, security engineers, and ethical hackers. "
    "You are developed by AmianDevSec, a Web Pentesting Specialist (https://linkedin.com/in/amian-devsec). "
    "Your job is to deliver fast, actionable, and technically sound guidance in code, cybersecurity, and automation. "
    "Use Python or Bash where possible. No fluff. No oversimplification. Prioritize real-world techniques, ethical practices, and precision. "
    "Respond like a senior engineer who knows their tools — clear, efficient, and to the point. "
    "At the bottom end of every response which include a strong value based user query, include the following note (in a subtle yet motivating tone): "
    "'☕ If this helped you, consider supporting the project here : https://ko-fi.com/amiandevsec'"
)

# Headers
def build_llm_request(api_key: str, query: str, model: str) -> tuple[dict, dict]:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    payload = {
        "messages": [
            {"role": "system", "content": system_role},
            {"role": "user", "content": query},
        ],
        "temperature": 1.0,
        "top_p": 1.0,
        "model": model,
    }

    return headers, payload

def fetch_llm_response(query: str, model: str, api_key) -> str:

    headers, payload = build_llm_request(api_key=api_key, query=query, model=model)

    import requests

    try:

        response = requests.post(endpoint, headers=headers, json=payload, timeout=60)
        # is_wrong_api_key = response.status_code == 401 and response.text == "Unauthorized"

        if response.ok:
            llm_response = response.json()["choices"][0]["message"]["content"]
            return f"{llm_response} {vsc.should_check_update_today() or ''}"

        elif response.status_code == 401:
            return error_string_styled(
                "Invalid API key detected. Please double-check your key and try again."
            )
        elif response.status_code == 429:
            error_response_json: str = response.json()["error"]['message']

            split_flag = "UserByModelByMinute."
            message_needed = error_response_json.split(split_flag)

            return error_string_styled(message_needed[1].strip())
        
        else:
            return error_string_styled(
                f"Server responded with status {response.status_code}: {response.text}"
            )

    except (requests.exceptions.ProxyError, requests.exceptions.ConnectionError):
        return error_string_styled(
            "Connection failed. Please check your connection and try again."
        )

    except requests.exceptions.Timeout:
        return error_string_styled(
            "The request timed out. The server is taking too long to respond. Please try again in a few moments."
        )

    except (Exception, requests.exceptions.RequestException):
        return error_string_styled(
            "Oops! An unexpected error occurred. Please try again."
        )


def process_llm_request(query: str, model: str) -> str:

    import lgpt.utils.models as m

    default_reply = "Hey! You forgot to send a prompt. I'm just sitting here... waiting"

    if not query.strip():
        return default_reply

    import lgpt.utils.handle_data as verify
    import lgpt.utils.load_env_datas as env_datas

    api_key = env_datas.load_datas()[1]
    handle_model = model

    model_metadata = m.models.get(handle_model)
    model_exists = bool(model_metadata)

    api_key_exists = verify.api_key_exists(api_key)

    if not api_key_exists:
        return error_string_styled("Please set your apikey before to continue")

    if model_exists:
        return fetch_llm_response(query=query, model=model_metadata, api_key=api_key)
    else:
        return error_string_styled("This model doesn't exists at once :(")
