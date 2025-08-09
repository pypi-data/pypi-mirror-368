# ASDFGH - Colorful Terminal Clock

A Python library that displays a continuously updating colored clock in your terminal.

## Installation

```bash
pip install ASDFGH
```

## Usage

```python
from ASDFGH import ColorClock

# Basic usage
clock = ColorClock()
clock.display()  # Press Ctrl+C to stop

# With options
clock = ColorClock(colored=False, military_time=True, show_date=True)
clock.display()
```

## Features

- Continuously updates in the same line
- Random colors (can be disabled)
- Supports 12/24 hour format
- Optional date display
- Graceful keyboard interrupt handling