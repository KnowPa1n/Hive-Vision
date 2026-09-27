# Known limitations & failure modes

Hive Vision's detectors are scored on real footage and the failure modes below
are the ones that actually show up — several are called out in the evaluation
reports. This page tells you which limit is hardware, which is detector, and
what the library already does about it.

> None of these are "the robot failed" excuses. They are the engineering
> reality of color- and shape-based detection on a real FTC field, and each one
> has a concrete mitigation.

## Detection limits

| Limitation | Why it happens | Recommended solution |
|------------|----------------|----------------------|
| **Extremely dark balls** | Deep shadow desaturates a ball to gray; no color-only detector can recover it (both HSV and Lab fail — Lab's own report shows this) | Neural detector (SSD on the Limelight 3A) — it uses shape + context, not just chroma |
| **Red false positives** | Red robot panels, tape, and field elements resemble the ball hue | `BallTracker.requireConfirmation(n)` (multi-frame confirmation) + target lock; raise `MIN_CONF`; bump threshold to 0.35–0.45 |
| **Extremely small / distant balls** | Below the blob-size band or the detector's pixel minimum | Higher-resolution model, closer approach (`FOLLOWER_APPROACH_DIST`), don't act beyond `MAX_PLAN_RANGE` |
| **Heavy motion blur** | Low exposure times + fast motion smudge small fast-moving balls | Neural detector; keep the camera framerate up; avoid acting on a single blurred frame (confirmation helps) |
| **Balls completely occluded by robots** | A robot can fully cover a ball; nothing sees through it | The tracker's lock + `predicted` coast keeps the last-known position while it's hidden for `LOCK_LOST_MS` |
| **Camera exposure changes** | White balance / exposure churn between the menu-lit practice and the match-lit field | Re-tune HSV/Lab in match lighting; `Lab`'s adaptive chroma floor is more forgiving than HSV |
| **New field lighting** | Every venue lights the field differently | Recalibrate the color tracks per venue; the neural detector is the stable across-lighting choice |
| **Two balls close together** | Nearest ball can flip-flop frame to frame | `BallTracker`'s angular + color-bound target lock (this is its primary job) |

## What your own evaluation showed

The reports behind the numbers (`cv/docs/cv_detector_report.md`,
`lab/docs/lab_detector_report.md`) document exactly the misses:

- **HSV yellow misses** are frequently the *wrong yellow blob being selected* —
  a selection problem, not a "no detection" problem. The target lock + a
  nearest/first-in-color policy is the mitigation.
- **Blue misses** are usually small or blurred balls near the horizon — a
  resolution/geometry limit.
- **Red produces the most false positives** because the field and robot are
  full of red-adjacent colors. The color-bound lock limits it, and multi-frame
  confirmation is the direct fix.
- **Dark balls are physically indistinguishable from gray** in Lab chroma — no
  color-only detector can recover them. Only the neural detector's shape + CNN
  context handles that.

## How the library already fights each one

| Mechanism | Where | What it does |
|-----------|-------|--------------|
| Target lock (angular + color-bound) | `BallTracker` | stops two-ball flip-flop and color theft |
| Multi-frame confirmation | `BallTracker.requireConfirmation(n)` | holds off acting until the same ball is seen N frames — the direct fix for single-frame false positives |
| `MIN_CONF` / staleness gate | `BallTracker` | never acts on a low-confidence or stale frame |
| `predicted` coasting | `BallTracker` | keeps facing a briefly-hidden locked ball instead of re-targeting |
| Camera-only final approach | `BallChaseFollower` | last inches are driven off `tx`/`ty`, so localization/geometry error stops mattering at pickup |

## Honest caveats

- The SSD (Limelight 3A) model is verified on PC runners; confirm it loads and
  reports on a real 3A before match day — see the
  [setup page](detector_tracks/limelight_3a_ssd/limelight_3a_setup.md).
- Detection metrics are **candidate-detection numbers against YOLO reference
  detections**, not end-to-end pickup success. Measure pickups on your own
  robot once the targets lock.
- "Shadow-robust" means *more robust than HSV* — it does not mean shadow-proof.