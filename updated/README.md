# Updated Python component

Feature assembly from Tova Krakauer's recovered MATLAB research source.

This is a reviewed component port for Python 3.10+, using only the standard library. The Jupyter notebook additionally uses IPython for display. The complete historical application is not restored.

## Run

~~~sh
python3 -m unittest discover -s updated/tests -v
~~~

Open [the notebook](notebooks/depth-features.ipynb) locally or [in Colab](https://colab.research.google.com/github/twerdster/face-depth-estimation-from-a-single-color-image/blob/main/updated/notebooks/depth-features.ipynb). Local execution imports the sibling helper; Colab downloads only that helper from this repository. No datasets, models or service credentials are needed.

## Differences from the original

The historical 21-by-35 patches are stacked vertically, not flattened into
one row per pixel. Nonzero pixels follow MATLAB column-major find order. Outside
the image the feature is zero; an in-image zero depth gives zero minus the center
depth. build_diff replaces NaNs before feature construction, as the original
script does. The port adds rectangular-input and positive-integer extent checks.
The MATLAB classifier training, its 502-frame loop and random probe shuffle are
not ported.

## Validation and provenance

The helper and initial tests were drafted by Claude Code, then reviewed and completed with Codex after Claude's usage limit. Aaron Wetzler maintains the update; original student and third-party credits remain unchanged. Synthetic fixtures and mathematical invariants are tested. MATLAB/Octave execution was unavailable, so this is not a cross-runtime numerical comparison or a full experiment reproduction. See VALIDATION.json for the actual test and notebook execution record. The checked-in notebook has no saved outputs. No blanket license is assigned to recovered work.
