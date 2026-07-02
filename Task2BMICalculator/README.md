# Task 2 — BMI Calculator

**OIBSIP | Oasis Infobyte Internship**
**Author:** Nandhitha Reddy

Two versions are included:
- `bmi_cli.py` — beginner tier, command-line
- `bmi_gui.py` — advanced tier, GUI with history + trend chart

---

## Features

### Beginner tier — `bmi_cli.py` (all complete)
- [x] Prompts for weight (kg) and height (m) via command line
- [x] Calculates BMI = weight / height²
- [x] Classifies into Underweight / Normal / Overweight / Obese
- [x] Displays BMI rounded to 2 decimal places, with category
- [x] Input validation — rejects non-numeric and non-positive input with a
      clear error message, then re-prompts (never crashes)

### Advanced tier — `bmi_gui.py` (all complete)
- [x] GUI window built with `tkinter` — no command line
- [x] Labeled input fields (Name, Weight, Height) + "Calculate" button
- [x] Colour-coded result box (blue/green/orange/red by category)
- [x] Multi-user support — records saved under whatever name you type
- [x] Historical records stored in an SQLite database (`bmi_records.db`,
      created automatically on first run)
- [x] "View BMI Trend" button opens a matplotlib line chart of that user's
      BMI history over time, with the healthy range (18.5–25) shaded
- [x] Error handling for database read/write failures (wrapped in
      try/except, shown as a message box instead of crashing)

---

## Setup

1. **Install dependencies** (tkinter and sqlite3 ship with Python already,
   only matplotlib needs installing):
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the CLI version**
   ```bash
   python bmi_cli.py
   ```

3. **Run the GUI version**
   ```bash
   python bmi_gui.py
   ```
   This creates `bmi_records.db` in the same folder the first time you run
   it — that's your local database, no setup needed.

## How to use the GUI
1. Type a name (used to group your history — e.g. your own name).
2. Enter weight in kg and height in m (e.g. `1.70`, not `170`).
3. Click **Calculate** — result box shows your BMI and category, colour-coded.
4. Click **View BMI Trend** to see a line chart of all your past entries
   for that name.

## Notes
- Height must be in **meters**, not centimeters (e.g. 5'7" ≈ 1.70 m).
- If you leave the Name field blank, the result still calculates but isn't
  saved to history — a message box will let you know.
- `bmi_records.db` will appear in your project folder after your first
  save; you can open it with any SQLite browser (e.g. "DB Browser for
  SQLite") if you want to inspect the raw data.

## Tech stack
`Python`, `input()` (CLI), `tkinter` (GUI), `sqlite3` (storage),
`matplotlib` (trend chart)
