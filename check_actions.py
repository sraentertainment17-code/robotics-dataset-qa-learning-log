"""Day 10 check: action distributions (QA Checklist #7, robot moves).

Looks for two kinds of bad joints:
  - DEAD joint: never changes during a try (like a stuck door hinge).
  - CLIPPED joint: jammed at its limit of +/-100 (like a volume knob stuck at
    max), so the real value is lost.

Run in Terminal:
    conda activate lerobot
    python check_actions.py
"""
import pandas as pd

LIMIT = 99.9       # at or beyond this (+ or -) counts as "at the limit"
CLIP_MAX_PCT = 1.0 # more than 1% of frames at the limit = clipping problem
DEAD_STD = 0.5     # a joint whose spread (std) in a try is below this = dead

# Load all the frames
df = pd.read_parquet(
    "hf://datasets/lerobot/svla_so101_pickplace/data/chunk-000/file-000.parquet"
)

# The action column packs 6 numbers per frame; split them into 6 columns
names = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll", "gripper"]
act = pd.DataFrame(df["action"].tolist(), columns=names)

# 1) Pooled summary: count, mean, std, min, 25%, 50%, 75%, max for each joint
print("Summary of all frames:")
print(act.describe().round(1))

# 2) Clipping: how many frames (and what %) sit at the +/-100 limit
at_limit = (act.abs() >= LIMIT).sum()
clip_pct = (at_limit / len(act) * 100).round(1)
print("\nFrames at the limit:")
print(pd.DataFrame({"frames": at_limit, "percent": clip_pct}))

# 3) Dead joints, checked per try (a pooled check can hide one frozen try)
act["episode_index"] = df["episode_index"]
per_try = act.groupby("episode_index").std()
dead = (per_try < DEAD_STD).sum()
print("\nTries where each joint is dead (std under", DEAD_STD, "):")
print(dead)

# Verdict (the final pass/fail decision)
clipped_joints = clip_pct[clip_pct > CLIP_MAX_PCT].index.tolist()
if dead.sum() == 0 and not clipped_joints:
    print(f"\nPASS: no dead joints in any try, clipping under {CLIP_MAX_PCT:g}% for every joint")
else:
    print("\nFAIL:")
    if dead.sum() > 0:
        for joint in names:
            bad = per_try.index[per_try[joint] < DEAD_STD].tolist()
            if bad:
                print(f"  dead {joint} in tries {bad}")
    if clipped_joints:
        print(f"  clipped joints (over {CLIP_MAX_PCT:g}% of frames at limit): {clipped_joints}")
