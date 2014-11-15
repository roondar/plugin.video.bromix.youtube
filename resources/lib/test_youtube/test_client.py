from resources.lib.youtube import Client

__author__ = 'bromix'

import unittest

class TestClient(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_playlist_items(self):
        client = Client()

        json_data = client.get_playlist_items_v3('PL024E341A0495DF9F')
        pass

    def test_get_playlists(self):
        client = Client()

        json_data = client.get_playlists_v3('UCLx053rWZxCiYWsBETgdKrQ')
        pass

    def test_get_videos_v3(self):
        client = Client()

        json_data = client.get_videos_v3(['vyD70Huufco', 'AFdezM3_m-c'])
        pass

    def test_search_v3(self):
        client = Client()

        json_data = client.search_v3(q='batman')
        pass

    def test_get_what_to_watch_tv(self):
        client = Client()

        # 'Popular on YouTube'
        json_data = client.get_what_to_watch_tv()
        pass

    def test_get_channel_sections_v3(self):
        client = Client(language='de-DE')

        # 'Lazy Game Reviews'
        json_data = client.get_channel_sections_v3(channel_id='UCLx053rWZxCiYWsBETgdKrQ')

        # 'Popular on YouTube'
        json_data = client.get_channel_sections_v3(channel_id='UCF0pVplsI8R5kcAqgtoRqoA')

        # 'Sports'
        json_data = client.get_channel_sections_v3(channel_id='UCEgdi0XIXXZ-qJOFPf4JSKw')

        # TODO: the first playlist of the section is the content of the 'HOME' and YouTube TV section
        pass

    def test_get_channels_v3(self):
        client = Client()

        # 'Lazy Game Reviews'
        json_data = client.get_channels_v3(channel_id='UCLx053rWZxCiYWsBETgdKrQ')

        # 'Popular on YouTube', 'Sport'
        json_data = client.get_channels_v3(channel_id=['UCF0pVplsI8R5kcAqgtoRqoA','UCEgdi0XIXXZ-qJOFPf4JSKw'])
        pass

    def test_get_guide_v3(self):
        client = Client(language='de-DE')

        json_data = client.get_guide_v3()
        pass

    def test_get_guide_tv(self):
        client = Client()

        json_data = client.get_guide_tv()
        pass

    pass
