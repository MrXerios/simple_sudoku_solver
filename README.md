# Simple Sudoku Solver
A simple sudoku solver implementing a few solving methods:

- Naked singles,
- hidden singles,
- naked tuples (pairs, triples, etc)
- hidden tuples (idem)
- pointing tuples (pairs or triple, by necessity)
- x-wing
- y-wing

This solver doesn't necessarily solve a sudoku completely since these methods aren't always enough, but it does not attempt to bruteforce the puzzle.

Example use:
```
sudoku = "XXX2XX5X9XXX5XXXXX295478XXX15X3X4X9XXX6XXXX5XX74X5X2XXXXXX23X4XX6384XXXX4X8XXX73X"

g = Grid(sudoku)

g
xxx | 2xx | 5x9
xxx | 5xx | xxx
295 | 478 | xxx
----+-----+----
15x | 3x4 | x9x
xx6 | xxx | x5x
x74 | x5x | 2xx
----+-----+----
xxx | x23 | x4x
x63 | 84x | xxx
4x8 | xxx | 73x

g.solve()
647 | 231 | 589
831 | 569 | 472
295 | 478 | 163
----+-----+----
152 | 384 | 697
986 | 712 | 354
374 | 956 | 218
----+-----+----
719 | 623 | 845
563 | 847 | 921
428 | 195 | 736
```
