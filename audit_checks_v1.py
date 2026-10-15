"""audit_checks_v1.py: one script that runs all my automated QA checks.

It combines four Week 2 scripts into one file:
  check_episodes.py -> check_episodes()  (Checklist #1 and #2: all tries there, none empty)
  check_timing.py   -> check_timing()    (Checklist #4: steady timing, no skipped frames)
  check_actions.py  -> check_actions()   (Checklist #7: no dead or clipped joints)
  check_empty.py    -> check_empty()     (Checklist #7: no empty / junk tries)
Added on Day 15:
  check_sync()                           (Checklist #5: each camera's video matches the robot's clock)
Added on Day 16:
  check_videos()                         (Checklist #5b: every MP4 opens and every frame decodes)
Added on Day 17:
  check_endings()                        (Checklist #9 hint: tries that end in an unusual pose)
Added on Day 20:
  check_lengths()                        (Checklist #3: no try way shorter or longer than normal)
  check_action_state()                   (Checklist #6: the robot follows its orders)
Added on Day 21:
  check_duplicates()                     (Checklist #1c: no copy-paste tries saved twice)

Each check is a "function": a small machine you hand data to, and it hands
back two things: passed (True/False) and a short message explaining why.

Nothing about the dataset is typed in by hand (no 50 tries, no 30 fps, no
joint names). Everything is read from the dataset's own info.json, so the
same script works on a different dataset (that's Day 14).

Run in Terminal:
    conda activate lerobot
    python audit_checks_v1.py                              # default dataset
    python audit_checks_v1.py some-user/some-dataset       # any other LeRobot v3 dataset
    python audit_checks_v1.py --videos                     # also download + decode every video (slow)
    python audit_checks_v1.py some-user/some-dataset --videos
"""
import argparse
import hashlib
import json

import numpy as np
import pandas as pd
from huggingface_hub import HfFileSystem, hf_hub_download

DEFAULT_REPO = "lerobot/svla_so101_pickplace"

# --- Thresholds (the pass/fail rules). Change them here, in one place. ---
SKIP_FACTOR = 2.0     # a time step over 2x the normal beat = a skipped frame
SCALE_MAX = 100.0     # the +/-100 scale that LeRobot calibration usually uses
LIMIT_TOL = 0.1       # within 0.1 of +/-100 (99.9 to 100.1) = "at the limit"
CLIP_MAX_PCT = 1.0    # more than 1% of frames at the limit = clipped joint
DEAD_STD = 0.5        # a joint whose spread in a try is under 0.5 = dead
EMPTY_RATIO = 0.25    # a try moving under 25% of the typical try = empty
SYNC_MAX_GAP = 0.5    # video vs robot-clock difference over 0.5 s = out of sync
END_SPREAD_X = 4.0    # end pose more than 4x the usual spread from the typical end ...
END_MIN_POINTS = 10.0 # ... AND more than 10 points away = "look at this try"
LEN_MIN_X = 0.5       # a try under 0.5x the normal (median) length = too short
LEN_MAX_X = 2.0       # a try over 2x the normal (median) length = too long
AS_BIG_GAP = 20.0     # an order-vs-reality gap over 20 points = a "big gap" row
AS_MAX_MEAN = 15.0    # a joint whose AVERAGE gap is over 15 = not following orders
AS_MAX_SHARE = 0.10   # a joint with big gaps in over 10% of rows = not following orders


# =====================================================================
# LOAD: read the label on the box (info.json) and the two parquet files
# =====================================================================
def load(repo_id):
    """Download what we need from the Hugging Face Hub.

    Returns: info (dict from info.json), eps (one row per try),
             df (one row per frame).
    """
    fs = HfFileSystem()
    base = f"datasets/{repo_id}"

    # info.json = the label on the box: robot type, fps, counts, joint names
    with fs.open(f"{base}/meta/info.json") as f:
        info = json.load(f)

    # A big dataset can split its tables across several files
    # (chunk-000/file-000, file-001, ...). glob finds them all; concat glues them.
    def read_all(folder):
        paths = sorted(fs.glob(f"{base}/{folder}/**/*.parquet"))
        if not paths:
            raise FileNotFoundError(f"no parquet files found in {folder}/")
        return pd.concat([pd.read_parquet(f"hf://{p}") for p in paths], ignore_index=True)

    eps = read_all("meta/episodes")  # one row per try
    df = read_all("data")            # one row per frame
    return info, eps, df


