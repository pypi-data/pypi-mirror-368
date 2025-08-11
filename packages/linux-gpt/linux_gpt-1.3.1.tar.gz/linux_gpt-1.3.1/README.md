<p align="center">
  <img src="lgpt.jpg" alt="Linux GPT Logo" width="100%" height='auto' />
</p>

<p align="center">
  <a href="https://ko-fi.com/amiandevsec" target="_blank" rel="noopener">
    <img src="https://cdn.ko-fi.com/cdn/kofi3.png?v=3" alt="Buy Me a Coffee at Ko-fi" style="height: 45px;" />
  </a>
  <br />
  <em>If you find Linux GPT useful, consider supporting development with a coffee ☕️</em>
</p>

# Linux GPT (lgpt)

[![GitHub Release](https://img.shields.io/github/v/release/AmianDevSec/Lgpt)](https://github.com/AmianDevSec/Lgpt/releases/latest)

**Lgpt (Linux GPT)** is a lightweight command-line tool that simplifies your Linux terminal experience by integrating powerful large language models (LLMs) — all **without needing API keys**.

## Supported Providers (No API Keys Required)

Lgpt currently supports these providers to process your queries:

* [GPT-4](https://openai.com/research/gpt-4)
* [GPT-4o](https://openai.com)
* [Deepseek](https://www.deepseek.com/)
* [Mistral](https://mistral.ai/)
* [LLaMA](https://ai.meta.com/llama/)
* [GPT-O3](https://openai.com)
* [Grok](https://x.ai/grok)
* [Cohere](https://cohere.ai/)
* [Codestral](https://mistral.ai)

---

## Usage

Run `lgpt` followed by your query or options:

```bash
Usage: lgpt.py [-h] [-t TOKEN] [--model {gpt-4,gpt-4o,deepseek,mistral,llama,gpt-o3,grok,cohere,codestral}] [-s SET_MODEL] [-u UPDATE] [-v] [prompt ...]

Lgpt: A command-line utility for managing and interacting with large language models (LLMs) directly from the Linux terminal.

Positional arguments:

  prompt                The prompt to send to the selected model.

Optional arguments:

  -h, --help            Show this help message and exit.

  -t, --token           Set your API key token.

  --model               Specify the model to use for query processing.
                        Available models: gpt-4, gpt-4o, deepseek, mistral, llama, gpt-o3, grok, cohere, codestral.
                        Default: grok.

  -s, --set_model       Set your default model.

  -u, --update          Update Lgpt to the latest version.

  -v, --version         Display the current version of Lgpt.
````

**Example:**

### Setting Your API Key

Set your API key by running:

```bash
lgpt --token <your_api_key_here>
```

---

### Using Lgpt with Your API Key

Once the API key is set, you can use Lgpt as follows:

```bash
lgpt "How to update my system packages?"
```

---

### Changing the Default Model

You can change the default model with:

```bash
lgpt --set_model <your_favorite_model>
```

> **Tip:** Run `lgpt -h` to view the list of available models.

---

## Installation

Run the following command to install:

```bash
pip install linux-gpt
```

After installation, verify by running:

```bash
lgpt --version
```

---

## Uninstallation

```bash
pip uninstall linux-gpt
```

---

## Contribution

Feel free to open issues or submit pull requests on the [GitHub repository](https://github.com/AmianDevSec/Lgpt). Contributions and feedback are welcome!

---

## License

This project is licensed under the GPLv3 License. See the [LICENSE](LICENSE) file for details.

---

<p align="center">This project was inspired by <a href="https://github.com/aandrew-me/tgpt" target='_blank' >Terminal GPT(tgpt)</a></p
