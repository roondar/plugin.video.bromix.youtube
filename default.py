# -*- coding: utf-8 -*-

import os

#import pydevd
#pydevd.settrace('localhost', stdoutToServer=True, stderrToServer=True)

import bromixbmc
__plugin__ = bromixbmc.Plugin()

# icons and images
__FANART__ = os.path.join(__plugin__.getPath(), "fanart.jpg")
__ICON_FALLBACK__ = os.path.join(__plugin__.getPath(), "resources/media/fallback_icon.png")
__ICON_SEARCH__ = os.path.join(__plugin__.getPath(), "resources/media/search.png")

# settings
__SETTING_SHOW_FANART__ = __plugin__.getSettingAsBool('showFanart')
if not __SETTING_SHOW_FANART__:
    __FANART__ = ''
__SETTING_RESULTPERPAGE__ = __plugin__.getSettingAsInt('resultPerPage', mapping={0:5, 1:10, 2:15, 3:20, 4:25, 5:30, 6:35, 7:40, 8:45, 9:50})
__SETTING_SHOW_PLAYLISTS__ = __plugin__.getSettingAsBool('showPlaylists')

#actions
__ACTION_SEARCH__ = 'search'
__ACTION_BROWSE_CHANNELS__ = 'browseChannels'
__ACTION_SHOW_CHANNEL_CATEGORY__ = 'showChannelCategory'
__ACTION_SHOW_PLAYLIST__ = 'showPlaylist'
__ACTION_SHOW_PLAYLISTS__ = 'showPlaylists'
__ACTION_SHOW_CHANNEL__ = 'showChannel'
__ACTION_SHOW_SUBSCRIPTIONS__ = 'showSubscriptions'
__ACTION_SHOW_WATCHLATER__ = 'showWatchLater'
__ACTION_PLAY__ = 'play'

from youtube import YouTubeClient

"""
This is a test token. This token will be generated and cached. The implementation of youtube should to that. So we can reuse the implementation without storing routines of
the addon.
"""
#__CACHEDTESTTOKEN__ = 'ya29.TwCGscExleVOMlMAAADwmCCr54hGDTeAODnrxuttdbp8uZD75HGM7NbPgyZU-DWdgrDHapbyyM33PdvgAd70F8ha9h4Vz57HobWlz5lY253WaPxBeIlojLlnDZid3LBDm3L1bBkxEsY7-gIq_D4'
__CACHEDTESTTOKEN__ = 'ya29.TwBoJK-9EwXmc1MAAACIQw69uQjgS3jSzO_mgUlFwcHJhMLaT4_him0PadKBFNhekFmtMrTj5ovLMc9mhwDMa_NIwJf0akRN0cJGQ7UtLTrbOxNb6uZPrr5y_u-CLDQGFELdhvJP93xXlBUwYoE'

__client__ = YouTubeClient(username = __plugin__.getSettingAsString('username'),
                           password = __plugin__.getSettingAsString('password'),
                           cachedToken = __CACHEDTESTTOKEN__,
                           language = bromixbmc.getLanguageId(),
                           maxResult = __SETTING_RESULTPERPAGE__
                           );


def showIndex():
    params = {'action': __ACTION_SEARCH__}
    __plugin__.addDirectory("[B]"+__plugin__.localize(30000)+"[/B]", params = params, thumbnailImage=__ICON_FALLBACK__, fanart=__FANART__)
    
    if __client__.hasLogin():
        params = {'action': __ACTION_SHOW_WATCHLATER__}
        __plugin__.addDirectory(__plugin__.localize(30005), params = params, thumbnailImage=__ICON_FALLBACK__, fanart=__FANART__)
        
        params = {'action': __ACTION_SHOW_SUBSCRIPTIONS__}
        __plugin__.addDirectory(__plugin__.localize(30004), params = params, thumbnailImage=__ICON_FALLBACK__, fanart=__FANART__)
        pass
    
    params = {'action': __ACTION_BROWSE_CHANNELS__}
    __plugin__.addDirectory(__plugin__.localize(30001), params = params, thumbnailImage=__ICON_FALLBACK__, fanart=__FANART__)
    
    __plugin__.endOfDirectory()
    
