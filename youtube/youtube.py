import urllib
import urllib2
import json
import re
import urlparse

__YOUTUBE_API_KEY__ = 'AIzaSyA8eiZmM1FaDVjRy-df2KTyQ_vz_yYM39w'

class YouTubeClient(object):
    def __init__(self, language='en-US', maxResult=5):
        self._opener = urllib2.build_opener()
        #opener.addheaders = [('User-Agent', 'stagefright/1.2 (Linux;Android 4.4.2)')]
        
        self._HL = language
        _language = language.split('-')
        self._RegionCode = _language[1]
        
        self._API_Key = __YOUTUBE_API_KEY__
        self._MaxResult = maxResult
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
    
    def getVideoStreams(self, videoId):
        result = {}
    
        opener = urllib2.build_opener()
        url = 'https://www.youtube.com/watch?v=%s' % (videoId)
        content = opener.open(url)
        
        html = content.read()
        
        # first find the format list and create a map of the resolutions
        fmtListMatch = re.compile(".+\"fmt_list\": \"(.+?)\".+").findall(html)
        if fmtListMatch!=None and len(fmtListMatch)>0 and len(fmtListMatch[0])>=1:
            valueString = fmtListMatch[0]
            values = valueString.split(',')
            
            for value in values:
                value = value.replace('\/', '|')
                
                try:
                    attr = value.split('|')
                    sizes = attr[1].split('x')
                    result[attr[0]] =  {'width': int(sizes[0]), 'height': int(sizes[1])}
                except:
                    # do nothing
                    pass
                pass
            pass
        
        streamsMatch = re.compile('.+\"url_encoded_fmt_stream_map\": \"(.+?)\".+').findall(html)
        if streamsMatch!=None and len(streamsMatch)>0 and len(streamsMatch[0])>=1:
            valueString = streamsMatch[0]
            values = valueString.split(',')
            
            for value in values:
                value = value.replace('\\u0026', '&')
                attr = dict(urlparse.parse_qsl( value ) )
                
                try:
                    url = urllib.unquote(attr['url'])
                    id = attr['itag']
                    type = attr['type'].split(';')[0]
                    result[id]['url'] = url
                    result[id]['type'] = type
                except:
                    # do nothing
                    pass
        
        """     
        adaptiveFormatsMatch = re.compile('.+\"adaptive_fmts\": \"(.+?)\".+').findall(html)
        if adaptiveFormatsMatch!=None and len(adaptiveFormatsMatch)>0 and len(adaptiveFormatsMatch[0])>=1:
            valueString = adaptiveFormatsMatch[0]
            values = valueString.split(',')
            
            for value in values:
                value = value.replace('\\u0026', '&')
                attr = dict(urlparse.parse_qsl( value ) )
                
                try:
                    url = urllib.unquote(attr['url'])
                    id = attr['itag']
                    sizes = attr['size'].split('x')
                    type = attr['type'].split(';')[0]
                    result[id] = {'url':url,
                                  'width': int(sizes[0]),
                                  'height': int(sizes[1]),
                                  'type': type}
                except:
                    # do nothing
                    pass
                    """
                
        return result
    
    def getBestFittingVideoStream(self, videoId=None, videoStreams=None, size=720):
        if videoId!=None:
            videoStreams = self.getVideoStreams(videoId)
    
        result = None
        lastSize = 0
        for key in videoStreams:
            stream = videoStreams[key]
            
            currentSize = stream['height']
            
            if currentSize>=lastSize and currentSize<=size:
                lastSize = currentSize
                result = stream
            pass
            
        return result