# VibeHowManyRs

AI-powered letter R counting using GPT.

## Usage

Install the package:
```bash
pip install vibehowmanyrs
```

Set your OpenAI API key as an environment variable.
```bash
export OPENAI_API_KEY=your_key_here
```

```python
from vibehowmanyrs import vibehowmanyrs

result = vibehowmanyrs("Raspberry")
print(result)  # 3

result = vibehowmanyrs("ROAR")
print(result)  # 2
```

## Test

```bash
pytest tests/
```

## Dependencies

- openai
- pydantic
- typing-extensions

⚠️ Requires OpenAI API key. Experimental project - not for production use.

## Why?

Because strawberry has 2 r's

## DISCLAIMER
Will not work half the time :) Enjoy!