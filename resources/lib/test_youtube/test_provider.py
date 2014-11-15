from resources.lib import kodimon
from resources.lib._old_youtube import Provider

__author__ = 'bromix'

import unittest


class TestProvider(unittest.TestCase):
    def setUp(self):
        pass

    def test_channel_playlists(self):
        provider = Provider()

        # 'Lazy Game Reviews'
        result = provider.navigate('/channel/UCLx053rWZxCiYWsBETgdKrQ/playlists/')

        items = result[0]
        kodimon.print_items(items)
        pass

    def test_channel(self):
        provider = Provider()

        # 'Lazy Game Reviews'
        result = provider.navigate('/channel/UCLx053rWZxCiYWsBETgdKrQ/')

        items = result[0]
        kodimon.print_items(items)
        pass

    def test_playlist_items(self):
        provider = Provider()

        result = provider.navigate('/playlist/PL024E341A0495DF9F/')

        items = result[0]
        kodimon.print_items(items)
        pass

    def test_search(self):
        provider = Provider()

        path = '/%s/query/' % provider.PATH_SEARCH
        result = provider.navigate(path, {'q': 'lgr'})

        items = result[0]
        kodimon.print_items(items)
        pass

    def test_on_guide(self):
        provider = Provider()
        result = provider.navigate('/guide/')

        items = result[0]
        self.assertGreater(len(items), 0)

        kodimon.print_items(items)
        pass

    def test_on_root(self):
        provider = Provider()
        result = provider.navigate('/')

        items = result[0]
        self.assertGreater(len(items), 0)
        pass

    pass
