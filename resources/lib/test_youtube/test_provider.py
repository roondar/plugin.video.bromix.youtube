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

    def test_on_guide(self):
        provider = Provider()
        result = provider.navigate('/guide/')

        items = result[0]
        self.assertGreater(len(items), 0)

        print_items(items)

    def test_on_root(self):
        provider = Provider()
        result = provider.navigate('/')

        items = result[0]
        self.assertGreater(len(items), 0)
        pass

    pass
