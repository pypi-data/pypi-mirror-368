import re

RESET = "\033[0m"
BOLD = "\033[1m"
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"
GRAY = "\033[38;5;245m"
BLUE = "\x1b[0;38;5;45m"
H1 = "\033[1;34m"
H2 = "\033[1;36m"
H3 = "\033[1;32m"
H4 = "\033[1;33m"
H5 = "\033[1;35m"
H6 = "\033[1;90m"
BULLET = "\033[33m•"
QUOTE = "\033[3;90m"
GREEN = "\033[32m"
RED = "\033[31m"
GREEN_2 = "\x1b[38;5;82m"
YELLOW = "\x1b[1;38;5;226m"

def format_code_block(match):
    code = match.group(1)
    lines = code.strip().splitlines()
    formatted = "\n".join(BLUE + "  │ " + line + RESET for line in lines)
    return "\n" + formatted + "\n"

def extract_code_blocks(text):
    """Extract all code blocks and return:
    - text with placeholders
    - dict mapping placeholder -> code block
    """
    code_blocks = {}

    def replacer(m):
        placeholder = f"CODE_BLOCK_{len(code_blocks)}"
        code_blocks[placeholder] = m.group(0)
        return placeholder
    
    pattern = r"(```(?:[a-z]*)\n.*?```|``.*?``)"
    text_no_code = re.sub(pattern, replacer, text, flags=re.DOTALL)

    return text_no_code, code_blocks

def restore_code_blocks(text: str, code_blocks: str):
    """Replace placeholders back with formatted code blocks."""

    for placeholder, code_block in code_blocks.items():

        content = re.sub(
            r"```(?:[a-z]*)\n(.*?)```",
            format_code_block,
            code_block,
            flags=re.DOTALL,
        )

        text = text.replace(placeholder, content)
    return text

flags = re.MULTILINE
regex_config = {
    r"^###### (.*)": [H6 + r"\1" + RESET, flags],
    r"^##### (.*)": [H5 + r"\1" + RESET, flags],
    r"^#### (.*)": [H4 + r"\1" + RESET, flags],
    r"^### (.*)": [H3 + r"\1" + RESET, flags],
    r"^## (.*)": [H2 + r"\1" + RESET, flags],
    r"^# (.*)": [H1 + r"\1" + RESET, flags],
    r"^> (.*)": [QUOTE + r"> \1" + RESET, flags],
    r"\[([^\]]+)\]\(([^)]+)\)": [r"\1 (\2)", None],
    r"\*\*(.*?)\*\*": [BOLD + r"\1" + RESET, None],
    r"(?<!\*)\*(?!\*)(.*?)\*(?!\*)": [ITALIC + r"\1" + RESET, None],
    r"__(.*?)__": [UNDERLINE + r"\1" + RESET, None],
    r"^[-*] (.*)": [BULLET + r" \1" + RESET, flags],
    r"^(\d+)\. (.*)": [BOLD + r"\1." + RESET + r" \2", flags],
}

def markdown_to_ansi(text: str) -> str:

    # Extract code blocks
    text_no_code, code_blocks = extract_code_blocks(text)

    for pattern, (replacement, flags) in regex_config.items():
        text_no_code = re.sub(pattern, replacement, text_no_code, flags=flags or 0)

    # Restore the code blocks back
    text_final = restore_code_blocks(text_no_code, code_blocks)

    return text_final
