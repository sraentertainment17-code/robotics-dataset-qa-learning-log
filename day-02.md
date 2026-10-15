# Day 2: Reading meta/ (the label on the box) ✅ (Oct 8, 2026)

## info.json
| Field | Value | Meaning |
|---|---|---|
| robot_type | so100_follower | Arm that recorded it (follower copies the human) |
| fps | 30 | 30 pictures per second |
| total_episodes | 50 | 50 tries at the job |
| total_frames | 11,939 | Total pictures across all tries |

**Frames vs fps (flipbook):** a frame is one page; fps is how fast you flip.
11,939 ÷ 30 ≈ 398 s of video total; ÷ 50 tries ≈ 8 s per try.

**Why it matters:** if the label says 30 fps but the camera took 25, the robot learns wrong speeds. If it says 50 tries but 45 exist, the team would be training on less data than expected.

## Python lessons (mistakes fixed)
- `%` = Terminal, `>>>` = Python. Type `python` before pasting Python code.
- New Terminal window: `conda activate lerobot` first (`(base)` = wrong env).
- Missing pandas: `pip install pandas pyarrow huggingface_hub`.
- Leave Python: `exit()` or Control + D.

## Task list
```python
import pandas as pd
tasks = pd.read_parquet("hf://datasets/lerobot/svla_so101_pickplace/meta/tasks.parquet")
print(tasks)
```
One task: **"pink lego brick into the transparent box"** (task_index 0).
Audit idea: a blue brick in the video would mean the label lies.

## Episode list
```python
eps = pd.read_parquet("hf://datasets/lerobot/svla_so101_pickplace/meta/episodes/chunk-000/file-000.parquet")
print(eps[["episode_index", "length", "tasks"]].head(5))
```
| episode_index | length (frames) | ≈ seconds |
|---|---|---|
| 0 | 303 | 10.1 |
| 1 | 266 | 8.9 |
| 2 | 230 | 7.7 |
| 3 | 183 | 6.1 |
| 4 | 215 | 7.2 |

Shorter isn't better. What matters is the try finishes the job. Flag tries way off from the rest (1 s = cut off/empty, 60 s = fumbling). Here 6–10 s looks healthy.

## In my words
Day 2 is reading the label: robot type, fps, frames, total episodes from info.json; the job from tasks; each try's number and length from the episodes list.
