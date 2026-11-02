#!/usr/bin/env python3
"""SudokuPress engine: Sudoku puzzle books (PDF) where every puzzle is
PROVEN to have exactly one solution.

How a puzzle is made: a complete valid grid is filled by backtracking,
then givens are dug out one at a time (in rotationally symmetric pairs)
— a removal is kept only while an independent solution counter still
finds exactly one solution. Digging stops at the difficulty's target
given-count or when no more givens can be removed. Before the book is
written, every puzzle is re-counted from its givens alone and must
return exactly one solution, identical to the generated grid.

Deterministic for a fixed seed. 100% local. Requires: reportlab.

Usage:
    python sudoku_press.py out/ [--puzzles 20] [--difficulty Mixed] [--seed 42]
"""
import os
import random
import sys

PAGE_W, PAGE_H = 612, 792
TARGETS = {"Easy": 40, "Medium": 34, "Hard": 28}

# ------------------------------------------------------------------ solver

def _candidates(grid, r, c):
    used = set(grid[r]) | {grid[i][c] for i in range(9)}
    br, bc = 3 * (r // 3), 3 * (c // 3)
    used |= {grid[i][j] for i in range(br, br + 3) for j in range(bc, bc + 3)}
    return [d for d in range(1, 10) if d not in used]


def count_solutions(grid, limit=2):
    """Count solutions of a (partial) grid, stopping at `limit`.
    Returns (count, first_solution_or_None). MRV backtracking."""
    g = [row[:] for row in grid]
    found = []

    def rec():
        if len(found) >= limit:
            return
        best, best_opts = None, None
        for r in range(9):
            for c in range(9):
                if g[r][c] == 0:
                    opts = _candidates(g, r, c)
                    if best_opts is None or len(opts) < len(best_opts):
                        best, best_opts = (r, c), opts
                        if len(opts) <= 1:
                            break
            if best_opts is not None and len(best_opts) <= 1:
                break
        if best is None:
            found.append([row[:] for row in g])
            return
        if not best_opts:
            return
        r, c = best
        for d in best_opts:
            g[r][c] = d
            rec()
            g[r][c] = 0
            if len(found) >= limit:
                return

    rec()
    return len(found), (found[0] if found else None)


def fill_grid(rng):
    """A complete valid Sudoku grid, randomized by the seeded rng."""
    g = [[0] * 9 for _ in range(9)]

    def rec():
        best, best_opts = None, None
        for r in range(9):
            for c in range(9):
                if g[r][c] == 0:
                    opts = _candidates(g, r, c)
                    if best_opts is None or len(opts) < len(best_opts):
                        best, best_opts = (r, c), opts
                        if len(opts) <= 1:
                            break
            if best_opts is not None and len(best_opts) <= 1:
                break
        if best is None:
            return True
        r, c = best
        order = best_opts[:]
        rng.shuffle(order)
        for d in order:
            g[r][c] = d
            if rec():
                return True
            g[r][c] = 0
        return False

    rec()
    return g

# ------------------------------------------------------------------ digging

def dig(full, rng, target):
    """Remove givens in symmetric pairs while the solution stays unique."""
    puzzle = [row[:] for row in full]
    cells = [(r, c) for r in range(9) for c in range(9)]
    rng.shuffle(cells)
    givens = 81
    seen = set()
    for r, c in cells:
        if givens <= target:
            break
        if (r, c) in seen or puzzle[r][c] == 0:
            continue
        pair = [(r, c)]
        r2, c2 = 8 - r, 8 - c
        if (r2, c2) != (r, c):
            pair.append((r2, c2))
        seen.update(pair)
        saved = [(rr, cc, puzzle[rr][cc]) for rr, cc in pair]
        for rr, cc, _ in saved:
            puzzle[rr][cc] = 0
        cnt, _ = count_solutions(puzzle, limit=2)
        if cnt == 1:
            givens -= len(saved)
        else:
            for rr, cc, v in saved:
                puzzle[rr][cc] = v
    return puzzle, givens


def generate_puzzle(rng, difficulty):
    full = fill_grid(rng)
    puzzle, givens = dig(full, rng, TARGETS[difficulty])
    return {"solution": full, "puzzle": puzzle, "givens": givens,
            "difficulty": difficulty}


def verify_puzzle(p):
    cnt, sol = count_solutions(p["puzzle"], limit=2)
    if cnt != 1:
        return False, f"solver found {cnt} solutions from givens alone"
    if sol != p["solution"]:
        return False, "unique solution != generated grid"
    g = sum(1 for row in p["puzzle"] for v in row if v != 0)
    if g != p["givens"]:
        return False, "given count mismatch"
    return True, ""

# ------------------------------------------------------------------ PDF

def _draw_grid(c, grid, cx, top, cell, bold_givens=None):
    x0 = cx - 9 * cell / 2
    for r in range(9):
        for col in range(9):
            x = x0 + col * cell
            y = top - (r + 1) * cell
            c.setLineWidth(0.5)
            c.setStrokeColorRGB(0.55, 0.55, 0.55)
            c.rect(x, y, cell, cell, stroke=1, fill=0)
            v = grid[r][col]
            if v:
                is_given = bold_givens is not None and bold_givens[r][col] != 0
                c.setFillColorRGB(0, 0, 0)
                c.setFont("Helvetica-Bold" if is_given or bold_givens is None
                          else "Helvetica", cell * 0.52)
                c.drawCentredString(x + cell / 2, y + cell * 0.32, str(v))
    c.setStrokeColorRGB(0, 0, 0)
    for i in range(4):
        c.setLineWidth(2)
        x = x0 + i * 3 * cell
        c.line(x, top, x, top - 9 * cell)
        y = top - i * 3 * cell
        c.line(x0, y, x0 + 9 * cell, y)


def build_book(count, outdir, seed=42, difficulty="Mixed",
               title="Sudoku Puzzle Book"):
    from reportlab.pdfgen import canvas as rl_canvas
    rng = random.Random(seed)
    os.makedirs(outdir, exist_ok=True)
    pdf_path = os.path.join(outdir, "sudoku_book.pdf")
    puzzles, reports = [], []
    cycle = ["Easy", "Medium", "Hard"]
    for k in range(count):
        diff = cycle[k % 3] if difficulty == "Mixed" else difficulty
        p = generate_puzzle(rng, diff)
        ok, why = verify_puzzle(p)
        if not ok:
            raise RuntimeError(f"puzzle {k + 1} failed verification: {why}")
        puzzles.append(p)
        reports.append({"puzzle": k + 1, "difficulty": diff,
                        "givens": p["givens"], "unique_solution": True,
                        "verified": True})
    c = rl_canvas.Canvas(pdf_path, pagesize=(PAGE_W, PAGE_H))
    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(PAGE_W / 2, PAGE_H / 2 + 60, title)
    c.setFont("Helvetica", 13)
    c.drawCentredString(PAGE_W / 2, PAGE_H / 2 + 28,
                        f"{count} Sudoku puzzles with full solutions")
    c.setFont("Helvetica", 10)
    c.drawCentredString(PAGE_W / 2, PAGE_H / 2 - 6,
                        "Every puzzle in this book was re-solved from its givens alone")
    c.drawCentredString(PAGE_W / 2, PAGE_H / 2 - 20,
                        "and proven to have exactly one solution.")
    c.showPage()
    for i, p in enumerate(puzzles):
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(PAGE_W / 2, PAGE_H - 54,
                            f"Puzzle {i + 1} — {p['difficulty']} ({p['givens']} givens)")
        _draw_grid(c, p["puzzle"], PAGE_W / 2, PAGE_H - 90, 40,
                   bold_givens=p["puzzle"])
        c.showPage()
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(PAGE_W / 2, PAGE_H / 2, "Solutions")
    c.showPage()
    for i, p in enumerate(puzzles):
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(PAGE_W / 2, PAGE_H - 54, f"Solution {i + 1}")
        _draw_grid(c, p["solution"], PAGE_W / 2, PAGE_H - 90, 40)
        c.showPage()
    c.save()
    return {"pdf_path": pdf_path, "puzzles": reports, "pages": 2 + 2 * count}


def run_sudokupress(count, outdir, seed=42, difficulty="Mixed", **kw):
    return build_book(count, outdir, seed=seed, difficulty=difficulty, **kw)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    opts = dict(a[2:].split("=") for a in sys.argv[1:] if a.startswith("--"))
    if len(args) != 1:
        print(__doc__)
        sys.exit(2)
    s = run_sudokupress(int(opts.get("puzzles", 20)), args[0],
                        seed=int(opts.get("seed", 42)),
                        difficulty=opts.get("difficulty", "Mixed"))
    print(f"{len(s['puzzles'])} puzzles, {s['pages']} pages\nPDF: {s['pdf_path']}")
