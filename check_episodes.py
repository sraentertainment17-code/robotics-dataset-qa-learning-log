"""Day 8 check: episode counts and integrity (QA Checklist #1 and #2).

Asks two questions:
  1. Are all tries there, numbered 0..49 with no gaps?
  2. Does every try have more than 0 frames?

Run in Terminal:
    conda activate lerobot
    python check_episodes.py
"""
import pandas as pd

# Load the episodes list (one row per try)
eps = pd.read_parquet(
    "hf://datasets/lerobot/svla_so101_pickplace/meta/episodes/chunk-000/file-000.parquet"
)
print("tries in the list:", len(eps))

# Check 1: no gaps. Compare the real try numbers to the perfect list 0..49
expected = list(range(50))
actual = sorted(eps["episode_index"].tolist())
print("numbers run 0..49 with no gaps:", actual == expected)

# Check 2: no empty tries (0 frames)
empty = (eps["length"] == 0).sum()
print("empty tries:", empty)
print("shortest try (frames):", eps["length"].min())

# One PASS/FAIL answer
if actual == expected and empty == 0:
    print("PASS: all 50 episodes present, none empty")
else:
    print("FAIL: missing or empty episodes found")