def _getPlaylistId(jsonData, name='uploads'):
    contentDetails = jsonData.get('contentDetails', {})
    relatedPlaylists = contentDetails.get('relatedPlaylists', {})
    return relatedPlaylists.get(name, None)

def _getBestThumbnailImage(jsonData):
    snippet = jsonData.get('snippet', {})
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
                return url
        pass
    
    return ''
    
def _listResult(jsonData, nextPageParams={}, pageIndex=1):
    items = jsonData.get('items', None)
    if items!=None:
        nextPageToken = jsonData.get('nextPageToken', None)
        
        """
        First try to collect all video items. We need each video ID to collect the duration
        in one go (max. 50 video IDs are possible). The YouTube API v3 only provide addtitional infos
        on videos. So we request them with this method.
        Per page this will cause one more call.        
        """
        videoIds = []
        for item in items:
            kind = item.get('kind', '')
            if kind=='youtube#searchResult':
                _id = item.get('id', {})
                videoId = _id.get('videoId', None)
                if videoId!=None:
                    videoIds.append(videoId)
            elif kind=='youtube#playlistItem':
                snippet = item.get('snippet', {})
                resourceId = snippet.get('resourceId', {})
                videoId = resourceId.get('videoId', None)
                if videoId!=None:
                    videoIds.append(videoId)
                    
        videoInfos = __client__.getVideosInfo(videoIds)
        
        """
        For each item we use some magic to show the content correct in XBMC.
        On call for all :)
        """
        for item in items:
            kind = item.get('kind', '')
            snippet = item.get('snippet', None)
            
            # a special kind of youtube category
            if kind=='youtube#guideCategory' and snippet!=None:
                _id = item.get('id', None)
                title = snippet.get('title', None)
                
                if title!=None and _id!=None:
                    params = {'action': __ACTION_SHOW_CHANNEL_CATEGORY__,
                              'id': _id}
                    __plugin__.addDirectory(name=title, params=params, thumbnailImage=__ICON_FALLBACK__, fanart=__FANART__)
                    pass
                pass
            elif kind=='youtube#subscription' and snippet!=None:
                title = snippet.get('title', None)
                thumbnailImage = _getBestThumbnailImage(item)
                resourceId = snippet.get('resourceId', {})
                channelId = resourceId.get('channelId', None)
                if channelId!=None and title!=None:
                    params = {'action': __ACTION_SHOW_CHANNEL__,
                              'id': channelId}
                    __plugin__.addDirectory(name=title, params=params, thumbnailImage=thumbnailImage, fanart=__FANART__)
                    pass
                pass
            elif kind=='youtube#searchResult' and snippet!=None:
                _id = item.get('id', {})
                kind = _id.get('kind', None)
                if kind!=None:
                    title = snippet.get('title', None)
                    description = snippet.get('description', '')
                    thumbnailImage = _getBestThumbnailImage(item)
                    
                    if kind=='youtube#channel':
                        channelId = _id.get('channelId', None)
                        if title!=None and channelId!=None:
                            params = {'action': __ACTION_SHOW_CHANNEL__,
                                      'id': channelId}
                            __plugin__.addDirectory(name="[B]"+title+"[/B]", params=params, thumbnailImage=thumbnailImage, fanart=__FANART__)
                            pass
                    elif kind=='youtube#video':
                        _id = _id.get('videoId', '')
                        params = {'action': __ACTION_PLAY__,
                                  'id': _id}
                        
                        videoInfo = videoInfos.get(_id, {})
                        infoLabels = {'plot': description,
                                      'duration': videoInfo.get('duration', '1')}
                        __plugin__.addVideoLink(name=title, params=params, thumbnailImage=thumbnailImage, fanart=__FANART__, infoLabels=infoLabels)
                    pass
                pass
            elif kind=='youtube#channel' and snippet!=None:
                title = snippet.get('title', None)
                channelId = item.get('id', None)
                
                if title!=None and channelId!=None:
                    thumbnailImage = _getBestThumbnailImage(item)
                    params = {'action': __ACTION_SHOW_CHANNEL__,
                              'id': channelId}
                    __plugin__.addDirectory(name="[B]"+title+"[/B]", params=params, thumbnailImage=thumbnailImage, fanart=__FANART__)
                    pass
            elif kind=='youtube#playlist' and snippet!=None:
                title = snippet.get('title')
                playlistId = item.get('id')
                thumbnailImage = _getBestThumbnailImage(item)
                params = {'action': __ACTION_SHOW_PLAYLIST__,
                          'id': playlistId}
                __plugin__.addDirectory(name=title, params=params, thumbnailImage=thumbnailImage, fanart=__FANART__,)
            elif kind=='youtube#playlistItem' and snippet!=None:
                title = snippet.get('title')
                description = snippet.get('description')
                
                thumbnailImage = _getBestThumbnailImage(item)
                resourceId = snippet.get('resourceId', {})
                videoId = resourceId.get('videoId', None)
                if videoId!=None:
                    
                    params = {'action': __ACTION_PLAY__,
                              'id': videoId}
                    
                    videoInfo = videoInfos.get(videoId, {})
                    infoLabels = {'plot': description,
                                  'duration': videoInfo.get('duration', '1')}
                    __plugin__.addVideoLink(name=title, params=params, thumbnailImage=thumbnailImage, fanart=__FANART__, infoLabels=infoLabels)
                    pass
                pass
            pass
        
        """
        A common solution for all results. If we have an nextPageToken then their will be more pages to go.
        Therefore we use the nextPageParams array to provide the information need to make call for the
        next page.
        """
        if nextPageToken!=None:
            params = {'pageIndex': str(pageIndex+1),
                      'pageToken': nextPageToken}
            params.update(nextPageParams)
            __plugin__.addDirectory(__plugin__.localize(30002)+' ('+str(pageIndex+1)+')', params=params, fanart=__FANART__)
            pass
        pass
    pass
    
