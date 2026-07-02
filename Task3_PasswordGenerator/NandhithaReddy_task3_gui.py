"""
Random Password Generator — OIBSIP Task 3 (Advanced Tier)
Author: Nandhitha Reddy

A tkinter GUI password generator using the `secrets` module (cryptographically
secure) instead of `random`. Includes a length slider, character-type
checkboxes, an ambiguous-character exclusion option, a strength indicator,
one-click clipboard copy, and an in-session history of the last 5 passwords.

Feature checklist covered:
  - GUI with slider for length + checkboxes for character types
  - secrets module used for all randomness (not random)
  - Password strength indicator (Weak / Medium / Strong)
  - Guarantees at least one character from each selected type
  - "Copy to Clipboard" button using pyperclip
  - Exclude ambiguous characters option (0, O, l, 1, I)
  - Generation history: last 5 passwords, in-memory only (not saved to disk)

Run:
    python password_gui.py
"""

import secrets
import string
import tkinter as tk
from tkinter import messagebox, ttk

try:
    import pyperclip
except ImportError:
    pyperclip = None

AMBIGUOUS_CHARS = "0O l1I".replace(" ", "")  # 0, O, l, 1, I
SYMBOLS = "!@#$%^&*()-_=+[]{}"

STRENGTH_COLORS = {
    "Weak": "#EF4444",
    "Medium": "#F59E0B",
    "Strong": "#22C55E",
}


def build_pool(use_upper, use_lower, use_digits, use_symbols, exclude_ambiguous) -> str:
    pool = ""
    if use_upper:
        pool += string.ascii_uppercase
    if use_lower:
        pool += string.ascii_lowercase
    if use_digits:
        pool += string.digits
    if use_symbols:
        pool += SYMBOLS

    if exclude_ambiguous:
        pool = "".join(c for c in pool if c not in AMBIGUOUS_CHARS)

    return pool


