import pytest

from publicmodel.common import calculate


@pytest.mark.parametrize("value,expected", [
    ('12/3', '4'),
    ('15*2', '30'),
    ('1+4-5', '0'),
    ('10/3', '3.3...'),
    ('10/4', '2.5'),
    ('100/3', '33.3...'),
    ('1.5+0.5', '2'),
    ('10/5', '2'),
    ('20/4', '5'),
])
def test_calculate(value, expected):
    assert calculate(value) == expected
