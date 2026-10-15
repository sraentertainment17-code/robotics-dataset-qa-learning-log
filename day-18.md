# Day 18: Calibration gaps ✅ (Oct 10, 2026)

## Goal

## Analogy: the robot's settings sheet
Calibration is like **zeroing a kitchen scale**. Before you weigh flour, you press "zero" with the empty bowl on it. If you don't, every number is off by the bowl's weight. A robot's calibration says where each joint's zero is and how far it can move, so the numbers mean something.

## Step 1: What files does each dataset have?
In Terminal: `conda activate lerobot`, then `python` (wait for `>>>`).
```python
from huggingface_hub import HfApi
api = HfApi()
for repo in ["lerobot/svla_so101_pickplace", "MaxT90/so101-pick-place"]:
    files = api.list_repo_files(repo, repo_type="dataset")
    print(repo, [f for f in files if not f.startswith(("data/", "videos/"))])
```
`list_repo_files` lists every file in the dataset on the Hub (here hiding the big `data/` and `videos/` folders).

Both datasets have only these (besides data and videos):

| File | What it is | Calibration? |
|---|---|---|
| `.gitattributes` | Git housekeeping (how big files are stored) | No |
| `README.md` | The dataset's description page | No |
| `meta/episodes/chunk-000/file-000.parquet` | The episodes list (length and bookmarks per try) | No |
| `meta/info.json` | The label on the box: robot type, fps, counts, **names** of the joints and cameras | No: names, not settings |
| `meta/stats.json` | Min, max, mean… of the recorded data | No: **results**, not settings |
| `meta/tasks.parquet` | The task text | No |

**Neither dataset has a calibration file.**

**Link to Day 14:** MaxT90's joints went past 100 (-104, 113.8) and we had to work out by ourselves that the scale was different. A calibration file would have **explained those 104 values right away**.

## Step 2: Does info.json say anything about settings?
```python
print(info["features"]["observation.state"])
```
For MaxT90:
```
{'dtype': 'float32', 'names': ['shoulder_pan.pos', 'shoulder_lift.pos', 'elbow_flex.pos', 'wrist_flex.pos', 'wrist_roll.pos', 'gripper.pos'], 'shape': [6]}
```
- `dtype: float32` = the numbers are decimals.
- `names` = which joint each number is (`.pos` = position).
- `shape: [6]` = 6 numbers per frame.

No zero position, no limits, no scale. **Verdict: calibration is missing in both datasets.** That's a professional-grade finding for a report.

## "Show me an example of calibration data"
Here's what a LeRobot SO-101 calibration file looks like.
**⚠️ EXAMPLE ONLY: these numbers are made up to show the format. They are not from either dataset.**
```json
{
  "shoulder_pan":  {"id": 1, "drive_mode": 0, "homing_offset": -1470, "range_min": 758,  "range_max": 3292},
  "shoulder_lift": {"id": 2, "drive_mode": 0, "homing_offset": 157,   "range_min": 612,  "range_max": 3401},
  "elbow_flex":    {"id": 3, "drive_mode": 0, "homing_offset": 1105,  "range_min": 920,  "range_max": 3095},
  "wrist_flex":    {"id": 4, "drive_mode": 0, "homing_offset": -1300, "range_min": 845,  "range_max": 3178},
  "wrist_roll":    {"id": 5, "drive_mode": 0, "homing_offset": 62,    "range_min": 0,    "range_max": 4095},
  "gripper":       {"id": 6, "drive_mode": 0, "homing_offset": 1407,  "range_min": 2031, "range_max": 3350}
}
```
What each field means:

| Field | Meaning |
|---|---|
| `id` | Which motor on the arm (1 = base, 6 = gripper) |
| `drive_mode` | Which way the motor counts (normal or flipped direction) |
| `homing_offset` | The **zero**: how far the motor's raw count is shifted so the middle pose reads 0 (the "press zero on the scale" setting) |
| `range_min` | The lowest raw position the joint can reach (its physical limit) |
| `range_max` | The highest raw position the joint can reach |

