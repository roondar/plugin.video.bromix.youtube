import json
import urlparse

import requests


__author__ = 'bromix'


class Client(object):
    BROWSE_ID_WHAT_TO_WATCH = 'FEwhat_to_watch'

    KEY = 'AIzaSyAd-YEOqZz9nXVzGtn3KWzYLbLaajhqIDA'  # TV

    def __init__(self, key='', language='en-US', items_per_page=50):
        self._key = self.KEY
        if key:
            self._key = key
            pass

        self._language = language
        self._country = language.split('-')[1]
        self._max_results = items_per_page
        pass

    def get_language(self):
        return self._language

    def get_playlist_items_v3(self, playlist_id, page_token=''):
        # prepare page token
        if not page_token:
            page_token = ''
            pass

        # prepare params
        params = {'part': 'snippet',
                  'maxResults': str(self._max_results),
                  'playlistId': playlist_id}
        if page_token:
            params['pageToken'] = page_token
            pass

        return self._perform_v3_request(method='GET', path='playlistItems', params=params)

    def get_playlists_v3(self, channel_id, page_token=''):
        # prepare page token
        if not page_token:
            page_token = ''
            pass

        # prepare params
        params = {'part': 'snippet,contentDetails',
                  'maxResults': str(self._max_results),
                  'channelId': channel_id}
        if page_token:
            params['pageToken'] = page_token
            pass

        return self._perform_v3_request(method='GET', path='playlists', params=params)

    def get_channel_sections_v3(self, channel_id):
        """
        Returns the sections of a channel
        :param channel_id:
        :return:
        """
        params = {'part': 'snippet,contentDetails,id',
                  'channelId': channel_id}
        return self._perform_v3_request(method='GET', path='channelSections', params=params)

    def search_v3(self, q, search_type=['video', 'channel', 'playlist'], page_token=''):
        """
        Returns the search result.
        :param q:
        :param search_type: acceptable values are: 'video' | 'channel' | 'playlist'
        :param page_token: can be ''
        :return:
        """

        # prepare search type
        if not search_type:
            search_type = ''
            pass
        if isinstance(search_type, list):
            search_type = ','.join(search_type)
            pass

        # prepare page token
        if not page_token:
            page_token = ''
            pass

        # prepare params
        params = {'q': q,
                  'part': 'snippet',
                  'regionCode': self._country,
                  'maxResults': str(self._max_results)}
        if search_type:
            params['type'] = search_type
            pass
        if page_token:
            params['pageToken'] = page_token
            pass

        return self._perform_v3_request(method='GET', path='search', params=params)

    def get_videos_v3(self, video_id):
        """

        :param video_id:
        :return:
        """
        if isinstance(video_id, list):
            video_id = ','.join(video_id)
            pass

        params = {'part': 'snippet,contentDetails',
                  'id': video_id}
        return self._perform_v3_request(method='GET', path='videos', params=params)

    def get_channels_v3(self, channel_id):
        """
        :param channel_id: list or comma-separated list of the YouTube channel ID(s)
        :return:
        """
        if isinstance(channel_id, list):
            channel_id = ','.join(channel_id)
            pass

        params = {'part': 'snippet,contentDetails,brandingSettings',
                  'id': channel_id}
        return self._perform_v3_request(method='GET', path='channels', params=params)

    def get_guide_v3(self):
        params = {'part': 'snippet',
                  'regionCode': self._country,
                  'hl': self._language}
        return self._perform_v3_request(method='GET', path='guideCategories', params=params)

    def get_what_to_watch_tv(self):
        return self.browse_id_tv(self.BROWSE_ID_WHAT_TO_WATCH)

    def browse_id_tv(self, browse_id):
        post_data = {'browseId': browse_id}
        return self._perform_tv_request(method='POST', path='browse', post_data=post_data)

    def get_guide_tv(self):
        return self._perform_tv_request(method='POST', path='guide')

    def _perform_v3_request(self, method='GET', headers=None, path=None, post_data=None, params=None,
                            allow_redirects=True):
        # params
        if not params:
            params = {}
            pass
        _params = {'key': self._key}
        _params.update(params)

        # headers
        if not headers:
            headers = {}
            pass
        _headers = {'Host': 'www.googleapis.com',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.36 Safari/537.36',
                    'X-JavaScript-User-Agent': 'Google APIs Explorer'}

        # postdata - IS ALWAYS JSON!
        if not post_data:
            post_data = {}
            pass
        _post_data = {}
        _post_data.update(post_data)

        _headers.update(headers)

        # url
        _url = 'https://www.googleapis.com/youtube/v3/%s' % path.strip('/')

        result = None
        if method == 'GET':
            result = requests.get(_url, params=_params, headers=_headers, verify=False, allow_redirects=allow_redirects)
        elif method == 'POST':
            result = requests.post(_url, data=json.dumps(_post_data), params=_params, headers=_headers, verify=False,
                                   allow_redirects=allow_redirects)
        elif method == 'PUT':
            result = requests.put(_url, data=json.dumps(_post_data), params=_params, headers=_headers, verify=False,
                                  allow_redirects=allow_redirects)
        elif method == 'DELETE':
            result = requests.delete(_url, data=json.dumps(_post_data), params=_params, headers=_headers, verify=False,
                                     allow_redirects=allow_redirects)
            pass

        if result is None:
            return {}

        return result.json()

    def _perform_tv_request(self, method='GET', headers=None, path=None, post_data=None, params=None,
                            allow_redirects=True):
        """
        This is part of the YouTube TV API for TVs
        :param method:
        :param headers:
        :param path:
        :param post_data:
        :param params:
        :param allow_redirects:
        :return:
        """

        # params
        if not params:
            params = {}
            pass
        _params = {'key': self._key}
        _params.update(params)

        # headers
        if not headers:
            headers = {}
            pass
        _headers = {'Host': 'www.googleapis.com',
                    'Connection': 'keep-alive',
                    'Origin': 'https://www.youtube.com',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.36 Safari/537.36',
                    'Content-Type': 'application/json',
                    'Accept': '*/*',
                    'DNT': '1',
                    'Referer': 'https://www.youtube.com/tv',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'en-US,en;q=0.8,de;q=0.6'}

        # postdata - IS ALWAYS JSON!
        if not post_data:
            post_data = {}
            pass
        _post_data = {'context': {'client': {'acceptLanguage': self._language,
                                             'acceptRegion': self._country,
                                             'clientName': 'TVHTML5',
                                             'clientVersion': '4'}}}
        if isinstance(post_data, dict):
            _post_data.update(post_data)
            pass

        _headers.update(headers)

        # url
        _url = 'https://www.googleapis.com/youtubei/v1/%s' % path.strip('/')

        result = None
        if method == 'GET':
            result = requests.get(_url, params=_params, headers=_headers, verify=False, allow_redirects=allow_redirects)
        elif method == 'POST':
            result = requests.post(_url, data=json.dumps(_post_data), params=_params, headers=_headers, verify=False,
                                   allow_redirects=allow_redirects)
        elif method == 'PUT':
            result = requests.put(_url, data=json.dumps(_post_data), params=_params, headers=_headers, verify=False,
                                  allow_redirects=allow_redirects)
        elif method == 'DELETE':
            result = requests.delete(_url, data=json.dumps(_post_data), params=_params, headers=_headers, verify=False,
                                     allow_redirects=allow_redirects)
            pass

        if result is None:
            return {}

        return result.json()

    pass