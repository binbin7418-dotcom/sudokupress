import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

from sudoku_press import run_sudokupress


def run_job(count, difficulty, seed, outdir):
    s = run_sudokupress(count, outdir, seed=seed, difficulty=difficulty)
    lines = [f"Puzzles built: {len(s['puzzles'])}", f"Pages: {s['pages']}"]
    for r in s["puzzles"]:
        lines.append(f"  Puzzle {r['puzzle']}: {r['difficulty']}, {r['givens']} givens, unique solution proven")
    lines.append(f"PDF: {s['pdf_path']}")
    return lines


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SudokuPress")
        self.geometry("640x520")
        self.resizable(False, False)
        self.count = tk.StringVar(value="50")
        self.difficulty = tk.StringVar(value="Mixed")
        self.seed = tk.StringVar(value="42")
        row = tk.Frame(self); row.pack(fill="x", padx=12, pady=(12, 2))
        tk.Label(row, text="Puzzles:", width=34, anchor="w").pack(side="left")
        tk.Entry(row, textvariable=self.count, width=10).pack(side="left")
        row = tk.Frame(self); row.pack(fill="x", padx=12, pady=2)
        tk.Label(row, text="Difficulty (Easy/Medium/Hard/Mixed):", width=34, anchor="w").pack(side="left")
        tk.Entry(row, textvariable=self.difficulty, width=10).pack(side="left")
        row = tk.Frame(self); row.pack(fill="x", padx=12, pady=2)
        tk.Label(row, text="Seed:", width=34, anchor="w").pack(side="left")
        tk.Entry(row, textvariable=self.seed, width=10).pack(side="left")
        tk.Button(self, text="Build the book", font=("Segoe UI", 11, "bold"),
                  command=self.start).pack(pady=10)
        self.log = scrolledtext.ScrolledText(self, width=76, height=16,
                                             font=("Consolas", 9))
        self.log.pack(padx=12, pady=4)
        self.write("Every puzzle is dug from a full grid and proven to have exactly one solution. Fast: a 50-puzzle book takes seconds.")

    def write(self, msg):
        self.log.insert(tk.END, str(msg) + "\n")
        self.log.see(tk.END)
        self.update_idletasks()

    def pick(self, var, types):
        p = filedialog.askopenfilename(filetypes=types)
        if p:
            var.set(p)
    def collect(self):
        diff = self.difficulty.get().strip().capitalize()
        if diff not in ("Easy", "Medium", "Hard", "Mixed"):
            raise ValueError("Difficulty must be Easy, Medium, Hard or Mixed.")
        return (int(self.count.get()), diff, int(self.seed.get()),
                os.path.join(os.getcwd(), "sudokupress_out"))

    def start(self):
        try:
            args = self.collect()
        except Exception as e:
            messagebox.showerror("SudokuPress", str(e))
            return
        self.write("Working... (the window stays responsive)")
        threading.Thread(target=self._run, args=args, daemon=True).start()

    def _run(self, *args):
        try:
            lines = run_job(*args)
            for line in lines:
                self.after(0, self.write, line)
        except Exception as e:
            self.after(0, self.write, f"ERROR: {e}")


if __name__ == "__main__":
    App().mainloop()
