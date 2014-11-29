import time
from resources.lib.youtube import Provider, YouTubeClient

__author__ = 'bromix'

from resources.lib import kodion

import unittest


class TestProvider(unittest.TestCase):
    def test_login(self):
        provider = Provider()
        path = kodion.utils.create_path('my_subscriptions')
        context = kodion.Context(path=path)
        context.get_settings().set_string(kodion.constants.setting.LOGIN_USERNAME, 'bromixbromix@gmail.com')
        context.get_settings().set_string(kodion.constants.setting.LOGIN_PASSWORD, 'lzZcnn0xMC1zCBuAU83g')
        result = provider.navigate(context)
        items = result[0]
        pass

    def test_play(self):
        provider = Provider()

        path = kodion.utils.create_path('play', 'puMYeBRTsHs')
        context = kodion.Context(path=path)
        result = provider.navigate(context)
        items = result[0]
        pass

    def test_on_channel_playlists(self):
        provider = Provider()

        path = kodion.utils.create_path('channel', 'UCDbAn9LEzqONk__uXA6a9jQ', 'playlists')
        context = kodion.Context(path=path)
        result = provider.navigate(context)
        items = result[0]
        pass

    def test_on_channel_playlist(self):
        provider = Provider()

        path = kodion.utils.create_path('channel', 'some_channel_id', 'playlist', 'UUDbAn9LEzqONk__uXA6a9jQ')
        context = kodion.Context(path=path)
        result = provider.navigate(context)
        items = result[0]
        pass

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

        context = context.clone(new_path=path, new_params={'q': 'lgr', 'search_type': 'playlist', 'page_token': 'CDIQAA'})
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

    def test_performance(self):
        provider = Provider()
        context = kodion.Context(path='/')
        context.get_settings().set_string(kodion.constants.setting.LOGIN_USERNAME, 'bromixbromix@gmail.com')
        context.get_settings().set_string(kodion.constants.setting.LOGIN_PASSWORD, '')

        # to initialize the client
        result = provider.navigate(context)

        new_context = context.clone(new_path='/my_subscriptions/')
        start_time = time.time()
        result = provider.navigate(new_context)
        end_time = time.time()
        print end_time-start_time
        pass

    pass
