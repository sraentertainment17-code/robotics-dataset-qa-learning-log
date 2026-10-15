"""Day 12 check: empty and junk episodes (QA Checklist #7, robot moves).

A junk try is one where the robot barely moves, like someone pressing
record and then standing still. We use a "step counter" for the arm:
add up how much every joint moved from one frame to the next, then total
it for each try. Tries with a tiny total are flagged as empty.

We use observation.state (where the joints REALLY were), not action
(where they were told to go).

Run in Terminal:
    conda activate lerobot
    python check_empty.py
"""
import pandas as pd

EMPTY_RATIO = 0.25  # a try moving less than 25% of the median try = empty

# Load all the frames
df = pd.read_parquet(
    "hf://datasets/lerobot/svla_so101_pickplace/data/chunk-000/file-000.parquet"
)

# Split the 6 packed joint positions into 6 named columns
names = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll", "gripper"]
st = pd.DataFrame(df["observation.state"].tolist(), columns=names)
st["episode_index"] = df["episode_index"]

# How far all 6 joints moved since the previous frame (inside each try only)
moves = st.groupby("episode_index")[names].diff().abs().sum(axis=1)

# Step counter: total movement for each try
total = moves.groupby(st["episode_index"]).sum()

median = total.median()
limit = median * EMPTY_RATIO

print("Tries with the least movement (bottom 5):")
print(total.sort_values().head(5).round(0))
print("\nmedian (typical) movement:", round(median))
print(f"empty limit ({EMPTY_RATIO:.0%} of median):", round(limit))

empty = total[total < limit]
print("empty tries:", len(empty))

# Verdict
if len(empty) == 0:
    print("\nPASS: no empty tries; every try moves at least",
          f"{total.min() / median:.0%} of the typical amount")
else:
    print("\nFAIL: empty tries found (watch these in the viewer):",
          empty.index.tolist())
