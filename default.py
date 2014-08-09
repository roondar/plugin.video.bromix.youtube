# -*- coding: utf-8 -*-

import os
import re
import hashlib

try:
    from xml.etree import ElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

#import pydevd
#pydevd.settrace('localhost', stdoutToServer=True, stderrToServer=True)

import bromixbmc
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
__ACTION_SHOW_SEARCH_INDEX__ = 'showSearchIndex'
__ACTION_SEARCH__ = 'search'
__ACTION_BROWSE_CHANNELS__ = 'browseChannels'
__ACTION_SHOW_CHANNEL_CATEGORY__ = 'showChannelCategory'
__ACTION_SHOW_MYSUBSCRIPTIONS__ = 'showMySubscriptions'
__ACTION_SHOW_PLAYLIST__ = 'showPlaylist'
__ACTION_SHOW_PLAYLISTS__ = 'showPlaylists'
__ACTION_SHOW_CHANNEL__ = 'showChannel'
__ACTION_SHOW_SUBSCRIPTIONS__ = 'showSubscriptions'
__ACTION_ADD_SUBSCRIPTION__ = 'addSubscription'
__ACTION_REMOVE_SUBSCRIPTION__ = 'removeSubscription'
__ACTION_PLAY__ = 'play'
__ACTION_ADD_TO_PLAYLIST__ = 'addToPlaylist'
__ACTION_REMOVE_FROM_PLAYLIST__ = 'removeFromPlaylist'
__ACTION_REMOVE_PLAYLIST__ = 'removePlaylist'

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
        
    params = {'action': __ACTION_SHOW_SEARCH_INDEX__}
    __plugin__.addDirectory("[B]"+__plugin__.localize(30000)+"[/B]", params = params, thumbnailImage=__ICON_FALLBACK__, fanart=__FANART__)
    
    if __client__.hasLogin():
        # My Channel
        if __plugin__.getSettingAsBool('menu.root.my_channel.show', True):
            if __YT_CANNEL_ID__!=None and len(__YT_CANNEL_ID__)>0:
                params = {'action': __ACTION_SHOW_CHANNEL__,
                          'id': __YT_CANNEL_ID__,
                          'mine': 'yes'}
                __plugin__.addDirectory(__plugin__.localize(30010), params=params, thumbnailImage=__ICON_FALLBACK__, fanart=__FANART__)
                pass
            pass
        
        # History
        if __plugin__.getSettingAsBool('menu.root.history.show', True):
            playlistId = __YT_PLAYLISTS__.get('watchHistory', None)
            if playlistId!=None:
                params = {'action': __ACTION_SHOW_PLAYLIST__,
                          'id': playlistId,
                          'mine': 'yes'}
                __plugin__.addDirectory(__plugin__.localize(30006), params = params, thumbnailImage=__ICON_FALLBACK__, fanart=__FANART__)
                pass
            pass
            
        # Watch Later
        if __plugin__.getSettingAsBool('menu.root.watch_later.show', True):
            playlistId = __YT_PLAYLISTS__.get('watchLater', None)
            if playlistId!=None:
                params = {'action': __ACTION_SHOW_PLAYLIST__,
                          'id': playlistId,
                          'mine': 'yes'}
                __plugin__.addDirectory(__plugin__.localize(30005), params = params, thumbnailImage=__ICON_FALLBACK__, fanart=__FANART__)
                pass
            pass
            
        # own playlists
        if __plugin__.getSettingAsBool('menu.root.playlists.show', True):
            params = {'action': __ACTION_SHOW_PLAYLISTS__,
                      'mine': 'yes'}
            __plugin__.addDirectory(__plugin__.localize(30003), params = params, thumbnailImage=__ICON_FALLBACK__, fanart=__FANART__)
            pass
        
        # Watch Later
        if __plugin__.getSettingAsBool('menu.root.liked_videos.show', True):
            playlistId = __YT_PLAYLISTS__.get('likes', None)
            if playlistId!=None:
                params = {'action': __ACTION_SHOW_PLAYLIST__,
                          'id': playlistId,
                          'mine': 'yes'}
                __plugin__.addDirectory(__plugin__.localize(30011), params = params, thumbnailImage=__ICON_FALLBACK__, fanart=__FANART__)
                pass
            pass
        
        params = {'action': __ACTION_SHOW_SUBSCRIPTIONS__}
        __plugin__.addDirectory(__plugin__.localize(30004), params = params, thumbnailImage=__ICON_FALLBACK__, fanart=__FANART__)
        pass
    
    # 'Browse Channels'
    if __plugin__.getSettingAsBool('menu.root.browse_channels.show', True):
        params = {'action': __ACTION_BROWSE_CHANNELS__}
        __plugin__.addDirectory(__plugin__.localize(30001), params = params, thumbnailImage=__ICON_FALLBACK__, fanart=__FANART__)
        pass
    
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

