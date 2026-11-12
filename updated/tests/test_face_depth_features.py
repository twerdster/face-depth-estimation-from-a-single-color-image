"""Tests for the Updated2026 face-depth feature port (stdlib unittest).

All depth images here are small SYNTHETIC arrays built in the tests; no
original data, calibration or model is used.
"""
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from face_depth_features import (  # noqa: E402
    COORDS_X, COORDS_Y, build_diff, expp, get_diff, get_diff_patches,
    matlab_find_order, probe_radius_profile)


def zeros(h, w):
    return [[0] * w for _ in range(h)]


class FindOrderTests(unittest.TestCase):
    def test_column_major_order_like_matlab_find(self):
        D = [[0, 5, 0],
             [7, 0, 9],
             [0, 3, 0]]
        # MATLAB: [x,y] = find(D) walks down columns: (2,1), (1,2), (3,2), (2,3)
        self.assertEqual(matlab_find_order(D), [(1, 0), (0, 1), (2, 1), (1, 2)])

    def test_nan_counts_as_nonzero(self):
        D = [[float("nan"), 0]]
        self.assertEqual(matlab_find_order(D), [(0, 0)])


class GetDiffShapeTests(unittest.TestCase):
    def test_rows_per_pixel_and_label_repetition(self):
        D = zeros(30, 40)
        CM = zeros(30, 40)
        D[10][10], CM[10][10] = 100, 3
        D[20][30], CM[20][30] = 200, 5
        diff, labels = get_diff(D, CM)
        self.assertEqual(len(diff), 2 * COORDS_X)
        self.assertTrue(all(len(row) == COORDS_Y for row in diff))
        # find order: column 10 before column 30
        self.assertEqual(labels, [3] * COORDS_X + [5] * COORDS_X)

    def test_even_extent_gives_extra_offset_like_matlab(self):
        D = [[1]]
        (_, patch), = get_diff_patches(D, coords_x=4, coords_y=2)
        # ceil(-2):floor(2) = -2..2 (5 rows); ceil(-1):floor(1) = -1..1 (3 cols)
        self.assertEqual(len(patch), 5)
        self.assertEqual(len(patch[0]), 3)

    def test_shape_mismatch_rejected(self):
        with self.assertRaises(ValueError):
            get_diff([[1, 2]], [[1]])

    def test_ragged_images_rejected_before_indexing(self):
        with self.assertRaises(ValueError):
            get_diff([[1, 2], [3]], [[1, 2], [3, 4]])
        with self.assertRaises(ValueError):
            get_diff([[1, 2], [3, 4]], [[1, 2], [3]])

    def test_patch_extents_must_be_positive_integers(self):
        for value in [0, -1, 2.5, True]:
            with self.assertRaises(ValueError):
                get_diff_patches([[1]], coords_x=value)