def joint_names(info, key="action"):
    """Read the joint names from info.json -> features -> action -> names.

    Some datasets store a plain list, others wrap it like {"motors": [...]}.
    We also drop the ".pos" ending so the names are short and readable.
    """
    names = info["features"][key].get("names")
    if isinstance(names, dict):              # e.g. {"motors": [...]}
        names = next(iter(names.values()))
    if not names:                            # no names given: number them
        size = info["features"][key]["shape"][0]
        names = [f"joint_{i}" for i in range(size)]
    return [n.removesuffix(".pos") for n in names]


def split_joints(df, column, names):
    """Unpack a column that holds several numbers per frame into named columns."""
    return pd.DataFrame(df[column].tolist(), columns=names)


# =====================================================================
# CHECK 1: episode counts and integrity (Checklist #1 and #2)
# =====================================================================
def check_episodes(eps, expected_episodes=None, expected_frames=None):
    """Are all tries there (numbered 0..N-1, no gaps) and none empty?

    Like a book: every page must be there, in order, and none blank.
    expected_episodes / expected_frames come from info.json.
    """
    n = expected_episodes if expected_episodes is not None else len(eps)
    expected = list(range(n))                          # the perfect list 0..N-1
    actual = sorted(eps["episode_index"].tolist())     # the real try numbers
    empty = int((eps["length"] == 0).sum())            # tries with 0 frames

    problems = []
    if actual != expected:
        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        problems.append(f"missing tries {missing[:10]}" if missing else "")
        problems.append(f"unexpected tries {extra[:10]}" if extra else "")
        if not missing and not extra:
            problems.append("duplicate try numbers")
    if empty:
        problems.append(f"{empty} empty tries")
    if expected_frames is not None and int(eps["length"].sum()) != expected_frames:
        problems.append(f"frames add up to {int(eps['length'].sum())}, info.json says {expected_frames}")
    problems = [p for p in problems if p]

    if problems:
        return False, "; ".join(problems)
    return True, f"all {n} tries present (0-{n - 1}), none empty, shortest {int(eps['length'].min())} frames"


# =====================================================================
# CHECK 2: frame rates and timestamps (Checklist #4)
# =====================================================================
def check_timing(df, fps):
    """Does a new frame arrive every 1/fps seconds, like a steady drum beat?"""
    beat = 1 / fps
    # Time between each frame and the one before it, inside each try only
    # (groupby keeps tries apart, so the reset to 0 between tries isn't counted)
    step = df.groupby("episode_index")["timestamp"].diff()
    skipped = step > beat * SKIP_FACTOR

    avg, biggest = step.mean(), step.max()
    if skipped.sum() == 0:
        return True, f"steady at {fps} fps (avg step {avg:.5f} s, biggest {biggest:.5f} s), 0 skipped frames"
    bad_tries = sorted(df.loc[skipped, "episode_index"].unique().tolist())
    return False, f"{int(skipped.sum())} skipped frames in tries {bad_tries[:10]} (biggest step {biggest:.3f} s)"


# =====================================================================
# CHECK 3: action distributions (Checklist #7: dead or clipped joints)
# =====================================================================
def check_actions(df, names=None):
    """Any dead joint (never moves in a try) or clipped joint (stuck at +/-100)?"""
    if names is None:
        names = [f"joint_{i}" for i in range(len(df["action"].iloc[0]))]
    act = split_joints(df, "action", names)

    # Clipping: what % of frames sit right AT the +/-100 limit, per joint.
    # (Day 14 fix: some datasets go past 100, e.g. 104 or 123. A value that
    # can go past 100 is not stuck at 100, so only 99.9 to 100.1 counts.)
    clip_pct = ((act.abs() - SCALE_MAX).abs() <= LIMIT_TOL).sum() / len(act) * 100
    past_scale = [j for j in names if act[j].abs().max() > SCALE_MAX + LIMIT_TOL]
    clipped = clip_pct[clip_pct > CLIP_MAX_PCT]

    # Dead joints: spread (std) of each joint inside each try
    act["episode_index"] = df["episode_index"].values
    per_try = act.groupby("episode_index")[names].std()
    dead = (per_try < DEAD_STD).sum()
    dead = dead[dead > 0]

    problems = []
    for joint, count in dead.items():
        tries = per_try.index[per_try[joint] < DEAD_STD].tolist()
        problems.append(f"{joint} dead in {count} tries {tries[:10]}")
    for joint, pct in clipped.items():
        problems.append(f"{joint} clipped in {pct:.1f}% of frames")

    if problems:
        return False, "; ".join(problems)
    top = clip_pct.idxmax()
    note = f"; note: {', '.join(past_scale)} go past +/-100 (scale not capped at 100)" if past_scale else ""
    return True, f"no dead joints in any try; clipping under {CLIP_MAX_PCT:g}% (highest: {top} {clip_pct.max():.1f}%){note}"


