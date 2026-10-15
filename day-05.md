# Day 5: Loading the dataset with LeRobot ✅ (Oct 8, 2026)

## Goal
Load `lerobot/svla_so101_pickplace` with LeRobot's own loader (not pandas) and print 4 facts: episodes, frames, fps, and one frame's keys. Audits run as code, and every automated check starts from this loader.

## Step 1: Import the loader (and fix the first error)
In a new Terminal: `conda activate lerobot`, then `python` (wait for `>>>`).
```python
from lerobot.datasets.lerobot_dataset import LeRobotDataset
```
First try failed:
```
ImportError: 'datasets' is required but not installed
```
What it means: LeRobot needs an extra toolbox (the `datasets` package) to load datasets, and the basic `pip install lerobot` from Day 1 didn't include it.

Fix:
1. `exit()` to leave Python and get back to Terminal.
2. Install LeRobot with its dataset extras:
   ```bash
   pip install 'lerobot[dataset]'
   ```
   The quotes matter: without them, zsh treats the square brackets as a special pattern and errors.
   It installed datasets-4.8.5, av-15.1.0 (video reader), torchcodec-0.11.1 (video decoder) and others, and **downgraded pandas 3.0.6 → 2.3.3** so versions fit together. That's normal.
3. `python` again, re-run the import: it worked (no message = success).

Side note: a stray ` ,` typed afterward gave an `IndentationError`. Harmless: Python just didn't understand that line. Nothing broke.

## Step 2: Load the dataset
```python
ds = LeRobotDataset("lerobot/svla_so101_pickplace")
```
It downloaded about **86 MB**, including the videos. It's now saved in `~/.cache/huggingface`, so next time it loads from disk.

Warnings (both harmless for now):

| Warning | What it means |
|---|---|
| objc: Class AVFFrameReceiver is implemented in both ... | Two copies of the same video library (one bundled with `av`, one from conda). Python warns but works. |
| HF_TOKEN / unauthenticated requests | Not logged in to Hugging Face. Fine for public data; just lower download speed limits. |

**My confusion:** I thought it was still running because I saw `>>> nstruction complete`. The progress bars had drawn over the `>>>` prompt, hiding it.
**Lesson:** if the screen looks stuck after a download, look for a hidden `>>>` and press Enter. A fresh `>>>` means Python is ready.

## Step 3: The three big numbers
```python
print(ds.num_episodes)
print(ds.num_frames)
print(ds.fps)
```

| Fact | Result | Day 2 (pandas / info.json) |
|---|---|---|
| Episodes (tries) | 50 | 50 ✅ |
| Frames (pictures) | 11939 | 11,939 ✅ |
| fps | 30 | 30 ✅ |

Two different ways of reading the dataset agree. That agreement is itself an audit check: if they disagreed, something in the files would be wrong.

## Step 4: Open one moment (frame 0)
```python
frame = ds[0]
print(frame.keys())
```
`ds[0]` is like opening a photo album to page 0: you get everything recorded at that one moment.

| Key | Meaning |
|---|---|
| observation.images.up | The **picture** from the up camera at this moment (new: pandas didn't have this) |
| observation.images.side | The **picture** from the side camera at this moment (new) |
| action | The 6 joint numbers the robot is told to go to next (the order) |
| observation.state | The 6 joint numbers where the arm really is now (the reality) |
| timestamp | Time inside the try, in seconds (0.0 for frame 0) |
| frame_index | Page number inside the try |
| episode_index | Which try (0–49) |
| index | Page number across the whole dataset (0–11,938) |
| task_index | Which job, as a number (0) |
| task | The job written in words (new) |

**Big idea:** pandas (Day 3) gave **numbers only**. LeRobot gives **numbers + the matching camera pictures from the same moment**. That bundle is exactly what a robot policy learns from: "when the picture looks like this, move the joints like this." That's why the Day 4 sync check matters: if pictures and numbers drift apart, the robot learns the wrong move for a picture.

## Step 5: The task text
```python
print(frame["task"])
```
Result: `pink lego brick into the transparent box` (same as tasks.parquet on Day 2).

## Step 6: The shape of a picture
```python
print(frame["observation.images.side"].shape)
```
Result: `torch.Size([3, 480, 640])`
- **3** = color layers: red, green, blue (RGB)
- **480** = picture height in pixels
- **640** = picture width in pixels

Analogy: 3 stacked sheets of graph paper, each 480 squares tall and 640 wide; one sheet says how red each square is, one how green, one how blue. Stacked, they make the color photo.
Matches the camera size in info.json (640×480), another check that agrees. ✅

## My questions and how they got answered
1. **"I don't have a robot yet, is it okay?"** Yes. The plan uses data other people recorded. Auditing only needs a laptop.
2. **"Is it still running?"** (the `>>> nstruction complete` screen) It was finished; the progress bars hid the `>>>`. Press Enter to see a fresh prompt.

## In my words (checked)
My answer: "I think ds[0] gives the exact number of what happened when we collected data, if we're trying to find the information."
Review note: close ✅. More precisely, `ds[0]` is **one moment** (frame 0) that bundles the joint numbers + both camera pictures + the task. pandas showed only the numbers.

## Storage note
The dataset is cached in `~/.cache/huggingface` (about 86 MB).

## Next: Day 6
What "usable" means: the 85/15 rule. Write QA checklist v1: 8–10 checks, one sentence each, saved as a text file.
