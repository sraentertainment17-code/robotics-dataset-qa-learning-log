"""Day 9 check: frame rates and timestamps (QA Checklist #4).

At 30 fps a new frame should arrive every 1/30 s (0.0333 s), like a steady
drum beat. This script measures the time step between frames inside each try
and counts any "skipped frames" (a step more than double the normal beat).

Run in Terminal:
    conda activate lerobot
    python check_timing.py
"""
import pandas as pd

FPS = 30                 # frames per second (from info.json)
BEAT = 1 / FPS           # normal time between frames: 0.0333 s
SKIP_LIMIT = 2 / FPS     # a step bigger than this = a skipped frame

# Load all the frames (one row per frame, all 50 tries)
df = pd.read_parquet(
    "hf://datasets/lerobot/svla_so101_pickplace/data/chunk-000/file-000.parquet"
)
print("frames:", len(df))
print("tries:", df["episode_index"].nunique())

# Time step between each frame and the one before it, inside each try only.
# groupby("episode_index") keeps tries separate, so the jump from the end of
# one try back to 0 at the start of the next is not counted.
df["step"] = df.groupby("episode_index")["timestamp"].diff()

print("average step (s):", df["step"].mean(), " expected:", BEAT)
print("biggest step (s):", df["step"].max())

skipped = (df["step"] > SKIP_LIMIT).sum()
print("skipped frames (step over 2/30 s):", skipped)

# One PASS/FAIL answer
if skipped == 0:
    print("PASS: timing is steady at", FPS, "fps, no skipped frames")
else:
    bad_tries = sorted(df.loc[df["step"] > SKIP_LIMIT, "episode_index"].unique().tolist())
    print("FAIL: skipped frames found in tries", bad_tries)
