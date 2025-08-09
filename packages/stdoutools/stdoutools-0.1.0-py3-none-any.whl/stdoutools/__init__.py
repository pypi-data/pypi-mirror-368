"""
stdoutools
==========

A Python utility module providing tools for animated and controlled output in the terminal,
as well as logging terminal activity (including input) to a file.

Features
--------
1. **Typing Animation** (`Typer`)
   - `print()` : Mimics `print()` but types out text character-by-character at a configurable rate.
   - `input()` : Mimics `input()` but types the prompt first, also at a configurable rate.

2. **Terminal Animations** (`Animate`)
   - `spinner()` : Displays a rotating ASCII spinner for a given duration, at a configurable rate (spins/sec).
   - `animate()` : Displays a custom frame-based animation for a given duration, at a configurable rate (cycles/sec).

3. **Terminal Management** (`Terminal`)
   - `clear()` : Clears the terminal (cross-platform support).
   - `size()` : Returns the terminal dimensions (columns and rows) as an object with `.columns` and `.rows` attributes.

4. **Flash Text** (`flashtext`)
   - Prints text (optionally typed), waits for a delay, then clears it from the screen.

5. **Logging** (`Logger`)
   - `start(filename, timestamp=False, timestamp_format="%Y-%m-%d_%H-%M-%S")` :
     Starts logging all terminal output and user input to a file.
       - The filename can contain `@timestamp`, which will be replaced with the current time formatted according to `timestamp_format`.
       - To use a literal `@timestamp`, escape it as `@@timestamp`.
     - If `timestamp=True`, each logged line will be prefixed with the current timestamp.
   - `end()` : Stops logging and restores normal terminal behavior.

Custom Exception
----------------
`StdoutoolsError` : Raised when the module encounters an invalid operation, such as an unsupported rate or platform.

Example
-------
```python
from stdoutools import *

# Animated typing
typer.print("Hello, World!", rate=15)
name = typer.input("What is your name? ", rate=12)

# Spinner
animate.spinner(3, message="Loading... ")

# Flash text
flashtext("Hi, ", name, "!")

# Terminal size
print("Width:", terminal.size().columns, "Height:", terminal.size().lines)

# Logging with timestamp in file name
logger.start("session-@timestamp.log", timestamp=True)
typer.print("This will be logged with timestamps.")
logger.end()
```
# Notes:
- Rates for animations are given in **spins per second** (for spinner) or **cycles per second** (for )
- Typing speed is in **characters per second**.
- Logging intercepts both stdout and stdin; user inputs will also be recorded in the log.
"""


# Built-in modules
import builtins
import time
import sys
import os
import shutil
from datetime import datetime

__all__ = [
    'Typer', 'Animate', 'Terminal', 'Logger', 'StdoutoolsError',
    'flashtext', 'typer', 'animate', 'terminal', 'logger'
]

# --------------------- Custom Exception ---------------------

class StdoutoolsError(Exception):
    '''Custom error for the stdoutools module.'''
    def __init__(self, message="") -> None:
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return (
            "Something went wrong in the python module stdoutools.\n"
            + (f"Details:\n{self.message}" if self.message else "")
        )


# --------------------- Typing Animation ---------------------

class Typer:
    '''Typing animation for print() and input().'''

    def print(self, *text, rate: int = 10, sep: str = "", end: str = "\n") -> None:
        '''Typing-style print. `rate` is characters per second.'''
        text = sep.join(map(str, text))
        delay = 1 / rate if rate > 0 else 0

        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
        builtins.print(end=end)

    def input(self, *text, rate: int = 10, sep: str = "", end: str = "") -> str:
        '''Typing-style input prompt. `rate` is characters per second.'''
        text = sep.join(map(str, text))
        delay = 1 / rate if rate > 0 else 0

        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)

        response = builtins.input()
        sys.stdout.write(end)
        sys.stdout.flush()
        return response


# --------------------- Terminal Animations ---------------------

