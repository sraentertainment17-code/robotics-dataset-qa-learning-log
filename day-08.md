# Day 8: Episode counts and integrity ✅ (Oct 9, 2026)

## Goal
The simplest check catches the most embarrassing defects: **missing tries**. Write Python that confirms the try numbers run 0 to 49 with no gaps, and that every try has more than 0 frames. This is checklist **#1 (episode count)** and **#2 (frame count / no empty tries)**.

## Analogy: a book with pages 0 to 49
- A **missing page** (e.g. page 3 is gone) = a gap = the book is broken.
- A **blank page** (nothing written on it) = an empty try = the book is broken.

A healthy book has every page, in order, and every page has writing on it.

## Step 1: Load the episodes list
In Terminal: `conda activate lerobot`, then `python` (wait for `>>>`).
```python
import pandas as pd
eps = pd.read_parquet("hf://datasets/lerobot/svla_so101_pickplace/meta/episodes/chunk-000/file-000.parquet")
print(len(eps))
```
Result: `50`, which matches info.json. ✅
`len(eps)` = how many rows (tries) are in the list.

**Why 50 rows isn't enough proof:** you could have 50 rows numbered 0, 1, 2, 4, 5, … 50 (try 3 missing, an extra 50 at the end). Still 50 rows, but there's a gap. So we also check the **numbers themselves**.

## Step 2: Check for gaps
```python
expected = list(range(50))
actual = sorted(eps["episode_index"].tolist())
print(actual == expected)
```
What each line does:
1. `expected = list(range(50))` makes the perfect list: 0, 1, 2, … 49 (50 numbers, starting at 0).
2. `actual = sorted(eps["episode_index"].tolist())` takes the real try numbers from the file, turns them into a plain list, and puts them in order.
3. `print(actual == expected)` asks a **True/False question**: "Is the real list exactly the same as the perfect list?"

`==` means "is it equal?" (one `=` saves a value; two `==` asks a question).
Result: `True` → no missing tries, no extra tries. ✅

## Step 3: Check for empty tries
```python
print((eps["length"] == 0).sum())
print(eps["length"].min())
```
1. `eps["length"] == 0` asks for every try: "Does it have 0 frames?" (True/False for each).
2. `.sum()` counts the Trues (True = 1, False = 0). Result: `0` → no empty tries. ✅
3. `.min()` finds the smallest length. Result: `183` frames ≈ **6 seconds** (try 3). Short, but a real try, not empty.

## Step 4: One PASS/FAIL answer
```python
if actual == expected and (eps["length"] == 0).sum() == 0:
    print("PASS: all 50 episodes present, none empty")
else:
    print("FAIL: missing or empty episodes found")
```
- `if` … `and` …: both must be true (no gaps **and** no empty tries).
- If yes, print PASS; `else` (otherwise) print FAIL.
- The 4 spaces before the print lines tell Python those lines belong to the if/else.

**Recurring lesson:** after an `if/else` block Python shows `...` and waits. Press **Enter on the empty `...` line** to run it.

Result:
```
PASS: all 50 episodes present, none empty
```

## My question
**"So I have to know the Python script to check like this, right?"**
Answer: you don't need to memorize it. Know the **question each check asks** ("are all tries there?", "is any try empty?"). The same small patterns repeat in every check:

| Pattern | What it asks |
|---|---|
| `len(...)` | How many? |
| `==` | Is it equal? (True/False) |
| `.sum()` | How many Trues? |
| `.min()` / `.max()` | Smallest / biggest? |

On Day 13 all the checks get bundled into one script file, so you run one command instead of typing them.

## In my words (checked)
> "this is real important step for if everything looks right before send report to user , if we catched the bad data ,we have to flag it and re record or do it again that data. The team care too much about this data because training a bad date will make some mistake when they training with a real robot"

Feedback: the **why** is right ✅. To be specific, this check catches two things: **missing tries** (gaps in the numbers) and **empty tries** (0 frames). Example: a team expected 100 tries but only got 93.

## Checklist progress
- #1 Episode count: ✅ now **automated**
- #2 Frame count / no empty tries: ✅ now **automated**

Script: [check_episodes.py](check_episodes.py). Run it with `python check_episodes.py`.

## Next: Day 9
Frame rates and timestamps: check the time between frames is about 1/30 s and flag any jumps.
