import time

__author__ = 'bromix'

import urlparse

from resources.lib.youtube.youtube_exceptions import LoginException


import json
import requests
# Verify is disabled and to avoid warnings we disable the warnings. Behind a proxy request isn't working correctly all
# the time and if so can't validate the hosts correctly resulting in a exception and the addon won't work properly.
try:
    from requests.packages import urllib3
    urllib3.disable_warnings()
except:
    # do nothing
    pass

from .helper.video_info import VideoInfo

"""
Google TV:

client_id       : 861556708454-d6dlm3lh05idd8npek18k6be8ba3oc68.apps.googleusercontent.com
client_secret   : SboVhoG9s0rNafixCSGGKXAT
code            : 4/gZREYbvKx93ONAJehIzCVpLPJVSd_QtkbtLIXYFmrMs
grant_type      : http://oauth.net/grant_type/device/1.0
"""


class YouTubeClient(object):
    YOUTUBE_TV_KEY = 'AIzaSyAd-YEOqZz9nXVzGtn3KWzYLbLaajhqIDA'
    YOUTUBE_TV_CLIENT_ID = '861556708454-d6dlm3lh05idd8npek18k6be8ba3oc68.apps.googleusercontent.com'
    YOUTUBE_TV_CLIENT_SECRET = 'SboVhoG9s0rNafixCSGGKXAT'

    YOUTUBE_APP_KEY = 'AIzaSyA8eiZmM1FaDVjRy-df2KTyQ_vz_yYM39w'
    #YOUTUBE_WEB_KEY = 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8'

    def __init__(self, key='', language='en-US', items_per_page=50, access_token=''):
        self._key = self.YOUTUBE_TV_KEY
        #self._key = self.YOUTUBE_APP_KEY
        #self._key = self.YOUTUBE_WEB_KEY
        if key:
            self._key = key
            pass

        self._language = language.replace('-', '_')
        self._country = language.split('-')[1]
        self._access_token = access_token
        self._max_results = items_per_page
        pass

    def revoke(self, refresh_token):
        headers = {'Host': 'www.youtube.com',
                   'Connection': 'keep-alive',
                   'Origin': 'https://www.youtube.com',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.28 Safari/537.36',
                   'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
                   'Accept': '*/*',
                   'DNT': '1',
                   'Referer': 'https://www.youtube.com/tv',
                   'Accept-Encoding': 'gzip, deflate',
                   'Accept-Language': 'en-US,en;q=0.8,de;q=0.6'}

        post_data = {'token': refresh_token}

        # url
        url = 'https://www.youtube.com/o/oauth2/revoke'

        result = requests.post(url, data=post_data, headers=headers, verify=False)
        if result.status_code != requests.codes.ok:
            raise LoginException('Logout Failed')

        pass

    def refresh_token(self, refresh_token, client_id='', client_secret='', grant_type=''):
        headers = {'Host': 'www.youtube.com',
                   'Connection': 'keep-alive',
                   'Origin': 'https://www.youtube.com',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.28 Safari/537.36',
                   'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
                   'Accept': '*/*',
                   'DNT': '1',
                   'Referer': 'https://www.youtube.com/tv',
                   'Accept-Encoding': 'gzip, deflate',
                   'Accept-Language': 'en-US,en;q=0.8,de;q=0.6'}

        _client_id = client_id
        if not client_id:
            _client_id = self.YOUTUBE_TV_CLIENT_ID
            pass
        _client_secret = client_secret
        if not _client_secret:
            _client_secret = self.YOUTUBE_TV_CLIENT_SECRET
            pass
        post_data = {'client_id': _client_id,
                     'client_secret': _client_secret,
                     'refresh_token': refresh_token,
                     'grant_type': 'refresh_token'}

        # url
        url = 'https://www.youtube.com/o/oauth2/token'

        result = requests.post(url, data=post_data, headers=headers, verify=False)
        if result.status_code != requests.codes.ok:
            raise LoginException('Login Failed')

        if result.headers.get('content-type', '').startswith('application/json'):
            json_data = result.json()
            access_token = json_data['access_token']
            expires_in = time.time() + int(json_data.get('expires_in', 3600))
            return access_token, expires_in

        return '', ''

    def get_device_token(self, code, client_id='', client_secret='', grant_type=''):
        headers = {'Host': 'www.youtube.com',
                   'Connection': 'keep-alive',
                   'Origin': 'https://www.youtube.com',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.28 Safari/537.36',
                   'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
                   'Accept': '*/*',
                   'DNT': '1',
                   'Referer': 'https://www.youtube.com/tv',
                   'Accept-Encoding': 'gzip, deflate',
                   'Accept-Language': 'en-US,en;q=0.8,de;q=0.6'}

        _client_id = client_id
        if not client_id:
            _client_id = self.YOUTUBE_TV_CLIENT_ID
            pass
        _client_secret = client_secret
        if not _client_secret:
            _client_secret = self.YOUTUBE_TV_CLIENT_SECRET
            pass
        post_data = {'client_id': _client_id,
                     'client_secret': _client_secret,
                     'code': code,
                     'grant_type': 'http://oauth.net/grant_type/device/1.0'}

        # url
        url = 'https://www.youtube.com/o/oauth2/token'

        result = requests.post(url, data=post_data, headers=headers, verify=False)
        if result.status_code != requests.codes.ok:
            raise LoginException('Login Failed')

        if result.headers.get('content-type', '').startswith('application/json'):
            return result.json()

        return None

    def generate_user_code(self, client_id=''):
        headers = {'Host': 'www.youtube.com',
                   'Connection': 'keep-alive',
                   'Origin': 'https://www.youtube.com',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.28 Safari/537.36',
                   'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
                   'Accept': '*/*',
                   'DNT': '1',
                   'Referer': 'https://www.youtube.com/tv',
                   'Accept-Encoding': 'gzip, deflate',
                   'Accept-Language': 'en-US,en;q=0.8,de;q=0.6'}

        _client_id = client_id
        if not client_id:
            _client_id = self.YOUTUBE_TV_CLIENT_ID
        post_data = {'client_id': _client_id,
                     'scope': 'http://gdata.youtube.com https://www.googleapis.com/auth/youtube-paid-content'}

        # url
        url = 'https://www.youtube.com/o/oauth2/device/code'

        result = requests.post(url, data=post_data, headers=headers, verify=False)
        if result.status_code != requests.codes.ok:
            raise LoginException('Login Failed')

        if result.headers.get('content-type', '').startswith('application/json'):
            return result.json()

        return None

    def get_access_token(self):
        return self._access_token

    def authenticate(self, username, password):
        headers = {'device': '38c6ee9a82b8b10a',
                   'app': 'com.google.android.youtube',
                   'User-Agent': 'GoogleAuth/1.4 (GT-I9100 KTU84Q)',
                   'content-type': 'application/x-www-form-urlencoded',
                   'Host': 'android.clients.google.com',
                   'Connection': 'Keep-Alive',
                   'Accept-Encoding': 'gzip'}

        post_data = {'device_country': self._country.lower(),
                     'operatorCountry': self._country.lower(),
                     'lang': self._language.replace('-', '_'),
                     'sdk_version': '19',
                     # 'google_play_services_version': '6188034',
                     'accountType': 'HOSTED_OR_GOOGLE',
                     'Email': username.encode('utf-8'),
                     'service': 'oauth2:https://www.googleapis.com/auth/youtube https://www.googleapis.com/auth/youtube.force-ssl https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/emeraldsea.mobileapps.doritos.cookie https://www.googleapis.com/auth/plus.stream.read https://www.googleapis.com/auth/plus.stream.write https://www.googleapis.com/auth/plus.pages.manage https://www.googleapis.com/auth/identity.plus.page.impersonation',
                     'source': 'android',
                     'androidId': '38c6ee9a82b8b10a',
                     'app': 'com.google.android.youtube',
                     # 'client_sig': '24bb24c05e47e0aefa68a58a766179d9b613a600',
                     'callerPkg': 'com.google.android.youtube',
                     #'callerSig': '24bb24c05e47e0aefa68a58a766179d9b613a600',
                     'Passwd': password.encode('utf-8')}

        # url
        url = 'https://android.clients.google.com/auth'

        result = requests.post(url, data=post_data, headers=headers, verify=False)
        if result.status_code != requests.codes.ok:
            raise LoginException('Login Failed')

        lines = result.text.replace('\n', '&')
        params = dict(urlparse.parse_qsl(lines))
        token = params.get('Auth', '')
        expires = int(params.get('Expiry', -1))
        if not token or expires == -1:
            raise LoginException('Failed to get token')

        return token, expires

    def get_language(self):
        return self._language

    def get_video_streams(self, context, video_id):
        video_info = VideoInfo(context, self)
        return video_info.load_stream_infos(video_id)

    def get_uploaded_videos_of_subscriptions(self, start_index=0):
        params = {'max-results': str(self._max_results),
                  'alt': 'json'}
        if start_index > 0:
            params['start-index'] = str(start_index)
            pass
        return self._perform_v2_request(method='GET', path='feeds/api/users/default/newsubscriptionvideos',
                                        params=params)

    def add_video_to_playlist(self, playlist_id, video_id):
        params = {'part': 'snippet',
                  'mine': 'true'}
        post_data = {'kind': 'youtube#playlistItem',
                     'snippet': {'playlistId': playlist_id,
                                 'resourceId': {'kind': 'youtube#video',
                                                'videoId': video_id}}}
        return self._perform_v3_request(method='POST', path='playlistItems', params=params, post_data=post_data)

    def remove_video_from_playlist(self, playlist_id, playlist_item_id):
        params = {'id': playlist_item_id}
        return self._perform_v3_request(method='DELETE', path='playlistItems', params=params)

    def unsubscribe(self, subscription_id):
        params = {'id': subscription_id}
        return self._perform_v3_request(method='DELETE', path='subscriptions', params=params)

    def subscribe(self, channel_id):
        params = {'part': 'snippet'}
        post_data = {'kind': 'youtube#subscription',
                     'snippet': {'resourceId': {'kind': 'youtube#channel',
                                                'channelId': channel_id}}}
        return self._perform_v3_request(method='POST', path='subscriptions', params=params, post_data=post_data)

    def get_subscription(self, channel_id, order='alphabetical', page_token=''):
        """

        :param channel_id: [channel-id|'mine']
        :param order: ['alphabetical'|'relevance'|'unread']
        :param page_token:
        :return:
        """
        params = {'part': 'snippet,contentDetails',
                  'maxResults': str(self._max_results),
                  'order': order}
        if channel_id == 'mine':
            params['mine'] = 'true'
            pass
        else:
            params['channelId'] = channel_id
            pass
        if page_token:
            params['pageToken'] = page_token
            pass

        return self._perform_v3_request(method='GET', path='subscriptions', params=params)

    def get_guide_category(self, guide_category_id, page_token=''):
        params = {'part': 'snippet,contentDetails,brandingSettings',
                  'maxResults': str(self._max_results),
                  'categoryId': guide_category_id,
                  'regionCode': self._country,
                  'hl': self._language}
        if page_token:
            params['pageToken'] = page_token
            pass
        return self._perform_v3_request(method='GET', path='channels', params=params)

    def get_guide_categories(self, page_token=''):
        params = {'part': 'snippet',
                  'maxResults': str(self._max_results),
                  'regionCode': self._country,
                  'hl': self._language}
        if page_token:
            params['pageToken'] = page_token
            pass

        return self._perform_v3_request(method='GET', path='guideCategories', params=params)

    def get_popular_videos(self, page_token=''):
        params = {'part': 'snippet,contentDetails',
                  'maxResults': str(self._max_results),
                  'regionCode': self._country,
                  'hl': self._language,
                  'chart': 'mostPopular'}
        if page_token:
            params['pageToken'] = page_token
            pass
        return self._perform_v3_request(method='GET', path='videos', params=params)

    def get_video_category(self, video_category_id, page_token=''):
        params = {'part': 'snippet,contentDetails',
                  'maxResults': str(self._max_results),
                  'videoCategoryId': video_category_id,
                  'chart': 'mostPopular',
                  'regionCode': self._country,
                  'hl': self._language}
        if page_token:
            params['pageToken'] = page_token
            pass
        return self._perform_v3_request(method='GET', path='videos', params=params)

    def get_video_categories(self, page_token=''):
        params = {'part': 'snippet',
                  'maxResults': str(self._max_results),
                  'regionCode': self._country,
                  'hl': self._language}
        if page_token:
            params['pageToken'] = page_token
            pass

        return self._perform_v3_request(method='GET', path='videoCategories', params=params)

    def get_activities(self, channel_id, page_token=''):
        params = {'part': 'snippet,contentDetails',
                  'maxResults': str(self._max_results),
                  'regionCode': self._country,
                  'hl': self._language}
        if channel_id == 'home':
            params['home'] = 'true'
            pass
        elif channel_id == 'mine':
            params['mine'] = 'true'
            pass
        else:
            params['channelId'] = channel_id
            pass
        if page_token:
            params['pageToken'] = page_token
            pass

        return self._perform_v3_request(method='GET', path='activities', params=params)

    def get_playlists(self, channel_id, page_token=''):
        params = {'part': 'snippet,contentDetails',
                  'maxResults': str(self._max_results)}
        if channel_id != 'mine':
            params['channelId'] = channel_id
            pass
        else:
            params['mine'] = 'true'
            pass
        if page_token:
            params['pageToken'] = page_token
            pass

        return self._perform_v3_request(method='GET', path='playlists', params=params)

    def get_playlist_item_id_of_video_id(self, playlist_id, video_id):
        json_data = self.get_playlist_items(playlist_id=playlist_id, video_id=video_id)
        items = json_data.get('items', [])
        if len(items) > 0:
            return items[0]['id']

        return None

    def get_playlist_items(self, playlist_id, video_id='', page_token=''):
        # prepare params
        params = {'part': 'snippet',
                  'maxResults': str(self._max_results),
                  'playlistId': playlist_id}
        if page_token:
            params['pageToken'] = page_token
            pass
        if video_id:
            params['videoId'] = video_id
            pass

        return self._perform_v3_request(method='GET', path='playlistItems', params=params)

    def get_channels(self, channel_id):
        """
        Returns a collection of zero or more channel resources that match the request criteria.
        :param channel_id: list or comma-separated list of the YouTube channel ID(s)
        :return:
        """
        if isinstance(channel_id, list):
            channel_id = ','.join(channel_id)
            pass

        params = {'part': 'snippet,contentDetails,brandingSettings'}
        if channel_id != 'mine':
            params['id'] = channel_id
            pass
        else:
            params['mine'] = 'true'
            pass
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

    def get_related_videos(self, video_id, page_token=''):
        # prepare page token
        if not page_token:
            page_token = ''
            pass

        # prepare params
        params = {'relatedToVideoId': video_id,
                  'part': 'snippet',
                  'type': 'video',
                  'regionCode': self._country,
                  'hl': self._language,
                  'maxResults': str(self._max_results)}
        if page_token:
            params['pageToken'] = page_token
            pass

        return self._perform_v3_request(method='GET', path='search', params=params)

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
                  'hl': self._language,
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
        if self._access_token:
            _headers['Authorization'] = 'Bearer %s' % self._access_token
            pass
        _headers.update(headers)

        # url
        _url = 'https://www.googleapis.com/youtube/v3/%s' % path.strip('/')

        result = None
        if method == 'GET':
            result = requests.get(_url, params=_params, headers=_headers, verify=False, allow_redirects=allow_redirects)
        elif method == 'POST':
            _headers['content-type'] = 'application/json'
            result = requests.post(_url, data=json.dumps(post_data), params=_params, headers=_headers, verify=False,
                                   allow_redirects=allow_redirects)
        elif method == 'PUT':
            result = requests.put(_url, data=json.dumps(_post_data), params=_params, headers=_headers, verify=False,
                                  allow_redirects=allow_redirects)
        elif method == 'DELETE':
            result = requests.delete(_url, params=_params, headers=_headers, verify=False,
                                     allow_redirects=allow_redirects)
            pass

        if result is None:
            return {}

        if result.headers.get('content-type', '').startswith('application/json'):
            return result.json()

        pass

    def _perform_v2_request(self, method='GET', headers=None, path=None, post_data=None, params=None,
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
        _headers = {'Host': 'gdata.youtube.com',
                    'X-GData-Key': 'key=%s' % self._key,
                    'GData-Version': '2.1',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.36 Safari/537.36'}
        if self._access_token:
            _headers['Authorization'] = 'Bearer %s' % self._access_token
            pass
        _headers.update(headers)

        # url
        url = 'https://gdata.youtube.com/%s/' % path.strip('/')

        result = None
        if method == 'GET':
            result = requests.get(url, params=_params, headers=_headers, verify=False, allow_redirects=allow_redirects)
        elif method == 'POST':
            _headers['content-type'] = 'application/json'
            result = requests.post(_url, data=json.dumps(post_data), params=_params, headers=_headers, verify=False,
                                   allow_redirects=allow_redirects)
        elif method == 'PUT':
            result = requests.put(_url, data=json.dumps(_post_data), params=_params, headers=_headers, verify=False,
                                  allow_redirects=allow_redirects)
        elif method == 'DELETE':
            result = requests.delete(_url, params=_params, headers=_headers, verify=False,
                                     allow_redirects=allow_redirects)
            pass

        if result is None:
            return {}

        if method != 'DELETE' and result.text:
            return result.json()
        pass

    pass