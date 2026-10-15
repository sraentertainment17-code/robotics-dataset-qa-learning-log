# Day 4: Reading videos/ (the robot's movie) ✅ (Oct 8, 2026)

## What lives in videos/
Dataset: `lerobot/svla_so101_pickplace` (LeRobot v3.0). Two cameras, one folder each:
- `videos/observation.images.side/chunk-000/file-000.mp4` (side camera)
- `videos/observation.images.up/chunk-000/file-000.mp4` (up camera)

Each camera has **one long MP4 holding all 50 tries back-to-back**, like one movie with 50 scenes. To find one try's clip you use **bookmarks** stored in the episodes list (meta/episodes).

## Load the episodes list and find the bookmarks
In Terminal: `conda activate lerobot`, then `python` (wait for `>>>`).
```python
import pandas as pd
eps = pd.read_parquet("hf://datasets/lerobot/svla_so101_pickplace/meta/episodes/chunk-000/file-000.parquet")
print([c for c in eps.columns if c.startswith("videos/")])
```
Each camera has 4 bookmark columns:

| Column | Meaning |
|---|---|
| videos/&lt;cam&gt;/chunk_index | Which chunk folder the MP4 is in (chunk-000) |
| videos/&lt;cam&gt;/file_index | Which MP4 file (file-000) |
| videos/&lt;cam&gt;/from_timestamp | Second where this try's clip **starts** inside the long MP4 |
| videos/&lt;cam&gt;/to_timestamp | Second where this try's clip **stops** |

## Two ways to measure a try's length
- **Data seconds** (the diary): rows (frames) ÷ 30 fps. Try 0: 303 ÷ 30 = **10.1 s**.
- **Video seconds** (the movie clip): to_timestamp − from_timestamp. Try 0: **10.1 s**.

If they match, video and data line up. First I compared the first 5 tries: all 5 matched.

## Full-dataset check: side camera (all 50 tries)
```python
side = "videos/observation.images.side/"
eps["video_sec"] = eps[side + "to_timestamp"] - eps[side + "from_timestamp"]
eps["data_sec"] = eps["length"] / 30
eps["gap"] = (eps["video_sec"] - eps["data_sec"]).abs()
print("biggest gap:", eps["gap"].max())
print("tries with gap over 0.1 s:", (eps["gap"] > 0.1).sum())
```
What each line does:
1. `side = ...` saves the start of the side camera's column names so I don't retype it.
2. `video_sec` = clip stop − clip start = video length of each try.
3. `data_sec` = frames ÷ 30 = data length of each try.
4. `gap` = how far apart they are; `.abs()` ignores plus/minus.
5. Print the biggest gap across all 50 tries.
6. Count tries with a gap over 0.1 s (the fail rule).

Result:
```
biggest gap: 2.6645352591003757e-14
tries with gap over 0.1 s: 0
```

## Up camera check
```python
up = "videos/observation.images.up/"
eps["up_sec"] = eps[up + "to_timestamp"] - eps[up + "from_timestamp"]
print("up camera tries with gap over 0.1 s:", ((eps["up_sec"] - eps["data_sec"]).abs() > 0.1).sum())
```
Result: `up camera tries with gap over 0.1 s: 0`

**Verdict: all 50 tries pass on both cameras.** My first real audit check run on a whole dataset.

## Key ideas
- **2.66e-14** is scientific notation for 0.0000000000000266, a tiny computer rounding crumb = effectively **zero**.
- **0.1 s limit** ≈ 3 frames (0.1 × 30). Gap under that = pass.
- **Gap = |video seconds − data seconds|.** It's 0 because the diary (data) and the camera started and stopped together.
- **"Try 0" is a name, not a time.** Python counts from 0: try 0 = 1st attempt, try 49 = 50th. Try 0 *lasted* 10.1 s. Others differ: try 1 = 266 frames ≈ 8.9 s, try 3 = 183 frames = 6.1 s.
- **Why it matters:** a robot learns by pairing a picture with the joint numbers from the same moment. If the video is shorter or shifted, it sees one moment but learns the move from another, so it learns wrong.
- **You don't watch all the videos.** Code checks all 50 in under a second; you only open flagged tries, check them, and write them up.
- **Limitation:** this checks the bookmarks only. Days 15–16 open the actual MP4 files (sync and corrupt-video checks).

## Examples that helped
- **Soccer game:** Person A writes a diary of a 90-minute game; Person B films it. Video 90 min = match = pass. Video only 60 min (camera died) = diary says "goal at minute 75" but the video has no minute 75 = fail.
- **Two stopwatches timing one runner:** data 10.1 s, video 10.1 s → 10.1 − 10.1 = 0 gap. Bad example: video stopped at 7.0 s → 10.1 − 7.0 = 3.1 s gap = fail (camera missed the last 3 seconds).

## My questions and how they got answered
1. **"How do they pass?"** Each try: diary length vs clip length; gap under 0.1 s = pass. All 50 had a gap of basically 0.
2. **"Give me a good example, I still did not catch it."** The soccer diary vs video example.
3. **"What does 303 lines at 30 per second = 10.1 s mean?"** The robot writes one line per camera picture, 30 per second. 30 lines = 1 s, 300 lines = 10 s, so 303 ÷ 30 = 10.1 s.
4. **"So it is try 0, why 10 seconds?"** "0" is the try's name (like a jersey number); 10.1 s is how long that first attempt took.
5. **"One more example why gap is 0."** The two-stopwatch example.
6. **"If there are 50 episodes, do I have to watch all the videos?"** No. Code checks all of them; I only watch flagged ones.

## In my words (checked)
"I have to check if the video matches the data. The video should be the same time as the data. If a try is flagged, I check it and document it." ✅

## Next: Day 5
Load a dataset in Python with LeRobot: print episodes, frames, fps, and one frame's keys.
