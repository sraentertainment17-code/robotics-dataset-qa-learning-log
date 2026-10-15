# Day 12: Empty and junk episodes ✅ (Oct 9, 2026)

## Goal
Tries where the robot barely moves are training garbage. Measure how much each try moves in total, list the 5 lowest, and watch one flagged video to confirm. This adds to checklist **#7 (robot moves)**.

## Analogies
- **Junk try** = someone hits record and then just stands still. The video exists, but nothing happens.
- **Step counter** for the arm: like a phone counting your steps all day, we add up how much every joint moved from one frame to the next, then total it for each try. A lazy day = few steps; a junk try = almost no movement.

**We use `observation.state`** (where the joints **really** were), not `action` (where they were told to go). We want to know if the arm actually moved.

## Step 1: Load and split the joints
In Terminal: `conda activate lerobot`, then `python` (wait for `>>>`).
```python
import pandas as pd
df = pd.read_parquet("hf://datasets/lerobot/svla_so101_pickplace/data/chunk-000/file-000.parquet")
names = ["shoulder_pan","shoulder_lift","elbow_flex","wrist_flex","wrist_roll","gripper"]
st = pd.DataFrame(df["observation.state"].tolist(), columns=names)
st["episode_index"] = df["episode_index"]
```
1. Load all 11,939 frames.
2. `names` = the 6 joints in info.json order.
3. `st = ...` unpacks the 6 real joint positions into 6 named columns (same trick as Day 10, but on `observation.state`).
4. Add the try number to each row so we can group by try.

## Step 2: Count the steps
```python
moves = st.groupby("episode_index")[names].diff().abs().sum(axis=1)
total = moves.groupby(st["episode_index"]).sum()
```
Piece by piece:
- `groupby("episode_index")[names].diff()`: for each joint, this frame minus the previous frame, inside each try only (same idea as Day 9, so the jump between tries isn't counted).
- `.abs()`: drop the minus sign, because moving down counts as movement too.
- `.sum(axis=1)`: add the 6 joints together → total movement for **that frame**.
- `total = moves.groupby(...).sum()`: add up every frame in a try → total movement for **that try** (the step count).

## Step 3: Who moved the least?
```python
print(total.sort_values().head(5).round(0))
print(total.median().round(0))
```
- `sort_values()` lines tries up from least to most movement; `.head(5)` shows the 5 lowest.
- `median()` = the middle try = what a typical try looks like.

| Rank | Try | Total movement |
|---|---|---|
| 1 (lowest) | 24 | 666 |
| 2 | 22 | 672 |
| 3 | 0 | 721 |
| 4 | 20 | 724 |
| 5 | 28 | 725 |
| Typical (median) | n/a | **860** |

## Step 4: What it means
- The lowest try (24, 666) moves about **3/4 of a typical try** (666 ÷ 860 ≈ 77%). That's **not near zero**. A truly empty try would score around **20–50**.
- **Try 0 is in the bottom 5**, and I watched it on Day 11 doing the task perfectly. So lower movement here means a **smoother, more efficient** try, not a broken one.

## Step 5: Confirm by eye (try 24)
I watched try 24 in the viewer: `https://lerobot-visualize-dataset.hf.space/lerobot/svla_so101_pickplace/episode_24`

> "the pink brick went in trasprant box and it took 7.4 second"

That matches the data (223 frames ÷ 30 = 7.4 s). Try 24 is an **efficient** try, not junk. ✅

## Workflow lesson
**Code flags → a human checks → write the verdict.**
The code ranks all 50 tries in seconds; I only watch the lowest one(s) to confirm.

## Verdict: PASS
0 empty tries. Even the least-moving try does the full task.

## Key ideas
- Total movement per try = a step counter for the arm.
- Use `observation.state` to measure real movement.
- Compare to the median (typical try), not to zero. Lowest here is 77% of typical; empty would be a tiny fraction.
- Low movement isn't automatically bad: it can mean a smooth, efficient try. Always confirm by watching.

## Checklist progress
- #1 Episode count: ✅ automated (Day 8)
- #2 Frame count / no empty tries: ✅ automated (Day 8)
- #4 Timing: ✅ automated (Day 9)
- #7 Robot moves: ✅ automated (Day 10 dead joints + Day 12 empty tries)
- #8 Camera clear, #9 Task finished, #10 Label correct: 👀 checked by hand on tries 0–3 (Day 11), plus try 24 today

Script: [check_empty.py](check_empty.py). Run it with `python check_empty.py`. It flags any try that moves less than 25% of the median as empty.

## Next: Day 13
Script review and cleanup: bundle the checks into one file (`audit_checks_v1.py`) with one function per check and a one-page summary.
