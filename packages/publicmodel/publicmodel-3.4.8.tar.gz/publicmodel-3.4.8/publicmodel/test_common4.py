import pytest

from publicmodel.common import erase


@pytest.mark.parametrize("value1,value2,expected", [
    ('hello', 'e', 'ello'),
    ('world', 'o', 'orld'),
    ('delete', 'd', 'delete'),
    (1234567, '4', '124567'),
])
def test_erase(value1, value2, expected):
    assert erase(value1, value2) == expected
