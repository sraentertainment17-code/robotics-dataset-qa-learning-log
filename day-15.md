# Day 15: Camera-robot sync ✅ (Oct 9, 2026)

**Week 3 starts: QA Checks II, the subtle killers.**

## Goal
The video and the robot's numbers are recorded separately, so they can drift apart. A 1-second offset ruins imitation learning. Compare each try's **video length** to the **robot's own clock** and flag any mismatch over **0.5 s**. This is checklist **#5 (video vs. data)**, done the strict way.

## Analogy: lips and voice out of sync
You've seen a video where the voice comes a bit after the lips move. It feels wrong. For a robot it's worse: with a 1 s offset, it sees an **old picture** and learns "move now" from it. So it learns the wrong move for what it sees.

## The code
In Terminal: `conda activate lerobot`, then `python` (wait for `>>>`). Load `df` (all frames) and `eps` (episodes list) as before:
```python
import pandas as pd
df = pd.read_parquet("hf://datasets/lerobot/svla_so101_pickplace/data/chunk-000/file-000.parquet")
eps = pd.read_parquet("hf://datasets/lerobot/svla_so101_pickplace/meta/episodes/chunk-000/file-000.parquet")

span = df.groupby("episode_index")["timestamp"].agg(lambda t: t.max() - t.min() + 1/30)

for cam in ["side", "up"]:
    v = f"videos/observation.images.{cam}/"
    vid = (eps[v+"to_timestamp"] - eps[v+"from_timestamp"]).values
    gap = abs(vid - span.values)
    print(cam, "biggest gap:", gap.max().round(3), "| tries over 0.5 s:", (gap > 0.5).sum())
```
Reminder (again!): after the `for` loop Python shows `...`. Press **Enter on the empty `...` line** to run it.

## Line by line ("first explain detail of it")
1. **`span = df.groupby("episode_index")["timestamp"]...`**: the **robot's clock** for each try.
   - `groupby("episode_index")` splits the frames into their 50 tries.
   - `["timestamp"]` uses the robot's own time stamps.
   - `.agg(lambda t: t.max() - t.min() + 1/30)` does this math for each try: **last time − first time + one frame**. We add one frame (1/30 s) because the last picture also lasts 1/30 s before the try ends.
   - **Try 0 example:** first timestamp 0, last timestamp 10.0667 → 10.0667 − 0 + 0.0333 = **10.1 s**.
2. **`for cam in ["side", "up"]:`**: do the next lines twice, once for each camera.
3. **`v = f"videos/observation.images.{cam}/"`**: builds the start of that camera's column names, e.g. `videos/observation.images.side/`. The `f"...{cam}..."` drops the camera name into the text.
4. **`vid = (eps[v+"to_timestamp"] - eps[v+"from_timestamp"]).values`**: the **video length** of each try = where its clip stops − where it starts (the bookmarks from Day 4). `.values` turns it into a plain list of numbers.
5. **`gap = abs(vid - span.values)`**: for each try, video length − robot clock span. `abs` drops the minus sign, so "too long" and "too short" both count.
6. **`print(...)`**: shows the **biggest gap** across all 50 tries, and **how many tries** have a gap over 0.5 s (`(gap > 0.5).sum()` counts the Trues).

## Output
```
side biggest gap: 0.0 | tries over 0.5 s: 0
up biggest gap: 0.0 | tries over 0.5 s: 0
```
Both cameras are perfectly in sync with the robot's clock, in all 50 tries. ✅ **PASS.**

