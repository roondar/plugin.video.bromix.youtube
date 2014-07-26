# -*- coding: utf-8 -*-

import os

#import pydevd
#pydevd.settrace('localhost', stdoutToServer=True, stderrToServer=True)

import bromixbmc
__plugin__ = bromixbmc.Plugin()

from youtube import YouTubeClient
__client__ = YouTubeClient(language=bromixbmc.getLanguageId());

# icons and images
__FANART__ = os.path.join(__plugin__.getPath(), "fanart.jpg")
__ICON_FALLBACK__ = os.path.join(__plugin__.getPath(), "resources/media/fallback_icon.png")
__ICON_SEARCH__ = os.path.join(__plugin__.getPath(), "resources/media/search.png")

# settings
__SETTING_SHOW_FANART__ = __plugin__.getSettingAsBool('showFanart')
if not __SETTING_SHOW_FANART__:
    __FANART__ = ''

#actions
__ACTION_SEARCH__ = 'search'
__ACTION_BROWSE_CHANNELS__ = 'browseChannels'
__ACTION_WHAT_TO_WATCH__ = 'whatToWatch'
__ACTION_PLAY__ = 'play'


def showIndex():
    params = {'action': __ACTION_SEARCH__}
    __plugin__.addDirectory("[B]"+__plugin__.localize(30000)+"[/B]", params = params, thumbnailImage=__ICON_FALLBACK__, fanart=__FANART__)
    
    params = {'action': __ACTION_WHAT_TO_WATCH__}
    __plugin__.addDirectory(__plugin__.localize(30002), params = params, thumbnailImage=__ICON_FALLBACK__, fanart=__FANART__)
    
    params = {'action': __ACTION_BROWSE_CHANNELS__}
    __plugin__.addDirectory(__plugin__.localize(30001), params = params, thumbnailImage=__ICON_FALLBACK__, fanart=__FANART__)
    
    __plugin__.endOfDirectory()
    
def _listResult(jsonData, additionalParams={}, pageIndex=1):
    items = jsonData.get('items', None)
    if items!=None:
        nextPageToken = jsonData.get('nextPageToken', None)
        for item in items:
            kind = item.get('kind', '')
            _id = item.get('id', None)
            snippet = item.get('snippet', None)
            
            if kind=='youtube#guideCategory' and snippet!=None:
                channelId = snippet.get('channelId')
                title = snippet.get('title')
                
                params = {'action': '',
                          'channelId': channelId}
                __plugin__.addDirectory(name=title, params=params, thumbnailImage=__ICON_FALLBACK__, fanart=__FANART__)
                pass
            elif kind=='youtube#searchResult' and snippet!=None and _id!=None:
                kind = _id.get('id', '')
                videoId = _id.get('videoId', '')
                
                title = snippet.get('title')
                description = snippet.get('description', '')
                thumbnails = snippet.get('thumbnails', {})
                imageResList = ['high', 'medium', 'default']
                for imageRes in imageResList:
                    thumbnailImage = thumbnails.get(imageRes, None)
                    if thumbnailImage!=None:
                        url = thumbnailImage.get('url', None)
                        if url!=None:
                            thumbnailImage=url
                            break
                    pass
                if thumbnailImage==None:
                    thumbnailImage=''
                    pass
                
                params = {'action': __ACTION_PLAY__,
                          'videoId': videoId}
                params.update(additionalParams)
                infoLabels = {'plot': description}
                __plugin__.addVideoLink(name=title, params=params, thumbnailImage=thumbnailImage, fanart=__FANART__, infoLabels=infoLabels)
                pass
            pass
        
        if nextPageToken!=None:
            params = {'pageIndex': str(pageIndex+1),
                      'pageToken': nextPageToken}
            params.update(additionalParams)
            __plugin__.addDirectory(__plugin__.localize(30003)+' ('+str(pageIndex+1)+')', params=params, fanart=__FANART__)
            pass
        pass
    pass
    
def search(query=None, pageToken=None, pageIndex=1):
    success = False
    
    additionalParams = {}
    jsonData = {}
    if query!=None and pageToken!=None:
        additionalParams = {'query': query,
                            'action': __ACTION_SEARCH__}
        jsonData = __client__.search(query, pageToken)
        success = True
    else:
        keyboard = bromixbmc.Keyboard(__plugin__.localize(30000))
        if keyboard.doModal():
            success = True
            
            search_string = keyboard.getText().replace(" ", "+")
            additionalParams = {'query': search_string,
                                'action': __ACTION_SEARCH__}
            jsonData = __client__.search(search_string)
            pass
        pass
    
    _listResult(jsonData, additionalParams=additionalParams, pageIndex=pageIndex)
    __plugin__.endOfDirectory(success)
    
def browseChannels():
    jsonData = __client__.getGuideCategories()
    _listResult(jsonData)
    
    __plugin__.endOfDirectory()

action = bromixbmc.getParam('action')
query = bromixbmc.getParam('query')
pageToken = bromixbmc.getParam('pageToken')
pageIndex = int(bromixbmc.getParam('pageIndex', '1'))

if action == __ACTION_SEARCH__:
    search(query, pageToken, pageIndex)
elif action == __ACTION_BROWSE_CHANNELS__:
    browseChannels();
else:
    showIndex()