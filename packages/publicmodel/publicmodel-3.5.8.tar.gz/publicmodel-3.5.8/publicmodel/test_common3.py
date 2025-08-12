import pytest

from publicmodel.common import delete_str


@pytest.mark.parametrize("value1,value2,expected", [
    ('hello', 'e', 'hllo'),
    ('world', 'o', 'wrld'),
    ('delete', 'd', 'elete'),
    ('except', 't', 'excep'),
    ('python', 'y', 'pthon'),
    ('python', 'on', 'pyth'),
    ('python', 'pyth', 'on'),
    ('python', 'n', 'pytho'),
    ('python', 'python', ''),
])
def test_delete_str(value1, value2, expected):
    assert delete_str(value1, value2) == expected
