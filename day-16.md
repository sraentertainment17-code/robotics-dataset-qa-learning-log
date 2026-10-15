# Day 16: Corrupted videos ✅ (Oct 10, 2026)

## Goal
A broken (truncated) MP4 looks fine in the file list, then crashes the training loader halfway through. Open **every video**, count the frames it can actually read, and flag anything broken. This is the **first time we open the real MP4 files**: Days 4 and 15 only checked the **bookmarks** (where each clip starts and stops).

Setup: at the start of the session the coach re-copied the updated `audit_checks_v1.py` (5 checks, with `check_sync` from Day 15) to my laptop.

## Analogy: a scratched DVD
The DVD looks fine in its case and the menu works, but when you play it, it **freezes halfway**. A corrupted video is the same: the file is there, the size looks normal, but the computer can't read past a certain point.

## Step 1: Download the two videos
In Terminal: `conda activate lerobot`, then `python` (wait for `>>>`).
```python
from huggingface_hub import hf_hub_download
side = hf_hub_download("lerobot/svla_so101_pickplace", "videos/observation.images.side/chunk-000/file-000.mp4", repo_type="dataset")
up = hf_hub_download("lerobot/svla_so101_pickplace", "videos/observation.images.up/chunk-000/file-000.mp4", repo_type="dataset")
print(side)
```
- `hf_hub_download(...)` downloads one file from the Hub and saves it on my laptop. `repo_type="dataset"` tells it this is a dataset, not a model.
- Side camera: **45.5 MB**. Up camera: **40.1 MB**. Each one holds all 50 tries back-to-back (Day 4).
- `print(side)` shows where the file was saved: a path inside `~/.cache/huggingface/hub/...`. It's cached, so next time it doesn't download again.

## Step 2: Try to read every frame
```python
import av
for name, path in [("side", side), ("up", up)]:
    good = 0
    try:
        with av.open(path) as c:
            for frame in c.decode(video=0):
                good += 1
        print(name, "readable frames:", good, "| expected: 11939")
    except Exception as e:
        print(name, "BROKEN after", good, "frames:", e)
```
Press **Enter on the empty `...` line** to run it.

## Output
```
side readable frames: 11939 | expected: 11939
up readable frames: 11939 | expected: 11939
```
Both videos play all the way to the end: **11,939 frames each**, exactly the number of frames in the data. ✅ **PASS.**

## Every step explained
1. **`import av`**: loads PyAV, the video-reading toolbox (it came with `lerobot[dataset]` on Day 5).
2. **`for name, path in [("side", side), ("up", up)]:`**: do the block twice. The first time `name` = "side" and `path` = the side video file; the second time it's "up".
3. **`good = 0`**: start a counter at 0 for this camera. It counts frames we read successfully.
4. **`try:`**: "try the next steps, and if anything breaks, don't crash; jump to `except`."
5. **`with av.open(path) as c:`**: open the video file and call it `c` (the container). `with` closes it automatically when we're done.
6. **`for frame in c.decode(video=0):`**: decode (unpack) the pictures one by one from the first video track (`video=0`).
7. **`good += 1`**: add 1 to the counter for every picture that decoded fine.
8. **`print(name, "readable frames:", good, "| expected: 11939")`**: if we got to the end without breaking, print how many frames we read next to how many there should be (11,939 from info.json).
9. **`except Exception as e:`**: if anything broke while reading, come here instead. `e` holds the error message.
10. **`print(name, "BROKEN after", good, "frames:", e)`**: say which camera broke, after how many good frames, and why.

## How to read all of this
**Three kinds of lines in the Terminal:**

| You see | What it means |
|---|---|
| `>>> ` at the start | Python is ready; **you** type a new command here |
| `... ` at the start | Python is waiting for **more lines** of the same block (a loop, `try`, `with`); press Enter on an empty `...` to run the block |
| No `>>>` or `...` | **Output**: Python's answer |

**The indentation tree** (the spaces show what belongs inside what):
```
for name, path in ...           <- repeat for each camera
    good = 0                    <-   inside the loop
    try:                        <-   inside the loop
        with av.open(path) as c:    <- inside try
            for frame in ...:           <- inside with
                good += 1                   <- inside the inner loop (runs once per frame)
        print(... readable ...)     <- inside try, after the with is done
    except Exception as e:      <-   inside the loop, partner of try
        print(... BROKEN ...)       <- inside except (only runs if something broke)
```
4 more spaces = one level deeper, "belongs to the line above".

