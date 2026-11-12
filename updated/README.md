# Depth-difference features (updated Python component)

This component translates feature assembly from the recovered project scripts `getDiff.m` and `buildDiff.m`, plus the deterministic probe-radius formula in `Test2nd.m`. It accepts depth/label arrays and returns numerical features and labels. It does not infer depth from a color image, train a classifier or restore the historical face-depth experiment.

## Setup and use

The helper requires Python 3.10+ and the standard library. Run tests from the repository root:

```sh
python3 -m unittest discover -s updated/tests -v
```

To import the helper, run Python from `updated/` and import `face_depth_features`. `get_diff(D, CM)` takes equally sized rectangular nested lists for a depth image and label map. `build_diff(frames)` accepts an iterable of `(D, CM)` pairs and concatenates their features/labels after replacing depth NaNs with zero.

[The notebook](notebooks/depth-features.ipynb) uses procedural arrays and IPython display. Open it in a local Jupyter environment or [in Colab](https://colab.research.google.com/github/twerdster/face-depth-estimation-from-a-single-color-image/blob/main/updated/notebooks/depth-features.ipynb). Local execution imports the sibling helper. In Colab, the setup cell downloads that helper from this repository; it does not download a dataset, trained model or credentials.

## Feature layout and behavior

Nonzero depth pixels are visited in MATLAB column-major `find` order. Each contributes a 21-by-35 patch of neighbor depth minus center depth. The patches are stacked vertically: `N` nonzero pixels produce `21*N` rows of 35 values and `21*N` labels. One output row is a patch row, not one whole pixel descriptor. Depth differences retain the input depth units; no millimeter calibration is supplied.

An out-of-image neighbor contributes zero. An in-image zero-depth neighbor contributes `0 - center_depth`; it is not masked out. Direct `get_diff` calls retain NaNs as the MATLAB helper does, while `build_diff` replaces them before assembly. The port adds rectangular-shape, equal-shape and positive-integer patch-extent checks. Default extents match the original; even custom extents follow the original colon expression and produce one extra offset.

`probe_radius_profile` returns the deterministic, unshuffled radius sequence. The MATLAB random probe shuffle, the fixed 502-frame training loop, `TreeBagger`, `getDepthFeatures` MEX code and missing calibration/model/data files are not ported.

## Recorded validation and limitations

[VALIDATION.json](VALIDATION.json) records 18 component unit tests and three notebook code cells passed on 2026-11-12 with Python 3.14.4 on macOS arm64. Tests check synthetic fixtures, layout/order, boundaries, label repetition, NaNs, validation errors and the probe-radius formula. The notebook is committed without saved outputs.

No MATLAB/Octave runtime was available, so these tests are not a cross-runtime numerical comparison. They do not establish training success, recognition/depth accuracy or reproduction of the historical experiment. Linux execution has not been recorded.

## Attribution

Claude Code drafted the helper and initial tests; Codex reviewed and completed the component for Aaron Wetzler in 2026. Original student and third-party credits remain unchanged. No blanket license is assigned to recovered or derived work.