# =====================================================================
# CHECK 4: empty and junk episodes (Checklist #7: robot moves)
# =====================================================================
def check_empty(df, names=None):
    """Does any try barely move? A "step counter" for the whole arm.

    Uses observation.state (where joints REALLY were). Falls back to
    action if a dataset has no observation.state column.
    """
    column = "observation.state" if "observation.state" in df.columns else "action"
    if names is None or len(names) != len(df[column].iloc[0]):
        names = [f"joint_{i}" for i in range(len(df[column].iloc[0]))]
    st = split_joints(df, column, names)
    st["episode_index"] = df["episode_index"].values

    # How far all joints moved since the previous frame, then total per try
    moves = st.groupby("episode_index")[names].diff().abs().sum(axis=1)
    total = moves.groupby(st["episode_index"]).sum()

    median = total.median()
    empty = total[total < median * EMPTY_RATIO]
    lowest = total.idxmin()

    if len(empty) == 0:
        return True, (f"0 empty tries; least-moving try {lowest} = "
                      f"{total.min() / median:.0%} of typical (median {median:.0f})")
    return False, f"{len(empty)} empty tries {empty.index.tolist()[:10]} (under {EMPTY_RATIO:.0%} of median {median:.0f})"


# =====================================================================
# CHECK 5: camera-robot sync (Checklist #5, added Day 15)
# =====================================================================
def check_sync(df, eps, fps):
    """Does each camera's video last as long as the robot's own clock says?

    Like lips and voice in a film: if they drift apart, the robot learns
    "move now" from an old picture.

    Robot clock span per try = last timestamp - first timestamp + one frame
    (the last frame also lasts 1/fps). E.g. try 0: 10.0667 - 0 + 0.0333 = 10.1 s.
    Video length per try = to_timestamp - from_timestamp (the bookmarks in
    the episodes table). We do this for EVERY camera the dataset has.
    """
    # Find the cameras: every "videos/<cam>/from_timestamp" column in eps
    cams = [c[len("videos/"):-len("/from_timestamp")]
            for c in eps.columns
            if c.startswith("videos/") and c.endswith("/from_timestamp")]
    if not cams:
        return False, "no camera bookmarks (videos/<cam>/from_timestamp) found, so sync can't be checked"

    # Robot clock span for each try, using the REAL timestamps (not frames / fps)
    span = df.groupby("episode_index")["timestamp"].agg(lambda t: t.max() - t.min() + 1 / fps)

    results, problems = [], []
    for cam in cams:
        v = f"videos/{cam}/"
        vid = (eps[v + "to_timestamp"] - eps[v + "from_timestamp"]).values
        # Line each try's video length up with the same try's clock span
        robot = span.reindex(eps["episode_index"]).values
        gap = abs(vid - robot)
        bad = eps["episode_index"][gap > SYNC_MAX_GAP].tolist()
        short = cam.removeprefix("observation.images.")
        results.append(f"{short} max gap {gap.max():.3f} s")
        if bad:
            problems.append(f"{short}: {len(bad)} tries over {SYNC_MAX_GAP:g} s {bad[:10]}")

    if problems:
        return False, "; ".join(problems)
    return True, f"{len(cams)} cameras in sync ({', '.join(results)}), 0 tries over {SYNC_MAX_GAP:g} s"


