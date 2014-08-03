# -*- coding: utf-8 -*-

import os
import re
import hashlib

#import pydevd
#pydevd.settrace('localhost', stdoutToServer=True, stderrToServer=True)

import bromixbmc
from _ast import Param
__plugin__ = bromixbmc.Plugin()

""" IMAGES """
__FANART__ = os.path.join(__plugin__.getPath(), "fanart.jpg")
__ICON_FALLBACK__ = os.path.join(__plugin__.getPath(), "resources/media/fallback_icon.png")
__ICON_SEARCH__ = os.path.join(__plugin__.getPath(), "resources/media/search.png")

""" GLOBAL SETTINGS """
__SETTING_SHOW_FANART__ = __plugin__.getSettingAsBool('showFanart')
if not __SETTING_SHOW_FANART__:
    __FANART__ = ''

""" ACTIONS """
__ACTION_SEARCH__ = 'search'
__ACTION_BROWSE_CHANNELS__ = 'browseChannels'
__ACTION_SHOW_CHANNEL_CATEGORY__ = 'showChannelCategory'
__ACTION_SHOW_MYSUBSCRIPTIONS__ = 'showMySubscriptions'
__ACTION_SHOW_PLAYLIST__ = 'showPlaylist'
__ACTION_SHOW_PLAYLISTS__ = 'showPlaylists'
__ACTION_SHOW_CHANNEL__ = 'showChannel'
__ACTION_SHOW_SUBSCRIPTIONS__ = 'showSubscriptions'
__ACTION_PLAY__ = 'play'
__ACTION_ADD_TO_PLAYLIST__ = 'addToPlaylist'

""" CACHED YOUTUBE DATA """
__YT_PLAYLISTS__ = {'likes': '', 'favorites': '', 'uploads': '', 'watchHistory': '', 'watchLater': ''}
__YT_CANNEL_ID__ = ''

"""
Based on the username and password we create a hash to validate, that the login hasn't changed.
If so, this will reset the data, so the login will start over for the new login data. This will
resolve the problem if you change the login somewhere in between. 
"""
__ACCESS_USERNAME__ = __plugin__.getSettingAsString('username', '')
__ACCESS_PASSWORD__ = __plugin__.getSettingAsString('password', '')

oldHash = __plugin__.getSettingAsString('oauth2_access_hash', '')
m = hashlib.md5()
m.update(__ACCESS_USERNAME__+__ACCESS_PASSWORD__)
currentHash = m.hexdigest()
if oldHash!=currentHash:
    """
    The hash has changed to we reset all data to force a new token with the new login data.
    I non login data is given, the client won't call any token based data.
    """
    __plugin__.setSettingAsFloat('oauth2_access_token_expires_at', -1)
    __plugin__.setSettingAsString('oauth2_access_token', '')
    
    __plugin__.setSettingAsString('oauth2_access_hash', currentHash)
    
    # reset cached playlist ids
    for key in __YT_PLAYLISTS__:
        name = 'yt_playlist_%s' % (key)
        __plugin__.setSettingAsString(name, '')
    
    # reset channel id
    __plugin__.setSettingAsString('yt_channel_id', '')
    pass

__YT_CANNEL_ID__ = __plugin__.getSettingAsString('yt_channel_id', '')

import youtube.video
from youtube import YouTubeClient
__client__ = YouTubeClient(username = __ACCESS_USERNAME__,
                           password = __ACCESS_PASSWORD__,
                           cachedToken = __plugin__.getSettingAsString('oauth2_access_token', None),
                           accessTokenExpiresAt = __plugin__.getSettingAsFloat('oauth2_access_token_expires_at', -1),
                           language = bromixbmc.getLanguageId(),
                           maxResult = __plugin__.getSettingAsInt('resultPerPage', default=5, mapping={0:5, 1:10, 2:15, 3:20, 4:25, 5:30, 6:35, 7:40, 8:45, 9:50})
                           );

