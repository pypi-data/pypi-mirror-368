import unittest
from unittest import TestCase

import pytest

from publicmodel.common import value4


class Test(TestCase):
    def test_value4(self):
        self.assertEqual(value4("4"), 4)
        self.assertEqual(value4("4.1"), 4.1)

    def test_value4_str(self):
        self.assertEqual(value4("one"), "one")

    def test_value4_using_pytest(self):
        assert value4(4.0) == 4

    def test_value4_using_pytest2(self):
        assert value4("4.0123") == 4.0123


@pytest.mark.parametrize("value,expected", [
    ("1", 1),
    (1, 1),
    (1.0, 1),
    (1.01, 1.01),
    ("1.a", "1.a"),
    ("1.01b", "1.01b"),
    ("abc", "abc"),
])
def test_value4(value, expected):
    assert value4(value) == expected


@pytest.fixture
def test_data():
    return {
        "v1": 1.0000, "ret_v1": 1,
        "v2": 2.000, "ret_v2": 2,
        "v3": 1.111, "ret_v3": 1.111,
    }


def test_value4_2(test_data):
    assert value4(test_data["v1"]) == test_data["ret_v1"]


if __name__ == "__main__":
    unittest.main()
