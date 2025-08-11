# vibetrimright

AI-powered string right-trimming using GPT.

## Usage

Install the package:
```bash
pip install vibetrimright
```

Set your OpenAI API key as an environment variable.
```bash
export OPENAI_API_KEY=your_key_here
```

```python
from vibetrimright import vibetrimright

result = vibetrimright("hello world   ")
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