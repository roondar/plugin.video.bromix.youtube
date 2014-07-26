# -*- coding: utf-8 -*-

import os

import pydevd
pydevd.settrace('localhost', stdoutToServer=True, stderrToServer=True)

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
    
def _listResult(jsonData):
    items = jsonData.get('items', None)
    if items!=None:
        for item in items:
            kind = item.get('kind', '')
            _id = item.get('id', '')
            snippet = item.get('snippet', None)
            if snippet!=None and kind=='youtube#guideCategory':
                channelId = snippet.get('channelId')
                title = snippet.get('title')
                
                params = {'action': '',
                          'channelId': channelId}
                __plugin__.addDirectory(name=title, params=params, thumbnailImage=__ICON_FALLBACK__, fanart=__FANART__)
                pass
            pass
        pass
    pass
    
def search():
    success = False
    
    keyboard = bromixbmc.Keyboard(__plugin__.localize(30000))
    if keyboard.doModal():
        success = True
        
        search_string = keyboard.getText().replace(" ", "+")
        jsonData = __client__.search(search_string)
        _listResult(jsonData)
        
    __plugin__.endOfDirectory(success)
    
def browseChannels():
    jsonData = __client__.getGuideCategories()
    _listResult(jsonData)
    
    __plugin__.endOfDirectory()

action = bromixbmc.getParam('action')

if action == __ACTION_SEARCH__:
    search()
elif action == __ACTION_BROWSE_CHANNELS__:
    browseChannels();
else:
    showIndex()