class GetDiffValueTests(unittest.TestCase):
    def test_linear_ramp_interior_patch_is_exact_plane(self):
        # Synthetic plane D = 3*r + 2*c + 50 (never zero).  Interior pixel:
        # feature(i, j) must equal 3*i + 2*j exactly, independent of centre.
        H, W = 41, 61
        D = [[3 * r + 2 * c + 50 for c in range(W)] for r in range(H)]
        CM = zeros(H, W)
        patches = dict(get_diff_patches(D))
        patch = patches[(20, 30)]
        for a, i in enumerate(range(-10, 11)):
            for b, j in enumerate(range(-17, 18)):
                self.assertEqual(patch[a][b], 3 * i + 2 * j)
        # Centre element is always zero.
        self.assertEqual(patch[10][17], 0)
        del CM

    def test_depth_offset_invariance_for_interior_pixels(self):
        H, W = 25, 40
        D = [[(r * 7 + c * 13) % 17 + 1 for c in range(W)] for r in range(H)]
        D2 = [[v + 1000 for v in row] for row in D]
        p1 = dict(get_diff_patches(D))[(12, 20)]
        p2 = dict(get_diff_patches(D2))[(12, 20)]
        self.assertEqual(p1, p2)

    def test_antisymmetry_between_two_pixels(self):
        H, W = 25, 40
        D = [[(r * 5 + c * 3) % 11 + 1 for c in range(W)] for r in range(H)]
        patches = dict(get_diff_patches(D))
        p, q = (12, 18), (15, 25)
        di, dj = q[0] - p[0], q[1] - p[1]
        fp = patches[p][di + 10][dj + 17]
        fq = patches[q][-di + 10][-dj + 17]
        self.assertEqual(fp, -fq)
        self.assertEqual(fp, D[q[0]][q[1]] - D[p[0]][p[1]])

    def test_out_of_image_is_zero_and_zero_depth_is_not_masked(self):
        D = zeros(5, 5)
        D[0][0] = 10
        (_, patch), = get_diff_patches(D)
        # Neighbours above/left of (0,0) are outside the image -> 0.
        self.assertTrue(all(v == 0 for v in patch[0]))        # i = -10
        self.assertTrue(all(patch[10][b] == 0 for b in range(17)))  # j < 0
        # In-image zero-depth neighbour (0,1): 0 - 10 = -10 (not masked).
        self.assertEqual(patch[10][18], -10)
        # Far in-image neighbour (4,4): also -10.
        self.assertEqual(patch[14][21], -10)

    def test_small_hand_computed_regression(self):
        D = [[1, 2],
             [4, 0]]
        CM = [[7, 8],
              [9, 0]]
        diff, labels = get_diff(D, CM, coords_x=3, coords_y=3)
        # find order: (0,0), (1,0), (0,1)
        expected = [
            [0, 0, 0], [0, 0, 1], [0, 3, -1],     # centre (0,0)=1
            [0, -3, -2], [0, 0, -4], [0, 0, 0],   # centre (1,0)=4
            [0, 0, 0], [-1, 0, 0], [2, -2, 0],    # centre (0,1)=2
        ]
        self.assertEqual(diff, expected)
        self.assertEqual(labels, [7, 7, 7, 9, 9, 9, 8, 8, 8])


class BuildDiffTests(unittest.TestCase):
    def test_nan_replaced_before_features_and_frames_concatenated(self):
        nan = float("nan")
        D1 = [[nan, 2], [3, 0]]
        CM1 = [[1, 1], [1, 1]]
        D2 = [[5]]
        CM2 = [[4]]
        diff, labels = build_diff([(D1, CM1), (D2, CM2)], coords_x=3, coords_y=3)
        # NaN pixel is zeroed -> not visited; frame 1 visits (1,0) and (0,1).
        self.assertEqual(len(diff), 3 * 3)
        self.assertEqual(labels, [1] * 6 + [4] * 3)
        self.assertFalse(any(math.isnan(v) for row in diff for v in row))
        # zeroed NaN neighbour of (1,0)=3 at offset (-1,0) gives 0-3.
        self.assertEqual(diff[0][1], -3)

    def test_get_diff_without_build_diff_propagates_nan(self):
        nan = float("nan")
        diff, _ = get_diff([[nan, 2]], [[0, 0]], coords_x=1, coords_y=3)
        self.assertTrue(math.isnan(diff[0][1]))


class ExppTests(unittest.TestCase):
    def test_endpoints_monotone_and_convex(self):
        v = expp(1.2, 21)
        self.assertEqual(len(v), 21)
        self.assertAlmostEqual(v[0], 0.0, places=15)
        self.assertAlmostEqual(v[-1], 1.0, places=15)
        diffs = [b - a for a, b in zip(v, v[1:])]
        self.assertTrue(all(d > 0 for d in diffs))
        self.assertTrue(all(d2 > d1 for d1, d2 in zip(diffs, diffs[1:])))

    def test_regression_value(self):
        # (exp(-0.6) - exp(-1.2)) / (1 - exp(-1.2)), midpoint of expp(1.2, 3)
        mid = expp(1.2, 3)[1]
        self.assertAlmostEqual(mid, (math.exp(-0.6) - math.exp(-1.2)) / (1 - math.exp(-1.2)),
                               places=15)
        self.assertAlmostEqual(mid, 0.35434369377420455, places=14)

    def test_probe_radius_profile(self):
        r = probe_radius_profile()
        self.assertEqual(len(r), 21)
        self.assertAlmostEqual(r[0], 0.0, places=9)
        self.assertAlmostEqual(r[-1], 25000.0, places=9)

    def test_invalid_arguments(self):
        with self.assertRaises(ValueError):
            expp(1.2, 1)
        with self.assertRaises(ValueError):
            expp(0.0, 5)


if __name__ == "__main__":
    unittest.main()
