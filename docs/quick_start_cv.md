# Hive Vision — 5-minute quick start (Control Hub CV / HSV)

The model-free track: no Limelight, no TensorFlow, no model — a pure
color-threshold `VisionProcessor` runs on the Control Hub itself and reports
ball *candidates*.

> **Candidate detector, not a guaranteed detector.** Measured precision on the
> dev video: yellow 40%, red 26%, blue 66%. Treat every blob as a candidate —
> require 3–5 consecutive frames at the same normalized position before the
> robot acts on it.

## What you need

| Thing | What it's for |
|-------|---------------|
| `cv/TeamCode/BallBlobPipeline.java` + `cv/TeamCode/BallDetectorPipeline.java` | the `VisionProcessor` drop-in + the base class it extends |
| `cv/tools/hsv_tuned.json` | shipped HSV config (ranges + gates) |
| FTC SDK project with a USB webcam | `VisionPortal` + EasyOpenCV |

## 1. Copy the pipeline

Copy `cv/TeamCode/BallBlobPipeline.java` (the base class) **and**
`cv/TeamCode/BallDetectorPipeline.java` from this repo into your FTC
project's `TeamCode/` folder (same level as your OpModes).

## 2. Register it in an OpMode

```java
import org.firstinspires.ftc.vision.VisionPortal;
import org.firstinspires.ftc.robotcore.external.hardware.camera.WebcamName;
import org.opencv.core.Size;

BallDetectorPipeline baller = new BallDetectorPipeline();

VisionPortal portal = new VisionPortal.Builder()
        .setCamera(hardwareMap.get(WebcamName.class, "Webcam 1"))
        .setCameraResolution(new Size(1280, 720))
        .addProcessor(baller)
        .enableLiveView(true)
        .build();
```

The `"Webcam 1"` string must match your Driver Station camera config name.

## 3. Read detections each loop

```java
BallDetectorPipeline.BallBlob red = baller.bestOf(BallDetectorPipeline.BallColor.RED);
if (red != null) {
    telemetry.addData("red", "cx=%.2f cy=%.2f", red.cxNorm, red.cyNorm);
}
```

`bestOf(...)` returns `null` when no blob of that color passes the gates, and
a `BallBlob` with `cxNorm` / `cyNorm` (0–1 screen-relative, centered) otherwise.
Colors are `BallColor.YELLOW`, `BallColor.RED`, `BallColor.BLUE`.

## 4. Check your resolution

The shipped area constants were tuned at 1920×1080. At any other resolution,
scale them by the pixel-count ratio:

```
scale = (W_new * H_new) / (1920 * 1080)
```

At 1280×720 that's ×0.444 — `MIN_AREA_PX` 900 → 400, `MAX_AREA_PX` 12000 →
5300. Adjust the same three constants in `BallDetectorPipeline.java` before
deploying at a different resolution. The full table is in
[Set up the HSV track](detector_tracks/control_hub/hub_hsv_setup.md).

## 5. Verify in 5 minutes

1. Deploy the OpMode and open the Driver Station **camera stream** (live view).
2. Point the webcam at a yellow ball. You should see a colored outline box +
   centroid lock onto it.
3. Slide the ball across the view — `cxNorm` should move 0 → 1 across the frame
   (0.5 ≈ center).
4. Repeat for red and blue. If the wrong color lights up, keep the field
   white-balanced and re-check `BallColor`.
5. Once blobs track reliably, gate them in code: only act when a blob stays
   within a small `cxNorm`/`cyNorm` window for 3–5 frames.

## Troubleshooting

| Symptom | First thing to check |
|---------|----------------------|
| No blobs anywhere | Webcam name matches config; white balance on; `MIN_AREA_PX` too high for your resolution |
| Blobs flicker / appear everywhere | Field white balance; deep shadows (that's the [Lab](quick_start_lab.md) track's job); raise the per-frame frame-consistency gate |
| Wrong color detected | Keep red vs blue luminance distinct; retune with `python cv/tools/hsv_tuner.py path/to/frame.jpg` |

## You're ready when

- [ ] The live stream draws a box over each ball color
- [ ] `bestOf(...).cxNorm/cyNorm` track the ball across the frame
- [ ] The 3–5 frame confirmation gate keeps one target when balls move

Deeper: [Set up the HSV track](detector_tracks/control_hub/hub_hsv_setup.md),
the full report in [cv/README.md](https://github.com/sidhuharjas/Hive-Vision/blob/main/cv/README.md),
and why color-only tracks have limits in [Known limitations](known_limitations.md).