def _createContextMenuForVideo(videoId, playlistItemId=None, isMyPlaylist=False, playlistId=None):
    contextMenu = []
    
    if __client__.hasLogin():
        # 'Watch Later'
        watchLaterPlaylistId = __YT_PLAYLISTS__.get('watchLater', None)
        if watchLaterPlaylistId!=None and watchLaterPlaylistId!=playlistId and videoId!=None:
            contextParams = {'action': __ACTION_ADD_TO_PLAYLIST__,
                             'id': videoId,
                             'playlistId': watchLaterPlaylistId}
            contextRun = 'RunPlugin('+__plugin__.createUrl(contextParams)+')'
            contextMenu.append( ("[B]"+__plugin__.localize(30005)+"[/B]", contextRun) )
            pass
        
        # 'Like'
        likedVideosPlaylistId = __YT_PLAYLISTS__.get('likes', None)
        if likedVideosPlaylistId!=None and likedVideosPlaylistId!=playlistId and videoId!=None:
            contextParams = {'action': __ACTION_ADD_TO_PLAYLIST__,
                             'id': videoId,
                             'playlistId': likedVideosPlaylistId}
            contextRun = 'RunPlugin('+__plugin__.createUrl(contextParams)+')'
            contextMenu.append( ("[B]"+__plugin__.localize(30014)+"[/B]", contextRun) )
            pass
            
        if isMyPlaylist and playlistItemId!=None:
            contextParams = {'action': __ACTION_REMOVE_FROM_PLAYLIST__,
                             'id': playlistItemId}
            contextRun = 'RunPlugin('+__plugin__.createUrl(contextParams)+')'
            contextMenu.append( ("[B]"+__plugin__.localize(30012)+"[/B]", contextRun) )
            pass
        pass
    
    return contextMenu

