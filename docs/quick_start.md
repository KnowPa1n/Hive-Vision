# Hive Vision — 5-minute quick start (Limelight 3A)

The neural track: a Limelight 3A runs the SSD detector on its own CPU, and
your code reads one chosen ball per frame. This is the most capable path —
the only one that understands shape, so shadows and dark balls still work.

> Looking for a model-free track you can run on a plain Control Hub + webcam
> with no Limelight? See the
> [Control Hub CV (HSV)](quick_start_cv.md) and
> [Control Hub Lab](quick_start_lab.md) quick starts instead.

> **Goal:** by the end of this page you have a working `BallTracker` (or the
> full `BallChaseFollower` chase) and you can read the current target from
> Java. That's the whole point — not just "boxes on a stream", but a target
> your code can act on.

## What you need

| Component | Version tested by this repo |
|-----------|-----------------------------|
| FTC SDK (RobotCore / Hardware) | **11.2.1** (11.x expected; older must be checked) |
| Pedro Pathing | **2.1.2** (2.x expected) — only for the auto/pathing variants, not for plain tracking |
| Limelight 3A | 3A (SSD neural detector on its own CPU) |
| Java / Android Studio | FTC's bundled toolchain |
| The library | `ftc_ball_chase_lib/` in this repo |

If you use different versions, **compatibility is not guaranteed** — this repo
compiles and is self-tested against exactly the versions above.

## 1. Add the library to your project

Copy the ship-ready classes into your FTC `TeamCode` source tree:

```text
TeamCode/src/main/java/org/firstinspires/ftc/teamcode/
    final/HiveConfig.java
    final/BallTracker.java
    final/BallChaseController.java
    final/BallChaseFollower.java
    final/BallHunt.java
    final/RobotTestBench.java        (bench opmode — optional but recommended)
    final/BallMath.java
    (wrapper/…)                      (the fluent verb API — optional)
```

Then open the project in Android Studio, let Gradle sync, and build. If the
project doesn't compile, verify your FTC SDK and Pedro versions **before**
troubleshooting Hive Vision itself.

## 2. Connect the Limelight 3A

1. Plug the 3A's USB-C into a **blue (USB 3.0)** port on the Control Hub.
   It runs the detector on its own CPU — no extra coprocessor needed.
