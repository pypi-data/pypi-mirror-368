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

    stats = stats[:max(0, width)]
    hint = hint[:max(0, width)]

    # Top title (centered)
    stdscr.attron(curses.color_pair(1))
    try:
        title = " Typetest "
        x = max(0, (width - len(title)) // 2)
        stdscr.addstr(0, x, title[:max(0, width)])
    except curses.error:
        pass
    stdscr.attroff(curses.color_pair(1))

    # Bottom stats (left)
    stdscr.attron(curses.color_pair(2))
    try:
        if height > 0:
            stdscr.addstr(height - 1, 0, stats)
    except curses.error:
        pass
    stdscr.attroff(curses.color_pair(2))

    # Bottom hint (right)
    stdscr.attron(curses.color_pair(1))
    try:
        if width >= len(hint) and height > 0:
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
    try:
        stdscr.addstr(y, x, message[:max(0, width)])
    except curses.error:
        pass
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
        # read at cursor (end of the prompt)
        word_count = int(stdscr.getstr().decode("utf-8"))
    except ValueError:
        return
    curses.noecho()

    # Guard against requesting more words than exist
    word_count = max(1, min(word_count, len(words)))

    selected_words = random.sample(words, word_count)
    sample_text = " ".join(selected_words)

    input_str = ""
    start_time = time.time()

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        usable_height = max(0, height - 1)  # keep last row for status bar

        # Metrics
        correct = sum(1 for i, c in enumerate(input_str) if i < len(sample_text) and c == sample_text[i])
        incorrect = len(input_str) - correct
        elapsed = max(time.time() - start_time, 1e-9)
        accuracy = (correct / len(input_str)) * 100 if input_str else 0.0
        wpm = (len(input_str) / 5) / (elapsed / 60) if input_str else 0.0

        draw_bars(stdscr, wpm, accuracy, correct, incorrect)

        # Wrap sample text to screen width
        lines_to_display = []
        current_line = ""
        for word in sample_text.split():
            add_len = len(word) + (1 if current_line else 0)
            if len(current_line) + add_len > max(1, width):
                lines_to_display.append(current_line)
                current_line = word
            else:
                current_line = f"{current_line} {word}".strip()
        if current_line:
            lines_to_display.append(current_line)

        # Print sample text starting at row 3
        top_text_row = 3
        for i, line in enumerate(lines_to_display):
            row = top_text_row + i
            if row >= usable_height:
                break
            try:
                stdscr.addstr(row, 0, line[:max(0, width)])
            except curses.error:
                pass

        # Separator line between sample text and input area
        sep_row = top_text_row + len(lines_to_display) + 1
        if sep_row < usable_height:
            try:
                stdscr.hline(sep_row, 0, curses.ACS_HLINE, max(0, width))
            except curses.error:
                pass

        # "Type here:" label
        label_row = sep_row + 2
        if label_row < usable_height:
            try:
                stdscr.addstr(label_row, 0, "Type here:")
            except curses.error:
                pass

        # Draw user input with wrapping and coloring
        input_row_start = label_row + 1
        if input_row_start < usable_height and width > 0:
            for i, ch in enumerate(input_str):
                if i >= len(sample_text):
                    break

                target_row = input_row_start + (i // width)
                target_col = i % width

                if target_row >= usable_height:
                    break  # don't draw off bottom (status bar)

                color = 3 if ch == sample_text[i] else 4
                stdscr.attron(curses.color_pair(color))
                try:
                    stdscr.addch(target_row, target_col, ch)
                except curses.error:
                    pass
                finally:
                    stdscr.attroff(curses.color_pair(color))

        stdscr.refresh()

        # Completion
        if len(input_str) >= len(sample_text):
            break

        # Input handling
        ch = stdscr.get_wch()
        if isinstance(ch, str) and ch.isprintable():
            input_str += ch
        elif ch in ("\b", "\x7f") or ch == curses.KEY_BACKSPACE:
            if input_str:
                input_str = input_str[:-1]
        elif ch == "\x1b":  # ESC
            if confirm_exit(stdscr):
                return

    # Save stats to CSV
    try:
        with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                time.strftime("%Y-%m-%d %H:%M:%S"),
                word_count,
                f"{wpm:.2f}",
                f"{accuracy:.2f}",
                correct,
                incorrect
            ])
    except OSError:
        pass  # fail silently if logging isn't possible

    done_row = input_row_start + (max(len(input_str), 1) - 1) // max(1, width) + 2
    done_row = min(done_row, usable_height - 1)
    try:
        stdscr.addstr(done_row, 0, "Test complete! Press any key to exit.")
    except curses.error:
        pass
    stdscr.getch()

def main():
    curses.wrapper(run)

def run(stdscr):
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)   # Title & hint
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Stats
    curses.init_pair(3, curses.COLOR_GREEN, -1)                  # Correct
    curses.init_pair(4, curses.COLOR_RED, -1)                    # Incorrect
    start_test(stdscr)

if __name__ == "__main__":
    main()