_INT_UPDATE_YOUTUBE_DATA_ = False
for key in __YT_PLAYLISTS__:
    name = 'yt_playlist_%s' % (key)
    __YT_PLAYLISTS__[key] = __plugin__.getSettingAsString(name, '')
    if len(__YT_PLAYLISTS__[key])==0:
        _INT_UPDATE_YOUTUBE_DATA_ = True
        break
    pass

if (_INT_UPDATE_YOUTUBE_DATA_ or len(__YT_CANNEL_ID__)==0 )and __client__.hasLogin():
    jsonData = __client__.getChannels(mine=True)
    items = jsonData.get('items', [])
    if len(items)>0:
        item = items[0]
        
        # get the own channel id
        __YT_CANNEL_ID__ = item.get('id', '')
        __plugin__.setSettingAsString('yt_channel_id', __YT_CANNEL_ID__)
        
        # try to get all ids of the playlists
        contentDetails = item.get('contentDetails', {})
        relatedPlaylists = contentDetails.get('relatedPlaylists', {})
        for key in relatedPlaylists:
            playlistId = relatedPlaylists.get(key, None)
            if playlistId!=None:
                __YT_PLAYLISTS__[key] = playlistId
                pass
            pass
        
        for key in __YT_PLAYLISTS__:
            name = 'yt_playlist_%s' % (key)
            __plugin__.setSettingAsString(name, __YT_PLAYLISTS__.get(key, ''))
            pass
    pass


def showIndex():
    if __client__.hasLogin():
        params = {'action': __ACTION_SHOW_MYSUBSCRIPTIONS__}
        __plugin__.addDirectory("[B]"+__plugin__.localize(30007)+"[/B]", params = params, thumbnailImage=__ICON_FALLBACK__, fanart=__FANART__)
        pass
        
    params = {'action': __ACTION_SEARCH__}
    __plugin__.addDirectory("[B]"+__plugin__.localize(30000)+"[/B]", params = params, thumbnailImage=__ICON_FALLBACK__, fanart=__FANART__)
    
    if __client__.hasLogin():
        # My Channel
        if __YT_CANNEL_ID__!=None and len(__YT_CANNEL_ID__)>0:
            params = {'action': __ACTION_SHOW_CHANNEL__,
                      'id': __YT_CANNEL_ID__,
                      'mine': 'yes'}
            __plugin__.addDirectory(__plugin__.localize(30010), params=params, thumbnailImage=__ICON_FALLBACK__, fanart=__FANART__)
        
        # History
        playlistId = __YT_PLAYLISTS__.get('watchHistory', None)
        if playlistId!=None:
            params = {'action': __ACTION_SHOW_PLAYLIST__,
                      'id': playlistId,
                      'mine': 'yes'}
            __plugin__.addDirectory(__plugin__.localize(30006), params = params, thumbnailImage=__ICON_FALLBACK__, fanart=__FANART__)
            
        # Watch Later
        playlistId = __YT_PLAYLISTS__.get('watchLater', None)
        if playlistId!=None:
            params = {'action': __ACTION_SHOW_PLAYLIST__,
                      'id': playlistId,
                      'mine': 'yes'}
            __plugin__.addDirectory(__plugin__.localize(30005), params = params, thumbnailImage=__ICON_FALLBACK__, fanart=__FANART__)
            
        # own playlists
        params = {'action': __ACTION_SHOW_PLAYLISTS__,
                  'mine': 'yes'}
        __plugin__.addDirectory(__plugin__.localize(30003), params = params, thumbnailImage=__ICON_FALLBACK__, fanart=__FANART__)
        
        # Watch Later
        playlistId = __YT_PLAYLISTS__.get('likes', None)
        if playlistId!=None:
            params = {'action': __ACTION_SHOW_PLAYLIST__,
                      'id': playlistId,
                      'mine': 'yes'}
            __plugin__.addDirectory(__plugin__.localize(30011), params = params, thumbnailImage=__ICON_FALLBACK__, fanart=__FANART__)
        
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

