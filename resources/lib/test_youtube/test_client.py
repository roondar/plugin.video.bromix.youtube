from resources.lib.youtube import YouTubeClient

__author__ = 'bromix'

import unittest


class TestClient(unittest.TestCase):
    def test_get_video_streams(self):
        client = YouTubeClient()

        # VEVO
        streams = client.get_video_streams('NmugSMBh_iI')
        #streams = client.get_video_streams('XbiH6pQI7pU')
        pass

    def test_get_playlists(self):
        client = YouTubeClient()

        json_data = client.get_playlists('UCDbAn9LEzqONk__uXA6a9jQ')
        pass

    def test_get_playlist_items(self):
        client = YouTubeClient()

        json_data = client.get_playlist_items(u'UUDbAn9LEzqONk__uXA6a9jQ')
        pass

    def test_get_channels(self):
        client = YouTubeClient()

        json_data = client.get_channels(['UCDbAn9LEzqONk__uXA6a9jQ', 'UC8i4HhaJSZhm-fu84Bl72TA'])
        pass

    def test_get_videos(self):
        client = YouTubeClient()

        json_data = client.get_videos(['vyD70Huufco', 'AFdezM3_m-c'])
        pass

    def test_search(self):
        client = YouTubeClient()

        #json_data = client.search(q='batman')
        #json_data = client.search(q='batman', search_type='channel')
        json_data = client.search(q='batman', search_type='playlist')
        pass

    pass
