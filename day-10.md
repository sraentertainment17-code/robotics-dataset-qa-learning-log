# Day 10: Action distributions ✅ (Oct 9, 2026)

## Goal
Robot actions should look like purposeful movement, not noise or a stuck joint. Use stats for each of the 6 joints to flag **dead** joints (never change) or **clipped** joints (stuck at ±100). This is checklist **#7 (robot moves)**.

## Analogies
- **Dead joint = a stuck door hinge.** The door never swings; the number never changes.
- **Clipped joint = a volume knob jammed at max.** It's stuck at ±100, so the real value is lost. Another way: a **ruler that only goes up to 100**. Anything longer still reads "100", so you can't tell 100 from 130.
- **Verdict** = the final pass/fail decision, like a judge's.

## Step 1: Load the frames and split the 6 joints
In Terminal: `conda activate lerobot`, then `python` (wait for `>>>`).
```python
import pandas as pd
df = pd.read_parquet("hf://datasets/lerobot/svla_so101_pickplace/data/chunk-000/file-000.parquet")
names = ["shoulder_pan","shoulder_lift","elbow_flex","wrist_flex","wrist_roll","gripper"]
act = pd.DataFrame(df["action"].tolist(), columns=names)
print(act.describe().round(1))
```
What each line does:
1. `names = [...]` lists the 6 joints in the order from info.json (Day 3).
2. `df["action"]` packs 6 numbers into each frame. `.tolist()` unpacks them, and `pd.DataFrame(..., columns=names)` lays them out as 6 named columns, one per joint.
3. `act.describe()` gives a summary for each joint; `.round(1)` keeps 1 decimal so it's easy to read.

## Step 2: Read the summary
`count` is 11939 for every joint (every frame has all 6 numbers).

| Joint | mean | std | min | 25% | 50% | 75% | max |
|---|---|---|---|---|---|---|---|
| shoulder_pan | 8.0 | 44.6 | -93.5 | -7.8 | 5.0 | 42.8 | 88.0 |
| shoulder_lift | -56.0 | 36.5 | -100.0 | -99.1 | -45.9 | -24.8 | 8.1 |
| elbow_flex | 65.3 | 29.0 | 13.0 | 38.1 | 57.0 | 99.5 | 100.0 |
| wrist_flex | 69.2 | 13.2 | 33.5 | 59.5 | 73.3 | 74.8 | 99.5 |
| wrist_roll | -53.4 | 17.8 | -92.8 | -61.0 | -53.8 | -40.7 | -20.0 |
| gripper | 6.8 | 9.0 | 0.0 | 1.2 | 1.5 | 12.8 | 33.0 |

What the columns mean:
- **mean** = the average position.
- **std** = how much it moves around (spread). Near 0 = barely moves = possibly dead.
- **min / max** = the lowest and highest values reached.
- **25% / 50% / 75%** = line up all values from low to high; these are the values a quarter, half, and three quarters of the way along.

**First read:** shoulder_lift's 25% (-99.1) and elbow_flex's 75% (99.5) look suspicious, very close to the ±100 limit. The coach's guess: that's the folded **rest pose** at the start and end of every try.

## Step 3: Check the suspicion with a number (clipping)
```python
print((act.abs() >= 99.9).sum())
print(((act.abs() >= 99.9).sum()/len(act)*100).round(1))
```
- `act.abs()` drops the minus sign, so -100 and +100 both count.
- `>= 99.9` asks True/False: "Is this frame at the limit?" `.sum()` counts the Trues.
- `/len(act)*100` turns the count into a percent of all frames.

| Joint | Frames at limit | Percent |
|---|---|---|
| shoulder_pan | 0 | 0.0% |
| shoulder_lift | 19 | 0.2% |
| elbow_flex | 82 | 0.7% |
| wrist_flex | 0 | 0.0% |
| wrist_roll | 0 | 0.0% |
| gripper | 0 | 0.0% |

**This corrected the guess:** those joints sit **near** the limit a lot, but are only **at** it in under 1% of frames. So there's **no real clipping**.
Report note (minor): "elbow_flex touches limit in 0.7% of frames, likely rest pose."
**Lesson: something looks suspicious → check it with a number** before you write it in a report.

## Step 4: Dead joints, and my question "how do you know no joint is dead?"
From the pooled summary, every joint moves a lot:

| Joint | Range (min → max) |
|---|---|
| shoulder_pan | -93.5 → 88.0 |
| shoulder_lift | -100.0 → 8.1 |
| elbow_flex | 13.0 → 100.0 |
| wrist_flex | 33.5 → 99.5 |
| wrist_roll | -92.8 → -20.0 |
| gripper | 0.0 → 33.0 |

The smallest std is 13.2 (wrist_flex), far from 0.
**But:** this pooled check mixes all 50 tries together. A joint that froze in just **one** try would hide among the other 49. So we checked **per try**:
```python
act["episode_index"] = df["episode_index"]
per_try = act.groupby("episode_index").std()
print((per_try < 0.5).sum())
```
1. Add the try number to each row.
2. `groupby("episode_index").std()` = the spread of each joint **inside each try** (50 rows × 6 joints).
3. `(per_try < 0.5).sum()` counts, for each joint, how many tries it barely moved in (std under 0.5).

Result: `0` for all 6 joints. ✅

**My question: "why 0 though?"** 0 = **zero problems**. Like a teacher counting sleeping students: 0 means nobody is asleep. If the elbow froze in try 12, elbow_flex would show 1.

## Verdict: PASS
No dead joints in any try, and clipping is under 1% for every joint.

## In my words (checked)
> "A dead joint is if robot elbow or wrist are not moving or stuck still 0 and what clipped joint is when robot shoulder or wrist gets stuck at its limit"

Feedback: right ✅. One fix: a dead joint can be stuck at **any** number, not just 0 (e.g. frozen at 45). This dataset had no dead joints, and clipping was under 1%.

## Key ideas
- std (spread) near 0 = the joint barely moves = possibly dead.
- Values piling up at ±100 = clipped; check the **percent** of frames, not just the min/max.
- Pooled stats can hide a problem in one try; check per try with groupby.
- Suspicious → check with a number → then write the report note.

## Checklist progress
- #1 Episode count: ✅ automated (Day 8)
- #2 Frame count / no empty tries: ✅ automated (Day 8)
- #4 Timing: ✅ automated (Day 9)
- #7 Robot moves: ✅ now **automated**

Script: [check_actions.py](check_actions.py). Run it with `python check_actions.py`.

## Next: Day 11
Label quality: read the task label, watch 10 s of 3 tries, and judge whether the label matches what really happens.
