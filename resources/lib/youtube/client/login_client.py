import time
import urlparse

__author__ = 'bromix'

import requests
# Verify is disabled and to avoid warnings we disable the warnings. Behind a proxy request isn't working correctly all
# the time and if so can't validate the hosts correctly resulting in a exception and the addon won't work properly.
try:
    from requests.packages import urllib3

    urllib3.disable_warnings()
except:
    # do nothing
    pass

from resources.lib.youtube.youtube_exceptions import LoginException


class LoginClient(object):
    YOUTUBE_TV_KEY = 'AIzaSyAd-YEOqZz9nXVzGtn3KWzYLbLaajhqIDA'
    YOUTUBE_TV_CLIENT_ID = '861556708454-d6dlm3lh05idd8npek18k6be8ba3oc68.apps.googleusercontent.com'
    YOUTUBE_TV_CLIENT_SECRET = 'SboVhoG9s0rNafixCSGGKXAT'

    YOUTUBE_APP_KEY = 'AIzaSyA8eiZmM1FaDVjRy-df2KTyQ_vz_yYM39w'
    # YOUTUBE_WEB_KEY = 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8'

    def __init__(self, key='', language='en-US', access_token=''):
        self._key = self.YOUTUBE_TV_KEY
        if key:
            self._key = key
            pass

        self._language = language.replace('-', '_')
        self._country = language.split('-')[1]
        self._access_token = access_token
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
    pass
