# -*- coding: utf-8 -*-

import os

import pydevd
pydevd.settrace('localhost', stdoutToServer=True, stderrToServer=True)

import bromixbmc
__plugin__ = bromixbmc.Plugin()

from youtube import YouTubeClient
__client__ = YouTubeClient();

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
    
def search():
    success = False
    
    keyboard = bromixbmc.Keyboard(__plugin__.localize(30000))
    if keyboard.doModal():
        success = True
        
        search_string = keyboard.getText().replace(" ", "+")
        result = __client__.search(search_string)
        
        """
        result = result.get('content', {})
        result = result.get('list', {})
        for key in result:
            item = result.get(key,None)
            if item!=None:
                title = item.get('result', None)
                id = item.get('formatid', None)
                if title!=None and id!=None:
                    params = {'action': __ACTION_SHOW_EPISODES__,
                              'id': id}
                    __plugin__.addDirectory(title, params=params)
                    """
        
    __plugin__.endOfDirectory(success)

action = bromixbmc.getParam('action')

if action == __ACTION_SEARCH__:
    search()
else:
    showIndex()