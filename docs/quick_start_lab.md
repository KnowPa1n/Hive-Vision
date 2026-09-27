# Hive Vision — 5-minute quick start (Control Hub Lab)

The shadow-robust, model-free track: CIELAB chromaticity (hue + an adaptive
chroma floor) separates "what color" from "how bright", so a ball sitting in
a mid shadow keeps its hue — where the HSV track reads it as a different
color, Lab mostly still works.

> **Candidate detector, not a guaranteed detector.** Same contract as the HSV
> track — confirm each blob across 3–5 frames before the robot acts.

## What you need

| Thing | What it's for |
|-------|---------------|
| `lab/TeamCode/LabBallDetectorPipeline.java` | the `VisionProcessor` drop-in |
| `lab/tools/lab_tuned.json` | shipped learned constants |
| FTC SDK project with a USB webcam | `VisionPortal` + EasyOpenCV |

## 1. Copy the pipeline

Copy `lab/TeamCode/LabBallDetectorPipeline.java` into your FTC project's
`TeamCode/` folder.

## 2. Register it in an OpMode

```java
import org.firstinspires.ftc.vision.VisionPortal;
import org.firstinspires.ftc.robotcore.external.hardware.camera.WebcamName;
import org.opencv.core.Size;

LabBallDetectorPipeline pipeline = new LabBallDetectorPipeline();

VisionPortal portal = new VisionPortal.Builder()
        .setCamera(hardwareMap.get(WebcamName.class, "Webcam 1"))
        .setCameraResolution(new Size(1280, 720))
        .addProcessor(pipeline)
        .build();
```

## 3. Read detections each loop

```java
LabBallDetectorPipeline.BallBlob ball = pipeline.bestOf(LabBallDetectorPipeline.BallColor.YELLOW);
if (ball != null) {
    telemetry.addData("ball", "cx=%.2f cy=%.2f", ball.cxNorm, ball.cyNorm);
}
```

`bestOf(...)` returns `null` when nothing of that color passes the gates, and
a `BallBlob` with `cxNorm` / `cyNorm` (0–1 screen-relative, centered)
otherwise. Colors are `BallColor.YELLOW`, `BallColor.RED`, `BallColor.BLUE`.

## 4. Resolution — nothing to do

Unlike the HSV track, the Lab area gates are stored per-1080p and scale
**automatically** to the live camera resolution, so 1280×720 just works.

## 5. Verify in 5 minutes

1. Deploy the OpMode and open the Driver Station **camera stream**.
2. Point the webcam at a yellow ball — first in full light, then with the ball
   pushed partly into a shadow. The blob should stay on the ball in both.
3. Slide it across the view: `cxNorm` should move 0 → 1 across the frame.
4. Repeat for red and blue.
5. Gate in code like the HSV track: only act on a blob that keeps its
   `cxNorm`/`cyNorm` position for 3–5 consecutive frames.

## Troubleshooting

| Symptom | First thing to check |
|---------|----------------------|
| No blobs anywhere | Webcam name matches config; white balance on; `MIN_L` floor too high for your lighting |
| Same as HSV track | That's expected on a stable-lighting field — the two should agree |
| A ball deep in shadow is missed | A ball so dark it loses chroma entirely is beyond *any* color-only detector — that case belongs to the [Limelight 3A track](quick_start.md) |

## You're ready when

- [ ] The live stream keeps a blob on a ball in both light and mid-shadow
- [ ] `bestOf(...).cxNorm/cyNorm` track the ball across the frame
- [ ] The 3–5 frame confirmation gate holds one target while balls move

Deeper: [Set up the Lab track](detector_tracks/control_hub/hub_lab_setup.md),
the dark-frame head-to-head in
[lab/docs/lab_detector_report.md](https://github.com/sidhuharjas/Hive-Vision/blob/main/lab/docs/lab_detector_report.md),
and the [Known limitations](known_limitations.md) page.