# =====================================================================
# CHECK 6: corrupted videos (Checklist #5b, added Day 16)
# =====================================================================
def check_videos(repo_id, info, expected_frames):
    """Does every camera's video actually open and play to the end?

    Like a scratched DVD that freezes halfway: the file looks fine in the
    folder list, but breaks when you play it. Days 4 and 15 only checked the
    bookmarks; this opens the real MP4 files and counts every frame.

    Slow: it downloads every video (about 86 MB for svla_so101_pickplace),
    so it only runs with --videos.
    """
    import av  # the video reader (installed with lerobot[dataset]); only needed here

    # Which cameras? info.json marks them with dtype "video"
    cams = [k for k, f in info["features"].items() if f.get("dtype") == "video"]
    if not cams:
        return False, "info.json lists no video features, so videos can't be checked"

    fs = HfFileSystem()
    results, problems = [], []
    for cam in cams:
        # A camera can be split into several files (file-000.mp4, file-001.mp4, ...)
        prefix = f"datasets/{repo_id}/"
        files = sorted(p[len(prefix):] for p in fs.glob(f"{prefix}videos/{cam}/**/*.mp4"))
        short = cam.removeprefix("observation.images.")
        if not files:
            problems.append(f"{short}: no MP4 files found")
            continue

        good = 0  # frames we managed to decode for this camera
        for name in files:
            path = hf_hub_download(repo_id, name, repo_type="dataset")  # cached after first time
            try:
                with av.open(path) as container:
                    for _frame in container.decode(video=0):
                        good += 1
            except Exception as err:  # noqa: BLE001 - a broken file is a finding
                problems.append(f"{short}: BROKEN in {name} after {good} frames ({err})")
                break
        else:
            if good != expected_frames:
                problems.append(f"{short}: readable {good} | expected {expected_frames}")
        results.append(f"{short} {good}/{expected_frames}")

    if problems:
        return False, "; ".join(problems)
    return True, f"{len(cams)} cameras fully readable ({', '.join(results)} frames)"


# =====================================================================
# CHECK 7: truncated episodes (Checklist #9 hint, added Day 17)
# =====================================================================
def check_endings(df, names=None):
    """Does any try END somewhere unusual? A hint that it may be cut off.

    Like a movie that stops right before the hero catches the ball. Most
    tries end the same way (arm folded home, gripper closed), like 50 kids
    going back to their seats. A try whose last pose is far from where the
    others end MIGHT have been cut off mid-task.

    This is a HINT, not proof: it returns "REVIEW" (watch these tries), never
    FAIL. Your eyes give the verdict.

    Rule, per joint: typical end = the median of all last poses; usual spread
    = a robust spread (median distance from the median, scaled x1.4826 so it's
    comparable to std, and not thrown off by one odd try). A try is flagged if
    a joint is more than END_SPREAD_X x spread AND more than END_MIN_POINTS
    away. Both are needed: the 10 points stops tiny wiggles on very still
    joints (spread near 0) from being flagged; the 4x stops normal variety on
    joints that naturally end in different places.
    """
    column = "observation.state" if "observation.state" in df.columns else "action"
    if names is None or len(names) != len(df[column].iloc[0]):
        names = [f"joint_{i}" for i in range(len(df[column].iloc[0]))]

    # The last frame of every try, and its joint positions
    last = df.groupby("episode_index").tail(1)
    end = pd.DataFrame(last[column].tolist(), columns=names, index=last["episode_index"].values)

    median = end.median()
    spread = (end - median).abs().median() * 1.4826
    limit = (spread * END_SPREAD_X).clip(lower=END_MIN_POINTS)   # the bigger of the two
    off = (end - median).abs() > limit

    flagged = off[off.any(axis=1)]
    if flagged.empty:
        return True, f"all {len(end)} tries end in the usual pose"
    details = []
    for ep, row in flagged.iterrows():
        joints = [f"{j} {end.loc[ep, j]:.1f} (usual {median[j]:.1f})" for j in names if row[j]]
        details.append(f"try {ep}: " + ", ".join(joints))
    word = "try" if len(flagged) == 1 else "tries"
    return "REVIEW", f"watch {len(flagged)} {word}, unusual end pose: " + "; ".join(details[:5])


