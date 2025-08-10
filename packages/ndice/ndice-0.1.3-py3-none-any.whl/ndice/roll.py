from .dice import Dice
from .rng import high, low, RNG


def roll(rng: RNG, *dice: Dice) -> int:
    total = 0
    for dice in dice:
        total = dice.op(total, sum(dice.die_rolls(rng)))
    return total


def min_roll(*dice: Dice) -> int:
    return roll(low, *dice)


def max_roll(*dice: Dice) -> int:
    return roll(high, *dice)
