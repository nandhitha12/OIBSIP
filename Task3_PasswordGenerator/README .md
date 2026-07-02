# Task 3 — Random Password Generator

**OIBSIP | Oasis Infobyte Internship**
**Author:** Nandhitha Reddy

Two versions are included:
- `password_cli.py` — beginner tier, command-line
- `password_gui.py` — advanced tier, GUI with secrets module, strength meter, clipboard

---

## Features

### Beginner tier — `password_cli.py` (all complete)
- [x] Prompts for password length, enforces an 8-character minimum
- [x] Prompts for character types (uppercase, lowercase, numbers, symbols),
      requires at least 2 types selected
- [x] Generates and displays a password matching the chosen criteria
- [x] Input validation — rejects invalid lengths and insufficient type
      selection with a clear message, then re-prompts
- [x] Option to generate another password without restarting

### Advanced tier — `password_gui.py` (all complete)
- [x] GUI window (tkinter) with a length slider and checkboxes for each
      character type
- [x] Uses the `secrets` module (cryptographically secure), not `random`,
      for every random choice — including a Fisher–Yates shuffle built on
      `secrets.randbelow`
- [x] Strength indicator (Weak / Medium / Strong), colour-coded, based on
      length and character diversity
- [x] Guarantees at least one character from each selected type
- [x] "Copy to Clipboard" button using `pyperclip` — also auto-copies the
      password the moment it's generated
- [x] "Exclude ambiguous characters" checkbox (removes 0, O, l, 1, I)
- [x] Generation history — last 5 passwords shown in a list box, kept only
      in memory for the current session (never written to disk, for
      security)

---

## Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   (`secrets`, `tkinter`, and `string` are part of the Python standard
   library — only `pyperclip` needs installing.)

2. **Run the CLI version**
   ```bash
   python password_cli.py
   ```

3. **Run the GUI version**
   ```bash
   python password_gui.py
   ```

## Why `secrets` instead of `random`?
Python's `random` module is a general-purpose pseudo-random number
generator — predictable enough for games or simulations, but not safe for
anything security-related, because its internal state can theoretically be
reconstructed from enough output. `secrets` is designed specifically for
generating tokens, passwords, and keys, drawing from the operating
system's cryptographically secure random source. The GUI version uses
`secrets.choice()` and `secrets.randbelow()` everywhere a password
character or shuffle decision is made.

## Notes on the history feature
The "last 5 passwords" list lives only in a Python list in memory while
the program is running — it is intentionally **not** saved to a file or
database, since persisting plaintext passwords anywhere on disk would be
a security risk. Closing the app clears the history completely.

## Tech stack
`Python`, `random`/`string` (CLI), `secrets`, `tkinter` (GUI), `pyperclip`
(clipboard)
