from resources.lib import kodion
from resources.lib.youtube import YouTubeClient

__author__ = 'bromix'

import unittest


class TestClient(unittest.TestCase):
    def test_login(self):
        client = YouTubeClient()

        token, expires = client.authenticate('bromixbromix@gmail.com', 'lzZcnn0xMC1zCBuAU83g')
        client = YouTubeClient(access_token=token)
        json_data = client.get_channels(channel_id='mine')
        pass

    def test_authenticate(self):
        client = YouTubeClient()

        token, expires = client.authenticate('bromixbromix@gmail.com', '')
        pass

    def test_get_video_streams(self):
        client = YouTubeClient()

        context = kodion.Context()

        #Live
        streams = client.get_video_streams(context, 'pvEWZY3Eqsg')

        # Restricted?
        #streams = client.get_video_streams(context, 'U4DbJWA9JEw')

        # VEVO (Restricted)
        #streams = client.get_video_streams(context, 'O-zpOMYRi0w')
        #streams = client.get_video_streams(context, 'NmugSMBh_iI')

        # VEVO Gema
        #streams = client.get_video_streams(context, 'XbiH6pQI7pU')
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