## Day 4 vs Day 15: what's the difference?
| | Day 4 | Day 15 |
|---|---|---|
| Robot side of the comparison | `length ÷ 30` (frame count ÷ fps) | Real timestamps: last − first + 1 frame |
| What it assumes | A perfect clock: every frame exactly 1/30 s | Nothing: uses the robot's real clock |
| What it can catch | Missing or extra frames vs video | Also **clock drift** (e.g. the robot's clock running slow) |
| Strength | A guess | **Proof** |

My reflection:
> "in day 4 , we only compare with video and time , day 15 you look at camera and robot sync together or not, we check the checklist"

Feedback: yes ✅. Day 4 = frame count ÷ 30, which is a **guess** (it assumes the clock is perfect). Day 15 = the robot's **real clock**, which is **proof**. This is checklist **#5 done the strict way.**

## In my words (checked)
> "Out of sync means video and robots are sync together , maybe something is lagging or delay .for example video is 1 second a head but robot move slow"

Feedback: the example is right ✅ (video 1 s ahead, robot lagging). One word fix: out of sync means the video and robot are **NOT** together. Why it hurts: the robot learns a move from the **wrong picture**.

## Added to the tool: check_sync()
`audit_checks_v1.py` now has a 5th check, `check_sync(df, eps, fps)` (the script is now 302 lines):
- Finds **every camera** in the episodes table by looking for `videos/<cam>/from_timestamp` columns, so it works whatever the cameras are called.
- Robot clock span per try = last − first timestamp + 1/fps (using the dataset's own fps, not 30).
- Video length per try = `to_timestamp − from_timestamp`, for each camera.
- Flags any try where they differ by more than **0.5 s** (`SYNC_MAX_GAP` in the thresholds block).
- Returns (passed, message), like the other checks.

It shows in the summary as **#5 Sync**, and #5 is gone from the "Not automated yet" list.

Tested on all 3 datasets, all **PASS 5/5**:

| Dataset | Cameras found | Biggest gap |
|---|---|---|
| lerobot/svla_so101_pickplace | side, up | 0.000 s |
| MaxT90/so101-pick-place | wrist, overhead | 0.000 s |
| lerobot/svla_so100_pickplace | top, wrist | 0.000 s |

Three datasets with three different sets of camera names, and the check found them all on its own.

Making sure it can FAIL: the coach cut 1 s off try 12's up-camera clip, in memory only → `FAIL: up: 1 tries over 0.5 s [12]`. With no camera columns at all → FAIL, "sync can't be checked" (an honest answer instead of a fake PASS).

New summary on svla_so101_pickplace:
```
========================================================================
ROBOT DATASET AUDIT: automated checks (audit_checks_v1)
========================================================================
Dataset:    lerobot/svla_so101_pickplace
Robot type: so100_follower
Episodes:   50   Frames: 11939   FPS: 30
Joints:     shoulder_pan, shoulder_lift, elbow_flex, wrist_flex, wrist_roll, gripper
------------------------------------------------------------------------
PASS  #1-2 Episodes     all 50 tries present (0-49), none empty, shortest 183 frames
PASS  #4   Timing       steady at 30 fps (avg step 0.03333 s, biggest 0.03333 s), 0 skipped frames
PASS  #5   Sync         2 cameras in sync (side max gap 0.000 s, up max gap 0.000 s), 0 tries over 0.5 s
PASS  #7   Actions      no dead joints in any try; clipping under 1% (highest: elbow_flex 0.7%)
PASS  #7   Empty tries  0 empty tries; least-moving try 24 = 77% of typical (median 860)
------------------------------------------------------------------------
OVERALL: PASS (5/5 automated checks passed)
Not automated yet: #3 odd lengths, #6 action vs state,
#8 camera clear, #9 task finished, #10 label correct (manual review).
========================================================================
```

## Key ideas
- Out of sync = video and robot numbers NOT lined up → the robot learns from the wrong picture.
- Use the robot's **real timestamps**, not frame count ÷ fps; that catches clock drift too.
- +1 frame: the last picture lasts 1/fps too.
- Find cameras from the data (column names), never type them in.
- Limitation: this still uses the **bookmarks**. Day 16 opens the actual MP4 files to make sure they're readable.

## Checklist progress
- #1, #2 Episodes: ✅ automated
- #4 Timing: ✅ automated
- #5 Video vs. data (sync): ✅ now **automated** (strict, real clock)
- #7 Robot moves (dead/clipped joints + empty tries): ✅ automated
- #3, #6: not in the tool yet
- #8, #9, #10: manual review (Day 11)

## Next: Day 16
Corrupted videos: open every video with OpenCV, count the frames it can actually read, and flag broken files.
