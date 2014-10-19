import json
import requests

__author__ = 'bromix'


class Client(object):
    KEY = 'AIzaSyAd-YEOqZz9nXVzGtn3KWzYLbLaajhqIDA'

    def __init__(self, key='', language='en-US'):
        self._key = self.KEY
        if key:
            self._key = key
            pass

        self._language = language
        self._country = language.split('-')[1]
        pass

    def get_guide(self):
        post_data = {"context": {
                        "client": {
                            "clientName": "TVHTML5",
                            "clientVersion": "4",
                            "acceptRegion": "%s" % self._country,
                            "acceptLanguage": "%s" % self._language}
                        }
                    }
        headers = {'Accept': '*/*',
                   'Content-Type': 'application/json'}
        return self._perform_request(method='POST',
                                     headers=headers,
                                     path='youtubei/v1/guide',
                                     post_data=json.dumps(post_data))


    def _perform_request(self, method='GET', headers=None, path=None, post_data=None, params=None,
                         allow_redirects=True):
        # params
        if not params:
            params = {}
            pass
        params['key'] = self._key

        # basic header
        _headers = {'Accept-Encoding': 'gzip, deflate',
                    'Host': 'www.googleapis.com',
                    'Connection': 'Keep-Alive',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.27 Safari/537.36'}
        if not headers:
            headers = {}
            pass
        _headers.update(headers)

        # url
        _url = 'https://www.googleapis.com/%s' % path

        result = None
        if method == 'GET':
            result = requests.get(_url, params=params, headers=_headers, verify=False, allow_redirects=allow_redirects)
        elif method == 'POST':
            result = requests.post(_url, data=post_data, params=params, headers=_headers, verify=False,
                                   allow_redirects=allow_redirects)
        elif method == 'PUT':
            result = requests.put(_url, data=post_data, params=params, headers=_headers, verify=False,
                                  allow_redirects=allow_redirects)
        elif method == 'DELETE':
            result = requests.delete(_url, data=post_data, params=params, headers=_headers, verify=False,
                                     allow_redirects=allow_redirects)
            pass

        if result is None:
            return {}

        return result.json()

    pass