def search(query=None, pageToken=None, pageIndex=1):
    success = False
    
    nextPageParams = {}
    jsonData = {}
    if query!=None and pageToken!=None:
        nextPageParams = {'query': query,
                          'action': __ACTION_SEARCH__}
        jsonData = __client__.search(query, pageToken)
        success = True
    else:
        keyboard = bromixbmc.Keyboard(__plugin__.localize(30000))
        if keyboard.doModal():
            success = True
            
            search_string = keyboard.getText().replace(" ", "+")
            nextPageParams = {'query': search_string,
                              'action': __ACTION_SEARCH__}
            jsonData = __client__.search(search_string)
            pass
        pass
    
    _listResult(jsonData, nextPageParams=nextPageParams, pageIndex=pageIndex)
    __plugin__.endOfDirectory(success)
    
def browseChannels():
    jsonData = __client__.getGuideCategories()
    _listResult(jsonData)
    
    __plugin__.endOfDirectory()
    
def showChannelCategory(_id, pageToken, pageIndex):
    jsonData = __client__.getChannelCategory(_id, pageToken)
    nextPageParams = {'action': __ACTION_SHOW_CHANNEL_CATEGORY__,
                      'id': _id}
    _listResult(jsonData, nextPageParams=nextPageParams, pageIndex=pageIndex)
    
    __plugin__.endOfDirectory()
    
def showPlaylist(playlistId, pageToken, pageIndex):
    mine = bromixbmc.getParam('mine', 'no')=='yes'
    
    __plugin__.setContent('episodes')
    jsonData = __client__.getPlaylistItems(playlistId=playlistId, mine=mine, nextPageToken=pageToken)
    nextPageParams = {'action': __ACTION_SHOW_PLAYLIST__,
                      'id': playlistId}
    if mine==True:
        nextPageParams['mine'] = 'yes'
        
    _listResult(jsonData, nextPageParams=nextPageParams, pageIndex=pageIndex)
    
    __plugin__.endOfDirectory()
    
def showPlaylists(channelId, pageToken, pageIndex):
    jsonData = __client__.getPlaylists(channelId, pageToken)
    nextPageParams = {'action': __ACTION_SHOW_PLAYLISTS__,
                      'id': _id}
    _listResult(jsonData, nextPageParams=nextPageParams, pageIndex=pageIndex)
    
    __plugin__.endOfDirectory()
    