def _getBestFanart(jsonData):
    if __SETTING_SHOW_FANART__:
        brandingSettings = jsonData.get('brandingSettings', {})
        image = brandingSettings.get('image', {})
        
        """
        We only use 'medium' because the image should be 1280x720. Full HD (1920x1080) images would more space and time time show
        """
        #bannerList = ['bannerTvHighImageUrl', 'bannerTvMediumImageUrl', 'bannerTvLowImageUrl', 'bannerTvImageUrl']
        bannerList = ['bannerTvMediumImageUrl', 'bannerTvLowImageUrl', 'bannerTvImageUrl']
        for banner in bannerList:
            fanart = image.get(banner, None)
            if fanart!=None:
                return fanart
            pass
        
        # fallback
        return __FANART__
    
    return ''

def _listResult(jsonData, nextPageParams={}, pageIndex=1, mine=False, fanart=__FANART__):
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
            elif kind=='youtube#activity':
                contentDetails = item.get('contentDetails', {})
                upload = contentDetails.get('upload', {})
                videoId = upload.get('videoId', None)
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
            
            uploadInfo = ''
            if __plugin__.getSettingAsBool('showUploadInfo', False):
                channelTitle = snippet.get('channelTitle', None)
                publishedAt = snippet.get('publishedAt', '')
                match = re.compile('(\d+)-(\d+)-(\d+)T(\d+)\:(\d+)\:(\d+)\.(.+)').findall(publishedAt)
                if match and len(match)>0 and len(match[0])>=7:
                    uploadInfo = __plugin__.localize(30008)+': '
                    uploadInfo = uploadInfo+bromixbmc.getFormatDateShort(match[0][0], match[0][1], match[0][2])
                    uploadInfo = uploadInfo+' '+bromixbmc.getFormatTime(match[0][3], match[0][4], match[0][5])
                    if channelTitle!=None:
                        uploadInfo = uploadInfo+"[CR]"+__plugin__.localize(30009)+": "
                        uploadInfo = uploadInfo+channelTitle
                        pass
                    
                    uploadInfo = '[B]'+uploadInfo+"[/B][CR][CR]"
                    pass
                pass
                
            # a special kind of youtube category
            if kind=='youtube#guideCategory' and snippet!=None:
                _id = item.get('id', None)
                title = snippet.get('title', None)
                
                if title!=None and _id!=None:
                    params = {'action': __ACTION_SHOW_CHANNEL_CATEGORY__,
                              'id': _id}
                    __plugin__.addDirectory(name=title, params=params, thumbnailImage=__ICON_FALLBACK__, fanart=fanart)
                    pass
                pass
            elif kind=='youtube#activity' and snippet!=None:
                title = snippet.get('title', None)
                description = snippet.get('description', '')
                thumbnailImage = _getBestThumbnailImage(item)
                contentDetails = item.get('contentDetails', {})
                
                upload = contentDetails.get('upload', {})
                videoId = upload.get('videoId', None)
                if videoId!=None and title!=None:
                    videoInfo = videoInfos.get(videoId, {})
                    infoLabels = {'plot': uploadInfo+description,
                                  'duration': videoInfo.get('duration', '1')}
                    params = {'action': __ACTION_PLAY__,
                              'id': videoId}
                    
                    contextMenu = []
                    playlistId = __YT_PLAYLISTS__.get('watchLater', None)
                    if playlistId!=None:
                        contextParams = {'action': __ACTION_ADD_TO_PLAYLIST__,
                                         'id': videoId,
                                         'playlistId': playlistId}
                        contextRun = 'RunPlugin('+__plugin__.createUrl(contextParams)+')'
                        contextMenu = [("[B]"+__plugin__.localize(30005)+"[/B]", contextRun)]
                    __plugin__.addVideoLink(name=title, params=params, thumbnailImage=thumbnailImage, fanart=fanart, infoLabels=infoLabels, contextMenu=contextMenu)
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
                    __plugin__.addDirectory(name=title, params=params, thumbnailImage=thumbnailImage, fanart=fanart)
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
                            __plugin__.addDirectory(name="[B]"+title+"[/B]", params=params, thumbnailImage=thumbnailImage, fanart=fanart)
                            pass
                    elif kind=='youtube#playlist':
                        playlistId = _id.get('playlistId', None)
                        if title!=None and playlistId!=None:
                            params = {'action': __ACTION_SHOW_PLAYLIST__,
                                      'id': playlistId}
                            __plugin__.addDirectory(name="[B]"+title+"[/B]", params=params, thumbnailImage=thumbnailImage, fanart=fanart)
                        pass
                    elif kind=='youtube#video':
                        videoId = _id.get('videoId', '')
                        params = {'action': __ACTION_PLAY__,
                                  'id': videoId}
                        
                        videoInfo = videoInfos.get(videoId, {})
                        infoLabels = {'plot': uploadInfo+description,
                                      'duration': videoInfo.get('duration', '1')}
                        __plugin__.addVideoLink(name=title, params=params, thumbnailImage=thumbnailImage, fanart=fanart, infoLabels=infoLabels)
                    pass
                pass
            elif kind=='youtube#channel' and snippet!=None:
                title = snippet.get('title', None)
                channelId = item.get('id', None)
                
                if title!=None and channelId!=None:
                    thumbnailImage = _getBestThumbnailImage(item)
                    params = {'action': __ACTION_SHOW_CHANNEL__,
                              'id': channelId}
                    __plugin__.addDirectory(name="[B]"+title+"[/B]", params=params, thumbnailImage=thumbnailImage, fanart=fanart)
                    pass
            elif kind=='youtube#playlist' and snippet!=None:
                title = snippet.get('title')
                playlistId = item.get('id')
                thumbnailImage = _getBestThumbnailImage(item)
                params = {'action': __ACTION_SHOW_PLAYLIST__,
                          'id': playlistId}
                
                if mine==True:
                    params['mine'] = 'yes'

                __plugin__.addDirectory(name=title, params=params, thumbnailImage=thumbnailImage, fanart=fanart)
            elif kind=='youtube#playlistItem' and snippet!=None:
                title = snippet.get('title')
                description = snippet.get('description')
                
                thumbnailImage = _getBestThumbnailImage(item)
                resourceId = snippet.get('resourceId', {})
                videoId = resourceId.get('videoId', None)
                if videoId!=None:
                    
                    isWatchLaterPlaylist = False
                    playlistId = snippet.get('playlistId', None)
                    if playlistId!=None and playlistId == __YT_PLAYLISTS__.get('watchLater', None):
                        isWatchLaterPlaylist = True
                        pass
                    
                    params = {'action': __ACTION_PLAY__,
                              'id': videoId}
                    
                    if isWatchLaterPlaylist:
                        params['watchLaterItemId'] = item.get('id', '')
                    
                    videoInfo = videoInfos.get(videoId, {})
                    infoLabels = {'plot': uploadInfo+description,
                                  'duration': videoInfo.get('duration', '1')}
                    __plugin__.addVideoLink(name=title, params=params, thumbnailImage=thumbnailImage, fanart=fanart, infoLabels=infoLabels)
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
            __plugin__.addDirectory(__plugin__.localize(30002)+' ('+str(pageIndex+1)+')', params=params, fanart=fanart)
            pass
        pass
    pass
    
