# SudokuPress

Build print-ready **Sudoku puzzle books for Amazon KDP** the honest way: fill a complete grid first, then *dig* givens out only while the solution stays provably unique.

## Why

There are two ways to make a Sudoku puzzle. The cheap way deals random givens and prints an answer key nobody checked — those books are full of puzzles with two, five, fifty solutions. The real way starts from a complete valid grid and removes givens one at a time, re-counting solutions after every removal: a removal is kept only if the puzzle still has **exactly one** solution. SudokuPress does it the real way, in rotationally symmetric pairs (the classic newspaper look), with difficulty bands by target given-count. Before the book is written, every puzzle is re-counted from its givens alone and must return exactly one solution, identical to the generated grid.

## Use

**App (Windows):** launch `SudokuPress.exe`, choose the puzzle count, difficulty (Easy / Medium / Hard / Mixed) and a seed, click **Build the book**. Output: `sudoku_book.pdf` in a `sudokupress_out` folder — title page, puzzle pages (bold givens, difficulty and given-count printed on each), then full solution grids. 8.5×11in (612×792pt).

**Command line:** `python sudoku_press.py out/ --puzzles=100 --difficulty=Mixed --seed=42`

A 6-puzzle sample book is included (`sample_book.pdf`).

## Difficulty bands (target givens)

Easy 40 · Medium 34 · Hard 28. Digging stops at the target or when no more givens can be removed without breaking uniqueness — the actual count is printed on every puzzle page, never hidden.

## Verified

Acceptance test (8/8 PASS, `test/acceptance_results.txt`): a 6-puzzle mixed book landed at Easy 40, Medium 33–34, Hard 27–29 givens; every puzzle re-counted from givens alone to exactly one solution matching the printed answers; whole book generated and verified in under a second; PDF exactly 14 pages at 612×792pt; generation deterministic for a fixed seed.

## Scope

Classic 9×9 Sudoku. Deterministic seeds make series production repeatable. 100% local — no uploads, no accounts, no per-book fees.

## Build from source

`pip install pyinstaller reportlab`, then `pyinstaller sudokupress.spec`. Or push to GitHub and let the included Actions workflow build the Windows package.