2. Open `http://limelight.local:5801` (or use Limelight Hardware Manager).
3. In the **settings**, set your team number + a hostname, then in your
   detector pipeline slot:
   - Pipeline type = **Neural Detector**
   - Upload `neural-net/weights/best_limelight3a_ssd_mobilenetv2_300x300.tflite`
   - Upload `neural-net/weights/labels.txt` (**keep the shipped order** —
     `yellow_pollen`, `red_nectar`, `blue_nectar`)
   - Runtime engine = **CPU** (leaving "Coral" on is the #1 way to see nothing)
   - Detection threshold = **0.35–0.45**
   - Input resolution = **300 × 300**

Full walkthrough (first-run settings, troubleshooting, staleness gotchas):
[Set up the Limelight 3A](detector_tracks/limelight_3a_ssd/limelight_3a_setup.md).

> **Verify at this step.** A box + class label should appear over each ball in
> the web UI stream. If boxes don't show here, the pipeline — not your code —
> is the problem. Fix it before writing Java.

## 3. Wire the device name

In the Driver Station **Configure** app, add a `Limelight3A` device. The name
must match `HiveConfig.LIMELIGHT_NAME` (`"limelight"` by default). If you
rename it, change it in exactly one place: `HiveConfig`.

```java
Limelight3A limelight = hardwareMap.get(Limelight3A.class,
        org.firstinspires.ftc.teamcode.HiveConfig.LIMELIGHT_NAME);
limelight.pipelineSwitch(org.firstinspires.ftc.teamcode.HiveConfig.LIMELIGHT_PIPELINE);
limelight.setPollRateHz(org.firstinspires.ftc.teamcode.HiveConfig.LIMELIGHT_POLL_RATE_HZ);
limelight.start();
```

## 4. Calibrate the camera

Open `HiveConfig.java` and measure the settings for **your** mount (robot →
camera). The five that matter most:

| Setting | What you measure | Example (this repo's defaults) |
|---------|------------------|--------------------------------|
| `CAM_H` | floor → camera **lens center**, in | `9.2` |
| `BALL_H` | floor → **center** of the game element, in | `3.0` |
| `CAM_PITCH_DEG` | camera's tilt **below horizontal** | `25.0` |
| `CAM_X_OFFSET` | camera FORWARD of robot center, in | `0.0` |
| `CAM_Y_OFFSET` | camera LEFT of robot center, in (− = right) | `0.0` |
| `HFOV_DEG` / `VFOV_DEG` | horizontal / vertical field of view | `54.5` / `42.0` |

The literal how-to for each measurement lives in
[Calibration](calibration.md) — measure the lens center, not the enclosure,
and the ball's *center*, not its top.

> **Don't copy numbers from another team's robot.** A wrong `CAM_PITCH_DEG` is
> the classic failure: the distance estimate drifts with target position and
> the robot drives past balls.

## 5. First test: run the bench, don't write code

Push `RobotTestBench` (it's already in `final/`) to the Control Hub. Select the
**DETECT** test with the left bumper and hold **A**:

- D-pad picks the class filter (UP red, DOWN blue, LEFT red+blue, RIGHT all)
- **A** `lockOn` the nearest visible ball, **B** drops the lock
- **Y** arms 4-frame confirmation, right bumper disarms — watch
  `confirm confirming streak=2/4` → `CONFIRMED` as a ball sits still

You want to see a moving `target` line:

```text
target: cls=1 tx=-8.4 ty=+3.2 dist=18.7 conf=0.91
lock:   LOCKED (confirm streak 4/4)
```

The robot is done with this test when the `target` stays on one ball while
balls move in view and `tx` sign matches which side a ball is on.

## 6. Your first real program

Once DETECT tracks, the smallest real program is the fluent one-liner, which
drives the whole collect by itself (it owns `follower.update()` for you):

```java
@Autonomous
class SimpleRedCollect extends LinearOpMode {
    @Override public void runOpMode() {
        Follower follower = FtcConfig.buildFollower(this);   // your team's follower
        Limelight3A limelight = hardwareMap.get(Limelight3A.class,
                org.firstinspires.ftc.teamcode.HiveConfig.LIMELIGHT_NAME);
        limelight.start();

        int picked = new org.firstinspires.ftc.teamcode.BallHunt(follower, limelight, intake)
                .reds().collect(2).within(20)
                .go(this);   // blocking: drives, picks 2 red balls, hands back

        // ...then drive to the backdrop and score them...
    }
}
```

Verb meanings: `.reds()`/`.blues()`/`.yellows()`/`.alliance()`/`.everything()`
color filter · `.collect(n)` balls · `.within(sec)` time budget ·
`.go(opMode)` = the blocking runner.

Prefer loop-driven control (auto + teleop)? Use `BallChaseController` for a
pure camera chase with no odometry, or `BallChaseFollower` state machine for a
Pedro-pathing auto — see the [API tab](../api/README.md).

## 7. Verify the three things that break you

1. **Target selection** — the robot consistently picks the intended color and
   doesn't flip-flop between two equal-range balls. (The tracker's target lock
   exists for exactly this; the Y-button confirmation strengthens it.)
2. **Distance** — put a ball at a known 24 in; the estimate should read 23–25.
   A large/proportional error means wrong camera geometry.
3. **Directions** — move a ball left, `tx` goes left; the robot turns toward
   it. If the robot drives the opposite way, **stop and fix the coordinate
   transform** — do not "fix" it by flipping random signs.

The full sign conventions are drawn in [Calibration](calibration.md).

## 8. Progress to a full robot test

Work each layer independently, in this order:

```text
Limelight sees target?        ─ no ─► fix the pipeline (web UI)
        │
        ▼ yes
Tracker selects the right ball ─ no ─► fix class filter / MIN_CONF
        │
        ▼ yes
Distance estimate reasonable    ─ no ─► fix CAM_PITCH_DEG / CAM_H / BALL_H
        │
        ▼ yes
Target lock stays stable        ─ no ─► raise CONFIRM_FRAMES / LOCK_GATE_DEG
        │
        ▼ yes
Robot approaches without oscillating
        │
        ▼ yes
Intake actually acquires the ball
```

**Do not start by testing the whole autonomous routine.** Each layer above is
independently debuggable; `RobotTestBench` is built to walk exactly this
progression on the real robot.

## Troubleshooting in 5 minutes or less

| Symptom | First thing to check |
|---------|----------------------|
| No detections anywhere | Engine = **CPU**? Threshold 0.35–0.45? Input 300×300? Boxes in the web UI? |
| Detections OK, `update()` returns nothing | Device name mismatch; `staleness > MAX_STALENESS_MS`; too few frames (try `CONFIRM_FRAMES = 0`) |
| Distance wrong | `CAM_PITCH_DEG` first, then `CAM_H`/`BALL_H`, then offsets |
| Switches between two balls | Target lock should already stop this — check `LOCK_GATE_DEG`, or raise confirmation |
| Robot drives the wrong direction | Coordinate sign conventions (see [Calibration](calibration.md)) |

## You're ready when

- [ ] The web UI shows boxes over balls
- [ ] `RobotTestBench` DETECT locks one ball and keeps it
- [ ] The one-liner `BallHunt` collects balls on the bench
- [ ] Distance and direction checks pass on the real robot

From here, the deep material: [Which detector track?](detector_tracks/),
[Collecting training data](training_data.md), and the [API tab](../api/README.md).