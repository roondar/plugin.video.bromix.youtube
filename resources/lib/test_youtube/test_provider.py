from resources.lib.youtube import Provider

__author__ = 'bromix'

import unittest


def print_items(items):
    for item in items:
        print item
        pass
    pass


class TestProvider(unittest.TestCase):
    def setUp(self):
        pass

    def test_on_root(self):
        provider = Provider()
        result = provider.navigate('/')

        items = result[0]
        self.assertEqual(0, len(items))

        print_items(items)
        pass

    pass