## "The video didn't fail, so explain FAIL to me first"
What a **broken** result would look like:

**Example 1: the file breaks partway**
```
up BROKEN after 6200 frames: Invalid data found when processing input
```
Read: the up video decoded 6,200 frames fine, then hit damaged data and couldn't go on. Everything after frame 6,200 (about tries 26–49) is lost.

**Example 2: the file ends early, no error**
```
side readable frames: 9000 | expected: 11939
```
Read: it played to the "end" without an error, but the end came too soon. 2,939 frames are missing, so the last tries have no pictures.

**Why a team cares:**
- **GPU hours wasted:** training runs for hours, then crashes when it reaches the broken part. That's compute time thrown away.
- **Crashes:** the training loader can stop the whole run on one bad file.
- **Wrong learning:** if the loader skips or repeats frames, the robot learns moves paired with the wrong pictures.

## In my words (checked)
> "A corrupted video is important for my team because it will freeze halfway through the video .If the team trains this kinda data ,it will be waste of time.And aslo the robot will learn wrong dataset and it is not safe for expensive robot to train this kinda data so i have to catch it for team before doing this"

Feedback: **great answer** ✅. Freezing, wasted time, wrong learning, and safety for an expensive robot: all the right reasons.

## Added to the tool: check_videos() and --videos
`audit_checks_v1.py` now has a 6th check, `check_videos(repo_id, info, expected_frames)` (the script is now 369 lines):
- Finds every camera from info.json (features with `dtype: "video"`).
- Finds every MP4 for that camera under `videos/` (a big dataset can split a camera into several files).
- Downloads each one with `hf_hub_download`, decodes it with `av`, and counts the frames.
- Compares the count to the total frames from info.json. A crash while reading = **BROKEN**.
- Returns (passed, message).

Because it downloads every video, it's **off by default** so the normal run stays fast (a few seconds). Turn it on with `--videos`:
```bash
python audit_checks_v1.py --videos
python audit_checks_v1.py some-user/some-dataset --videos
```
Without `--videos` the summary shows `SKIP  #5b  Videos  skipped (run with --videos)`, and a skipped check doesn't count toward the total.

Output on svla_so101_pickplace with `--videos` (about 19 s on the coach's computer):
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
PASS  #5b  Videos       2 cameras fully readable (up 11939/11939, side 11939/11939 frames)
PASS  #7   Actions      no dead joints in any try; clipping under 1% (highest: elbow_flex 0.7%)
PASS  #7   Empty tries  0 empty tries; least-moving try 24 = 77% of typical (median 860)
------------------------------------------------------------------------
OVERALL: PASS (6/6 automated checks passed)
Not automated yet: #3 odd lengths, #6 action vs state,
#8 camera clear, #9 task finished, #10 label correct (manual review).
========================================================================
```

**Making sure it can FAIL:** the coach cut a copy of the side video in half (a fake "scratched DVD") and fed it to the check:
```
side: BROKEN in videos/observation.images.side/chunk-000/file-000.mp4 after 5985 frames (Invalid data found when processing input)
```
That's exactly the Example 1 pattern from above, on a real broken file.

## Key ideas
- A file can look fine and still be broken. Only reading every frame proves it plays.
- readable frames should equal the total frames; fewer = truncated, an error = corrupted.
- Bookmarks (Days 4 and 15) check the plan; decoding (Day 16) checks the actual file.
- Slow checks go behind a switch (`--videos`) so the everyday run stays fast.

## Checklist progress
- #1, #2 Episodes: ✅ automated
- #4 Timing: ✅ automated
- #5 Sync: ✅ automated (Day 15)
- #5b Videos readable: ✅ now **automated** (with `--videos`)
- #7 Robot moves: ✅ automated
- #3, #6: not in the tool yet
- #8, #9, #10: manual review (Day 11)

## Next: Day 17
Truncated episodes: look at the last 2 seconds of a few tries, and flag tries whose final gripper state suggests they were cut off mid-task.
