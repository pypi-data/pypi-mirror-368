from .constants import two_d6
from .dice import d, nd
from .mods import minus, plus, times
from .rng import mid
from .roll import max_roll, min_roll, roll


def test_roll():
    total = roll(mid)
    assert total == 0

    total = roll(mid, d(6))
    assert total == 3

    total = roll(mid, d(6), nd(2, 10))
    assert total == 13

    total = roll(mid, two_d6, minus(2), times(10))
    assert total == 40

    total = roll(mid, plus(5))
    assert total == 5

    total = roll(mid, nd(0, 6))
    assert total == 0

    total = roll(mid, nd(2, 0))
    assert total == 0


def test_min_roll():
    total = min_roll()
    assert total == 0

    total = min_roll(d(6))
    assert total == 1

    total = min_roll(d(6), nd(2, 10))
    assert total == 3

    total = min_roll(two_d6, minus(2), times(10))
    assert total == 0

    total = min_roll(plus(5))
    assert total == 5

    total = min_roll(nd(0, 6))
    assert total == 0

    total = min_roll(nd(2, 0))
    assert total == 0


def test_max_roll():
    total = max_roll()
    assert total == 0

    total = max_roll(d(6))
    assert total == 6

    total = max_roll(d(6), nd(2, 10))
    assert total == 26

    total = max_roll(two_d6, minus(2), times(10))
    assert total == 100

    total = max_roll(plus(5))
    assert total == 5

    total = max_roll(nd(0, 6))
    assert total == 0

    total = max_roll(nd(2, 0))
    assert total == 0
