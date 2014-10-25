from functools import partial
from resources.lib import kodimon
from resources.lib.kodimon import DirectoryItem
from resources.lib.kodimon.helper.function_cache import FunctionCache
from resources.lib.youtube import youtube_v3
import youtube_tv

__author__ = 'bromix'


class Provider(kodimon.AbstractProvider):
    def __init__(self, plugin=None):
        kodimon.AbstractProvider.__init__(self, plugin)

        from resources.lib import youtube

        # TODO: set language of XBMC/KODI (en-US) in the client. YouTube will already localize some strings
        self._client = youtube.Client()
        pass

    def get_client(self):
        """
        Return the internal client. Respect the class definition!
        :return:
        """
        return self._client

    @kodimon.RegisterPath('^/browse/tv/(?P<browse_id>.+)/$')
    def _on_browse_id_tv(self, path, params, re_match):
        result = []

        browse_id = re_match.group('browse_id')
        json_data = self._client.browse_id_tv(browse_id=browse_id)
        result.extend(youtube_tv.process_response(provider=self, json_data=json_data))

        return result

    @kodimon.RegisterPath('^/guide/$')
    def _on_guide(self, path, params, re_match):
        result = []

        # cashing
        json_data = self.call_function_cached(partial(self._client.get_guide_tv), seconds=FunctionCache.ONE_MINUTE*5)
        result.extend(youtube_tv.process_response(self, json_data))

        return result

    def on_search(self, search_text, path, params, re_match):
        result = []

        page_token = params.get('page_token', '')
        json_data = self._client.search_v3(q=search_text, page_token=page_token)

        # for next page we adjust the path for 'query'
        new_path = self.PATH_SEARCH+'/query/'
        new_params = {'q': search_text}
        new_params.update(params)
        result.extend(youtube_v3.process_response(provider=self, path=new_path, params=new_params, json_data=json_data))

        return result

    def on_root(self, path, params, re_match):
        result = []

        # TODO: call settings dialog for login
        # possible sign in
        sign_in_item = DirectoryItem('[B]Sign in (Dummy)[/B]', '')
        result.append(sign_in_item)

        # search
        search_item = DirectoryItem(self.localize(self.LOCAL_SEARCH),
                                    self.create_uri([self.PATH_SEARCH, 'list']))
        search_item.set_fanart(self.get_fanart())
        result.append(search_item)

        # TODO: try to implement 'What to Watch'
        # what to watch
        what_to_watch_item = DirectoryItem('What to watch (Dummy)',
                                           self.create_uri(['browse/tv', self._client.BROWSE_ID_WHAT_TO_WATCH]))
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

    pass