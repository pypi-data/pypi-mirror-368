# vibefunc 💤

**Vibefunc** is a Python decorator that lets you write *only* the function signature & docstring.
When you call the function, it automatically asks an AI to fill in the body — and then runs it.

---

## 💻 Installation

```bash
pip install lazyfunc
```

## 🎮 Usage

Set your OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY=your_openai_api_key
```

Then, you can use the `vibefunc` decorator to create functions that will be filled in by AI:

```python
from vibefunc import vibefunc

@vibefunc()
def sort(a: list):
    """Sort the list in ascending order and print the sorted list."""
    ...

sort([1, 222, 3333, 4, 45634, 1314235, 233])
```

Result:

```
[1, 4, 222, 3333, 45634, 1314235]
```

## ⚠️ Warnings

- Don’t run this in production unless you like surprises (and bugs).

Happy(Damn) vibing! ✨

![vibe_coding](./vibe.jpg)

## Parameters

- `model`: The OpenAI model to use (default: "gpt-4.1-mini").
- `base_url`: The base URL for the OpenAI SDK (default: "https://api.openai.com/v1").
- `save_money`: If `True`, stores the same function body in a file instead of calling the OpenAI API (default: `True`).
- `mode`: `serious` or `chaotic`, just for fun (default: `serious`).
