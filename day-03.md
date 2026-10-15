# Day 3: Reading data/ (the robot's diary) ✅ (Oct 8, 2026)

## Load the data file
In Terminal: `conda activate lerobot`, then `python` (wait for `>>>`).
```python
import pandas as pd
df = pd.read_parquet("hf://datasets/lerobot/svla_so101_pickplace/data/chunk-000/file-000.parquet")
print(df.columns.tolist())
```
Result: `['action', 'observation.state', 'timestamp', 'frame_index', 'episode_index', 'index', 'task_index']`

## The 7 columns (each row = one frame / flipbook page)
| Column | Meaning |
|---|---|
| action | Where the robot is **told** to put each joint next (the order) |
| observation.state | Where each joint **actually** is right now (the reality) |
| timestamp | Stopwatch time inside the try, in seconds (restarts at 0 each try) |
| frame_index | Page number inside the try (restarts at 0) |
| episode_index | Which try (0–49) |
| index | Page number across the whole dataset (0–11,938) |
| task_index | Which job (always 0 = pink lego brick) |

## The 6 joint numbers (checked in info.json → features → action → names)
Order goes from body out to the hand:
1. shoulder_pan (turn left/right)
2. shoulder_lift (raise/lower arm)
3. elbow_flex (bend elbow)
4. wrist_flex (tilt wrist)
5. wrist_roll (twist wrist)
6. gripper (open/close hand)

Scale is like a slider from calibration: -100 = one end, 0 = middle, +100 = other end. Gripper usually 0 (closed) to 100 (open).
The order is fixed for this dataset; other robots have different lists (ALOHA ~14, humanoids 20–40+), so always read `names` in info.json first.

## Order vs reality (row 0)
```python
print(df["action"][0])
print(df["observation.state"][0])
```
| Joint | Action | State | Gap |
|---|---|---|---|
| shoulder_pan | 1.91 | 1.96 | 0.04 |
| shoulder_lift | -99.41 | -98.74 | 0.67 |
| elbow_flex | 99.54 | 98.92 | 0.62 |
| wrist_flex | 74.84 | 74.82 | 0.02 |
| wrist_roll | -48.52 | -51.45 | 2.93 |
| gripper | 1.62 | 1.41 | 0.21 |

Small gaps (<3 points) = healthy. Gaps of 30–50 points = stuck/broken/badly calibrated motor (red flag). (Numbers rounded for readability; scripts keep full values.)

## Timestamps
```python
ep0 = df[df["episode_index"] == 0]
print(ep0[["frame_index", "timestamp"]].head(5))
```
0.000, 0.033, 0.067, 0.100, 0.133 → steps of 1/30 s = true 30 fps, matches info.json. Uneven jumps (e.g. 0.033 → 0.200) = missing frames (Day 9 check).

## Watching the arm move (try 0)
```python
for i in [0, 150, 302]:
    print(i, ep0["action"].iloc[i])
```
(Python loop: press Enter on the empty `...` line to run it.)

| Joint | Start (0 s) | Middle (~5 s) | End (~10 s) |
|---|---|---|---|
| shoulder_pan | 1.9 | 8.3 | 4.5 |
| shoulder_lift | -99.4 | 0.4 | -99.4 |
| elbow_flex | 99.5 | 35.0 | 99.5 |
| wrist_flex | 74.8 | 47.8 | 74.8 |
| wrist_roll | -48.5 | -50.6 | -58.9 |
| gripper | 1.6 | 20.7 | 1.5 |

Start = folded, hand closed. Middle = arm reaching out, hand open. End = back home, hand closed. Healthy try: start → reach → return. Numbers barely changing = empty try (Day 12).

## In my words
action is the next move the robot is told; observation.state is where the joints really are; timestamp is the time inside that try.
