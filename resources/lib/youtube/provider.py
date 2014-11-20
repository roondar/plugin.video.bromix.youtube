__author__ = 'bromix'

from resources.lib import kodion
from resources.lib.kodion.utils import FunctionCache
from resources.lib.kodion.items import *
from .youtube_client import YouTubeClient
from .helper import v3, ResourceManager


class Provider(kodion.AbstractProvider):
    def __init__(self):
        kodion.AbstractProvider.__init__(self)

        self._local_map = {'youtube.channels': 30500,
                           'youtube.playlists': 30501}

        self._client = None
        pass

    def get_client(self, context):
        if not self._client:
            self._client = YouTubeClient()
            pass

        return self._client

    def get_fanart(self, context):
        return context.create_resource_path('media', 'fanart.jpg')

    @kodion.RegisterProviderPath('^/playlist/(?P<playlist_id>.*)/$')
    def _on_playlist(self, context, re_match):
        result = []

        playlist_id = re_match.group('playlist_id')
        page = int(context.get_param('page', 1))
        page_token = context.get_param('page_token', '')

        json_data = self.get_client(context).get_playlist_items(playlist_id, page_token)
        result.extend(v3.response_to_items(self, context, json_data))

        return result

    @kodion.RegisterProviderPath('^/channel/(?P<channel_id>.*)/playlists/$')
    def _on_channel_playlists(self, context, re_match):
        result = []

        channel_id = re_match.group('channel_id')
        page = int(context.get_param('page', 1))
        page_token = context.get_param('page_token', '')

        json_data = context.get_function_cache().get(FunctionCache.ONE_HOUR, self.get_client(context).get_playlists,
                                                     channel_id, page_token)
        result.extend(v3.response_to_items(self, context, json_data))

        return result

    @kodion.RegisterProviderPath('^/channel/(?P<channel_id>.*)/$')
    def _on_channel(self, context, re_match):
        resource_manager = ResourceManager(context, self.get_client(context))

        result = []

        channel_id = re_match.group('channel_id')
        channel_fanarts = resource_manager.get_fanarts([channel_id])
        page = int(context.get_param('page', 1))
        page_token = context.get_param('page_token', '')

        if page == 1:
            playlists_item = DirectoryItem('[B]'+context.localize(self._local_map['youtube.playlists'])+'[/B]',
                                           context.create_uri(['channel', channel_id, 'playlists']))
            playlists_item.set_fanart(channel_fanarts.get(channel_id, self.get_fanart(context)))
            result.append(playlists_item)
            pass

        playlists = resource_manager.get_related_playlists(channel_id)
        upload_playlist = playlists.get('uploads', '')
        if upload_playlist:
            json_data = context.get_function_cache().get(FunctionCache.ONE_MINUTE * 5,
                                                         self.get_client(context).get_playlist_items, upload_playlist,
                                                         page_token)
            result.extend(v3.response_to_items(self, context, json_data))
            pass

        return result

    def on_search(self, search_text, context, re_match):
        context.set_content_type(kodion.constants.content_type.EPISODES)

        result = []

        page_token = context.get_param('page_token', '')
        search_type = context.get_param('search_type', 'video')
        page = int(context.get_param('page', 1))

        if page == 1 and search_type == 'video':
            channel_params = {}
            channel_params.update(context.get_params())
            channel_params['search_type'] = 'channel'
            channel_item = DirectoryItem('[B]' + context.localize(self._local_map['youtube.channels']) + '[/B]',
                                         context.create_uri([context.get_path()], channel_params))
            channel_item.set_fanart(self.get_fanart(context))
            result.append(channel_item)

            playlist_params = {}
            playlist_params.update(context.get_params())
            playlist_params['search_type'] = 'playlist'
            playlist_item = DirectoryItem('[B]' + context.localize(self._local_map['youtube.playlists']) + '[/B]',
                                          context.create_uri([context.get_path()], playlist_params))
            playlist_item.set_fanart(self.get_fanart(context))
            result.append(playlist_item)
            pass

        json_data = context.get_function_cache().get(FunctionCache.ONE_MINUTE * 10, self.get_client(context).search,
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