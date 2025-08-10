# VibeIsEven

> "Why use math when you have AI?"

VibeIsEven is a satirical, production-quality Python package that determines if a number is even by asking a large language model (LLM) like OpenAI GPT or Gemini, instead of using arithmetic. It’s a parody of using AI for trivial tasks, but is fully functional and well-structured.

## Installation

```bash
pip install vibeiseven
```

## Usage

Set your API key as an environment variable:

- For OpenAI: `OPENAI_API_KEY`
- For Gemini: `GEMINI_API_KEY`

```python
from vibeiseven import vibeiseven, vibeiseven_batch

print(vibeiseven(42))  # True
print(vibeiseven(13, provider='gemini'))  # False
print(vibeiseven_batch([1, 2, 3, 4]))  # [False, True, False, True]
```

## Example

See `vibeiseven/example.py` for a runnable example.

## Development

- Clone the repo
- Install dependencies: `pip install -r requirements.txt`
- Run tests/examples with real API keys

## Contributing

Pull requests are welcome! For major changes, please open an issue first.

## License

MIT
