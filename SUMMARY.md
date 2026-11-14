# face-depth-estimation-from-a-single-color-image: maintenance context

Read this file first, then SKILL.md and README.md. This context describes the repository as of 2026-11-12.

## Updated-work navigation (2026-11-14)

Aaron authorized a top-of-page `New!` badge and “Updated and ported for modern hardware” link in the root README. Both lead to the corresponding heading in `updated/README.md`, which now opens with a brief description of the actual port, repairs or reimplementation and its limits. An italic line marks the following content as the historical reference. The historical root reference body remains unchanged; current implementation details stay under `updated/`.

This documentation change does not alter source, submodule pins, media or recorded validation. Earlier root-README byte-identity statements and hashes apply to their recorded baseline; current preservation checks remove only the authorized navigation block before comparing the historical body.

## Purpose and current source

Historical title/aim: estimating face depth from a color image. The archived project description identifies random-forest facial-region classification on paired mannequin color/depth images; buildDiff.m assembles labeled depth features and trains TreeBagger. Updated code assembles depth-difference patches and labels only.

Test2nd.m, buildDiff.m and getDiff.m retain recovered bytes. Calibration, image/depth data, model files and the getDepthFeatures MEX helper are absent. The Python port does not estimate depth from a color image or train TreeBagger.

## Use and validation

From repository root: python3 -m unittest discover -s updated/tests -v. See updated/README.md for nested-list API and Jupyter/Colab setup.

updated/VALIDATION.json records 18 unit tests and three real notebook code cells passed on 2026-11-12, macOS arm64 / Python 3.14.4. These check synthetic layout/order/boundary/NaN/radius fixtures, not MATLAB runtime parity or recognition accuracy.

MATLAB/Octave and Linux execution are unrecorded. The 502-frame training loop and MATLAB random probe shuffle are not ported. Default patches are stacked vertically (21 rows of 35 values per selected pixel); labels repeat per patch row.

## Documentation maintenance

The 2026-11-12 documentation revision organizes the README around implementation, available source, setup, recorded checks and limits. It preserves historical visuals and links, with captions separating historical results from updated examples. No runnable code, source provenance, pinned revisions, licenses or validation results changed in this revision. Recorded earlier tests were not rerun for the prose-only edits.

Preserve original source and authorship. New ports belong under updated/ and require their own scope/validation. Do not infer a blanket license from recovery. Review this file and SKILL.md before every commit and synchronize changes to workflow, commands, validation or status. Check relative links and figure rendering; never describe inventory counts or component tests as full-application validation.

Two actual Claude editorial review rounds on 2026-11-12 covered the README and related changed documentation, including context files, component guides and applicable algorithm/build notes or schematic text. Useful qualifications were checked against source, preserved project records and saved validation logs, then applied. Editorial review adds no runtime coverage.
