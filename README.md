# Face Depth Estimation from a Single Color Image

[![New!](updated/assets/new-badge.svg)](updated/README.md#updated-and-ported-for-modern-hardware) [Updated and ported for modern hardware](updated/README.md#updated-and-ported-for-modern-hardware)

*Historical project reference follows. Current builds and results are in the updated section above.*

![Original archived project figure](assets/project.jpg)

![MATLAB original](https://img.shields.io/badge/Original-MATLAB-0076A8) ![Python update](https://img.shields.io/badge/Updated-Python_3-3776AB) ![Partial archive](https://img.shields.io/badge/Archive-partial-6c757d)

The historical project title describes the aim of estimating face depth from a color image. The [archived project description](https://twerdster.github.io/#face-depth-estimation-from-a-single-color-image) describes random-forest facial-region classification using paired color/depth images of a painted mannequin face; the recovered `buildDiff.m` assembles labeled depth-difference features and trains a `TreeBagger` classifier. The repository preserves three MATLAB research scripts and an updated Python implementation of their depth-difference feature assembly. It does not include a trained classifier or a complete color-to-depth system.

Student: Tova Krakauer. Supervision: Aaron Wetzler.

*The figure is unchanged imagery from the archived project page, not output from the Python component.*

## What is available

[Original MATLAB source](source/original/) contains `Test2nd.m`, `buildDiff.m` and `getDiff.m`. Their recovered bytes are unchanged; [source provenance](source/PROVENANCE.json) records the hashes. The scripts reference image/depth data, calibration, features and classifiers that are absent.

The [updated helper](updated/face_depth_features.py) takes depth images and matching label maps as nested Python lists. For each nonzero depth pixel it builds a 21-by-35 neighborhood of depth differences, stacks those patches vertically, and repeats the center label for each patch row. It also implements the deterministic probe-radius formula from `Test2nd.m`. It does not train `TreeBagger`, predict regions or estimate depth from a new color image.

## Use the Python component

Python 3.10 or newer is required; the helper uses only the standard library. Run from the repository root:

```sh
python3 -m unittest discover -s updated/tests -v
```

[Open the notebook](updated/notebooks/depth-features.ipynb) locally with Jupyter/IPython or [in Colab](https://colab.research.google.com/github/twerdster/face-depth-estimation-from-a-single-color-image/blob/main/updated/notebooks/depth-features.ipynb). It uses procedural arrays without a model or dataset. In Colab, its setup cell downloads the Python helper from this repository at runtime. The [component guide](updated/README.md) explains input indexing, output layout and the notebook's Colab helper download.

## Validation and limitations

The [2026-11-12 execution record](updated/VALIDATION.json) reports 18 component unit tests and three notebook code cells executed on macOS arm64 with Python 3.14.4. The tests check synthetic fixtures, patch/label layout, column-major traversal, boundary behavior, NaN handling and the radius formula. They are component tests, not classifier training, recognition accuracy or a face-depth benchmark.

MATLAB/Octave was unavailable, so there is no cross-runtime numerical comparison. The historical scripts require MATLAB image-processing, camera-calibration and `TreeBagger`/`predict` routines, plus missing calibration, data, learned-model files and the `getDepthFeatures` MEX helper. They contain fixed paths and file writes that must be reviewed before use. The Python helper does not reproduce the 502-frame training loop or MATLAB random probe shuffle. Linux execution has not been recorded.

## Original code and updated work

The helper and initial tests were drafted with Claude Code and reviewed/completed with Codex for Aaron Wetzler in 2026. This is a component port with added input checks. Original student and third-party notices remain unchanged; no blanket license is assigned. Authors can open an issue to contribute changes, correct attribution or request removal.

## Links

- [Project entry on Aaron Wetzler's website](https://twerdster.github.io/#face-depth-estimation-from-a-single-color-image)
