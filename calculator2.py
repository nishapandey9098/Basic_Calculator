import tkinter
import math
import re

# -------- Buttons layout --------
button_values = [
    ["AC", "⌫", "%", "÷"],
    ["7", "8", "9", "×"],
    ["4", "5", "6", "-"],
    ["1", "2", "3", "+"],
    ["0", ".", "(", ")"],
    ["√", "x²", "+/-", "="]
]

right_symbols = ["÷", "×", "-", "+", "=", "√", "x²"]
top_symbols = ["AC", "⌫", "%"]
bottom_symbols = ["."]
row_count = len(button_values)
column_count = len(button_values[0])

# -------- Colors & window --------
color_pink = "#F442D0"
color_purple = "#8304F3"
color_dark_gray = "#505050"
color_green = "#00FFCC"
color_white = "white"
color_black = "black"

window = tkinter.Tk()
window.title("Calculator")
window.resizable(False, False)

frame = tkinter.Frame(window)
label = tkinter.Label(frame, text="0", font=("Arial", 45),
                      background=color_black, foreground=color_white,
                      anchor="e", width=column_count)
label.grid(row=0, column=0, columnspan=column_count, sticky="we")

# -------- Helpers to format & evaluate --------
def insert_implicit_multiplication(expr: str) -> str:
    """
    Do not change the displayed text. For evaluation we insert '*' where
    multiplication is implied (e.g. '5(' -> '5*(', '5√' -> '5*√', ')(' -> ')*(').
    """
    # between digit and '(' or digit and '√'
    expr = re.sub(r'(?<=\d)\s*(?=\()', '*', expr)
    expr = re.sub(r'(?<=\d)\s*(?=√)', '*', expr)
    # between ')' and '('
    expr = re.sub(r'\)\s*(?=\()', ')*', expr)
    # between ')' and '√'
    expr = re.sub(r'(?<=\))\s*(?=√)', ')*', expr)
    return expr

def format_expression(expr: str) -> str:
    """
    Convert the user expression (with √, ×, ÷, x², %) into a valid Python expression
    using math.sqrt, *, /, **2, etc. Handles implicit multiplication in formatted output.
    """
    if not expr:
        return ""

    # Make implicit multiplication marks in a temporary copy
    tmp = insert_implicit_multiplication(expr)

    # Basic replacements
    tmp = tmp.replace("×", "*").replace("÷", "/")
    tmp = tmp.replace("x²", "**2")

    # Percent: convert "50%" -> "(50/100)"
    tmp = re.sub(r'([0-9]+(?:\.[0-9]+)?)\s*%', r'(\1/100)', tmp)

    # Convert "√(" -> "math.sqrt(" directly
    tmp = tmp.replace("√(", "math.sqrt(")

    # Convert "√number" -> "math.sqrt(number)"
    # This pattern handles numbers after the √ symbol (with optional decimal)
    tmp = re.sub(r'√\s*([0-9]+(?:\.[0-9]+)?)', r'math.sqrt(\1)', tmp)

    return tmp

def format_result(res):
    if isinstance(res, float):
        res = round(res, 10)  # reduce floating point noise
        if res.is_integer():
            res = int(res)
    return str(res)

def safe_eval(expr: str):
    # Evaluate with only math module available
    return eval(expr, {"__builtins__": None}, {"math": math})

# -------- Actions --------
def clear_all():
    label["text"] = "0"

def backspace():
    s = label["text"]
    if s in ("", "0", "Error"):
        label["text"] = "0"
        return
    # remove x² as a unit
    if s.endswith("x²"):
        new = s[:-2]
    else:
        new = s[:-1]
    label["text"] = new if new else "0"

def toggle_sign():
    s = label["text"]
    if not s or s in ("0", "Error"):
        return
    # find last numeric token or parenthesized token
    m = re.search(r'([0-9]+(?:\.[0-9]+)?|\([^\(\)]*\))$', s)
    if not m:
        return
    token = m.group(1)
    start = m.start(1)
    # If token already wrapped as (-...), unwrap it
    if token.startswith("(-") and token.endswith(")"):
        new_token = token[2:-1]
    else:
        new_token = f"(-{token})"
    label["text"] = s[:start] + new_token

def evaluate_expression():
    expr = label["text"]
    if not expr or expr in ("Error",):
        return
    # If ends with an operator, strip it (prevents obvious syntax error)
    if expr[-1] in "+-×÷*/":
        expr = expr[:-1]
    try:
        formatted = format_expression(expr)
        result = safe_eval(formatted)
        label["text"] = format_result(result)
    except Exception:
        label["text"] = "Error"

# -------- Button click handler --------
digits = "0123456789"

def button_clicked(value):
    cur = label["text"]
    # Reset after Error (except AC / backspace)
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

    # If current is just "0", replace it when appropriate
    if cur == "0":
        if value in digits:
            label["text"] = value
            return
        if value == ".":
            label["text"] = "0."
            return
        if value in ("√", "("):
            # Replace leading 0 with the symbol so you don't get "0√"
            label["text"] = value
            return
        if value == "x²":
            # user pressed x² while display is 0 => treat as 0x² (will evaluate to 0)
            label["text"] = "0x²"
            return
        # for other operators, just append to 0 (keeps behavior simple)
        label["text"] = cur + value
        return

    # Normal append
    label["text"] = cur + value

# -------- Create & style buttons --------
for r in range(row_count):
    for c in range(column_count):
        try:
            value = button_values[r][c]
        except IndexError:
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

for i in range(column_count):
    frame.grid_columnconfigure(i, weight=1)

frame.pack(padx=8, pady=8, expand=True, fill="both")

# Center window
window.update_idletasks()
w, h = window.winfo_width(), window.winfo_height()
sw, sh = window.winfo_screenwidth(), window.winfo_screenheight()
x, y = int((sw / 2) - (w / 2)), int((sh / 2) - (h / 2))
window.geometry(f"{w}x{h}+{x}+{y}")

window.mainloop()
