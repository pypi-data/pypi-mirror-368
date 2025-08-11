# vibesum

AI-powered number addition using GPT.

## Usage

Install the package:
```bash
pip install vibesum
```

Set your OpenAI API key as an environment variable.
```bash
export OPENAI_API_KEY=your_key_here
```

```python
from vibesum import vibesum

result = vibesum(5, 3)
print(result)  # 8
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