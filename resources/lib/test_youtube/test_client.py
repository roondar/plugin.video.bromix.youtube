from resources.lib.youtube import Client

__author__ = 'bromix'

import unittest

class TestClient(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_guide(self):
        client = Client()

        json_data = client.get_guide()
        pass

    pass
