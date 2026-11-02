#!/usr/bin/env python3
"""SudokuPress acceptance test: generate a real 6-puzzle mixed-difficulty
book; assert every puzzle's uniqueness is proven from its givens alone,
given counts land in the difficulty bands, harder puzzles have fewer
givens than easy ones, PDF structure is right, and generation is
deterministic for a fixed seed."""
import os
import random
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from sudoku_press import build_book, generate_puzzle, verify_puzzle

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
results = []


def check(name, cond, detail=""):
    results.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


def main():
    t0 = time.time()
    p1 = generate_puzzle(random.Random(11), "Medium")
    p2 = generate_puzzle(random.Random(11), "Medium")
    check("generation is deterministic for a fixed seed", p1["puzzle"] == p2["puzzle"])

    s = build_book(6, OUT, seed=7, difficulty="Mixed")
    check("book PDF written", os.path.getsize(s["pdf_path"]) > 5000,
          f"{os.path.getsize(s['pdf_path'])} bytes")
    check("every puzzle verified unique-from-givens",
          all(r["verified"] and r["unique_solution"] for r in s["puzzles"]))
    givens = {r["difficulty"]: r["givens"] for r in s["puzzles"]}
    check("givens in sane bands (Easy<=44, Medium<=38, Hard<=34)",
          all(r["givens"] <= {"Easy": 44, "Medium": 38, "Hard": 34}[r["difficulty"]]
              for r in s["puzzles"]), f"{[ (r['difficulty'], r['givens']) for r in s['puzzles'] ]}")
    check("Hard puzzles have fewer givens than Easy ones",
          max(r["givens"] for r in s["puzzles"] if r["difficulty"] == "Hard") <
          min(r["givens"] for r in s["puzzles"] if r["difficulty"] == "Easy"))
    check("page count = 2 + 2*6", s["pages"] == 14, f"got {s['pages']}")

    from pypdf import PdfReader
    r = PdfReader(s["pdf_path"])
    check("PDF reopens with 14 pages", len(r.pages) == 14)
    mb = r.pages[0].mediabox
    check("page size 612x792", float(mb.width) == 612 and float(mb.height) == 792)
    print(f"(total {time.time() - t0:.1f}s)")
    failed = [x for x in results if not x[1]]
    print(f"\n{len(results) - len(failed)}/{len(results)} PASS")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