class Animate:
    '''ASCII terminal animations like spinners and frame-based cycles.'''

    def spinner(self, duration: float, rate: int = 2, message: str = "Loading... ") -> None:
        '''Simple spinner animation with message.'''
        phases = ["|", "/", "-", "\\"]
        frames_per_cycle = len(phases)
        total_frames = int(duration * rate * frames_per_cycle)
        delay = 1 / (rate * frames_per_cycle)

        for i in range(total_frames):
            phase = phases[i % frames_per_cycle]
            print(f"\r{message}{phase}", end="", flush=True)
            time.sleep(delay)

        print("\r" + " " * (len(message) + 1), end="\r")

    def animate(self, duration: float, *frames: str, rate: int = 2) -> None:
        '''Frame-based animation.'''
        if not frames:
            frames = ("|", "/", "-", "\\")

        frames_per_cycle = len(frames)
        total_frames = int(duration * rate * frames_per_cycle)
        delay = 1 / (rate * frames_per_cycle)
        max_width = len(max(frames, key=len))

        for i in range(total_frames):
            frame = frames[i % frames_per_cycle]
            print(f"\r{frame}", end="", flush=True)
            time.sleep(delay)

        print("\r" + " " * max_width, end="\r")


# --------------------- Terminal Utilities ---------------------

class Terminal:
    '''Terminal utilities like clear and size.'''

    def clear(self) -> None:
        '''Clear the terminal screen.'''
        os.system('cls' if os.name == 'nt' else 'clear')

    def size(self):
        '''Return terminal size as (columns, rows).'''
        return shutil.get_terminal_size()


# --------------------- Flash Text Function ---------------------

def flashtext(*text, delay: float = 3, typing: bool = False, typerate: int = 10, sep: str = "", end: str = "\n") -> None:
    '''Flash a line of text for a brief duration, then clear it.'''
    text_str = sep.join(map(str, text))

    if typing:
        typer.print(text_str, rate=typerate, end=end)
    elif typing is False:
        sys.stdout.write(text_str)
        sys.stdout.flush()
    else:
        raise StdoutoolsError("The 'typing' parameter for flashtext must be True or False.")

    time.sleep(delay)
    cols = shutil.get_terminal_size().columns
    sys.stdout.write("\r" + " " * cols + "\r")
    sys.stdout.flush()
    print(end=end)


# --------------------- Logger Class ---------------------

class Logger:
    '''Logs terminal output and input to a file, with optional timestamps.'''

    def __init__(self):
        self._original_stdout = sys.stdout
        self._original_input = builtins.input
        self._log_file = None
        self._timestamp_enabled = False
        self._timestamp_format = "%Y-%m-%d_%H-%M-%S"

    def start(self, filename: str, timestamp: bool = False, format: str = "%Y-%m-%d_%H-%M-%S") -> None:
        '''Start logging to a file. Use @timestamp in filename to insert the current time.'''
        if self._log_file:
            raise StdoutoolsError("Logging already started. Call end() before starting again.")

        self._timestamp_enabled = timestamp
        self._timestamp_format = format

        # Handle @timestamp and @@timestamp
        now = datetime.now().strftime(format)
        filename = filename.replace("@@timestamp", "@TEMP_PLACEHOLDER")
        filename = filename.replace("@timestamp", now)
        filename = filename.replace("@TEMP_PLACEHOLDER", "@timestamp")

        try:
            self._log_file = open(filename, 'w', encoding='utf-8')
            sys.stdout = self._Tee(sys.stdout, self._log_file, self._timestamp_enabled, self._timestamp_format)
            builtins.input = self._input_override
        except Exception as e:
            raise StdoutoolsError(f"Failed to start logging to '{filename}': {e}")

    def end(self) -> None:
        '''Stop logging and restore stdout and input.'''
        if not self._log_file:
            raise StdoutoolsError("Logging was not started.")
        sys.stdout = self._original_stdout
        builtins.input = self._original_input
        self._log_file.close()
        self._log_file = None

    def _input_override(self, prompt=""):
        '''Custom input() that logs both prompt and user response.'''
        response = self._original_input(prompt)
        if self._log_file:
            entry = prompt + response
            if self._timestamp_enabled:
                timestamp = datetime.now().strftime(self._timestamp_format)
                entry = f"[{timestamp}] {entry}"
            self._log_file.write(entry + "\n")
            self._log_file.flush()
        return response

    class _Tee:
        '''Writes to multiple streams with optional timestamps.'''
        def __init__(self, *streams, timestamp=False, timestamp_format="%Y-%m-%d_%H-%M-%S"):
            self.streams = streams[:-2]
            self.timestamp = streams[-2]
            self.timestamp_format = streams[-1]

        def write(self, data):
            if self.timestamp and data.strip():
                timestamp = datetime.now().strftime(self.timestamp_format)
                data = f"[{timestamp}] {data}"
            for stream in self.streams:
                stream.write(data)
                stream.flush()

        def flush(self):
            for stream in self.streams:
                stream.flush()


# --------------------- Globals ---------------------

typer = Typer()
animate = Animate()
terminal = Terminal()
logger = Logger()