def _listVideo(title, videoId,
               duration='1',
               plot='',
               thumbnailImage=__ICON_FALLBACK__,
               fanart=__FANART__,
               publishedAt=None,
               channelName=None,
               playlistItemId=None,
               isMyPlaylist=False,
               playlistId=None):
    
    plot2 = ''
    if __plugin__.getSettingAsBool('showUploadInfo', False):
        if channelName!=None:
            plot2 = '[B]'+__plugin__.localize(30009)+': '+channelName+'[/B][CR]'
            pass
        
        try:
            if publishedAt!=None:
                match = re.compile('(\d+)-(\d+)-(\d+)T(\d+)\:(\d+)\:(\d+)\.(.+)').findall(publishedAt)
                if match and len(match)>0 and len(match[0])>=7:
                    plot2 = plot2+'[B]'+__plugin__.localize(30008)+': '+bromixbmc.getFormatDateShort(match[0][0], match[0][1], match[0][2])+' '+bromixbmc.getFormatTime(match[0][3], match[0][4], match[0][5])+'[/B][CR][CR]'
                    pass
                pass
            pass
        except:
            if publishedAt==None:
                publishedAt=''
            __plugin__.logError("Failed to set the published date for video '%s' publishedAt='%s'" % (videoId, publishedAt))
            pass
    plot2 = plot2+plot
    
    params = {'action': __ACTION_PLAY__,
              'id': videoId}
    
    infoLabels = {'duration': duration,
                  'plot': plot2}
    
    contextMenu = _createContextMenuForVideo(videoId, playlistItemId, isMyPlaylist, playlistId=playlistId)
    
    __plugin__.addVideoLink(name=title, params=params, thumbnailImage=thumbnailImage, fanart=fanart, infoLabels=infoLabels, contextMenu=contextMenu)
    pass

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
            publishedAt = snippet.get('publishedAt', '')
            
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
                contentDetails = item.get('contentDetails', {})
                
                upload = contentDetails.get('upload', {})
                videoId = upload.get('videoId', None)
                if videoId!=None and title!=None:
                    videoInfo = videoInfos.get(videoId, {})
                    _listVideo(title=title,
                               videoId=videoId,
                               duration=videoInfo.get('duration', '1'),
                               plot=description,
                               thumbnailImage=videoInfo.get('thumbnailImage', __ICON_FALLBACK__),
                               fanart=fanart,
                               publishedAt=publishedAt,
                               channelName=videoInfo.get('channel_name', ''))
                    pass
                pass
            elif kind=='youtube#subscription' and snippet!=None:
                title = snippet.get('title', None)
                subscriptionId = item.get('id', None)
                thumbnailImage = _getBestThumbnailImage(item)
                resourceId = snippet.get('resourceId', {})
                channelId = resourceId.get('channelId', None)
                if channelId!=None and title!=None:
                    params = {'action': __ACTION_SHOW_CHANNEL__,
                              'id': channelId}
                    
                    contextMenu = []
                    contextParams = {'action': __ACTION_REMOVE_SUBSCRIPTION__,
                                         'id': subscriptionId}
                    contextRun = 'RunPlugin('+__plugin__.createUrl(contextParams)+')'
                    contextMenu.append( ("[B]"+__plugin__.localize(30016)+"[/B]", contextRun) )
                    
                    __plugin__.addDirectory(name=title, params=params, thumbnailImage=thumbnailImage, fanart=fanart, contextMenu=contextMenu)
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
                            
                            contextMenu = []
                            contextParams = {'action': __ACTION_ADD_SUBSCRIPTION__,
                                             'id': channelId}
                            contextRun = 'RunPlugin('+__plugin__.createUrl(contextParams)+')'
                            contextMenu.append( ("[B]"+__plugin__.localize(30015)+"[/B]", contextRun) )
                            
                            __plugin__.addDirectory(name="[B]"+title+"[/B]", params=params, thumbnailImage=thumbnailImage, fanart=fanart, contextMenu=contextMenu)
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
                        
                        videoInfo = videoInfos.get(videoId, {})
                        _listVideo(title=title,
                                   videoId=videoId,
                                   duration=videoInfo.get('duration', ''),
                                   plot=description,
                                   thumbnailImage=thumbnailImage,
                                   fanart=fanart,
                                   publishedAt=publishedAt,
                                   channelName=videoInfo.get('channel_name', ''))
                    pass
                pass
            elif kind=='youtube#channel' and snippet!=None:
                title = snippet.get('title', None)
                channelId = item.get('id', None)
                
                if title!=None and channelId!=None:
                    thumbnailImage = _getBestThumbnailImage(item)
                    params = {'action': __ACTION_SHOW_CHANNEL__,
                              'id': channelId}
                    
                    contextMenu = []
                    contextParams = {'action': __ACTION_ADD_SUBSCRIPTION__,
                                     'id': channelId}
                    contextRun = 'RunPlugin('+__plugin__.createUrl(contextParams)+')'
                    contextMenu.append( ("[B]"+__plugin__.localize(30015)+"[/B]", contextRun) )
                    
                    __plugin__.addDirectory(name="[B]"+title+"[/B]", params=params, thumbnailImage=thumbnailImage, fanart=fanart, contextMenu=contextMenu)
                    pass
            elif kind=='youtube#playlist' and snippet!=None:
                title = snippet.get('title')
                playlistId = item.get('id')
                thumbnailImage = _getBestThumbnailImage(item)
                params = {'action': __ACTION_SHOW_PLAYLIST__,
                          'id': playlistId}
                
                contextMenu = None
                if mine==True:
                    params['mine'] = 'yes'
                    
                    contextMenu= []
                    contextParams = {'action': __ACTION_REMOVE_PLAYLIST__,
                                     'id': playlistId}
                    contextRun = 'RunPlugin('+__plugin__.createUrl(contextParams)+')'
                    contextMenu.append( ("[B]"+__plugin__.localize(30012)+"[/B]", contextRun) )
                    pass

                __plugin__.addDirectory(name=title, params=params, thumbnailImage=thumbnailImage, fanart=fanart, contextMenu=contextMenu)
            elif kind=='youtube#playlistItem' and snippet!=None:
                title = snippet.get('title')
                description = snippet.get('description')
                
                resourceId = snippet.get('resourceId', {})
                videoId = resourceId.get('videoId', None)
                if videoId!=None:
                    
                    playlistId = snippet.get('playlistId', None)
                    
                    params = {'action': __ACTION_PLAY__,
                              'id': videoId}
                    
                    #if isWatchLaterPlaylist:
                    #   params['watchLaterItemId'] = item.get('id', '')
                    
                    videoInfo = videoInfos.get(videoId, {})
                    
                    _listVideo(title=title,
                               videoId=videoId,
                               duration=videoInfo.get('duration', '1'),
                               plot=description,
                               thumbnailImage=videoInfo.get('thumbnailImage', __ICON_FALLBACK__),
                               fanart=fanart,
                               publishedAt=publishedAt,
                               channelName=videoInfo.get('channel_name', ''),
                               playlistItemId=item.get('id', None),
                               isMyPlaylist=mine,
                               playlistId=playlistId)
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

