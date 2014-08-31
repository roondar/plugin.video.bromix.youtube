# -*- coding: utf-8 -*-

import urllib
import urllib2
import json
import re
import time
import requests

__YOUTUBE_API_KEY__ = 'AIzaSyA8eiZmM1FaDVjRy-df2KTyQ_vz_yYM39w' #prim
#__YOUTUBE_API_KEY__ = 'AIzaSyAjbrAsTJS55zRnLb_P3Pf4-vAnMi125GI' #seco

class YouTubeClient(object):
    def __init__(self, username=None, password=None, language='en-US', maxResult=5, cachedToken=None, accessTokenExpiresAt=-1):
        self._opener = urllib2.build_opener()
        #opener.addheaders = [('User-Agent', 'stagefright/1.2 (Linux;Android 4.4.2)')]
        
        self._Username = username
        self._Password = password
        
        self.AccessToken = cachedToken
        self.AccessTokenExpiresAt = accessTokenExpiresAt
        
        self._HL = language
        _language = language.split('-')
        self._RegionCode = _language[1]
        
        self._API_Key = __YOUTUBE_API_KEY__
        self._MaxResult = maxResult
        pass
    
    def hasLogin(self):
        if not self._hasValidToken():
            self._updateToken()
            
        return self.AccessToken!=None
    
    def getUserToken(self):
        if self._Username==None or len(self._Username)==0:
            return {}
        
        if self._Password==None or len(self._Password)==0:
            return {}
        
        params = {'device_country': self._RegionCode.lower(),
                  'operatorCountry': self._RegionCode.lower(),
                  'lang': self._HL.replace('-', '_'),
                  'sdk_version': '19',
                  #'google_play_services_version': '5084034',
                  #'accountType' : 'HOSTED_OR_GOOGLE',
                  'Email': self._Username,
                  #'service': 'oauth2:https://www.googleapis.com/auth/youtube https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/emeraldsea.mobileapps.doritos.cookie https://www.googleapis.com/auth/plus.stream.read https://www.googleapis.com/auth/plus.stream.write https://www.googleapis.com/auth/plus.pages.manage',
                  'service': 'oauth2:https://www.googleapis.com/auth/youtube https://www.googleapis.com/auth/youtube.readonly https://www.googleapis.com/auth/youtube.upload',
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
        
        self.AccessToken = result.get('Auth', None)
        
        return result
    
    def _createUrlV3(self, command, params={}):
        url = 'https://www.googleapis.com/youtube/v3/%s' % (command)
        
        _params = {}
        _params.update(params)
        _params['key'] = self._API_Key
        
        if _params!=None and len(_params)>0:
            return url + '?' + urllib.urlencode(_params)
        
        return url
    
    def _updateToken(self):
        authData = self.getUserToken()
        self.AccessToken = authData.get('Auth', None)
        self.AccessTokenExpiresAt = authData.get('Expiry', None)
        
    def _hasValidToken(self):
        isExpired = self.AccessTokenExpiresAt < time.time()
        if (self.AccessToken==None or len(self.AccessToken)==0 or isExpired):
            return False
        
        # and (self._Username!=None and self._Password!=None and len(self._Username)>0 and len(self._Password)>0):
        
        return True
    
    def _executeApiV3(self, command, params={}, jsonData=None, tries=1, method='GET'):
        if 'access_token' in params:
            if not self._hasValidToken():
                self._updateToken()
                params['access_token'] = self.AccessToken
                
        headers = {'X-JavaScript-User-Agent': 'Google APIs Explorer',
                   'Host': 'www.googleapis.com',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.58 Safari/537.36'}
        if 'access_token' in params:
            headers['Authorization'] = 'Bearer %s' % (self.AccessToken)
            del params['access_token']
        
        url = self._createUrlV3(command=command, params=params)
        
        try:
            if method=='GET':
                content = requests.get(url, headers=headers, verify=False)
                return json.loads(content.text)
            elif method=='POST':
                headers['content-type'] = 'application/json'
                content = requests.post(url, data=json.dumps(jsonData), headers=headers, verify=False)
            elif method=='DELETE':
                content = requests.delete(url, headers=headers, verify=False)
                pass
        except:
            if tries>=1:
                tries = tries-1
                return self._executeApiV3(command, params, tries, method)
        
            return {}
        pass
    
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
            
            result[_id] = {}
            contentDetails = video.get('contentDetails', {})
            duration = contentDetails.get('duration', None)
            if id!=None and duration!=None:
                durationMatch = re.compile('PT((\d+)H)?((\d+)M)?((\d+)S)?').findall(duration)
                
                minutes = 1
                if durationMatch!=None and len(durationMatch)>0:
                    hours = 0
                    if durationMatch[0][1]!='':
                        hours = int(durationMatch[0][1])
                        pass
                    
                    minutes = 1
                    if durationMatch[0][3]!='':
                        minutes = int(durationMatch[0][3])
                        pass
                    
                    minutes = (hours*60)+minutes
                    pass
                
                duration = str(minutes)
                result[_id]['duration'] = duration
                pass
            
            snippet = video.get('snippet', None)
            if snippet!=None:
                result[_id]['channelName'] = snippet.get('channelTitle', '')
                result[_id]['channelId'] = snippet.get('channelId', '')
                result[_id]['plot'] = snippet.get('description', '')
                
                thumbnails = snippet.get('thumbnails', {})
                #imageResList = ['maxres', 'standard', 'high', 'medium', 'default']
                imageResList = ['high', 'medium', 'default']
                for imageRes in imageResList:
                    item = thumbnails.get(imageRes, None)
                    if item!=None:
                        width = item.get('width', None)
                        height = item.get('height', None)
                        
                        url = item.get('url', None)
                        if url!=None and (url.find('yt3.')>0 or imageRes=='medium' or (width!=None and height!=None)):
                            result[_id]['thumbnailImage'] = url
                            break
                    pass
                pass
            pass
        
        return result
    
    def getVideos(self, videoIds=[]):
        params = {'part': 'snippet,contentDetails',
                  'id': self._makeCommaSeparatedList(videoIds)}
        #'access_token': self.AccessToken}
        return self._executeApiV3('videos', params)
    
    def _sortItems(self, item):
        snippet = item.get('snippet', {})
        publishedAt = snippet.get('publishedAt', '') 
        return publishedAt
    
    def getSubscriptions(self, mine=None, order='alphabetical', nextPageToken=None):
        params = {'part': 'snippet',
                  'order': order,
                  'maxResults': self._MaxResult}
        
        if mine!=None and mine==True:
            params['access_token'] = self.AccessToken
            params['mine'] = 'true'
            
        if nextPageToken!=None:
            params['pageToken'] = nextPageToken
        
        return self._executeApiV3('subscriptions', params)
    
    def addSubscription(self, channelId):
        params = {'part': 'snippet',
                  'access_token': self.AccessToken}
        
        jsonData = {'kind': 'youtube#subscription',
                    'snippet':{'resourceId': {'kind': 'youtube#channel',
                                              'channelId': channelId}
                               }
                    }
        
        result = self._executeApiV3('subscriptions', params=params, jsonData=jsonData, method='POST')
        pass
    
    def removeSubscription(self, channelId):
        params = {'id': channelId,
                  'access_token': self.AccessToken}
        
        result = self._executeApiV3('subscriptions', params=params, method='DELETE')
        pass
    
    def getGuideCategories(self):
        params = {'part': 'snippet',
                  'regionCode': self._RegionCode,
                  'hl': self._HL}
        return self._executeApiV3('guideCategories', params)
    
    def getChannelCategory(self, categoryId, nextPageToken=None):
        params = {'part': 'snippet,contentDetails',
                  'categoryId': categoryId,
                  'maxResults': self._MaxResult}
        if nextPageToken!=None:
            params['pageToken'] = nextPageToken

        return self._executeApiV3('channels', params)
    
    def getPlaylists(self, channelId=None, mine=None, nextPageToken=None):
        params = {'part': 'snippet',
                  'maxResults': self._MaxResult}
        if nextPageToken!=None:
            params['pageToken'] = nextPageToken
            
        if channelId!=None:
            params['channelId'] = channelId
        elif mine!=None and mine==True:
            params['access_token'] = self.AccessToken
            params['mine'] = 'true'

        return self._executeApiV3('playlists', params)
    
    def getPlaylistItems(self, playlistId, mine=False, nextPageToken=None):
        params = {'part': 'snippet',
                  'playlistId': playlistId,
                  'maxResults': self._MaxResult}
        
        if mine==True:
            params['access_token'] = self.AccessToken
            
        
        if nextPageToken!=None:
            params['pageToken'] = nextPageToken

        return self._executeApiV3('playlistItems', params)
    
    def removePlaylist(self, playlistId):
        params = {'id': playlistId,
                  'access_token': self.AccessToken}
        
        result = self._executeApiV3('playlists', params=params, method='DELETE')
        pass
    
    def addPlayListItem(self, playlistId, videoId):
        params = {'part': 'snippet',
                  'mine': 'true',
                  'access_token': self.AccessToken}
        
        jsonData = {'kind': 'youtube#playlistItem',
                    'snippet':{'playlistId': playlistId,
                               'resourceId': {'kind': 'youtube#video',
                                              'videoId': videoId}
                               }
                    }
        
        result = self._executeApiV3('playlistItems', params=params, jsonData=jsonData, method='POST')
        pass
    
    def removePlaylistItem(self, playlistItemId):
        params = {'id': playlistItemId,
                  'access_token': self.AccessToken}
        
        result = self._executeApiV3('playlistItems', params=params, method='DELETE')
        pass
    
    def getActivities(self, channelId=None, home=None, mine=None, nextPageToken=None):
        #publishedAfter = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
        
        params = {'part': 'snippet,contentDetails',
                  'maxResults': self._MaxResult,
                  #'regionCode': self._RegionCode,
                  #'publishedBefore': publishedAfter
                  }
        
        if channelId!=None:
            params['channelId'] = channelId
        elif home!=None and home==True:
            params['home'] = 'true'
            params['access_token'] = self.AccessToken
        elif mine!=None and mine==True:
            params['mine'] = 'true'
            params['access_token'] = self.AccessToken
            
        if nextPageToken!=None:
            params['pageToken'] = nextPageToken
        
        jsonData = self._executeApiV3('activities', params)
        sortedItems = sorted(jsonData.get('items', []), key=self._sortItems, reverse=True)
        jsonData['items'] = sortedItems
        return jsonData
    
    def getChannels(self, channelId=None, mine=None, nextPageToken=None):
        params = {'part': 'snippet,contentDetails,brandingSettings'}
        
        if channelId!=None:
            params['id'] = channelId
            
        if mine!=None and mine==True:
            params['mine'] = 'true'
            params['access_token'] = self.AccessToken
            
        if nextPageToken!=None:
            params['pageToken'] = nextPageToken

        return self._executeApiV3('channels', params)
    
    def search(self, text, searchForVideos=None, searchForChannels=None, searchForPlaylists=None, nextPageToken=None):
        params = {'q': text,
                  'part': 'snippet',
                  'maxResults': self._MaxResult}
        
        types = []
        if searchForVideos!=None and searchForVideos==True:
            types.append('video')
        if searchForChannels!=None and searchForChannels==True:
            types.append('channel')
        if searchForPlaylists!=None and searchForPlaylists==True:
            types.append('playlist')
        if len(types)>0:
            params['type'] = self._makeCommaSeparatedList(types)
        
        if nextPageToken!=None:
            params['pageToken'] = nextPageToken

        return self._executeApiV3('search', params)
    
    def _createUrlV2(self, url, params={}):
        url = 'https://gdata.youtube.com/%s' % (url)
        
        _params = {}
        _params.update(params)
        
        if _params!=None and len(_params)>0:
            return url + '?' + urllib.urlencode(_params)
        
        return url
    
    def _executeApiV2(self, url, params={}, tries=1, method='GET'):
        if 'access_token' in params:
            if not self._hasValidToken():
                self._updateToken()
                params['access_token'] = self.AccessToken
                
        headers = {'Host': 'gdata.youtube.com',
                   'X-GData-Key': 'key=%s' % (__YOUTUBE_API_KEY__),
                   'GData-Version': '2',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.58 Safari/537.36'}
        if 'access_token' in params:
            headers['Authorization'] = 'Bearer %s' % (self.AccessToken)
            del params['access_token']
        
        url = self._createUrlV2(url=url, params=params)
        
        try:
            if method=='GET':
                content = requests.get(url, headers=headers, verify=False)
                return content.text
        except:
            if tries>=1:
                tries = tries-1
                return self._executeApiV3(url, params, tries, method)
        
            return ''
        pass
    
    def getNewSubscriptionVideosV2(self, startIndex=None):
        params = {'access_token': self.AccessToken,
                  'max-results': str(self._MaxResult)}
        
        if startIndex!=None:
            params['start-index'] = str(startIndex)
            
        return self._executeApiV2('feeds/api/users/default/newsubscriptionvideos', params=params)