# =====================================================================
# CHECK: odd lengths (Checklist #3, added Day 20)
# =====================================================================
def check_lengths(eps, fps):
    """Is any try way shorter or longer than the normal try?

    Like a height chart: most kids are about the same height, a 1-foot or
    9-foot "kid" is worth a second look. Normal = the median (middle) length,
    so one weird try can't drag it up or down. Too short = under LEN_MIN_X x
    normal (recording may have stopped early); too long = over LEN_MAX_X x
    normal (robot stuck, or nobody pressed stop).
    """
    lengths = eps["length"]
    med = lengths.median()
    lo, hi = med * LEN_MIN_X, med * LEN_MAX_X
    odd = eps[(lengths < lo) | (lengths > hi)]
    info = (f"normal {med:g} frames ({med / fps:.1f} s), range {int(lengths.min())}-{int(lengths.max())}, "
            f"limits {lo:.0f}-{hi:.0f}")
    if odd.empty:
        return True, f"no odd tries; {info}"
    short = odd["episode_index"][odd["length"] < lo].tolist()
    long_ = odd["episode_index"][odd["length"] > hi].tolist()
    parts = []
    if short:
        parts.append(f"{len(short)} too short {short[:10]}")
    if long_:
        parts.append(f"{len(long_)} too long {long_[:10]}")
    return False, "; ".join(parts) + f"; {info}"


# =====================================================================
# CHECK: action vs state (Checklist #6, added Day 20)
# =====================================================================
def check_action_state(df, names=None):
    """Does the robot do what it was told? Order (action) vs reality (state).

    Like telling a dog "sit" and checking it sits. Small gaps are normal, and
    short big gaps happen during fast moves while the arm catches up to its
    order. A joint whose gap is big on AVERAGE, or big in many rows, may have
    a broken motor or a heavy load.
    """
    if "observation.state" not in df.columns:
        return None, "skipped: no observation.state column, nothing to compare"
    act = np.stack(df["action"].values).astype(float)
    st = np.stack(df["observation.state"].values).astype(float)
    if act.shape[1] != st.shape[1]:
        return None, (f"skipped: action has {act.shape[1]} numbers but state has {st.shape[1]}, "
                      f"so they can't be compared joint by joint (check by hand)")
    if names is None or len(names) != act.shape[1]:
        names = [f"joint_{i}" for i in range(act.shape[1])]
    gap = pd.DataFrame(np.abs(act - st), columns=names)

    mean = gap.mean()
    share = (gap > AS_BIG_GAP).mean()
    bad_mean = mean[mean > AS_MAX_MEAN]
    bad_share = share[share > AS_MAX_SHARE]

    problems = []
    for joint, m in bad_mean.items():
        problems.append(f"{joint} mean gap {m:.1f} (limit {AS_MAX_MEAN:g})")
    for joint, sh in bad_share.items():
        problems.append(f"{joint} gaps >{AS_BIG_GAP:g} in {sh * 100:.1f}% of rows (limit {AS_MAX_SHARE * 100:g}%)")
    if problems:
        return False, "; ".join(problems)
    top = share.idxmax()
    return True, (f"robot follows orders; mean gap {mean.min():.1f}-{mean.max():.1f}, "
                  f"gaps >{AS_BIG_GAP:g} in at most {share.max() * 100:.1f}% of rows ({top})")


# =====================================================================
# CHECK: duplicate episodes (Checklist #1c, added Day 21)
# =====================================================================
def check_duplicates(df):
    """Is any try a copy-paste of another try?

    Day 21 "break it on purpose": I copied try 5 over try 6 and every other
    check still said PASS, because none of them compares tries WITH EACH
    OTHER. A copy is a perfectly normal-looking try. Like grading two
    identical essays separately: each one looks fine on its own.

    Fix: give each try a "fingerprint" (like a barcode) made from ALL its
    observation.state numbers. Two tries with the same fingerprint are the
    same try. The fingerprint itself means nothing; only matches matter.

    Limit: this only catches EXACT copies. A copy with tiny noise added
    gets a different fingerprint and slips through.
    """
    column = "observation.state" if "observation.state" in df.columns else "action"
    prints = {}
    for ep, rows in df.groupby("episode_index", sort=True)[column]:
        arr = np.ascontiguousarray(np.stack(rows.values))
        h = hashlib.sha1(str(arr.shape).encode() + str(arr.dtype).encode() + arr.tobytes()).hexdigest()
        prints.setdefault(h, []).append(int(ep))

    groups = [sorted(eps_) for eps_ in prints.values() if len(eps_) > 1]
    if not groups:
        return True, f"no copy-paste tries ({len(prints)} unique fingerprints)"
    groups.sort()
    details = "; ".join(f"{len(g)} identical tries: {g}" for g in groups[:10])
    return False, details


