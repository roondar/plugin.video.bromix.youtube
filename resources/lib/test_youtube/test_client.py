from resources.lib.youtube import Client

__author__ = 'bromix'

import unittest

class TestClient(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_channels_v3(self):
        client = Client()

        # 'Popular on YouTube', 'Sport'
        json_data = client.get_channels_v3(channel_id=['UCF0pVplsI8R5kcAqgtoRqoA','UCEgdi0XIXXZ-qJOFPf4JSKw'])
        pass

    def test_get_guide_v3(self):
        client = Client()

        json_data = client.get_guide_v3()
        pass

    def test_get_guide_tv(self):
        client = Client()

        json_data = client.get_guide_tv()
        pass

    pass
