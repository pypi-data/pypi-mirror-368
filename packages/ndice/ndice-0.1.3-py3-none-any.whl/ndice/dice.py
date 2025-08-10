from __future__ import annotations

from dataclasses import dataclass

from .interned import interned
from .op import Op
from .rng import RNG


@interned
@dataclass(frozen=True, slots=True)
class Dice:
    count: int
    sides: int
    op: Op = Op.PLUS

    def is_mod(self) -> bool:
        return 0 == self.count or 0 == self.sides or 1 == self.sides

    def die_rolls(self, rng: RNG) -> list[int]:
        if self.is_mod():
            return [self.count * self.sides]
        else:
            return [rng(self.sides) for _ in range(self.count)]

    def to_plus(self) -> Dice:
        return self.__class__(self.count, self.sides, Op.PLUS)

    def to_minus(self) -> Dice:
        return self.__class__(self.count, self.sides, Op.MINUS)

    def to_times(self) -> Dice:
        return self.__class__(self.count, self.sides, Op.TIMES)

    @classmethod
    def die(cls, sides: int) -> Dice:
        return cls(1, sides)

    @classmethod
    def mod(cls, value: int, op: Op) -> Dice:
        return cls(value, 1, op)

    @classmethod
    def n_dice(cls, count: int, sides: int | Dice) -> Dice:
        sides_value = sides.sides if isinstance(sides, Dice) else sides
        return cls(count, sides_value, Op.PLUS)


d = Dice.die
mod = Dice.mod
nd = Dice.n_dice
