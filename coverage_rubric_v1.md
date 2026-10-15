# Coverage Rubric v1

**Purpose:** a clean dataset can still be **narrow**. This rubric scores how much **variety** a robot dataset has, so a team knows what their robot will (and won't) learn from it. It's advice, not PASS/FAIL.

**How to use:** look at the **first frame of at least 10 tries** spread across the dataset (pull frames straight from the MP4s, not a web viewer). Tally start positions, objects and lighting. Give **one score per category for the whole dataset** (not per try). Back it up with numbers where you can (brick location in pixels, average brightness, start pose from `observation.state`).

## The 3 categories

| Category | 1 = one dish | 2 = small menu | 3 = big menu |
|---|---|---|---|
| **Position** (where the object starts) | One spot, or almost the same spot every time | A handful of fixed spots (about 2–9); clear gaps in the workspace; little or no rotation | Many spots spread over the whole reachable table, including edges and different rotations |
| **Objects** (what gets picked) | One object | 2–3 objects, similar shape or size | Many objects: different shapes, sizes, colors, materials |
| **Lighting** (the room) | One lighting setup | 2 setups (for example daylight and lamp) | Many conditions: bright, dim, shadows, different light colors, different backgrounds |

**Total:** 3–9. **3–4 = narrow**, **5–7 = moderate**, **8–9 = broad**.

## Score: `lerobot/svla_so101_pickplace` (Oct 10, 2026)

Sample: first frames of tries 0, 5, 10, …, 45 (10 of 50), up and side cameras.

| Category | Score | Evidence |
|---|---|---|
| Position | **2** | Brick starts in **5 fixed spots** (far-left, far-right, middle-left, middle-right, near-right), each used for a block of tries. No near-left, no edge positions; mostly the same orientation. |
| Objects | **1** | One object: the pink brick. Same clear tray as the target in every try. |
| Lighting | **1** | One setup. Average brightness: up camera 154–163, side camera 113–123 (0–255 scale): small wobble only. |
| **Total** | **4 / 9** | **Narrow** |

Other notes:
- All 10 tries start in the same rest pose (`observation.state` frame 0: shoulder_lift ≈ -98.6, elbow_flex ≈ 99, gripper ≈ 1.5). Only the brick position varies.
- Tries 40 and 45: the brick is **hidden from the side camera** by the robot body at the start (checklist #8, camera clear).
- Caveat: 10 of 50 tries sampled; the unsampled tries may contain a few more positions.

**Team note:** "Brick starts in only 5 spots, one object, one lighting. A robot trained on this may fail if the brick, object or room changes. Recommend adding more positions, objects and lighting."

Suggested next recordings: brick in the missing areas (near-left, table edges, beside the tray) and rotated; 3–5 different objects (other colors, sizes, shapes); at least one dim and one side-lit session.
