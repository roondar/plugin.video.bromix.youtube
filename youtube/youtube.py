import urllib
import urllib2
import json

__YOUTUBE_API_KEY__ = 'AIzaSyA8eiZmM1FaDVjRy-df2KTyQ_vz_yYM39w'

class YouTubeClient(object):
    def __init__(self, language='en-US'):
        self._opener = urllib2.build_opener()
        #opener.addheaders = [('User-Agent', 'stagefright/1.2 (Linux;Android 4.4.2)')]
        
        self._HL = language
        _language = language.split('-')
        self._RegionCode = _language[1]
        
        self._API_Key = __YOUTUBE_API_KEY__
        self._MaxResult = 5
        pass
    
    def _createUrl(self, command, params={}):
        url = 'https://www.googleapis.com/youtube/v3/%s' % (command)
        
        _params = {}
        _params.update(params)
        _params['key'] = self._API_Key
        
        if _params!=None and len(_params)>0:
            return url + '?' + urllib.urlencode(_params)
        
        return url
    
    def _executeApi(self, command, params={}):
        url = self._createUrl(command=command, params=params)
        content = self._opener.open(url)
        return json.load(content, encoding='utf-8')
    
    def getGuideCategories(self):
        params = {'part': 'snippet',
                  'regionCode': self._RegionCode,
                  'hl': self._HL}
        return self._executeApi('guideCategories', params)
    
    def getChannelCategory(self, categoryId, nextPageToken=None):
        params = {'part': 'snippet,contentDetails',
                  'categoryId': categoryId,
                  'maxResults': self._MaxResult}
        if nextPageToken!=None:
            params['pageToken'] = nextPageToken

        return self._executeApi('channels', params)
    
    def getPlaylistItems(self, playlistId, nextPageToken=None):
        params = {'part': 'snippet',
                  'playlistId': playlistId,
                  'maxResults': self._MaxResult}
        if nextPageToken!=None:
            params['pageToken'] = nextPageToken

        return self._executeApi('playlistItems', params)
    
    def search(self, text, nextPageToken=None):
        params = {'q': text,
                  'part': 'snippet',
                  'maxResults': self._MaxResult}
        if nextPageToken!=None:
            params['pageToken'] = nextPageToken

        return self._executeApi('search', params)