LeRobot uses `range_min` and `range_max` to turn the motor's raw counts into the -100 to 100 numbers we've been reading all along.

## "How can I know the checklist if I don't even see it?"
Fair question: you can't check for something you've never seen. So the coach turned the example file into **5 questions** and scored both datasets:

| # | Question | svla_so101_pickplace | MaxT90/so101-pick-place |
|---|---|---|---|
| 1 | Does it say where 0 is for each joint? | ❌ | ❌ |
| 2 | Does it give each joint's limits? | ❌ | ❌ |
| 3 | Does it say what the numbers mean (scale/units)? | ❌ | ❌ |
| 4 | Does it describe the cameras (name, mount, size)? | ✅ (info.json: side/up, 640×480) | ✅ (info.json: wrist/overhead, 640×480) |
| 5 | Is a calibration file included? | ❌ | ❌ |
| | **Score** | **1 / 5** | **1 / 5** |

Then I asked for an example of a team-style checklist, and the coach showed one written as plain checks a team can read (the cleaned-up version is saved as [calibration_checklist_v1.md](calibration_checklist_v1.md)).

## "Why isn't calibration usually included?"
LeRobot saves the calibration file on the **recorder's own computer**, in a hidden settings folder, **not in the dataset folder**. When people upload their dataset, the calibration stays behind.
Analogy: you mail someone your baking results, but not the note saying "my scale was 5 g off". They can't trust or fix your numbers.
**Advice to teams: upload the calibration file with each dataset.**

## My checklist
> "zero position : dataset said joint start it from 0 / Joint limits ;dataset gives the lowest and highest value each joint can reach / Scale ; dataset mean what the number mean like -100 or 100 . what degress / Camera details ; dataset name each camera where is mounted and what its picture size / calibration file included; calibration file included so everyone can go check dataset"

Feedback: line 1 should say **where 0 is for each joint**, not "joints start at 0" (a try can start anywhere; 0 is the reference point). The rest is good ✅.

Cleaned-up version:
1. **Zero position:** the dataset says where 0 is for each joint.
2. **Joint limits:** the dataset gives the lowest and highest value each joint can reach.
3. **Scale and units:** the dataset says what the numbers mean (e.g. -100 to 100, or degrees).
4. **Camera details:** the dataset names each camera, where it's mounted, and its picture size.
5. **Calibration file included:** the calibration file is uploaded so anyone can check the dataset.

## My questions on scale, units, degrees and picture size
| Word | Simple meaning |
|---|---|
| **Scale** | The **range** of numbers a joint uses, like a volume slider from 0 to 100 |
| **Units** | What the numbers are **measured in** (centimetres, degrees, percent…) |
| **Degrees** | Turning measured like a clock face: **360 = a full circle**, **90 = a quarter turn** |
| **-100 to 100** | LeRobot's **percentage-style** scale: -100 = one end of the joint's range, 0 = middle, 100 = the other end |
| **Picture size** | Pixels **width × height**: our cameras are **640 × 480** |

## Key ideas
- Calibration = the settings sheet (zero, limits, scale). Results (stats.json) are not settings.
- Neither test dataset includes calibration: both score **1/5**.
- Missing calibration explains surprises like Day 14's 104 values, and it's a finding most auditors miss.
- Tell teams to upload the calibration file with every dataset.

## Deliverable
[calibration_checklist_v1.md](calibration_checklist_v1.md): the 5 checks, both scores, and the team recommendation.

## Checklist progress
- Main QA checklist: #1, #2, #4, #5, #5b, #7 automated; #9 hint (REVIEW); #8, #10 manual; #3, #6 not in the tool yet.
- New: **calibration presence** checklist v1 (manual, 5 checks).

## Next: Day 19
Edge-case coverage: skim 10 episode videos, tally object positions, lighting and variety, then score one dataset 1–3 on each.
