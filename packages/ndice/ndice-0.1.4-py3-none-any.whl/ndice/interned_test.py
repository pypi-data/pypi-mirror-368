from dataclasses import dataclass

from .interned import interned


@interned
@dataclass(frozen=True, order=True, slots=True)
class Person:
    name: str
    age: int


def test_interned():
    person1 = Person('Waldo', 15)
    person2 = Person('Waldo', 15)
    person3 = Person('Waldo', 16)

    assert person1 == person2
    assert person1 is person2

    assert person1 != person3
    assert person1 is not person3
