# stdoutools

A lightweight Python module to enhance terminal I/O: animated printing, spinners, dynamic effects, and **full terminal logging** (with input + timestamps).

## ✨ Features

- `typer`: Print or prompt with typing animation
- `animate`: Spinners and frame-based terminal animation
- `flashtext`: Show temporary messages that auto-clear
- `terminal`: Clear screen, get terminal size (cross-platform)
- `Logger`: Log terminal output *and* input to a file with timestamps

---

## 🔧 Installation

No external dependencies. Pure Python 3.

Install from PyPI:
```bash
pip install stdoutools
```

---

## 🚀 Usage Examples

### Typing Output and Input

```python
from stdoutools import typer

typer.print("Hello world!", rate=10)
name = typer.input("What's your name? ", rate=20)
print("Hi", name)
```

---

### Spinner and Frame Animation

```python
from stdoutools import animate

animate.spinner(duration=3, message="Loading...")
animate.animate(5, "🌑", "🌓", "🌕", rate=2)
```

---

### Flashing Temporary Text

```python
from stdoutools import flashtext

flashtext("Processing...", delay=2)
```

---

### Logging Everything (Output + Input)

```python
from stdoutools import logger

logger.start("log-@timestamp.txt", timestamp=True, timestamp_format="%Y-%m-%d_%H-%M-%S")

print("Program started")
name = input("Enter your name: ")
print("Hi,", name)

logger.end()
```

#### 🗒️ Features of Logger

- Log **stdout** (e.g. `print()`)
- Log **input prompts and responses**
- Add **timestamps** to each line
- Auto-format filename using `@timestamp`
  - Escape with `@@timestamp` → `@timestamp` literal

#### Filename examples

Assuming the time is 7/08/2025 at 16:05:

| Filename Template          | Example Output Filename             |
|----------------------------|-------------------------------------|
| `log-@timestamp.txt`       | `log-2025-08-07_16-05-00.txt`       |
| `session-@@timestamp.txt`  | `session-@timestamp.txt`            |

---

## 📄 License

MIT License

---

## 🧠 Author

Created by [Juno Wu] with ♥️.