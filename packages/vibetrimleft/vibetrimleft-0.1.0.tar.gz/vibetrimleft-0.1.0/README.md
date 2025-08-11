# Vibetrimleft

AI-powered string left-trimming using GPT.

## Usage

Install the package:
```bash
pip install vibetrimleft
```

Set your OpenAI API key as an environment variable.
```bash
export OPENAI_API_KEY=your_key_here
```

```python
from vibetrimleft import vibetrimleft

result = vibetrimleft("   hello world")
print(repr(result))  # 'hello world'
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

## DISCLAIMER
Will not work half the time :) Enjoy!