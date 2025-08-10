from .constants import d4, three_d6, two_d6
from .dice import Dice, d, mod, nd
from .mods import minus
from .op import Op
from .rng import AscendingRNG, rng


def test_new_instance_caching():
    first_3d8 = nd(3, 8)
    second_3d8 = nd(3, 8)
    assert first_3d8 == second_3d8
    assert first_3d8 is second_3d8

    another_2d6 = nd(2, 6)
    assert another_2d6 != first_3d8
    assert another_2d6 is two_d6


def test_roll_each_die():
    a_rng = AscendingRNG(1)
    assert three_d6.roll_each_die(a_rng) == [1, 2, 3]

    assert nd(0, 6).roll_each_die(rng) == [0]
    assert minus(2).roll_each_die(rng) == [2]


def test_to_plus():
    minus_dice = Dice(3, 4, Op.MINUS)
    plus_dice = minus_dice.to_plus()
    assert plus_dice.number == 3
    assert plus_dice.sides == 4
    assert plus_dice.op == Op.PLUS


def test_to_minus():
    plus_dice = Dice(2, 8, Op.PLUS)
    minus_dice = plus_dice.to_minus()
    assert minus_dice.number == 2
    assert minus_dice.sides == 8
    assert minus_dice.op == Op.MINUS


def test_to_times():
    plus_dice = Dice(1, 10, Op.PLUS)
    times_dice = plus_dice.to_times()
    assert times_dice.number == 1
    assert times_dice.sides == 10
    assert times_dice.op == Op.TIMES


def test_die():
    dice = Dice.die(12)
    assert dice.number == 1
    assert dice.sides == 12
    assert dice.op == Op.PLUS

    dice = d(20)
    assert dice.number == 1
    assert dice.sides == 20
    assert dice.op == Op.PLUS


def test_mod():
    dice = Dice.mod(3, Op.MINUS)
    assert dice.number == 3
    assert dice.sides == 1
    assert dice.op == Op.MINUS

    dice = mod(2, Op.TIMES)
    assert dice.number == 2
    assert dice.sides == 1
    assert dice.op == Op.TIMES


def test_n_dice():
    dice = Dice.n_dice(2, 8)
    assert dice.number == 2
    assert dice.sides == 8
    assert dice.op == Op.PLUS

    dice = Dice.n_dice(4, d4)
    assert dice.number == 4
    assert dice.sides == 4
    assert dice.op == Op.PLUS

    dice = nd(3, 6)
    assert dice.number == 3
    assert dice.sides == 6
    assert dice.op == Op.PLUS