def search(query=None, pageToken=None, pageIndex=1):
    __plugin__.setContent('episodes')
    success = False
    
    searchVideos=__plugin__.getSettingAsBool('searchVideos')
    searchChannels=__plugin__.getSettingAsBool('searchChannels')
    searchPlaylists=__plugin__.getSettingAsBool('searchPlaylists')
    
    nextPageParams = {}
    jsonData = {}
    if query!=None and pageToken!=None:
        nextPageParams = {'query': query,
                          'action': __ACTION_SEARCH__}
        jsonData = __client__.search(text=query,
                                     searchVideos=searchVideos,
                                     searchChannels=searchChannels,
                                     searchPlaylists=searchPlaylists,
                                     nextPageToken=pageToken
                                     )
        success = True
    else:
        keyboard = bromixbmc.Keyboard(__plugin__.localize(30000))
        if keyboard.doModal():
            success = True
            
            search_string = keyboard.getText().replace(" ", "+")
            nextPageParams = {'query': search_string,
                              'action': __ACTION_SEARCH__}
            jsonData = __client__.search(text=search_string,
                                         searchVideos=searchVideos,
                                         searchChannels=searchChannels,
                                         searchPlaylists=searchPlaylists,
                                         nextPageToken=pageToken
                                         )
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
    
