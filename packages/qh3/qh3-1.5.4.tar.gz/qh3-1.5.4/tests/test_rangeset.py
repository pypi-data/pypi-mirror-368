from __future__ import annotations

import pytest

from qh3._hazmat import RangeSet


class TestRangeSet:
    def test_add_single_duplicate(self):
        rangeset = RangeSet()

        rangeset.add(0)
        assert list(rangeset) == [(0, 1)]

        rangeset.add(0)
        assert list(rangeset) == [(0, 1)]

    def test_add_single_ordered(self):
        rangeset = RangeSet()

        rangeset.add(0)
        assert list(rangeset) == [(0, 1)]

        rangeset.add(1)
        assert list(rangeset) == [(0, 2)]

        rangeset.add(2)
        assert list(rangeset) == [(0, 3)]

    def test_add_single_merge(self):
        rangeset = RangeSet()

        rangeset.add(0)
        assert list(rangeset) == [(0, 1)]

        rangeset.add(2)
        assert list(rangeset) == [(0, 1), (2, 3)]

        rangeset.add(1)
        assert list(rangeset) == [(0, 3)]

    def test_add_single_reverse(self):
        rangeset = RangeSet()

        rangeset.add(2)
        assert list(rangeset) == [(2, 3)]

        rangeset.add(1)
        assert list(rangeset) == [(1, 3)]

        rangeset.add(0)
        assert list(rangeset) == [(0, 3)]

    def test_add_range_ordered(self):
        rangeset = RangeSet()

        rangeset.add(0, 2)
        assert list(rangeset) == [(0, 2)]

        rangeset.add(2, 4)
        assert list(rangeset) == [(0, 4)]

        rangeset.add(4, 6)
        assert list(rangeset) == [(0, 6)]

    def test_add_range_merge(self):
        rangeset = RangeSet()

        rangeset.add(0, 2)
        assert list(rangeset) == [(0, 2)]

        rangeset.add(3, 5)
        assert list(rangeset) == [(0, 2), (3, 5)]

        rangeset.add(2, 3)
        assert list(rangeset) == [(0, 5)]

    def test_add_range_overlap(self):
        rangeset = RangeSet()

        rangeset.add(0, 2)
        assert list(rangeset) == [(0, 2)]

        rangeset.add(3, 5)
        assert list(rangeset) == [(0, 2), (3, 5)]

        rangeset.add(1, 5)
        assert list(rangeset) == [(0, 5)]

    def test_add_range_overlap_2(self):
        rangeset = RangeSet()

        rangeset.add(2, 4)
        rangeset.add(6, 8)
        rangeset.add(10, 12)
        rangeset.add(16, 18)
        assert list(rangeset) == [(2, 4), (6, 8), (10, 12), (16, 18)]

        rangeset.add(1, 15)
        assert list(rangeset) == [(1, 15), (16, 18)]

    def test_add_range_reverse(self):
        rangeset = RangeSet()

        rangeset.add(6, 8)
        assert list(rangeset) == [(6, 8)]

        rangeset.add(3, 5)
        assert list(rangeset) == [(3, 5), (6, 8)]

        rangeset.add(0, 2)
        assert list(rangeset) == [(0, 2), (3, 5), (6, 8)]

    def test_add_range_unordered_contiguous(self):
        rangeset = RangeSet()

        rangeset.add(0, 2)
        assert list(rangeset) == [(0, 2)]

        rangeset.add(4, 6)
        assert list(rangeset) == [(0, 2), (4, 6)]

        rangeset.add(2, 4)
        assert list(rangeset) == [(0, 6)]

    def test_add_range_unordered_sparse(self):
        rangeset = RangeSet()

        rangeset.add(0, 2)
        assert list(rangeset) == [(0, 2)]

        rangeset.add(6, 8)
        assert list(rangeset) == [(0, 2), (6, 8)]

        rangeset.add(3, 5)
        assert list(rangeset) == [(0, 2), (3, 5), (6, 8)]

    def test_subtract(self):
        rangeset = RangeSet()
        rangeset.add(0, 10)
        rangeset.add(20, 30)

        rangeset.subtract(0, 3)
        assert list(rangeset) == [(3, 10), (20, 30)]

    def test_subtract_no_change(self):
        rangeset = RangeSet()
        rangeset.add(5, 10)
        rangeset.add(15, 20)
        rangeset.add(25, 30)

        rangeset.subtract(0, 5)
        assert list(rangeset) == [(5, 10), (15, 20), (25, 30)]

        rangeset.subtract(10, 15)
        assert list(rangeset) == [(5, 10), (15, 20), (25, 30)]

    def test_subtract_overlap(self):
        rangeset = RangeSet()
        rangeset.add(1, 4)
        rangeset.add(6, 8)
        rangeset.add(10, 20)
        rangeset.add(30, 40)
        assert list(rangeset) == [(1, 4), (6, 8), (10, 20), (30, 40)]

        rangeset.subtract(0, 2)
        assert list(rangeset) == [(2, 4), (6, 8), (10, 20), (30, 40)]

        rangeset.subtract(3, 11)
        assert list(rangeset) == [(2, 3), (11, 20), (30, 40)]

    def test_subtract_split(self):
        rangeset = RangeSet()
        rangeset.add(0, 10)
        rangeset.subtract(2, 5)
        assert list(rangeset) == [(0, 2), (5, 10)]

    def test_contains(self):
        rangeset = RangeSet()
        assert not 0 in rangeset

        rangeset = RangeSet()
        rangeset.add(0, 1)
        assert 0 in rangeset
        assert not 1 in rangeset

        rangeset = RangeSet()
        rangeset.add(0, 1)
        rangeset.add(3, 6)
        assert 0 in rangeset
        assert not 1 in rangeset
        assert not 2 in rangeset
        assert 3 in rangeset
        assert 4 in rangeset
        assert 5 in rangeset
        assert not 6 in rangeset

    def test_eq(self):
        r0 = RangeSet()
        r0.add(0, 1)

        r1 = RangeSet()
        r1.add(1, 2)
        r1.add(3, 4)

        r2 = RangeSet()
        r2.add(3, 4)
        r2.add(1, 2)

        assert r0 == r0
        assert not r0 == r1
        assert not r0 == 0

        assert r1 == r1
        assert not r1 == r0
        assert r1 == r2
        assert not r1 == 0

        assert r2 == r2
        assert r2 == r1
        assert not r2 == r0
        assert not r2 == 0

    def test_len(self):
        rangeset = RangeSet()
        assert len(rangeset) == 0

        rangeset = RangeSet()
        rangeset.add(0, 1)
        assert len(rangeset) == 1

    def test_pop(self):
        rangeset = RangeSet()
        rangeset.add(1, 2)
        rangeset.add(3, 4)

        r = rangeset.shift()
        assert r == (1, 2)
        assert list(rangeset) == [(3, 4)]

    def test_repr(self):
        rangeset = RangeSet()
        rangeset.add(1, 2)
        rangeset.add(3, 4)
        assert repr(rangeset) == "RangeSet([range(1, 2), range(3, 4)])"
