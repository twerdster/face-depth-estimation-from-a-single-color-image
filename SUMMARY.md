# Historical student-project archive

## Current source state — 2026-11-12

**Partial MATLAB research source recovered.** The three original files are in [`source/original/`](source/original/): `Test2nd.m`, `buildDiff.m` and `getDiff.m`. They are research snapshots rather than a complete final application, trained model or dataset.

All three published MATLAB files preserve the recovered attachment bytes. Raw correspondence, generic face-image archives and unrelated/unverified datasets were not published.

## Setup and validation

The files use MATLAB image-processing, camera-calibration and random-forest routines (`TreeBagger`/`predict`). Referenced calibration, classifier, feature, image and depth files are absent. No MATLAB/Octave run or successful end-to-end build is claimed. Supply appropriately licensed data and review all paths and file outputs before attempting these historical scripts.

Publication validation covers the source allowlist, SHA-256 provenance, text/XML or project metadata where applicable, and credential/private-material scanning. It is not an end-to-end runtime result. Read README.md and source/PROVENANCE.json before further edits; preserve source/original and existing documents. Any future updated implementation belongs in updated/ with its own requirements, tests, attribution and a clear description of its differences. Do not introduce a blanket license. Review this context file before committing; keep actual validation and source counts accurate.

## Interactive possibilities

The difference-feature calculation is a small candidate for a tested Python notebook with synthetic inputs. Reproducing the face-depth experiment requires its missing data, calibration and learned model.
