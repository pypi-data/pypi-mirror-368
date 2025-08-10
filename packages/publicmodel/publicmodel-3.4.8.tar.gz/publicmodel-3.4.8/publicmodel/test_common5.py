import pytest

from publicmodel.common import VCG


@pytest.mark.parametrize("value1,value2,expected", [
    ('1', ['0', '1', '2', '3', '4', '5', '6', '7', '8'], ['9']),
    ('1', ['0', '1', '2', '3', '4', '5', '6', '7'], ['8', '9']),
    ('1', ['0', '1', '2', '3', '4', '5', '6'], ['8', '9', '7']),
    ('1', ['1', '2', '3', '4', '5', '6'], ['8', '9', '7', '0']),

])
def test_erase(value1, value2, expected):
    vcg = VCG(value1, value2)
    assert vcg.generate_code() in expected