def generate_password(length: int, use_upper, use_lower, use_digits,
                       use_symbols, exclude_ambiguous) -> str:
    """
    Generate a cryptographically secure password using `secrets`.
    Guarantees at least one character from each selected type.
    """
    pool = build_pool(use_upper, use_lower, use_digits, use_symbols, exclude_ambiguous)
    if not pool:
        raise ValueError("No character types selected.")

    def filtered(charset: str) -> str:
        if exclude_ambiguous:
            charset = "".join(c for c in charset if c not in AMBIGUOUS_CHARS)
        return charset

    guaranteed = []
    if use_upper:
        charset = filtered(string.ascii_uppercase)
        if charset:
            guaranteed.append(secrets.choice(charset))
    if use_lower:
        charset = filtered(string.ascii_lowercase)
        if charset:
            guaranteed.append(secrets.choice(charset))
    if use_digits:
        charset = filtered(string.digits)
        if charset:
            guaranteed.append(secrets.choice(charset))
    if use_symbols:
        charset = filtered(SYMBOLS)
        if charset:
            guaranteed.append(secrets.choice(charset))

    remaining = max(0, length - len(guaranteed))
    rest = [secrets.choice(pool) for _ in range(remaining)]

    chars = guaranteed + rest
    # cryptographically secure shuffle (Fisher-Yates using secrets)
    for i in range(len(chars) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        chars[i], chars[j] = chars[j], chars[i]

    return "".join(chars[:length]) if len(chars) > length else "".join(chars)


def rate_strength(password: str) -> str:
    """
    Simple strength heuristic based on length and character diversity.
    Not a substitute for a full entropy calculation, but good enough for
    a visual indicator.
    """
    length_score = 0
    if len(password) >= 12:
        length_score = 2
    elif len(password) >= 8:
        length_score = 1

    diversity = sum([
        any(c.isupper() for c in password),
        any(c.islower() for c in password),
        any(c.isdigit() for c in password),
        any(c in SYMBOLS for c in password),
    ])

    score = length_score + diversity
    if score <= 2:
        return "Weak"
    elif score <= 4:
        return "Medium"
    else:
        return "Strong"


class PasswordApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Password Generator")
        self.geometry("440x600")
        self.resizable(False, False)
        self.configure(bg="#F3F4F6")

        self.history = []  # last 5 generated passwords (in-memory only)

        self._build_widgets()

    def _build_widgets(self) -> None:
        tk.Label(self, text="Password Generator", font=("Segoe UI", 18, "bold"),
                  bg="#F3F4F6").pack(pady=(16, 8))

        # --- length slider ---
        length_frame = tk.Frame(self, bg="#F3F4F6")
        length_frame.pack(pady=6, padx=20, fill="x")
        tk.Label(length_frame, text="Password length:", bg="#F3F4F6").pack(anchor="w")
        self.length_var = tk.IntVar(value=12)
        self.length_label = tk.Label(length_frame, text="12", bg="#F3F4F6", font=("Segoe UI", 10, "bold"))
        self.length_label.pack(anchor="e")
        length_slider = tk.Scale(length_frame, from_=8, to=32, orient="horizontal",
                                  variable=self.length_var, bg="#F3F4F6",
                                  command=self._on_length_change, showvalue=False)
        length_slider.pack(fill="x")

        # --- character type checkboxes ---
        types_frame = tk.LabelFrame(self, text="Character types", bg="#F3F4F6", padx=10, pady=8)
        types_frame.pack(pady=10, padx=20, fill="x")

        self.upper_var = tk.BooleanVar(value=True)
        self.lower_var = tk.BooleanVar(value=True)
        self.digits_var = tk.BooleanVar(value=True)
        self.symbols_var = tk.BooleanVar(value=True)
        self.exclude_ambiguous_var = tk.BooleanVar(value=False)

        tk.Checkbutton(types_frame, text="Uppercase (A-Z)", variable=self.upper_var, bg="#F3F4F6").pack(anchor="w")
        tk.Checkbutton(types_frame, text="Lowercase (a-z)", variable=self.lower_var, bg="#F3F4F6").pack(anchor="w")
        tk.Checkbutton(types_frame, text="Numbers (0-9)", variable=self.digits_var, bg="#F3F4F6").pack(anchor="w")
        tk.Checkbutton(types_frame, text="Symbols (!@#$...)", variable=self.symbols_var, bg="#F3F4F6").pack(anchor="w")
        tk.Checkbutton(types_frame, text="Exclude ambiguous characters (0, O, l, 1, I)",
                        variable=self.exclude_ambiguous_var, bg="#F3F4F6").pack(anchor="w", pady=(6, 0))

        # --- generate button ---
        tk.Button(self, text="Generate Password", command=self.on_generate,
                   bg="#4F46E5", fg="white", font=("Segoe UI", 11, "bold"),
                   relief="flat", padx=12, pady=8, cursor="hand2").pack(pady=(6, 4))

        # --- result display ---
        self.result_var = tk.StringVar(value="")
        result_entry = tk.Entry(self, textvariable=self.result_var, font=("Consolas", 13),
                                  justify="center", state="readonly", readonlybackground="#E5E7EB")
        result_entry.pack(pady=(6, 4), padx=20, fill="x")

        self.strength_label = tk.Label(self, text="", font=("Segoe UI", 10, "bold"), bg="#F3F4F6")
        self.strength_label.pack(pady=(0, 6))

        tk.Button(self, text="Copy to Clipboard", command=self.on_copy,
                   bg="#10B981", fg="white", relief="flat", padx=10, pady=6,
                   cursor="hand2").pack(pady=(0, 10))

        # --- history ---
        tk.Label(self, text="Last 5 passwords (this session only):",
                  bg="#F3F4F6", font=("Segoe UI", 9)).pack(anchor="w", padx=20)
        self.history_box = tk.Listbox(self, height=5, font=("Consolas", 10))
        self.history_box.pack(pady=(4, 10), padx=20, fill="x")

    def _on_length_change(self, value) -> None:
        self.length_label.config(text=str(value))

    def on_generate(self) -> None:
        length = self.length_var.get()
        use_upper = self.upper_var.get()
        use_lower = self.lower_var.get()
        use_digits = self.digits_var.get()
        use_symbols = self.symbols_var.get()
        exclude_ambiguous = self.exclude_ambiguous_var.get()

        selected_count = sum([use_upper, use_lower, use_digits, use_symbols])
        if selected_count < 2:
            messagebox.showerror("Invalid Selection",
                                  "Please select at least 2 character types.")
            return

        try:
            password = generate_password(length, use_upper, use_lower,
                                          use_digits, use_symbols, exclude_ambiguous)
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return

        self.result_var.set(password)

        strength = rate_strength(password)
        self.strength_label.config(text=f"Strength: {strength}",
                                    fg=STRENGTH_COLORS[strength])

        # update history (last 5, newest first, in-memory only)
        self.history.insert(0, password)
        self.history = self.history[:5]
        self.history_box.delete(0, tk.END)
        for pw in self.history:
            self.history_box.insert(tk.END, pw)

        # auto-copy on generation, per the feature checklist
        self._copy_to_clipboard(password, silent=True)

    def on_copy(self) -> None:
        password = self.result_var.get()
        if not password:
            messagebox.showinfo("Nothing to Copy", "Generate a password first.")
            return
        self._copy_to_clipboard(password, silent=False)

    def _copy_to_clipboard(self, text: str, silent: bool) -> None:
        if pyperclip is None:
            if not silent:
                messagebox.showwarning("Clipboard Unavailable",
                                        "Install pyperclip to enable clipboard copying:\n"
                                        "pip install pyperclip")
            return
        try:
            pyperclip.copy(text)
            if not silent:
                messagebox.showinfo("Copied", "Password copied to clipboard.")
        except Exception as e:
            if not silent:
                messagebox.showerror("Clipboard Error", f"Could not copy password:\n{e}")


if __name__ == "__main__":
    app = PasswordApp()
    app.mainloop()