# =====================================================================
# RUN everything and print a one-page summary
# =====================================================================
def main():
    # Read the command line: an optional dataset name, and an optional --videos switch
    parser = argparse.ArgumentParser(description="Automated QA checks for a LeRobot v3 dataset")
    parser.add_argument("repo_id", nargs="?", default=DEFAULT_REPO)
    parser.add_argument("--videos", action="store_true",
                        help="also download and decode every video file (slow)")
    args = parser.parse_args()
    repo_id = args.repo_id
    print(f"Loading {repo_id} ...")
    info, eps, df = load(repo_id)

    fps = info["fps"]
    action_names = joint_names(info, "action")
    state_names = (joint_names(info, "observation.state")
                   if "observation.state" in info["features"] else action_names)

    # Run each check. If one crashes (e.g. a column is missing), record it as
    # FAIL with the error instead of stopping the whole audit.
    checks = [
        ("#1-2 Episodes", lambda: check_episodes(eps, info.get("total_episodes"), info.get("total_frames"))),
        ("#1c  Duplicates", lambda: check_duplicates(df)),
        ("#3   Lengths", lambda: check_lengths(eps, fps)),
        ("#4   Timing", lambda: check_timing(df, fps)),
        ("#5   Sync", lambda: check_sync(df, eps, fps)),
        ("#5b  Videos", lambda: check_videos(repo_id, info, info.get("total_frames", len(df)))),
        ("#6   Action/state", lambda: check_action_state(df, state_names)),
        ("#7   Actions", lambda: check_actions(df, action_names)),
        ("#7   Empty tries", lambda: check_empty(df, state_names)),
        ("#9   Endings (hint)", lambda: check_endings(df, state_names)),
    ]
    results = []
    for label, run in checks:
        if label.startswith("#5b") and not args.videos:
            results.append((label, None, "skipped (run with --videos)"))  # None = not run
            continue
        try:
            passed, message = run()
        except Exception as err:  # noqa: BLE001 - report, don't crash
            passed, message = False, f"could not run: {type(err).__name__}: {err}"
        results.append((label, passed, message))

    # ---- One-page summary ----
    line = "=" * 72
    print()
    print(line)
    print("ROBOT DATASET AUDIT: automated checks (audit_checks_v1)")
    print(line)
    print(f"Dataset:    {repo_id}")
    print(f"Robot type: {info.get('robot_type', 'unknown')}")
    print(f"Episodes:   {info.get('total_episodes', len(eps))}   "
          f"Frames: {info.get('total_frames', len(df))}   FPS: {fps}")
    print(f"Joints:     {', '.join(action_names)}")
    print("-" * 72)
    for label, passed, message in results:
        if passed is None:
            status = "SKIP"
        elif passed == "REVIEW":
            status = "REVIEW"   # a hint for a human, not a failure
        else:
            status = "PASS" if passed else "FAIL"
        print(f"{status:<6} {label:<19} {message}")
    print("-" * 72)
    # Skipped checks don't count. REVIEW counts as "not failed".
    ran = [p for _, p, _ in results if p is not None]
    n_fail = sum(1 for p in ran if p is False)
    n_review = sum(1 for p in ran if p == "REVIEW")
    verdict = "PASS" if n_fail == 0 else "FAIL"
    if n_review:
        print(f"OVERALL: {verdict} ({len(ran) - n_fail}/{len(ran)} automated checks did not fail: "
              f"{len(ran) - n_fail - n_review} PASS, {n_review} REVIEW)")
        print(f"*** HUMAN REVIEW NEEDED: watch the tries listed on the REVIEW line before signing off")
    else:
        print(f"OVERALL: {verdict} ({len(ran) - n_fail}/{len(ran)} automated checks passed)")
    print("Not automated yet: #8 camera clear, #10 label correct (manual review);")
    print("#9 is a hint only.")
    print(line)


if __name__ == "__main__":
    main()
