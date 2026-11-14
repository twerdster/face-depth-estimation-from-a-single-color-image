# Maintaining face-depth-estimation-from-a-single-color-image

Read SUMMARY.md, then this file, then README.md. Inspect relevant code, original usage records and any updated/VALIDATION.json before changing technical claims.

## Updated-work navigation

Aaron explicitly authorized the root README’s local `New!` badge and exact “Updated and ported for modern hardware” link on 2026-11-14. Keep both linked to `updated/README.md#updated-and-ported-for-modern-hardware`; retain the italic historical-reference qualifier and preserve the rest of the historical root reference. The matching updated README heading must introduce a short, factual account of the actual changes and limitations before the existing visuals, setup and evidence. Keep implementation descriptions and detailed results under `updated/`.

This navigation addition is the authorized exception to older root-README preservation instructions below. Verify the historical body after removing only that block, preserve source hashes/pins and leave historical validation hashes attached to their original freezes. Documentation-only navigation edits do not add runtime coverage or require a package rebuild.

## Repository workflow

From repository root: python3 -m unittest discover -s updated/tests -v. See updated/README.md for nested-list API and Jupyter/Colab setup.

Treat these commands as scoped component or historical inspection procedures exactly as documented. No build/package step bundles this repository's wrapper documentation. Do not rerun missing-dependency/full-hardware applications merely to verify prose edits. When code changes, run the affected component checks and record actual environment, skips and limits.

## Preservation and claims

Keep original source bytes, submodule pins, provenance manifests, student/third-party credits and licenses intact. Do not edit upstream README files in submodules or historical source documentation to modernize the wrapper. Put any future implementation or dependency adaptation in a separately labeled updated/ area with its own tests.

MATLAB/Octave and Linux execution are unrecorded. The 502-frame training loop and MATLAB random probe shuffle are not ported. Default patches are stacked vertically (21 rows of 35 values per selected pixel); labels repeat per patch row.

Before each commit, review and synchronize SUMMARY.md and this file. Validate Markdown/relative links, retained figure paths and diff scope. Keep historical figures distinct from current output, and synthetic examples distinct from measurements. Explain what unit-test counts cover; do not convert source inspection or failed builds into compatibility, correctness or benchmark claims. Do not claim an external review unless it actually occurred.