def showSearchIndex():
    params = {'action': __ACTION_SEARCH__}
    __plugin__.addDirectory(name='[B]'+__plugin__.localize(30013)+'[/B]', params=params, thumbnailImage=__ICON_FALLBACK__, fanart=__FANART__)
    
    searchHistory = bromixbmc.SeachHistory(__plugin__)
    items = searchHistory.getSearchItems()
    for item in items:
        params = {'action': __ACTION_SEARCH__,
                  'query': item}
        __plugin__.addDirectory(name=item, params=params, thumbnailImage=__ICON_FALLBACK__, fanart=__FANART__)
        pass
    
    __plugin__.endOfDirectory()
    pass
    
def search(query=None, pageToken=None, pageIndex=1):
    __plugin__.setContent('episodes')
    success = False
    
    searchFindVideos=__plugin__.getSettingAsBool('search.find.videos')
    searchFindChannels=__plugin__.getSettingAsBool('search.find.channels')
    searchFindPlaylists=__plugin__.getSettingAsBool('search.find.playlists')
    
    nextPageParams = {}
    jsonData = {}
    if query!=None and len(query)>0:
        if pageToken==None:
            """
            If we have no page token -> this must be the first direct search!!! :)
            Update the order of the history to move the new search to the top.
            """
            size = __plugin__.getSettingAsInt('search.history.size', default=5, mapping={0:0, 1:10, 2:20, 3:30, 4:40, 5:50})
            searchHistory = bromixbmc.SeachHistory(__plugin__, size)
            searchHistory.updateSearchItem(query)
            pass
        
        
        nextPageParams = {'query': query,
                          'action': __ACTION_SEARCH__}
        jsonData = __client__.search(text=query,
                                     searchForVideos=searchFindVideos,
                                     searchForChannels=searchFindChannels,
                                     searchForPlaylists=searchFindPlaylists,
                                     nextPageToken=pageToken
                                     )
        success = True
    else:
        keyboard = bromixbmc.Keyboard(__plugin__.localize(30000))
        if keyboard.doModal():
            success = True
            
            search = keyboard.getText()
            
            """
            Update the search history
            """
            size = __plugin__.getSettingAsInt('search.history.size', default=5, mapping={0:0, 1:10, 2:20, 3:30, 4:40, 5:50})
            searchHistory = bromixbmc.SeachHistory(__plugin__, size)
            searchHistory.updateSearchItem(search)
            
            nextPageParams = {'query': search,
                              'action': __ACTION_SEARCH__}
            jsonData = __client__.search(text=search,
                                         searchForVideos=searchFindVideos,
                                         searchForChannels=searchFindChannels,
                                         searchForPlaylists=searchFindPlaylists,
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
        
    _listResult(jsonData, nextPageParams=nextPageParams, pageIndex=pageIndex, mine=mine)
    
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
        if __plugin__.getSettingAsBool('menu.channel.playlists.show'):
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
    
def showMySubscriptions(pageIndex=1, startIndex=None):
    """
    We have to use at this point V2 of the API.
    V3 doesn't support any kind of new uploaded videos.
    
    NAMESPACES:
    
    xmlns=http://www.w3.org/2005/Atom
    xmlns:media=http://search.yahoo.com/mrss/
    xmlns:openSearch=http://a9.com/-/spec/opensearch/1.1/
    xmlns:gd=http://schemas.google.com/g/2005
    xmlns:gml=http://www.opengis.net/gml
    xmlns:yt=http://gdata.youtube.com/schemas/2007
    xmlns:georss=http://www.georss.org/georss
    """
    __plugin__.setContent('episodes')
    
    try:
        xmlData = __client__.getNewSubscriptionVideosV2(startIndex=startIndex)
        xmlData = xmlData.encode('utf-8')
        
        root = ET.fromstring(xmlData)
        
        entries = root.findall('{http://www.w3.org/2005/Atom}entry')
        if len(entries)==0:
            bromixbmc.logDebug('No new uploaded videos found')
            pass
        
        videoInfos = {}
        videoIds = []
        for entry in entries:
            try:
                mediaGroup = entry.find('{http://search.yahoo.com/mrss/}group')
                if mediaGroup!=None:
                    videoId = unicode(mediaGroup.find('{http://gdata.youtube.com/schemas/2007}videoid').text)
                    videoIds.append(videoId)
                    pass
                pass
            except:
                # do nothing
                pass
            
        videoInfos = __client__.getVideosInfo(videoIds)
        
        for entry in entries:
            try:
                channelName = ''
                author = entry.find('{http://www.w3.org/2005/Atom}author')
                if author!=None:
                    channelName = unicode(author.find('{http://www.w3.org/2005/Atom}name').text)
                    pass
                publishedAt = unicode(entry.find('{http://www.w3.org/2005/Atom}published').text)
                title = unicode(entry.find('{http://www.w3.org/2005/Atom}title').text)
                mediaGroup = entry.find('{http://search.yahoo.com/mrss/}group')
                if mediaGroup!=None:
                    videoId = unicode(mediaGroup.find('{http://gdata.youtube.com/schemas/2007}videoid').text)
                    videoInfo = videoInfos.get(videoId, {})
                    
                    _listVideo(title=title,
                               videoId=videoId,
                               duration=videoInfo.get('duration', '1'),
                               plot=videoInfo.get('plot'),
                               thumbnailImage=videoInfo.get('thumbnailImage', __ICON_FALLBACK__),
                               publishedAt=publishedAt,
                               channelName=channelName)
                    pass
                pass
            except:
                __plugin__.logError('Failed to add new uploaded video')
                pass
            pass
        
        totalResults = 0
        pageInfo = root.find('{http://a9.com/-/spec/opensearch/1.1/}totalResults')
        if pageInfo!=None:
            totalResults = int(pageInfo.text)
            pass
        
        itemsPerPage = 0
        pageInfo = None
        pageInfo = root.find('{http://a9.com/-/spec/opensearch/1.1/}itemsPerPage')
        if pageInfo!=None:
            itemsPerPage = int(pageInfo.text)
            pass
        
        if (startIndex+itemsPerPage)<totalResults:
            params = {'action': __ACTION_SHOW_MYSUBSCRIPTIONS__,
                      'pageIndex': str(pageIndex+1),
                      'startIndex': str(startIndex+itemsPerPage)}
            __plugin__.addDirectory(__plugin__.localize(30002)+' ('+str(pageIndex+1)+')', params=params, fanart=__FANART__)
            pass
    except:
        bromixbmc.logDebug('Failed to load new uploaded videos')
        pass
    
    __plugin__.endOfDirectory()
    
def showSubscriptions(pageToken, pageIndex):
    jsonData = __client__.getSubscriptions(mine=True, nextPageToken=pageToken)
    nextPageParams = {'action': __ACTION_SHOW_SUBSCRIPTIONS__,
                      'mine': 'yes'}
    _listResult(jsonData, nextPageParams=nextPageParams, pageIndex=pageIndex, mine=True)
    __plugin__.endOfDirectory()
    
def addSubscription(channelId):
    __client__.addSubscription(channelId)
    pass

def removeSubscription(channelId):
    __client__.removeSubscription(channelId)
    bromixbmc.executebuiltin("Container.Refresh");
    pass
    
def play(videoId):
    allow3D = __plugin__.getSettingAsBool('allow3D', False)
    quality = __plugin__.getSettingAsInt('videoQuality', mapping={0:576, 1:720, 2:1080})
    stream = youtube.video.getBestFittingVideoStreamInfo(videoId=videoId, size=quality, allow3D=allow3D)
    if stream!=None:
        url = stream.getUrl()
        if url!=None:
            __plugin__.setResolvedUrl(url)
            
            if __client__.hasLogin():
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

def addToPlaylist(videoId):
    playlistId = bromixbmc.getParam('playlistId', None)
    if playlistId!=None:
        __client__.addPlayListItem(playlistId, videoId)
        pass
    pass

def removePlaylist(playlistId):
    __client__.removePlaylist(playlistId)
    bromixbmc.executebuiltin("Container.Refresh");
    pass

def removeFromPlaylist(playlistItemId):
    __client__.removePlaylistItem(playlistItemId)
    bromixbmc.executebuiltin("Container.Refresh");
    pass

action = bromixbmc.getParam('action')
_id = bromixbmc.getParam('id')
query = bromixbmc.getParam('query', '')
pageToken = bromixbmc.getParam('pageToken')
pageIndex = int(bromixbmc.getParam('pageIndex', '1'))
mine = bromixbmc.getParam('mine', 'no')=='yes'

if action == __ACTION_SHOW_SEARCH_INDEX__:
    showSearchIndex()
elif action == __ACTION_SEARCH__:
    search(query, pageToken, pageIndex)
elif action == __ACTION_ADD_TO_PLAYLIST__ and _id!=None:
    addToPlaylist(_id)
elif action == __ACTION_REMOVE_FROM_PLAYLIST__ and _id!=None:
    removeFromPlaylist(_id)
elif action == __ACTION_SHOW_MYSUBSCRIPTIONS__:
    startIndex = int(bromixbmc.getParam('startIndex', '1'))
    showMySubscriptions(pageIndex=pageIndex, startIndex=startIndex)
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
elif action == __ACTION_REMOVE_PLAYLIST__ and _id!=None:
    removePlaylist(_id)
elif action == __ACTION_ADD_SUBSCRIPTION__ and _id!=None:
    addSubscription(_id)
elif action == __ACTION_REMOVE_SUBSCRIPTION__ and _id!=None:
    removeSubscription(_id)
else:
    showIndex()
    
# token and expiration date
if __plugin__.getSettingAsString('oauth2_access_token', '') != __client__.AccessToken:
    if __client__.AccessToken!=None and len(__client__.AccessToken)>0:
        __plugin__.setSettingAsFloat('oauth2_access_token_expires_at', __client__.AccessTokenExpiresAt)
        __plugin__.setSettingAsString('oauth2_access_token', __client__.AccessToken)