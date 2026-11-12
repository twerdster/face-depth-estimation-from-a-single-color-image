"""Updated Python port of the recovered face-depth difference features.

Port drafted with Claude Code, reviewed and completed with Codex for
Aaron Wetzler (2026-11-12).

Original algorithm: ``source/original/getDiff.m`` and ``source/original/buildDiff.m``
(Face Depth Estimation from a Single Color Image, student Tova Krakauer,
supervision Aaron Wetzler).  ``expp`` / ``probe_radius_profile`` port the
deterministic radius formula from ``source/original/Test2nd.m``.

Standard library only.  Images are plain nested lists indexed ``image[row][col]``
(0-based); MATLAB's 1-based ``D(x, y)`` corresponds to ``image[x-1][y-1]``.

This is a port of the feature *assembly* only.  It does not include the MATLAB
``TreeBagger`` random forest, the missing calibration/feature/depth files, the
missing ``getDepthFeatures`` MEX helper, or any trained model, so it cannot
reproduce the original experiment or its accuracy.

Faithful behaviours that may look surprising (kept on purpose, see README):

* Pixels are visited in MATLAB ``find`` order: column-major (down each column,
  then across columns).  ``NaN`` counts as non-zero in ``find``.
* Each visited pixel contributes a 21 x 35 patch (row offsets -10..10, column
  offsets -17..17).  ``getDiff.m`` stacks these patches *vertically*, so the
  returned feature matrix has 21 rows of 35 values per pixel, and the label of
  the centre pixel is repeated 21 times.  One training row is therefore one
  patch row, not one pixel.
* Out-of-image neighbours give 0.  In-image zero-depth neighbours are *not*
  masked: they give ``0 - D(centre)``.
"""

from __future__ import annotations

import math
from typing import Iterable, List, Sequence, Tuple

Matrix = List[List[float]]

#: Patch extents hard-coded in getDiff.m (``coords_x = 21; coords_y = 35``).
COORDS_X = 21
COORDS_Y = 35


def _offsets(extent: int) -> range:
    """MATLAB ``ceil(-extent/2):floor(extent/2)`` as a Python range.

    For odd extents this gives ``extent`` offsets; for even extents MATLAB's
    expression gives ``extent + 1`` offsets, which is reproduced here.
    """
    if isinstance(extent, bool) or not isinstance(extent, int) or extent < 1:
        raise ValueError("patch extents must be positive integers")
    return range(math.ceil(-extent / 2), math.floor(extent / 2) + 1)


def _shape(image: Sequence[Sequence[float]]) -> Tuple[int, int]:
    """Validate a rectangular nested-list image before indexing it."""
    cols = len(image[0]) if image else 0
    if any(len(row) != cols for row in image):
        raise ValueError("images must be rectangular")
    return len(image), cols


def matlab_find_order(D: Sequence[Sequence[float]]) -> List[Tuple[int, int]]:
    """Return 0-based ``(row, col)`` of non-zero entries in MATLAB ``find`` order."""
    rows, cols = _shape(D)
    out = []
    for c in range(cols):
        for r in range(rows):
            if D[r][c] != 0:  # NaN != 0 is True, matching MATLAB find
                out.append((r, c))
    return out


def get_diff_patches(D: Sequence[Sequence[float]],
                     coords_x: int = COORDS_X,
                     coords_y: int = COORDS_Y) -> List[Tuple[Tuple[int, int], Matrix]]:
    """Per-pixel depth-difference patches used inside ``getDiff.m``.

    Returns a list of ``((row, col), patch)`` in MATLAB ``find`` order, where
    ``patch[a][b] = D[row+i][col+j] - D[row][col]`` for row offset ``i`` and
    column offset ``j``, or ``0`` when the neighbour is outside the image.
    """
    rows, cols = _shape(D)
    off_r = _offsets(coords_x)
    off_c = _offsets(coords_y)
    result = []
    for (r, c) in matlab_find_order(D):
        centre = D[r][c]
        patch = []
        for i in off_r:
            rr = r + i
            row_vals = []
            for j in off_c:
                cc = c + j
                if rr < 0 or cc < 0 or rr >= rows or cc >= cols:
                    row_vals.append(0)
                else:
                    row_vals.append(D[rr][cc] - centre)
            patch.append(row_vals)
        result.append(((r, c), patch))
    return result


def get_diff(D: Sequence[Sequence[float]],
             CM: Sequence[Sequence[float]],
             coords_x: int = COORDS_X,
             coords_y: int = COORDS_Y) -> Tuple[Matrix, List[float]]:
    """Port of ``[diffMat, class] = getDiff(D, CM)``.

    ``diffMat`` is the vertical stack of every pixel's patch (``coords_x``
    rows per non-zero pixel, ``coords_y`` columns).  ``class`` repeats
    ``CM[row][col]`` once per patch row, as ``getDiff.m`` does.
    """
    if _shape(CM) != _shape(D):
        raise ValueError("CM must have the same shape as D")
    diff_mat: Matrix = []
    labels: List[float] = []
    for (r, c), patch in get_diff_patches(D, coords_x, coords_y):
        diff_mat.extend(patch)
        labels.extend([CM[r][c]] * len(patch))
    return diff_mat, labels


def build_diff(frames: Iterable[Tuple[Sequence[Sequence[float]], Sequence[Sequence[float]]]],
               coords_x: int = COORDS_X,
               coords_y: int = COORDS_Y) -> Tuple[Matrix, List[float]]:
    """Port of the feature-assembly loop in ``buildDiff.m``.

    ``frames`` yields ``(D, CM)`` pairs (depth image, label map).  As in
    ``buildDiff.m``, NaN depths are set to 0 before calling ``get_diff`` and
    all results are concatenated vertically.  The original then trains
    ``TreeBagger(10, diffMat, class, 'oobpred', 'on')``; that step, the
    ``load DATATESTf1`` input and the hard-coded 502-frame loop are not ported.
    """
    diff_mat: Matrix = []
    labels: List[float] = []
    for D, CM in frames:
        clean = [[0 if (isinstance(v, float) and math.isnan(v)) else v for v in row]
                 for row in D]
        d, l = get_diff(clean, CM, coords_x, coords_y)
        diff_mat.extend(d)
        labels.extend(l)
    return diff_mat, labels


def expp(s: float, n: int) -> List[float]:
    """Port of ``expp=@(s,n) (exp(-s:s/(n-1):0)-exp(-s))/(1-exp(-s))`` (Test2nd.m).

    Returns ``n`` values rising from 0 to 1.  The MATLAB colon range is
    evaluated as ``-s + k*s/(n-1)`` for ``k = 0..n-1``; MATLAB's own colon
    arithmetic can differ in the last floating-point bit.
    """
    if n < 2:
        raise ValueError("n must be at least 2")
    if s <= 0:
        raise ValueError("s must be positive (s = 0 divides by zero in the original)")
    base = math.exp(-s)
    step = s / (n - 1)
    return [(math.exp(-s + k * step) - base) / (1 - base) for k in range(n)]


def probe_radius_profile(probe_size: float = 50000, n_div: int = 20,
                         steepness: float = 1.2) -> List[float]:
    """Sorted probe radii ``probeSize*expp(steepness, nDiv+1)/2`` from Test2nd.m.

    The original then shuffles ``radius(randperm(nDiv)+1)`` with MATLAB's
    legacy ``rand('seed', 0)`` generator; that random stream is not
    reproduced, so this returns the unshuffled ``nDiv + 1`` values.
    """
    return [probe_size * v / 2 for v in expp(steepness, n_div + 1)]
