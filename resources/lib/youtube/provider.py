__author__ = 'bromix'

from resources.lib import kodion
from resources.lib.kodion.utils import FunctionCache
from resources.lib.kodion.items import *
from .youtube_client import YouTubeClient
from .helper import v3


class Provider(kodion.AbstractProvider):
    def __init__(self):
        kodion.AbstractProvider.__init__(self)

        self._client = None
        pass

    def _get_client(self, context):
        if not self._client:
            self._client = YouTubeClient()
            pass

        return self._client

    def _get_fanart(self, context):
        return context.create_resource_path('media', 'fanart.jpg')

    def on_search(self, search_text, context, re_match):
        # self._set_default_content_type_and_sort_methods()

        result = []

        page_token = context.get_param('page_token', '')
        search_type = context.get_param('search_type', 'video')
        page = int(context.get_param('page', 1))

        if page == 1 and search_type == 'video':
            channel_params = {}
            channel_params.update(context.get_params())
            channel_params['search_type'] = 'channel'
            channel_item = DirectoryItem('_Channels',
                                         context.create_uri([context.get_path()], channel_params))
            channel_item.set_fanart(self._get_fanart(context))
            result.append(channel_item)

            playlist_params = {}
            playlist_params.update(context.get_params())
            playlist_params['search_type'] = 'playlist'
            playlist_item = DirectoryItem('_Playlists',
                                          context.create_uri([context.get_path()], playlist_params))
            playlist_item.set_fanart(self._get_fanart(context))
            result.append(playlist_item)
            pass

        json_data = context.get_function_cache().get(FunctionCache.ONE_MINUTE * 10, self._get_client(context).search,
                                                     q=search_text, search_type=search_type, page_token=page_token)
        result.extend(v3.response_to_items(self, context, json_data))

        return result

    def on_root(self, context, re_match):
        result = []

        # search
        search_item = kodion.items.create_search_item(context)
        result.append(search_item)

        return result

    pass