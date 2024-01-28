from unittest import TestCase

from utils.dict import get_nested


class TestDictPackage(TestCase):
    def test_get_nested(self):
        params = [
            (None, 'a', None),
            ({}, 'a', None),
            ({'a': 1}, 'a', 1),
            ({'a': 1}, 'b', None),
            ({'a': 1, 'b': 2}, 'a', 1),
            ({'a': {'a': 2}}, 'a.a', 2),
            ({'aa': 1, 'a': {'aa': 2}}, 'aa', 1),
            ({'aa': 1, 'a': {'aa': 2}}, 'a.aa', 2),
        ]

        for d, path, expected in params:
            with self.subTest():
                # act
                result = get_nested(d, path)
                # assert
                self.assertEqual(result, expected)
