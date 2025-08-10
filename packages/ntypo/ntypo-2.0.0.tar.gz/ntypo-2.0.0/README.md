# Ntypo - Yet Another Typing Test

**Ntypo** is a minimal terminal-based typing speed test built with Python and `ncurses`.

It lets you challenge yourself to type a custom number of randomly selected words from a list, no distractions, no GUI fluff. Just you, your keyboard, and the clock.

## Features

- Choose how many words you want to type (e.g. 30, 50, 100…)
- Loads words from an external file (`words.txt`)
- Measures WPM (Words Per Minute)
- Tracks accuracy, correct and incorrect keystrokes
- ESC to quit anytime (with confirmation)
- Saves session logs to CSV (`ntypo.csv`)
- Adaptive layout with top/bottom bars
- Fully keyboard-driven and terminal-native

## Installation

Install via pip:

```bash
pip install ntypo
```

Then run the app:
```bash
ntypo
```

To install from source:

```bash
git clone https://github.com/bearenbey/ntypo.git
cd ntypo
pip install .
```

## Dependencies:

- Python 3.8 or higher
- A terminal that supports ncurses

## Usage

1. Launch the app in your terminal
2. Enter how many words you want to practice
3. Type the displayed text — your speed and stats will be tracked
4. Press ESC anytime to quit (confirmation popup included)

Keybindings:

- Type normally: your input is tracked in real time
- Backspace: delete last character
- ESC: open quit confirmation
- Any key: dismiss the end-of-test message

The app adjusts to terminal size and wraps text dynamically. All results are saved to ntypo.csv.

## Words File

The app uses a simple plaintext file (words.txt) where each line is a word:

```bash
apple
orange
keyboard
syntax
...
```
You can modify this list or swap it out for your own vocabulary.

## License

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see https://www.gnu.org/licenses/.

© 2025 Eren Öğrül — termapp@pm.me