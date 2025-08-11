import subprocess as sub
from lgpt.utils.markdown_handler import GREEN, RESET, BOLD
from lgpt.utils.utils import typewriter, loading_effect, error_string_styled
import threading
import sys

# Setup loading animation
stop_event = threading.Event()

loading_thread = threading.Thread(
    target=loading_effect, kwargs={"stop_event": stop_event}
)

def lgpt_updater() -> None:
    output = ""

    try:

        sub.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "linux-gpt"],
            check=True,
        )

        output = f"{GREEN}{BOLD}✔ Update complete!.{RESET}"

    except sub.CalledProcessError as e:
        output = error_string_styled(
            f"Update failed. Try manually with: pip install --upgrade linux-gpt"
        )
    except Exception as e:
        output = error_string_styled(
            f"An error occurred during update: {e}"
        )
    finally:
        stop_event.set()
        loading_thread.join()

    return typewriter(output)
