import urllib
import urllib2
import json

__YOUTUBE_API_KEY__ = 'AIzaSyA8eiZmM1FaDVjRy-df2KTyQ_vz_yYM39w'

class YouTubeClient(object):
    def __init__(self):
        self._opener = urllib2.build_opener()
        #opener.addheaders = [('User-Agent', 'stagefright/1.2 (Linux;Android 4.4.2)')]
        
        self._API_Key = __YOUTUBE_API_KEY__
        pass
    
    def _createUrl(self, command, params={}):
        url = 'https://www.googleapis.com/youtube/v3/%s' % (command)
        
        _params = {}
        _params.update(params)
        _params['key'] = self._API_Key
        
        if _params!=None and len(_params)>0:
            return url + '?' + urllib.urlencode(_params)
        
        return url
    
    def _doSearch(self, text):
        params = {'q': text,
                  'part': 'snippet'}
        url = self._createUrl(command='search', params=params)
        content = self._opener.open(url)
        return json.load(content, encoding='utf-8')
    
    def search(self, text):
        return self._doSearch(text)
        pass