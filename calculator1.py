import tkinter
import math
import re

# ----------------------------
# Layout (6 rows x 4 columns)
# ----------------------------
button_values = [
    ["AC", "⌫", "%", "÷"],
    ["7", "8", "9", "×"],
    ["4", "5", "6", "-"],
    ["1", "2", "3", "+"],
    ["0", ".", "(", ")"],
    ["√", "x²", "+/-", "="]
]

# Styling groups
right_symbols = ["÷", "×", "-", "+", "=", "√", "x²"]
top_symbols = ["AC", "⌫", "%"]
bottom_symbols = ["."]
row_count = len(button_values)
column_count = len(button_values[0])

# Colors
color_pink = "#F442D0"
color_purple = "#8304F3"
color_dark_gray = "#505050"
color_green = "#00FFCC"
color_white = "white"
color_black = "black"

# ----------------------------
# Window & Display
# ----------------------------
window = tkinter.Tk()
window.title("Calculator")
window.resizable(False, False)

frame = tkinter.Frame(window)
label = tkinter.Label(frame, text="0", font=("Arial", 45), background=color_black,
                      foreground=color_white, anchor="e", width=column_count)
label.grid(row=0, column=0, columnspan=column_count, sticky="we")

# ----------------------------
# Helpers: format & evaluate
# ----------------------------
def format_expression(expr: str) -> str:
    """
    Convert the user-friendly expression (with √, ×, ÷, x², %) into a valid
    Python expression using math.sqrt, *, /, **2, etc.
    """
    if not expr:
        return ""

    # Replace operator symbols for python
    expr = expr.replace("×", "*").replace("÷", "/")
    # Replace square operator (x²) with **2
    expr = expr.replace("x²", "**2")
    # Replace '√(' with 'math.sqrt(' (handles cases like √(9+16))
    expr = expr.replace("√(", "math.sqrt(")
    # Replace occurrences like √9  -> math.sqrt(9)
    expr = re.sub(r"√\s*([0-9]+(?:\.[0-9]+)?)", r"math.sqrt(\1)", expr)
    # Replace percent 50% -> (50/100)
    expr = re.sub(r"([0-9]+(?:\.[0-9]+)?)\%", r"(\1/100)", expr)

    return expr

def format_result(res):
    # Round floats to reasonable precision and strip .0 when integer
    if isinstance(res, float):
        res = round(res, 10)  # avoid messy floating point tails
        if res.is_integer():
            res = int(res)
    return str(res)

def safe_eval(expr: str):
    """
    Evaluate formatted expression using a restricted eval environment.
    math functions are available via 'math'.
    """
    try:
        # restrict builtins, provide only math module
        result = eval(expr, {"__builtins__": None}, {"math": math})
        return result
    except Exception:
        raise

# ----------------------------
# Actions: clear, backspace, toggle sign, evaluate
# ----------------------------
def clear_all():
    label["text"] = "0"

def backspace():
    s = label["text"]
    if not s or s == "0":
        label["text"] = "0"
        return

    # If ends with special two-character token "x²", remove both
    if s.endswith("x²"):
        label["text"] = s[:-2] or "0"
    else:
        # Remove last character
        new = s[:-1]
        label["text"] = new if new else "0"

def toggle_sign():
    s = label["text"]
    if not s or s == "0":
        label["text"] = "0"
        return

    # Find start index of last numeric token
    # We consider operators + - × ÷ * / and parentheses as separators
    sep_match = re.search(r"[+\-×÷*/()]$", s)
    if sep_match:
        # last char is an operator; nothing to toggle
        return

    # Find index of last operator (one of + - × ÷ * /)
    last_op_match = None
    for m in re.finditer(r"[+\-×÷*/]", s):
        last_op_match = m
    if last_op_match:
        idx = last_op_match.end()
        token = s[idx:]
        prefix = s[:idx]
    else:
        token = s
        prefix = ""

    # If token already wrapped as negative like (-12), unwrap
    if token.startswith("(-") and token.endswith(")"):
        new_token = token[2:-1]
    else:
        new_token = f"(-{token})"

    label["text"] = prefix + new_token

def evaluate_expression():
    expr = label["text"]
    if not expr:
        return
    # Replace any trailing operator with nothing (prevent eval errors)
    if expr[-1] in "+-×÷*/":
        # ignore trailing operator
        expr = expr[:-1]

    formatted = format_expression(expr)
    try:
        res = safe_eval(formatted)
        label["text"] = format_result(res)
    except Exception:
        label["text"] = "Error"

# ----------------------------
# Button click handler
# ----------------------------
def button_clicked(value):
    cur = label["text"]
    # If label shows Error, reset when user starts typing
    if cur == "Error" and value not in ("AC", "⌫"):
        cur = "0"
        label["text"] = cur

    if value == "AC":
        clear_all()
        return
    if value == "⌫":
        backspace()
        return
    if value == "=":
        evaluate_expression()
        return
    if value == "+/-":
        toggle_sign()
        return

    # Append or replace depending on current display
    # If current is "0" and adding a digit -> replace
    if cur == "0":
        if value in "0123456789":
            label["text"] = value
            return
        elif value == ".":
            label["text"] = "0."
            return
        else:
            # append operator/symbol after 0
            if value in right_symbols or value in ("(", ")"):
                label["text"] = cur + value
                return

    # Normal append
    label["text"] = cur + value

# ----------------------------
# Create buttons grid
# ----------------------------
for r in range(row_count):
    for c in range(column_count):
        try:
            value = button_values[r][c]
        except IndexError:
            # if a row is shorter, skip
            continue

        btn = tkinter.Button(frame, text=value, font=("Arial", 28),
                             width=5, height=1,
                             command=lambda v=value: button_clicked(v))

        if value in top_symbols:
            btn.config(foreground=color_black, background=color_pink)
        elif value in right_symbols:
            btn.config(foreground=color_white, background=color_green)
        elif value in bottom_symbols:
            btn.config(foreground=color_black, background=color_purple)
        else:
            btn.config(foreground=color_white, background=color_dark_gray)

        btn.grid(row=r+1, column=c, sticky="nsew", padx=2, pady=2)

# Make columns expand evenly (nice layout)
for i in range(column_count):
    frame.grid_columnconfigure(i, weight=1)

frame.pack(padx=8, pady=8, expand=True, fill="both")

# Center the window on screen
window.update_idletasks()
window_width = window.winfo_width()
window_height = window.winfo_height()
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
window_x = int((screen_width / 2) - (window_width / 2))
window_y = int((screen_height / 2) - (window_height / 2))
window.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")

window.mainloop()