def showPlaylist(playlistId, pageToken, pageIndex, mine=False):
    __plugin__.setContent('episodes')
    jsonData = __client__.getPlaylistItems(playlistId=playlistId, mine=mine, nextPageToken=pageToken)
    nextPageParams = {'action': __ACTION_SHOW_PLAYLIST__,
                      'id': playlistId}
    if mine==True:
        nextPageParams['mine'] = 'yes'
        
    _listResult(jsonData, nextPageParams=nextPageParams, pageIndex=pageIndex)
    
    __plugin__.endOfDirectory()
    
def showPlaylists(channelId, pageToken, pageIndex, mine=False):
    jsonData = __client__.getPlaylists(channelId=channelId, mine=mine, nextPageToken=pageToken)
    nextPageParams = {'action': __ACTION_SHOW_PLAYLISTS__,
                      'id': _id}
    if mine==True:
        nextPageParams['mine'] = 'yes'
    _listResult(jsonData, nextPageParams=nextPageParams, pageIndex=pageIndex, mine=mine)
    
    __plugin__.endOfDirectory()
    
def showChannel(channelId, pageToken, pageIndex, mine=False):
    __plugin__.setContent('episodes')
    
    jsonData = __client__.getChannels(channelId=channelId)
    items = jsonData.get('items', [])
    if len(items)>0:
        item = items[0]
        contentDetails = item.get('contentDetails', {})
        fanart = _getBestFanart(item)
        
        """
        Show the playlists of a channel on the first page (only if the setting is true)
        """
        if __plugin__.getSettingAsBool('showPlaylists'):
            # default for all public playlists
            params = {'action': __ACTION_SHOW_PLAYLISTS__,
                      'id': channelId}
            
            # this is for the own playlist, so we can also see the private playlists 
            if mine==True: 
                params = {'action': __ACTION_SHOW_PLAYLISTS__,
                          'mine': 'yes'}
            
            __plugin__.addDirectory(name="[B]"+__plugin__.localize(30003)+"[/B]", params=params, thumbnailImage=__ICON_FALLBACK__, fanart=fanart)
            pass
        
        relatedPlaylists = contentDetails.get('relatedPlaylists', {})
        playlistId = relatedPlaylists.get('uploads', None)
        
        if playlistId!=None:
            jsonData = __client__.getPlaylistItems(playlistId=playlistId, mine=mine, nextPageToken=pageToken)
            nextPageParams = {'action': __ACTION_SHOW_PLAYLIST__,
                              'id': playlistId}
            
            if mine==True:
                nextPageParams['mine'] = 'yes'
            
            _listResult(jsonData, nextPageParams=nextPageParams, pageIndex=pageIndex, fanart=fanart)
            pass
        pass
    
    __plugin__.endOfDirectory()
    
def showMySubscriptions(pageToken, pageIndex):
    __plugin__.setContent('episodes')
    jsonData = __client__.getActivities(home=True, nextPageToken=pageToken)
    nextPageParams = {'action': __ACTION_SHOW_MYSUBSCRIPTIONS__}
    _listResult(jsonData, nextPageParams=nextPageParams, pageIndex=pageIndex)
    __plugin__.endOfDirectory()
    