def showChannel(channelId, pageToken, pageIndex):
    __plugin__.setContent('episodes')
    
    """
    Show the playlists of a channel on the first page (only if the setting is true)
    """
    if __SETTING_SHOW_PLAYLISTS__:
        params = {'action': __ACTION_SHOW_PLAYLISTS__,
                  'id': channelId}
        __plugin__.addDirectory(name="[B]"+__plugin__.localize(30003)+"[/B]", params=params, thumbnailImage=__ICON_FALLBACK__, fanart=__FANART__)
        pass
    
    jsonData = __client__.getChannels(channelId=channelId)
    items = jsonData.get('items', [])
    if len(items)>0:
        item = items[0]
        contentDetails = item.get('contentDetails', {})
        relatedPlaylists = contentDetails.get('relatedPlaylists', {})
        playlistId = relatedPlaylists.get('uploads', None)
        
        if playlistId!=None:
            jsonData = __client__.getPlaylistItems(playlistId, pageToken)
            nextPageParams = {'action': __ACTION_SHOW_PLAYLIST__,
                              'id': playlistId}
            _listResult(jsonData, nextPageParams=nextPageParams, pageIndex=pageIndex)
            pass
        pass
    
    __plugin__.endOfDirectory()
    
def showWatchLater(pageToken, pageIndex):
    jsonData = __client__.getChannels(mine=True)
    items = jsonData.get('items', [])
    if len(items)>0:
        item = items[0]
        contentDetails = item.get('contentDetails', {})
        relatedPlaylists = contentDetails.get('relatedPlaylists', {})
        playlistId = relatedPlaylists.get('watchLater', None)
        
        if playlistId!=None:
            jsonData = __client__.getPlaylistItems(playlistId, mine=True, nextPageToken=pageToken)
            nextPageParams = {'action': __ACTION_SHOW_PLAYLIST__,
                              'id': playlistId,
                              'mine': 'yes'}
            _listResult(jsonData, nextPageParams=nextPageParams, pageIndex=pageIndex)
            pass
        pass
    
    __plugin__.endOfDirectory()
    
def showSubscriptions(pageToken, pageIndex):
    jsonData = __client__.getSubscriptions(mine=True, nextPageToken=pageToken)
    nextPageParams = {'action': __ACTION_SHOW_SUBSCRIPTIONS__}
    _listResult(jsonData, nextPageParams=nextPageParams, pageIndex=pageIndex)
    __plugin__.endOfDirectory()
    
def play(videoId):
    quality = __plugin__.getSettingAsInt('videoQuality', mapping={0:576, 1:720, 2:1080})
    stream = __client__.getBestFittingVideoStream(videoId=videoId, size=quality)
    if stream!=None:
        url = stream.get('url', None)
        if url!=None:
            __plugin__.setResolvedUrl(url)

action = bromixbmc.getParam('action')
_id = bromixbmc.getParam('id')
query = bromixbmc.getParam('query')
pageToken = bromixbmc.getParam('pageToken')
pageIndex = int(bromixbmc.getParam('pageIndex', '1'))

if action == __ACTION_SEARCH__:
    search(query, pageToken, pageIndex)
elif action == __ACTION_SHOW_SUBSCRIPTIONS__:
    showSubscriptions(pageToken, pageIndex)
elif action == __ACTION_SHOW_WATCHLATER__:
    showWatchLater(pageToken, pageIndex)
elif action == __ACTION_BROWSE_CHANNELS__:
    browseChannels();
elif action == __ACTION_SHOW_CHANNEL__ and _id!=None:
    showChannel(_id, pageToken, pageIndex)
elif action == __ACTION_SHOW_CHANNEL_CATEGORY__ and _id!=None:
    showChannelCategory(_id, pageToken, pageIndex)
elif action == __ACTION_SHOW_PLAYLIST__ and _id!=None:
    showPlaylist(_id, pageToken, pageIndex)
elif action == __ACTION_SHOW_PLAYLISTS__ and _id!=None:
    showPlaylists(_id, pageToken, pageIndex)
elif action == __ACTION_PLAY__:
    play(_id)
else:
    showIndex()