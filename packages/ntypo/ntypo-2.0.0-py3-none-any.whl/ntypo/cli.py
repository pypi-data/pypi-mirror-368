# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# © 2025 Eren Öğrül - termapp@pm.me

import curses
import time
import random
import os
import csv

WORDS_FILE = os.path.join(os.path.dirname(__file__), "words.txt")
LOG_FILE = os.path.join(os.path.dirname(__file__), "ntypo.csv")

def load_words():
    with open(WORDS_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def draw_bars(stdscr, wpm, accuracy, correct, incorrect):
    height, width = stdscr.getmaxyx()
    stats = f"WPM: {wpm:.2f} | Accuracy: {accuracy:.2f}% | Correct: {correct} | Wrong: {incorrect}"
    hint = "[ Press ESC to quit ]"

    stats = stats[:width]
    hint = hint[:width]

    # Draw top bar (centered)
    stdscr.attron(curses.color_pair(1))
    try:
        title = " Typetest "
        x = max(0, (width - len(title)) // 2)
        stdscr.addstr(0, x, title[:width])
    except curses.error:
        pass
    stdscr.attroff(curses.color_pair(1))

    # Draw bottom stats (left)
    stdscr.attron(curses.color_pair(2))
    try:
        stdscr.addstr(height - 1, 0, stats)
    except curses.error:
        pass
    stdscr.attroff(curses.color_pair(2))

    # Draw ESC hint (right)
    stdscr.attron(curses.color_pair(1))
    try:
        if width >= len(hint):
            x = max(0, width - len(hint))
            stdscr.addstr(height - 1, x, hint)
    except curses.error:
        pass
    stdscr.attroff(curses.color_pair(1))

def confirm_exit(stdscr):
    height, width = stdscr.getmaxyx()
    message = "Exit without finishing? (y/n)"
    x = max(0, (width - len(message)) // 2)
    y = max(1, height // 2)
    stdscr.attron(curses.color_pair(1))
    stdscr.addstr(y, x, message)
    stdscr.attroff(curses.color_pair(1))
    stdscr.refresh()
    ch = stdscr.getch()
    return ch in [ord('y'), ord('Y')]

def start_test(stdscr):
    words = load_words()

    curses.curs_set(1)
    stdscr.clear()
    stdscr.refresh()
    stdscr.addstr(2, 2, "How many words? ")
    curses.echo()
    try:
        word_count = int(stdscr.getstr().decode("utf-8"))
    except ValueError:
        return
    curses.noecho()

    selected_words = random.sample(words, word_count)
    sample_text = " ".join(selected_words)

    input_str = ""
    start_time = time.time()

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # Debug statement to check terminal size
        stdscr.addstr(0, 0, f"Height: {height}, Width: {width}")
        stdscr.refresh()

        correct = sum(1 for i, c in enumerate(input_str) if i < len(sample_text) and c == sample_text[i])
        incorrect = len(input_str) - correct
        elapsed = max(time.time() - start_time, 1)
        accuracy = (correct / len(input_str)) * 100 if input_str else 0
        wpm = (len(input_str) / 5) / (elapsed / 60) if input_str else 0

        draw_bars(stdscr, wpm, accuracy, correct, incorrect)

        # Text to type (with word wrap)
        lines_to_display = []
        current_line = ""
        for word in sample_text.split():
            if len(current_line) + len(word) + 1 > width:
                lines_to_display.append(current_line)
                current_line = word
            else:
                if current_line:
                    current_line += " " + word
                else:
                    current_line = word
        lines_to_display.append(current_line)

        for i, line in enumerate(lines_to_display):
            if i < height - 1:
                stdscr.addstr(3 + i, 0, line)

        stdscr.hline(4 + len(lines_to_display), 0, curses.ACS_HLINE, width)
        stdscr.addstr(6 + len(lines_to_display), 0, "Type here:")

        # Colored user input with wrapping (character by character)
        for i, ch in enumerate(input_str):
            if i < len(sample_text):
                if i < height - 1:
                    if ch == sample_text[i]:
                        stdscr.attron(curses.color_pair(3))  # Green for correct
                    else:
                        stdscr.attron(curses.color_pair(4))  # Red for incorrect
                    stdscr.addch(7 + len(lines_to_display), i % width, ch)
                    stdscr.attroff(curses.color_pair(3) if ch == sample_text[i] else curses.color_pair(4))

        stdscr.refresh()

        if len(input_str) >= len(sample_text):
            break

        ch = stdscr.get_wch()
        if isinstance(ch, str) and ch.isprintable():
            input_str += ch
        elif ch == "\x7f":  # Backspace
            input_str = input_str[:-1]
        elif ch == "\x1b":  # ESC
            if confirm_exit(stdscr):
                return

    # Save stats to CSV
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), word_count, f"{wpm:.2f}", f"{accuracy:.2f}", correct, incorrect])

    stdscr.addstr(9 + len(lines_to_display), 0, "Test complete! Press any key to exit.")
    stdscr.getch()

def main():
    curses.wrapper(run)

def run(stdscr):
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)     # Top & hint bar
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)    # Stats
    curses.init_pair(3, curses.COLOR_GREEN, -1)                    # Correct typed
    curses.init_pair(4, curses.COLOR_RED, -1)                      # Incorrect typed
    start_test(stdscr)

if __name__ == "__main__":
    main()