def showSubscriptions(pageToken, pageIndex):
    jsonData = __client__.getSubscriptions(mine=True, nextPageToken=pageToken)
    nextPageParams = {'action': __ACTION_SHOW_SUBSCRIPTIONS__}
    _listResult(jsonData, nextPageParams=nextPageParams, pageIndex=pageIndex)
    __plugin__.endOfDirectory()
    
def play(videoId):
    allow3D = __plugin__.getSettingAsBool('allow3D', False)
    quality = __plugin__.getSettingAsInt('videoQuality', mapping={0:576, 1:720, 2:1080})
    stream = youtube.video.getBestFittingVideoStreamInfo(videoId=videoId, size=quality, allow3D=allow3D)
    if stream!=None:
        url = stream.getUrl()
        if url!=None:
            __plugin__.setResolvedUrl(url)
            
            if __client__.hasLogin():
                # try to add the video to the history
                if __plugin__.getSettingAsBool('enableHistory'):
                    playlistId = __YT_PLAYLISTS__.get('watchHistory', None)
                    if playlistId!=None:
                        __client__.addPlayListItem(playlistId, videoId)
                        pass
                    pass
                
                # remove the video from the 'Watch Later' playlist
                if __plugin__.getSettingAsBool('automaticWatchLater'):
                    watchLaterItemId = bromixbmc.getParam('watchLaterItemId', None)
                    if watchLaterItemId!=None:
                        __client__.removePlaylistItem(watchLaterItemId)
                        bromixbmc.executebuiltin("Container.Refresh");
                        pass
                    pass
                pass
            pass
        pass
    pass

def addToPlayList(videoId):
    playlistId = bromixbmc.getParam('playlistId', None)
    if playlistId!=None:
        __client__.addPlayListItem(playlistId, videoId)
        pass
    pass

action = bromixbmc.getParam('action')
_id = bromixbmc.getParam('id')
query = bromixbmc.getParam('query')
pageToken = bromixbmc.getParam('pageToken')
pageIndex = int(bromixbmc.getParam('pageIndex', '1'))
mine = bromixbmc.getParam('mine', 'no')=='yes'

if action == __ACTION_SEARCH__:
    search(query, pageToken, pageIndex)
elif action == __ACTION_ADD_TO_PLAYLIST__ and _id!=None:
    addToPlayList(_id)
elif action == __ACTION_SHOW_MYSUBSCRIPTIONS__:
    showMySubscriptions(pageToken, pageIndex)
elif action == __ACTION_SHOW_SUBSCRIPTIONS__:
    showSubscriptions(pageToken, pageIndex)
elif action == __ACTION_BROWSE_CHANNELS__:
    browseChannels();
elif action == __ACTION_SHOW_CHANNEL__ and (_id!=None or mine==True):
    showChannel(_id, pageToken, pageIndex, mine=mine)
elif action == __ACTION_SHOW_CHANNEL_CATEGORY__ and _id!=None:
    showChannelCategory(_id, pageToken, pageIndex)
elif action == __ACTION_SHOW_PLAYLIST__ and _id!=None:
    showPlaylist(_id, pageToken=pageToken, pageIndex=pageIndex, mine=mine)
elif action == __ACTION_SHOW_PLAYLISTS__ and (_id!=None or mine==True):
    showPlaylists(_id, pageToken=pageToken, pageIndex=pageIndex, mine=mine)
elif action == __ACTION_PLAY__:
    play(_id)
else:
    showIndex()
    
# token and expiration date
if __plugin__.getSettingAsString('oauth2_access_token', '') != __client__.AccessToken:
    if __client__.AccessToken!=None and len(__client__.AccessToken)>0:
        __plugin__.setSettingAsFloat('oauth2_access_token_expires_at', __client__.AccessTokenExpiresAt)
        __plugin__.setSettingAsString('oauth2_access_token', __client__.AccessToken)