# PacificPy

A Python web framework for building scalable and maintainable web applications.

## Installation

```bash
pip install pacificpy
```

## Usage

```python
from pacificpy import PacificApp

app = PacificApp()

@app.route("/")
async def index(request):
    return "Hello, PacificPy!"

if __name__ == "__main__":
    app.run()
```

## License

MIT