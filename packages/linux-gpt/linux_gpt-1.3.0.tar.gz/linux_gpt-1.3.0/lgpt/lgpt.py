import sys
from argparse import ArgumentParser
from lgpt.utils.llms_handler import process_llm_request
from lgpt.utils.utils import typewriter, helper, error_string_styled
from lgpt.utils.lgpt_updater import stop_event, loading_thread, lgpt_updater
import lgpt.utils.models as m
import lgpt.utils.handle_data as h_api_key
import lgpt.utils.load_env_datas as env_datas
import lgpt.utils.__version__ as vs

def lgpt() -> None:

    response = ""
    default_model = env_datas.load_datas()[0]
    available_models = m.models.keys()

    try:
        loading_thread.start()
        parser = ArgumentParser(
            add_help=False,
            description="Lgpt: A command-line utility for managing and interacting with large language models (LLMs) from the Linux terminal."
        )

        parser.add_argument(
            "-m",
            "--model",
            type=str,
            choices=list(available_models),
            default=default_model,
            help="The model to use for processing the query.",
        )

        parser.add_argument(
            '-h', 
            '--help', 
            action='store_true', 
            help='Show help and exit')

        parser.add_argument(
            "prompt",
            type=str,
            nargs='*',
            help="The prompt to send to the model."
        )

        parser.add_argument(
            "-u",
            "--update",
            action="store_true",
            help="Update Lgpt to latest version."
        )

        parser.add_argument(
            "-v",
            "--version",
            action="store_true",
            help="Prints the current version of Lgpt.",
        )

        parser.add_argument(
            "-t",
            "--token",
            type=str,
            help="Set your api key token.",
        )

        parser.add_argument(
            "-s",
            "--set_model",
            type=str,
            help="Set your default model.",
        )

        args = parser.parse_args()

        model = args.model
        update = args.update

        version = args.version
        help = args.help

        api_key = args.token
        default_model_ = args.set_model

        prompt = ""

        if update:
            return lgpt_updater()

        elif help:

            avail_models_string = ",".join(available_models)

            response = helper(
                models="{" + avail_models_string + "}", default_model=default_model
            )

        elif version:
            response = vs.__version__

        elif api_key or default_model_:

            response = h_api_key.save_env_data(
                api_key=api_key,
                default_model=default_model_,
                available_models=available_models,
            )

        else:
            piped_input = sys.stdin.read().strip() if not sys.stdin.isatty() else ''
            prompt = f"{' '.join(args.prompt)} {piped_input}"

            llm_response = process_llm_request(query=prompt, model=model)
            response = llm_response if not bool(response) and bool(prompt) else response

    except (KeyboardInterrupt, EOFError):
        response = error_string_styled("Process interrupted by user. Exiting...")
    except Exception as e:
        response = error_string_styled(f"An error occurred: {e}")
    finally:
        stop_event.set()
        loading_thread.join()

    return typewriter(response)


def main():
    lgpt()

if __name__ == "__main__":
    main()
