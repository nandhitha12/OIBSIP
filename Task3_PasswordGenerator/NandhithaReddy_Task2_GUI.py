"""
BMI Calculator — OIBSIP Task 2 (Advanced Tier)
Author: Nandhitha Reddy

A tkinter GUI application that calculates BMI, stores historical records
per named user in an SQLite database, and plots a user's BMI trend over
time using matplotlib.

Feature checklist covered:
  - GUI window (tkinter), no command line
  - Labeled input fields for weight/height + "Calculate" button
  - Colour-coded result feedback (green/blue/orange/red by category)
  - Multi-user support (records saved under a name)
  - Historical records stored in SQLite (bmi_records.db)
  - Graph view: matplotlib line chart of BMI trend over time
  - Error handling for database read/write failures

Run:
    python bmi_gui.py
"""

import sqlite3
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

DB_PATH = "bmi_records.db"

CATEGORY_COLORS = {
    "Underweight": "#3B82F6",  # blue
    "Normal": "#22C55E",       # green
    "Overweight": "#F59E0B",   # orange
    "Obese": "#EF4444",        # red
}


# --------------------------------------------------------------------------
# Database layer
# --------------------------------------------------------------------------
def init_db() -> None:
    """Create the records table if it doesn't already exist."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS bmi_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_name TEXT NOT NULL,
                    weight_kg REAL NOT NULL,
                    height_m REAL NOT NULL,
                    bmi REAL NOT NULL,
                    category TEXT NOT NULL,
                    recorded_at TEXT NOT NULL
                )
                """
            )
    except sqlite3.Error as e:
        messagebox.showerror("Database Error",
                              f"Could not initialize database:\n{e}")


def save_record(user_name: str, weight: float, height: float,
                 bmi: float, category: str) -> bool:
    """Insert a new BMI record. Returns True on success, False on failure."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                """
                INSERT INTO bmi_records
                    (user_name, weight_kg, height_m, bmi, category, recorded_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (user_name, weight, height, bmi, category,
                 datetime.now().isoformat(timespec="seconds")),
            )
        return True
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Could not save record:\n{e}")
        return False


def get_user_history(user_name: str):
    """Return list of (recorded_at, bmi) tuples for a user, oldest first."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute(
                """
                SELECT recorded_at, bmi FROM bmi_records
                WHERE user_name = ?
                ORDER BY recorded_at ASC
                """,
                (user_name,),
            )
            return cursor.fetchall()
    except sqlite3.Error as e:
        messagebox.showerror("Database Error",
                              f"Could not read history:\n{e}")
        return []


# --------------------------------------------------------------------------
# BMI logic (shared with the CLI version)
# --------------------------------------------------------------------------
def classify_bmi(bmi: float) -> str:
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"


def calculate_bmi(weight_kg: float, height_m: float) -> float:
    return weight_kg / (height_m ** 2)


# --------------------------------------------------------------------------
# GUI application
# --------------------------------------------------------------------------
class BMIApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BMI Calculator")
        self.geometry("420x480")
        self.resizable(False, False)
        self.configure(bg="#F3F4F6")

        init_db()
        self._build_widgets()

    def _build_widgets(self) -> None:
        pad = {"padx": 12, "pady": 6}

        title = tk.Label(self, text="BMI Calculator", font=("Segoe UI", 18, "bold"),
                          bg="#F3F4F6")
        title.pack(pady=(16, 8))

        form = tk.Frame(self, bg="#F3F4F6")
        form.pack(**pad)

        tk.Label(form, text="Name:", bg="#F3F4F6", width=10, anchor="w").grid(row=0, column=0, sticky="w", pady=4)
        self.name_entry = ttk.Entry(form, width=22)
        self.name_entry.grid(row=0, column=1, pady=4)

        tk.Label(form, text="Weight (kg):", bg="#F3F4F6", width=10, anchor="w").grid(row=1, column=0, sticky="w", pady=4)
        self.weight_entry = ttk.Entry(form, width=22)
        self.weight_entry.grid(row=1, column=1, pady=4)

        tk.Label(form, text="Height (m):", bg="#F3F4F6", width=10, anchor="w").grid(row=2, column=0, sticky="w", pady=4)
        self.height_entry = ttk.Entry(form, width=22)
        self.height_entry.grid(row=2, column=1, pady=4)

        calc_btn = tk.Button(self, text="Calculate", command=self.on_calculate,
                              bg="#4F46E5", fg="white", font=("Segoe UI", 11, "bold"),
                              relief="flat", padx=12, pady=6, cursor="hand2")
        calc_btn.pack(pady=(10, 4))

        self.result_frame = tk.Frame(self, bg="#F3F4F6")
        self.result_frame.pack(pady=8, fill="x", padx=20)

        self.result_label = tk.Label(self.result_frame, text="", font=("Segoe UI", 14, "bold"),
                                      bg="#E5E7EB", fg="#111827", pady=10)
        self.result_label.pack(fill="x")

        graph_btn = tk.Button(self, text="View BMI Trend", command=self.on_view_trend,
                               bg="#10B981", fg="white", font=("Segoe UI", 10, "bold"),
                               relief="flat", padx=10, pady=6, cursor="hand2")
        graph_btn.pack(pady=(6, 4))

        info = tk.Label(self, text="Enter your name to save & track results over time.",
                         bg="#F3F4F6", fg="#6B7280", font=("Segoe UI", 8))
        info.pack(pady=(4, 0))

    # ----------------------------------------------------------------
    def on_calculate(self) -> None:
        name = self.name_entry.get().strip()
        weight_raw = self.weight_entry.get().strip()
        height_raw = self.height_entry.get().strip()

        # --- validation ---
        try:
            weight = float(weight_raw)
            height = float(height_raw)
        except ValueError:
            messagebox.showerror("Invalid Input",
                                  "Weight and height must be numbers.")
            return

        if weight <= 0 or height <= 0:
            messagebox.showerror("Invalid Input",
                                  "Weight and height must be positive numbers.")
            return

        bmi = calculate_bmi(weight, height)
        category = classify_bmi(bmi)
        color = CATEGORY_COLORS[category]

        self.result_label.config(
            text=f"BMI: {bmi:.2f}  —  {category}",
            bg=color,
            fg="white",
        )

        if name:
            save_record(name, weight, height, bmi, category)
        else:
            messagebox.showinfo("Not Saved",
                                 "Enter a name to save this result to your history.")

    # ----------------------------------------------------------------
    def on_view_trend(self) -> None:
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showinfo("Name Required",
                                 "Enter a name first to view that user's BMI trend.")
            return

        history = get_user_history(name)
        if not history:
            messagebox.showinfo("No Data",
                                 f"No saved records found for '{name}' yet.")
            return

        TrendWindow(self, name, history)


class TrendWindow(tk.Toplevel):
    """Popup window showing a matplotlib line chart of BMI over time."""

    def __init__(self, parent, user_name: str, history):
        super().__init__(parent)
        self.title(f"BMI Trend — {user_name}")
        self.geometry("560x420")

        dates = [row[0][:10] for row in history]  # just the date part
        bmis = [row[1] for row in history]

        fig = Figure(figsize=(5.5, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(dates, bmis, marker="o", color="#4F46E5")
        ax.set_title(f"BMI Trend for {user_name}")
        ax.set_xlabel("Date")
        ax.set_ylabel("BMI")
        ax.axhspan(18.5, 25, color="green", alpha=0.08)  # normal range band
        fig.autofmt_xdate(rotation=45)

        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)


if __name__ == "__main__":
    app = BMIApp()
    app.mainloop()
