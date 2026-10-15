# Day 9: Frame rates and timestamps ✅ (Oct 9, 2026)

## Goal
A dataset recorded at "30 fps" with jumping timestamps is training poison. Check that the time between frames is steady at 1/30 s and flag any skipped frames. This is checklist **#4 (timing)**.

## Analogy: a drum beat
At 30 fps a new frame (picture + joint numbers) should arrive every **1/30 s = 0.0333 s**, like a steady drum: boom, boom, boom, always the same gap.

## Step 1: Load all the frames
In Terminal: `conda activate lerobot`, then `python` (wait for `>>>`).
```python
import pandas as pd
df = pd.read_parquet("hf://datasets/lerobot/svla_so101_pickplace/data/chunk-000/file-000.parquet")
print(len(df))
```
Result: `11939` frames (all 50 tries), which matches info.json. ✅

## Step 2: Measure the step between frames
```python
df["step"] = df.groupby("episode_index")["timestamp"].diff()
```
What this line does, piece by piece:
- `df.groupby("episode_index")` splits the frames into their 50 tries, so each try is measured on its own.
- `["timestamp"]` uses the time column (seconds inside the try).
- `.diff()` subtracts each frame's time from the next one: e.g. 0.0667 − 0.0333 = 0.0333.
- `df["step"] = ...` saves the answers as a new column called `step`.

**Why groupby matters:** the timestamp restarts at 0 for every try. Without groupby, the jump from the end of one try (e.g. 10.07 s) back to 0.0 at the start of the next would count as a giant fake gap. groupby keeps tries separate. (The first frame of each try has no frame before it, so its step is blank and gets skipped.)

## Step 3: Average and biggest step
```python
print(df["step"].mean())
print(df["step"].max())
```
| Measure | Result | Meaning |
|---|---|---|
| mean (average step) | 0.03333333 | Exactly 1/30 s ✅ |
| max (biggest step) | 0.03333378 | Tiny rounding crumb above 1/30 s, effectively the same ✅ |

## Step 4: Count skipped frames
```python
print((df["step"] > 2/30).sum())
```
- `2/30` = 0.0667 s = double the normal beat. A step bigger than that means at least one frame is missing.
- `> 2/30` asks True/False for every step; `.sum()` counts the Trues.

Result: `0` skipped frames. ✅

**Result: PASS for all 50 tries and 11,939 frames.** The beat is perfectly steady.

## My question: "explain me to like a baby"
- **A clock:** good timing sounds like *tick, tick, tick, tick*. Bad timing sounds like *tick, tick, ……… tick*: the long silence means missing pictures.
- **A video of catching a ball with the middle missing:** the hands look like they teleport to the ball. A robot trained on that learns jumpy, jerky moves.

## In my words (checked)
> "today day 8 , i learn about timing , how to check the timing is right or wrong in python .I checked the mean , max , mean is average gap and max is biggest gap . everyhing look good and skip frames is 0"

Feedback: great summary ✅. Small fix: today is **Day 9**, not 8. The part to add: a **bad** result means a **big gap**, so missing pictures and jumpy moves for the robot.

## Key ideas
- mean = the average gap between frames; max = the biggest gap. Both should be about 1/30 s.
- Skipped frame = a gap more than double the beat (over 2/30 s).
- Use groupby so each try is measured on its own.
- Timing defects corrupt action labels silently; this check catches them.

## Checklist progress
- #1 Episode count: ✅ automated (Day 8)
- #2 Frame count / no empty tries: ✅ automated (Day 8)
- #4 Timing: ✅ now **automated**

Script: [check_timing.py](check_timing.py). Run it with `python check_timing.py`.

## Next: Day 10
Action distributions: per-joint stats (min, max, mean, std) to flag dead joints (never change) or clipped joints (stuck at ±100).
