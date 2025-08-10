from .constants import d4, two_d6
from .dice import Dice
from .mods import minus, plus, times
from .op import Op


def test_plus():
    dice = plus(2)
    assert dice.count == 2
    assert dice.sides == 1
    assert dice.op == Op.PLUS

    minus_2d6 = Dice(2, 6, Op.MINUS)
    dice = plus(minus_2d6)
    assert dice.count == 2
    assert dice.sides == 6
    assert dice.op == Op.PLUS


def test_minus():
    dice = minus(1)
    assert dice.count == 1
    assert dice.sides == 1
    assert dice.op == Op.MINUS

    dice = minus(two_d6)
    assert dice.count == 2
    assert dice.sides == 6
    assert dice.op == Op.MINUS


def test_times():
    dice = times(10)
    assert dice.count == 10
    assert dice.sides == 1
    assert dice.op == Op.TIMES

    dice = times(d4)
    assert dice.count == 1
    assert dice.sides == 4
    assert dice.op == Op.TIMES
