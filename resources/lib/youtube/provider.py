from resources.lib import kodimon
from resources.lib.kodimon import DirectoryItem

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

        json_data = self._client.get_guide_tv()
        result.extend(self._do_youtube_tv_response(json_data))

        return result

    def on_root(self, path, params, re_match):
        result = []

        # possible sign in
        sign_in_item = DirectoryItem('[B]Sign in (Dummy)[/B]', '')
        result.append(sign_in_item)

        # search
        search_item = DirectoryItem(self.localize(self.LOCAL_SEARCH),
                                    self.PATH_SEARCH)
        search_item.set_fanart(self.get_fanart())
        result.append(search_item)

        # what to watch
        what_to_watch_item = DirectoryItem('What to watch (Dummy)', '')
        result.append(what_to_watch_item)

        # guide
        json_data = self._client.get_guide_tv()
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

                image = guide_entry_renderer.get('thumbnail', {}).get('thumbnails', [{'url': ''}])[0].get('url', '')
                image = image.strip('//')

                if browse_id:
                    guide_item = DirectoryItem(title,
                                               self.create_uri(['browse/tv', browse_id]),
                                               image=image)
                    result.append(guide_item)
                    pass
                pass
            pass

        return result

pass