from resources.lib import kodimon
from resources.lib.kodimon import DirectoryItem

__author__ = 'bromix'


class Provider(kodimon.AbstractProvider):
    def __init__(self, plugin=None):
        kodimon.AbstractProvider.__init__(self, plugin)

        from resources.lib import youtube

        self._client = youtube.Client()
        pass

    def on_root(self, path, params, re_match):
        result = []

        # Guide
        json_data = self._client.get_guide()
        result.extend(self._do_youtube_tv_response(json_data))

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
                if browse_id:
                    guide_item = DirectoryItem(title,
                                               self.create_uri(['browse/tv', browse_id]))
                    result.append(guide_item)
                    pass
                pass
            pass

        return result

    pass