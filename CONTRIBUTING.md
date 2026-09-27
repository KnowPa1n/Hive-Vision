# Contributing to Hive Vision

Thanks for helping. Two kinds of contributions are most useful: detector/model
data and code. Data submission has its own workflow — see
[Training-data workflow](docs/training_data.md). This page covers code.

## Scope

Hive Vision is a model-plus-advice project: published reference weights
(YOLOv8n ONNX, Limelight 3A SSD-MobileNetV2 TFLite), Control Hub OpenCV/Lab
pipelines, PC tooling, and the FTC-side `ftc_ball_chase_lib`. The API is small
by design. Before opening a PR, say what problem it solves — the tracker,
the docs, or the robot libraries.

## Setting up

```bash
pip install -r requirements.txt        # PC tooling (Python 3.10+)
```

The FTC-side library is standalone — no Python needed. Build/test it with the
laptop self-test:

```cmd
cd ftc_ball_chase_lib
\.compile_check.cmd -runall
```

## What a good PR looks like

- **One logical change per PR.** Fix the docs and the code in the same PR
  when they are coupled (e.g. a new class field with its reference entry).
- **Run the eval before and after** any detector or config change:
  `python cv/tools/eval_cv_vs_yolo.py` and
  `python lab/tools/eval_lab_vs_yolo.py` — see [README](README.md) for the
  exact commands. Report the numbers in the PR body.
- **Never re-order shipped class IDs or labels.** `yellow`, `red`, `blue`
  class order is load-bearing across the Limelight labels and the Control Hub
  pipelines.
- **Keep the performance table in README in sync** with any measured change.
  The numbers are candidate-level detector benchmarks, not robot results;
  keep the caveats with them.
- **Docs reorganize, don't prune.** When reworking a page, merge content
  rather than deleting it.

## Testing

- Pure-documentation PRs need no test run.
- Library changes: `\.compile_check.cmd -runall` (all tests must pass).
- Detector/tooling changes: run the relevant eval script on a short clip and
  paste the output. CI runs the eval smoke check on every PR — it fails on
  tooling regressions and prints the metrics for review.

## Licensing

MIT for code, docs, and configuration. YOLO model artifacts and
Ultralytics-dependent material are AGPL-3.0 — see
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). By contributing you agree to
release your contribution under those terms.