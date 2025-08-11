import requests
from packaging import version
import lgpt.utils.__version__ as vs
from lgpt.utils.markdown_handler import (
    BOLD,
    YELLOW,
    RESET,
    BLUE,
    GREEN,
    UNDERLINE,
    QUOTE,
)

from datetime import datetime, UTC

def get_latest_version(package_name: str):
    try:
        url = f"https://pypi.org/pypi/{package_name}/json"
        response = requests.get(url, timeout=3)
        
        if response.ok:
            return response.json()["info"]["version"]
    except requests.RequestException:
        pass
    
    return None

def notify_if_update_available(current_version: str = vs.__version__, package_name: str = "lgpt"):
    latest = get_latest_version(package_name)

    latest_v_condition = latest and version.parse(latest)
    current_v_condition = version.parse(current_version)

    if latest_v_condition > current_v_condition:
        return version_message(
            current_version=current_version,
            latest_version=latest
            )

def version_message(current_version: str, latest_version: str) -> str:
    return f"""

{BOLD}{YELLOW}A new version of Lgpt is available!{RESET}
You're currently using {BOLD}{BLUE}v{current_version}{RESET} → Latest version is {BOLD}{GREEN}v{latest_version}{RESET}.

{UNDERLINE}To update it, run{RESET}:

    {BOLD}{QUOTE}lgpt --update{RESET}
"""

def should_check_update_today() -> str|None:
    today = datetime.now(UTC).date().weekday()
    is_sunday = today == 6 

    if is_sunday:
        return notify_if_update_available()
