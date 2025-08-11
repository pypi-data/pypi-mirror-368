from .dice import Dice
from .rng import high, low, RNG


def roll(rng: RNG, *dice_expression: Dice) -> int:
    total = 0
    for dice_term in dice_expression:
        total = dice_term.op(total, sum(dice_term.roll_each_die(rng)))
    return total


def min_roll(*dice_expression: Dice) -> int:
    return roll(low, *dice_expression)


def max_roll(*dice_expression: Dice) -> int:
    return roll(high, *dice_expression)
