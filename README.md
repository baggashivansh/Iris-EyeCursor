# Iris-EyeCursor

---

````markdown
# Iris - Animated Eye Tray App for macOS

**Author:** Shivansh Bagga

Iris is a fun macOS tray application that displays two cartoon eyes which follow your mouse cursor in real-time. The eyes can blink randomly and enter a "sleepy mode" after inactivity.  

---

## Features

- Floating tray icon in the menu bar
- Smooth pupil tracking following your mouse
- Random blinking
- Sleepy mode after inactivity
- Configurable refresh rate and behavior via `config.json`

---

## Requirements

- macOS
- Python 3.13+ (tested)
- PyQt5
- PyObjC

---

## Installation

1. Clone the repository or copy the files to your local machine:

```bash
git clone this repo
cd Iris
````

2. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install PyQt5 pyobjc
```

---

## Running the App Manually

From the project root directory:

```bash
python app/iris.py
```

> The tray icon should appear in the macOS menu bar. Click the icon for options or to quit.

Optional: Run via a root-level `main.py`:

```python
from app.iris import IrisTray
from PyQt5 import QtWidgets
import sys

app = QtWidgets.QApplication(sys.argv)
tray = IrisTray(app)
sys.exit(app.exec_())
```

Then run:

```bash
python main.py
```

---

## Configuration

* `config.json` stores your preferences such as:

  * `random_blink`: `true/false`
  * `sleepy_mode`: `true/false`
  * `refresh_rate`: in milliseconds

Default config is generated automatically if it does not exist.

---

## Icon

Make sure the tray icon exists at:

```
assets/iris_icon.png
```

For building a macOS `.app` using `py2app`, an `.icns` icon is required at:

```
assets/iris_icon.icns
```

---

## Author

**Shivansh Bagga**

---
---
