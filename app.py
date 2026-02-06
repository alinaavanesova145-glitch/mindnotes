import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import json
import os
from datetime import datetime

# ===== CONSTANTS =====
NOTES_FILE = "notes.json"
QUOTES_FILE = "quotes.json"

BG_COLOR = "#fffaf0"       # мягкий светлый фон
NOTE_COLOR = "#fffef6"     # фон заметок
QUOTE_COLOR = "#fff3e6"    # фон цитаты
FG_COLOR = "#333333"       # основной текст
BUTTON_COLOR = "#ffd6ba"   # пастельные кнопки
FONT = ("Segoe UI", 11)
LEAF_PADDING = 10

MOODS = {
    1: "😃 Happy",
    2: "😐 Neutral",
    3: "😔 Sad",
    4: "😡 Angry",
    5: "🤩 Overloaded"
}

# ===== UTILS =====
def load_json(filename, default):
    if not os.path.exists(filename):
        return default
    with open(filename, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return default

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ===== QUOTES =====
def load_quotes():
    return load_json(QUOTES_FILE, {"quotes": [
        "The best way to get started is to quit talking and begin doing.",
        "Don’t let yesterday take up too much of today.",
        "It’s not whether you get knocked down, it’s whether you get up.",
        "If you are working on something exciting, it will keep you motivated.",
        "Success is not in what you have, but who you are."
    ]})

def save_quotes(data_quotes):
    save_json(QUOTES_FILE, data_quotes)

def get_quote_of_the_day():
    quotes_data = load_quotes()
    if not quotes_data["quotes"]:
        return "Add some quotes to see them here!"
    index = datetime.now().toordinal() % len(quotes_data["quotes"])
    return quotes_data["quotes"][index]

def add_custom_quote():
    user_quote = simpledialog.askstring("Add Quote", "Enter your quote:", parent=root)
    if user_quote and user_quote.strip():
        quotes_data = load_quotes()
        quotes_data["quotes"].append(user_quote.strip())
        save_quotes(quotes_data)
        messagebox.showinfo("Success", "Your quote has been added!")
        refresh_notes()
    else:
        messagebox.showwarning("Empty Quote", "You must enter a quote.")

def delete_quote():
    quotes_data = load_quotes()
    if not quotes_data["quotes"]:
        messagebox.showinfo("Info", "No quotes to delete.")
        return
    selected_quote = simpledialog.askstring("Delete Quote", "Paste the exact quote text to delete:")
    if selected_quote in quotes_data["quotes"]:
        quotes_data["quotes"].remove(selected_quote)
        save_quotes(quotes_data)
        messagebox.showinfo("Deleted", "Quote deleted successfully!")
        refresh_notes()
    else:
        messagebox.showwarning("Not found", "Quote not found.")

# ===== NOTES =====
def add_note():
    text = note_text.get("1.0", tk.END).strip()
    if not text:
        messagebox.showwarning("Empty Note", "Please enter some text for the note.")
        return
    mood = mood_var.get()
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M')
    note = {"text": text, "mood": mood, "created_at": created_at}
    data["notes"].append(note)
    save_json(NOTES_FILE, data)
    note_text.delete("1.0", tk.END)
    refresh_notes()
    messagebox.showinfo("Saved", "Your note has been added!")

def refresh_notes():
    canvas.delete("all")
    x, y = 20, 20
    for idx, note in enumerate(data["notes"], start=1):
        draw_note(canvas, x, y, idx, note)
        y += 120
    canvas.config(scrollregion=canvas.bbox("all"))

def draw_note(canvas, x, y, idx, note):
    width, height = 600, 100
    canvas.create_rectangle(x, y, x+width, y+height, fill=NOTE_COLOR, outline="#ccc", width=1)
    text = f"{idx}. [{note['created_at']}] {note['mood']}\n{note['text']}"
    canvas.create_text(x+LEAF_PADDING, y+LEAF_PADDING, anchor="nw", text=text,
                       font=FONT, fill=FG_COLOR, width=width-2*LEAF_PADDING)

# ===== SEARCH & DELETE NOTES =====
def search_notes():
    query = simpledialog.askstring("Search Notes", "Enter keyword to search:")
    if not query:
        return
    results = [note for note in data["notes"] if query.lower() in note["text"].lower()]
    canvas.delete("all")
    x, y = 20, 20
    if results:
        for idx, note in enumerate(results, start=1):
            draw_note(canvas, x, y, idx, note)
            y += 120
    else:
        canvas.create_text(300, 200, text="No notes found.", font=FONT, fill=FG_COLOR)

def delete_note():
    selected_index = simpledialog.askinteger("Delete Note", "Enter note number to delete (starting from 1):")
    if selected_index and 1 <= selected_index <= len(data["notes"]):
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this note?")
        if confirm:
            del data["notes"][selected_index-1]
            save_json(NOTES_FILE, data)
            refresh_notes()
            messagebox.showinfo("Deleted", "Note deleted successfully.")
    else:
        messagebox.showwarning("Invalid", "Invalid note number.")

def show_statistics():
    if not data["notes"]:
        messagebox.showinfo("Statistics", "No notes to analyze yet.")
        return
    mood_count = {mood: 0 for mood in MOODS.values()}
    for note in data["notes"]:
        mood_count[note["mood"]] += 1
    hours = {}
    for note in data["notes"]:
        hour = int(note["created_at"][11:13])
        hours[hour] = hours.get(hour, 0) + 1
    most_active = max(hours, key=hours.get)
    msg = "Mood statistics:\n"
    for mood, count in mood_count.items():
        msg += f"{mood}: {count}\n"
    msg += f"\nMost active hour: {most_active}:00\n"
    messagebox.showinfo("Statistics", msg)

# ===== GUI SETUP =====
root = tk.Tk()
root.title("💛 MindNotes")
root.geometry("700x850")
root.configure(bg=BG_COLOR)

# ===== QUOTE FRAME (TOP CENTER) =====
quote_frame = tk.Frame(root, bg=BG_COLOR)
quote_frame.pack(pady=10, fill="x")

quote_label = tk.Label(
    quote_frame,
    text=f'💬 Quote of the day:\n"{get_quote_of_the_day()}"',
    bg=QUOTE_COLOR,
    fg=FG_COLOR,
    font=("Segoe UI", 12, "italic"),
    wraplength=650,
    justify="center",
    bd=2,
    relief="ridge",
    padx=10,
    pady=10
)
quote_label.pack(pady=5)

# ===== NOTE ENTRY =====
note_frame = tk.Frame(root, bg=BG_COLOR)
note_frame.pack(padx=20, pady=5, fill="x")

note_text = tk.Text(note_frame, height=5, bg=NOTE_COLOR, fg=FG_COLOR, insertbackground=FG_COLOR, font=FONT)
note_text.pack(fill="x")

mood_var = tk.StringVar(value=MOODS[2])
mood_menu = ttk.Combobox(note_frame, textvariable=mood_var, values=list(MOODS.values()), state="readonly", font=FONT)
mood_menu.pack(pady=5)

# ===== BUTTONS =====
btn_frame = tk.Frame(root, bg=BG_COLOR)
btn_frame.pack(pady=5)

tk.Button(btn_frame, text="Add note", command=add_note, bg=BUTTON_COLOR, fg=FG_COLOR, font=FONT, width=15).grid(row=0, column=0, padx=5, pady=5)
tk.Button(btn_frame, text="Search notes", command=search_notes, bg=BUTTON_COLOR, fg=FG_COLOR, font=FONT, width=15).grid(row=0, column=1, padx=5, pady=5)
tk.Button(btn_frame, text="Delete note", command=delete_note, bg="#ffb3b3", fg=FG_COLOR, font=FONT, width=32).grid(row=1, column=0, columnspan=2, pady=5)
tk.Button(btn_frame, text="Show statistics", command=show_statistics, bg=BUTTON_COLOR, fg=FG_COLOR, font=FONT, width=32).grid(row=2, column=0, columnspan=2, pady=5)
tk.Button(btn_frame, text="Add your quote", command=add_custom_quote, bg="#ffe0b3", fg=FG_COLOR, font=FONT, width=32).grid(row=3, column=0, columnspan=2, pady=5)
tk.Button(btn_frame, text="Delete a quote", command=delete_quote, bg="#ffb3b3", fg=FG_COLOR, font=FONT, width=32).grid(row=4, column=0, columnspan=2, pady=5)

# ===== CANVAS FOR NOTES =====
canvas_frame = tk.Frame(root, bg=BG_COLOR)
canvas_frame.pack(padx=20, pady=10, fill="both", expand=True)

canvas = tk.Canvas(canvas_frame, bg=BG_COLOR)
canvas.pack(side=tk.LEFT, fill="both", expand=True)

scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill="y")
canvas.config(yscrollcommand=scrollbar.set)

# ===== LOAD DATA =====
data = load_json(NOTES_FILE, {"notes": []})
refresh_notes()

root.mainloop()




