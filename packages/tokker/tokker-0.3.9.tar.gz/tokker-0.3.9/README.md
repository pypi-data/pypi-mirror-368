# Tokker

Tokker 0.3.9: a fast local-first CLI tokenizer with all the best models in one place.
---

## Features

- **Simple Usage**: Just `tok 'your text'` - that's it!
- **Models**:
  - OpenAI: GPT-OSS, o-family (o1, o3, o4), GPT-4o, GPT-4, GPT-3.5, GPT-3
  - Google: the entire Gemini family
  - HuggingFace: popular models like Deepseek-R1, Qwen-3, GLM-4.5 and many other within [transformers](https://huggingface.co/models?library=transformers) library (some may not be supported yet)
- **Output Formats**: color (like [this](https://platform.openai.com/tokenizer)), count, JSON, pivot, and more
- **Text Analysis**: Token count, word count, character count, and token frequency
- **Model History**: See your recently used models
- **Local-first**: Works locally on device (except Google)

---

## Installation

```bash
# Install tokker without model provider packages (optional)
pip install tokker

# Install at least one model provider package:
pip install 'tokker[all]' # for all models at once
pip install 'tokker[tiktoken]' # for models from OpenAI
pip install 'tokker[google-genai]' # for models from Google
pip install 'tokker[transformers]' # for models from HuggingFace
```
---

## Command Reference

```
usage: tok [--help] [-w MODEL] [-o {color,count,json,pivot,del}] [-m] [-c]
           [-dm MODEL] [-do OUTPUT] [-h] [-x]
           [text]

Tokker 0.3.9: a fast local-first CLI tokenizer with all the best models in one place

positional arguments:
  text                  text to tokenize (or read from stdin)

options:
  --help                (or just `tok`) to show this help message
  -w, --with MODEL      with specific (non-default) model
  -o, --output {color,count,json,pivot,del}
                        output format
  -m, --models          list all models
  -c, --config          show config with settings
  -dm, --default-model MODEL
                        set default model
  -do, --default-output OUTPUT
                        set default output
  -h, --history         show history of used models
  -x, --history-clear   clear history
```

## Usage

### Tokenization

When using `bash` or `zsh`, wrap input text in **single** quotes ('like this') to avoid conflicts with special characters like `!`.

```bash
# Tokenize with default model (o200k_base) and output (color)
$ tok 'Hello world!'
# Get pivot summary of token frequencies
$ tok 'Hello world!' -o pivot
# Tokenize with Deepseek-R1
$ tok 'Hello world!' -w zai-org/GLM-4.5
# Get just the count with Gemini-2.5-pro
$ tok 'Hello world!' -w gemini-2.5-pro -o count

```

### Pipeline Usage

```bash
# Process files
$ cat document.txt | tok -w deepseek-ai/DeepSeek-R1 -o count

# Chain with other tools
$ curl -s https://example.com | tok -w openai/gpt-oss-120b

# Compare models
$ echo "I'm tired boss, I can't do matmul anymore" | tok -w gemini-2.5-flash
$ echo "I'm tired boss, I can't do matmul anymore" | tok -w gemini-2.0-flash
```

### Models

```bash
# List all available models
$ tok -m
```

Output:
```text
============
OpenAI:

o200k_base            - for GPT-OSS, o-family (o1, o3, o4) and GPT-4o
cl100k_base           - for GPT-3.5 (late), GPT-4
p50k_base             - for GPT-3.5 (early)
p50k_edit             - for GPT-3 edit models (text-davinci, code-davinci)
r50k_base             - for GPT-3 base models (davinci, curie, babbage, ada)
------------
Google:

gemini-2.5-pro
gemini-2.5-flash-lite
gemini-2.5-flash
gemini-2.0-flash-lite
gemini-2.0-flash

Auth setup required   ->   https://github.com/igoakulov/tokker/blob/main/google-auth-guide.md
------------
HuggingFace:

  1. Go to   ->   https://huggingface.co/models?library=transformers
  2. Search models within TRANSFORMERS library (some not supported yet)
  3. Copy its `USER/MODEL` into your command, for example:

openai/gpt-oss-120b
Qwen/Qwen3-Coder-480B-A35B-Instruct
zai-org/GLM-4.5
deepseek-ai/DeepSeek-R1
facebook/bart-base
google-bert/bert-base-uncased
google/electra-base-discriminator
microsoft/phi-4
============
```

### Config

Stored locally in `~/.config/tokker/config.json`.

Show config:
```bash
# Show config with settings
$ tok -c
```

Returns:
```text
{
  "default_model": "o200k_base",
  "default_output": "color",
  "delimiter": "⎮"
}
```

Set defaults:
```bash
# Set a Deepseek-R1 as the default model
$ tok -dm deepseek-ai/DeepSeek-R1
# Set count as the default output
$ tok -do count
```

### History

Stored locally in `~/.config/tokker/history.json`.

Show history:
```bash
$ tok -h
```

Returns:
```text
============
History:

gemini-2.5-pro                  2025-08-09 19:58
cl100k_base                     2025-08-09 19:52
gpt2                            2025-08-08 16:23
============
```

Clear history:
```bash
# Does not ask for confirmation
$ tok -x
```

---

## Output Formats

### Color Output (Default)

- Marks each token with an alternating color.
- Color formatting does not render in the example below, but it's like [this](https://platform.openai.com/tokenizer).
- Color formatting is not preserved when copying the CLI output.

Command:
```bash
$ tok 'Hello world!'
```

Returns:
```text
Hello world!
3 tokens, 2 words, 12 chars
```

### Del (=Delimited) Output

- Preserves visual token separation when you copy (unlike color)
- After pasting, remove "⎮" easily with Find & Replace if needed
- "⎮" (U+23AE VERTICAL LINE EXTENSION) is a rare symbol, and will not interfere with the standard "|" (U+007C VERTICAL LINE)

Command:
```bash
$ tok 'Hello world!' -o del
```

Returns:
```text
Hello⎮ world⎮!
3 tokens, 2 words, 12 chars
```

### Count Output

Command:
```bash
$ tok 'Hello world!' -o count
```

Returns:
```text
{
  "token_count": 3,
  "word_count": 2,
  "char_count": 12
}
```

### Pivot Output

The pivot output prints a JSON object with token frequencies, sorted by highest count first, then by token (A–Z).

Command:
```bash
tok 'never gonna give you up neve gonna let you down' -o pivot
```

Returns:
```text
{
  " gonna": 2,
  " you": 2,
  " down": 1,
  " give": 1,
  " let": 1,
  " ne": 1,
  " up": 1,
  "never": 1,
  "ve": 1
}
```

### Full JSON Output

Command:
```bash
tok 'Hello world!' -o json
```

Returns:
```text
{
  "delimited_text": "Hello⎮ world⎮!",
  "token_strings": ["Hello", " world", "!"],
  "token_ids": [9906, 1917, 0],
  "token_count": 3,
  "word_count": 2,
  "char_count": 12
}
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contributing

Issues and pull requests are welcome! Visit the [GitHub repository](https://github.com/igoakulov/tokker).

---

## Acknowledgments

- OpenAI for the tiktoken library
- HuggingFace for the transformers library
- Google for the Gemini models and APIs
