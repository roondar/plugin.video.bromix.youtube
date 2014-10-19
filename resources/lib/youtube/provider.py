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
        items = json_data.get('items', [])
        if len(items) > 0:
            guide_section_renderer = items[0].get('guideSectionRenderer', {})
            title = guide_section_renderer.get('title', '')
            if title:
                guide_item = DirectoryItem(title,
                                           '')
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

    pass