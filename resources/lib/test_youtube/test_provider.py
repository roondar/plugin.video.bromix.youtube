from resources.lib.youtube import Provider

__author__ = 'bromix'

from resources.lib import kodion

import unittest


class TestProvider(unittest.TestCase):
    def test_on_channel(self):
        provider = Provider()

        path = kodion.utils.create_path('channel', 'UCDbAn9LEzqONk__uXA6a9jQ')
        context = kodion.Context(path=path)
        result = provider.navigate(context)
        items = result[0]
        pass

    def test_on_search_playlist(self):
        provider = Provider()

        path = kodion.utils.create_path(kodion.constants.paths.SEARCH, 'query')
        context = kodion.Context(path=path, params={'q': 'lgr', 'search_type': 'playlist'})
        result = provider.navigate(context)
        items = result[0]
        self.assertGreater(len(items), 0)
        kodion.utils.print_items(items)

        context = kodion.Context(path=path, params={'q': 'lgr', 'search_type': 'playlist', 'page_token': 'CDIQAA'})
        result = provider.navigate(context)
        items = result[0]
        self.assertGreater(len(items), 0)
        kodion.utils.print_items(items)
        pass

    def test_on_search_video(self):
        provider = Provider()

        path = kodion.utils.create_path(kodion.constants.paths.SEARCH, 'query')
        context = kodion.Context(path=path, params={'q': 'lgr'})
        result = provider.navigate(context)
        items = result[0]
        self.assertGreater(len(items), 0)
        kodion.utils.print_items(items)
        pass

    def test_on_root(self):
        provider = Provider()

        context = kodion.Context(path='/')
        result = provider.navigate(context)

        items = result[0]
        self.assertGreater(len(items), 0)

        kodion.utils.print_items(items)
        pass

    pass
