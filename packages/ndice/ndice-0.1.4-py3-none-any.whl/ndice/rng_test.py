from .rng import AscendingRNG, FixedRNG, low, high, mid, PRNG, rng


def test_rng():
    for _ in range(10):
        assert 1 <= rng(6) <= 6


def test_low():
    for _ in range(10):
        assert 1 == low(6)
    for _ in range(10):
        assert 1 == low(8)


def test_high():
    for _ in range(10):
        assert 6 == high(6)
    for _ in range(10):
        assert 12 == high(12)


def test_mid():
    for _ in range(10):
        assert 3 == mid(6)
    for _ in range(10):
        assert 4 == mid(7)
    for _ in range(10):
        assert 5 == mid(10)


def test_ascending_rng():
    ascending = AscendingRNG(1)
    assert 1 == ascending(4)
    assert 2 == ascending(4)
    assert 3 == ascending(4)
    assert 4 == ascending(4)
    assert 1 == ascending(4)
    assert 2 == ascending(4)


def test_ascending_rng_too_low():
    ascending = AscendingRNG(0)
    assert 1 == ascending(4)
    assert 1 == ascending(4)
    assert 2 == ascending(4)
    assert 3 == ascending(4)
    assert 4 == ascending(4)
    assert 1 == ascending(4)


def test_ascending_rng_too_high():
    ascending = AscendingRNG(5)
    assert 1 == ascending(4)
    assert 2 == ascending(4)
    assert 3 == ascending(4)
    assert 4 == ascending(4)
    assert 1 == ascending(4)


def test_fixed_rng():
    fixed = FixedRNG(3)
    for _ in range(10):
        assert 3 == fixed(6)


def test_fixed_rng_too_low():
    fixed = FixedRNG(0)
    for _ in range(10):
        assert 1 == fixed(6)


def test_fixed_rng_too_high():
    fixed = FixedRNG(7)
    for _ in range(10):
        assert 6 == fixed(6)


def test_prng():
    prng = PRNG(123456789)
    rolls = [prng(100) for _ in range(10)]
    assert rolls == [83, 57, 70, 91, 78, 51, 39, 89, 60, 51]
