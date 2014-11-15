import json
import requests

__author__ = 'bromix'


class YouTubeClient(object):
    YOUTUBE_TV_KEY = 'AIzaSyAd-YEOqZz9nXVzGtn3KWzYLbLaajhqIDA'

    def __init__(self, key='', language='en-US', items_per_page=50):
        self._key = self.YOUTUBE_TV_KEY
        if key:
            self._key = key
            pass

        self._language = language
        self._country = language.split('-')[1]
        self._max_results = items_per_page
        pass

    def get_channels(self, channel_id):
        """
        Returns a collection of zero or more channel resources that match the request criteria.
        :param channel_id: list or comma-separated list of the YouTube channel ID(s)
        :return:
        """
        if isinstance(channel_id, list):
            channel_id = ','.join(channel_id)
            pass

        params = {'part': 'snippet,contentDetails,brandingSettings',
                  'id': channel_id}
        return self._perform_v3_request(method='GET', path='channels', params=params)

    def get_videos(self, video_id):
        """
        Returns a list of videos that match the API request parameters
        :param video_id: list of video ids
        :return:
        """
        if isinstance(video_id, list):
            video_id = ','.join(video_id)
            pass

        params = {'part': 'snippet,contentDetails',
                  'id': video_id}
        return self._perform_v3_request(method='GET', path='videos', params=params)

    def search(self, q, search_type=['video', 'channel', 'playlist'], page_token=''):
        """
        Returns a collection of search results that match the query parameters specified in the API request. By default,
        a search result set identifies matching video, channel, and playlist resources, but you can also configure
        queries to only retrieve a specific type of resource.
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

    pass
