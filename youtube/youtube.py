# -*- coding: utf-8 -*-

import urllib
import urllib2
import json
import re
import urlparse

__YOUTUBE_API_KEY__ = 'AIzaSyA8eiZmM1FaDVjRy-df2KTyQ_vz_yYM39w'

class YouTubeClient(object):
    def __init__(self, username=None, password=None, language='en-US', maxResult=5, cachedToken=None):
        self._opener = urllib2.build_opener()
        #opener.addheaders = [('User-Agent', 'stagefright/1.2 (Linux;Android 4.4.2)')]
        
        self._Username = username
        self._Password = password
        self._CachedToken = cachedToken
        
        self._HL = language
        _language = language.split('-')
        self._RegionCode = _language[1]
        
        self._API_Key = __YOUTUBE_API_KEY__
        self._MaxResult = maxResult
        pass
    
    def hasLogin(self):
        return self._CachedToken!=None and self._Username!=None and self._Password!=None
    
    def getUserToken(self):
        params = {'device_country': self._RegionCode.lower(),
                  'operatorCountry': self._RegionCode.lower(),
                  'lang': self._HL.replace('-', '_'),
                  'sdk_version': '19',
                  #'google_play_services_version': '5084034',
                  #'accountType' : 'HOSTED_OR_GOOGLE',
                  'Email': self._Username,
                  'service': 'oauth2:https://www.googleapis.com/auth/youtube https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/emeraldsea.mobileapps.doritos.cookie https://www.googleapis.com/auth/plus.stream.read https://www.googleapis.com/auth/plus.stream.write https://www.googleapis.com/auth/plus.pages.manage',
                  'source': 'android',
                  #'androidId': '3b7ee32203b0465cb586551ee989b5ae',
                  'app': 'com.google.android.youtube',
                  #'callerPkg' : 'com.google.android.youtube',
                  'Passwd' : self._Password
                  }
    
        params = urllib.urlencode(params)
        
        result = {}
        
        try:
            url = 'https://android.clients.google.com/auth'
            request = urllib2.Request(url, data=params) 
            #request.add_header('device', '3b7ee32203b0465cb586551ee989b5ae')
            request.add_header('app', 'com.google.android.youtube')
            request.add_header('User-Agent', 'GoogleAuth/1.4 (GT-I9100 KTU84P) (GT-I9100 KTU84P)')
            request.add_header('content-type', 'application/x-www-form-urlencoded')
            request.add_header('Host', 'android.clients.google.com')
            request.add_header('Connection', 'Keep-Alive')
            #request.add_header('Accept-Encoding', 'gzip') 
            
            content = urllib2.urlopen(request)
            data = content.read()
            lines = data.split('\n')
            for line in lines:
                _property = line.split('=')
                if len(_property)>=2:
                    result[_property[0]] = _property[1]
        except:
            # do nothing
            pass
        
        self._CachedToken = result.get('Auth', None)
        
        return result
    
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
        return json.load(content)
    
    def _makeCommaSeparatedList(self, values=[]):
        result = ''
        
        for value in values:
            result = result+value
            result = result+','
        if len(result)>0:
            result = result[:-1]
        
        return result;
    
    def getVideosInfo(self, videoIds=[]):
        result = {}
        
        if len(videoIds)==0:
            return result
        
        videos = self.getVideos(videoIds)
        videos = videos.get('items', [])
        for video in videos:
            _id = video.get('id', None)
            contentDetails = video.get('contentDetails', {})
            duration = contentDetails.get('duration', None)
            if id!=None and duration!=None:
                durationMatch = re.compile('PT((\d)*H)*((\d*)M)+((\d*)S)+').findall(duration)
                
                minutes = 1
                if durationMatch!=None and len(durationMatch)>0:
                    minutes = 1
                    if len(durationMatch[0])>=2 and durationMatch[0][3]!='':
                        minutes = int(durationMatch[0][3])
                        
                    if len(durationMatch[0])>=1 and durationMatch[0][1]!='':
                        minutes = minutes+ int(durationMatch[0][1])*60
                    pass
                
                duration = str(minutes)
                result[_id] = {'duration': duration}
                pass
            pass
        
        return result
    
    def getVideos(self, videoIds=[]):
        params = {'part': 'contentDetails',
                  'id': self._makeCommaSeparatedList(videoIds)}
        return self._executeApi('videos', params)
    
    def getSubscriptions(self, mine=None, nextPageToken=None):
        params = {'part': 'snippet'}
        
        if mine!=None and mine==True:
            params['access_token'] = self._CachedToken
            params['mine'] = 'true'
            
        if nextPageToken!=None:
            params['pageToken'] = nextPageToken
        
        return self._executeApi('subscriptions', params)
    
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
    
    def getPlaylists(self, channelId, nextPageToken=None):
        params = {'part': 'snippet',
                  'channelId': channelId,
                  'maxResults': self._MaxResult}
        if nextPageToken!=None:
            params['pageToken'] = nextPageToken

        return self._executeApi('playlists', params)
    
    def getPlaylistItems(self, playlistId, mine=False, nextPageToken=None):
        params = {'part': 'snippet',
                  'playlistId': playlistId,
                  'maxResults': self._MaxResult}
        
        if mine==True:
            params['access_token'] = self._CachedToken
            
        
        if nextPageToken!=None:
            params['pageToken'] = nextPageToken

        return self._executeApi('playlistItems', params)
    
    def getChannels(self, channelId=None, mine=None, nextPageToken=None):
        params = {'part': 'snippet, contentDetails'}
        
        if channelId!=None:
            params['id'] = channelId
            
        if mine!=None and mine==True:
            params['mine'] = 'true'
            params['access_token'] = self._CachedToken
            
        if nextPageToken!=None:
            params['pageToken'] = nextPageToken

        return self._executeApi('channels', params)
    
    def search(self, text, nextPageToken=None):
        params = {'q': text,
                  'part': 'snippet',
                  'maxResults': self._MaxResult}
        if nextPageToken!=None:
            params['pageToken'] = nextPageToken

        return self._executeApi('search', params)
    
    def _getDecodedSignature(self, signature):
        result = ''
        try:
            url = 'http://www.freemake.com/SignatureDecoder/decoder.php?text=%s' % (signature)
            request = urllib2.Request(url) 
            request.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
            request.add_header('Accept-Language', 'en-US;q=0.6,en;q=0.4')
            request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.107 Safari/537.36')
            request.add_header('Host', 'www.freemake.com')
            
            content = urllib2.urlopen(request)
            result = content.read()
        except:
            # do nothing
            pass
        
        return result
    
    def getVideoStreams(self, videoId):
        result = {}
    
        opener = urllib2.build_opener()
        url = 'https://www.youtube.com/watch?v=%s' % (videoId)
        content = opener.open(url)
        
        html = content.read()
        
        # first find the format list and create a map of the resolutions
        fmtListMatch = re.compile('.+\"fmt_list\": \"(.+?)\".+').findall(html)
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
                    
                    signature = None
                    if attr.get('s', None)!=None:
                        signature = self._getDecodedSignature(attr.get('s', None))
                    elif attr.get('sig', None)!=None:
                        signature = attr.get('sig', '')
                        
                    if signature!=None and len(signature)>0:
                        url = url + '&signature='
                        url = url + signature
                        
                    
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
                    
                    signature = None
                    if attr.get('s', None)!=None:
                        signature = _getDecodedSignature(attr.get('s', None))
                    elif attr.get('sig', None)!=None:
                        signature = attr.get('sig', '')
                        
                    if signature!=None and len(signature)>0:
                        url = url + '&signature='
                        url = url + signature
                    
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