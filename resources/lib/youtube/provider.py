from functools import partial
from resources.lib import kodimon
from resources.lib.kodimon import DirectoryItem
from resources.lib.kodimon.helper.function_cache import FunctionCache

__author__ = 'bromix'


class Provider(kodimon.AbstractProvider):
    def __init__(self, plugin=None):
        kodimon.AbstractProvider.__init__(self, plugin)

        from resources.lib import youtube

        # TODO: set language of XBMC/KODI (en-US) in the client. YouTube will already localize some strings
        self._client = youtube.Client()
        pass

    @kodimon.RegisterPath('^/guide/$')
    def _on_guide(self, path, params, re_match):
        result = []

        # cashing
        json_data = self.call_function_cached(partial(self._client.get_guide_tv), seconds=FunctionCache.ONE_MINUTE*5)
        result.extend(self._do_youtube_tv_response(json_data))

        return result

    def on_root(self, path, params, re_match):
        result = []

        # TODO: call settings dialog for login
        # possible sign in
        sign_in_item = DirectoryItem('[B]Sign in (Dummy)[/B]', '')
        result.append(sign_in_item)

        # search
        search_item = DirectoryItem(self.localize(self.LOCAL_SEARCH),
                                    self.PATH_SEARCH)
        search_item.set_fanart(self.get_fanart())
        result.append(search_item)

        # TODO: try to implement 'What to Watch'
        # what to watch
        what_to_watch_item = DirectoryItem('What to watch (Dummy)', '')
        result.append(what_to_watch_item)

        # TODO: setting to disable this item
        # guide - we call this function the get the localized string directly from YouTube
        json_data = self.call_function_cached(partial(self._client.get_guide_tv), seconds=FunctionCache.ONE_MINUTE*10)
        if json_data.get('kind', '') == 'youtubei#guideResponse':
            title = json_data.get('items', [{}])[0].get('guideSectionRenderer', {}).get('title', '')
            if title:
                guide_item = DirectoryItem(title,
                                           self.create_uri(['guide']))
                guide_item.set_fanart(self.get_fanart())
                result.append(guide_item)
                pass
            pass

        return result

    def get_fanart(self):
        """
            This will return a darker and (with blur) fanart
            :return:
            """
        return self.create_resource_path('media', 'fanart.jpg')

    def _do_youtube_tv_response(self, json_data):
        channel_map = {}
        result = []

        kind = json_data.get('kind', '')
        items = json_data.get('items', [])
        for item in items:
            # if kind=='youtubei#guideResponse'
            sub_items = item.get('guideSectionRenderer', {}).get('items', [])
            for sub_item in sub_items:
                guide_entry_renderer = sub_item.get('guideEntryRenderer', {})
                title = guide_entry_renderer['title']
                browse_id = guide_entry_renderer.get('navigationEndpoint', {}).get('browseEndpoint', {}).get('browseId',
                                                                                                             '')
                if browse_id:
                    guide_item = DirectoryItem(title, self.create_uri(['browse/tv', browse_id]))
                    result.append(guide_item)

                    channel_map[browse_id] = guide_item
                    pass
                pass
            pass

        # we update the channels with the correct thumbnails and fanarts
        json_channel_data = self._client.get_channels_v3(channel_id=list(channel_map.keys()))
        items = json_channel_data.get('items', [])
        for item in items:
            guide_item = channel_map[item['id']] # should crash if something is missing

            image = item.get('snippet', {}).get('thumbnails', {}).get('medium', {}).get('url', '')
            guide_item.set_image(image)

            fanart = item.get('brandingSettings', {}).get('image', {}).get('bannerTvImageUrl', self.get_fanart())
            guide_item.set_fanart(fanart)
            pass

        return result

pass