from .op import Op


def test_call():
    assert Op.PLUS(1, 3) == 4
    assert Op.MINUS(3, 2) == 1
    assert Op.TIMES(3, 4) == 12


def test_order():
    assert Op.PLUS < Op.MINUS < Op.TIMES


def test_repr():
    assert repr(Op.PLUS) == '<Op.PLUS>'
    assert repr(Op.MINUS) == '<Op.MINUS>'
    assert repr(Op.TIMES) == '<Op.TIMES>'


def test_str():
    assert str(Op.PLUS) == '+'
    assert str(Op.MINUS) == '-'
    assert str(Op.TIMES) == 'x'
