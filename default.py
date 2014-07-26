# -*- coding: utf-8 -*-

import os
import re

#import pydevd
#pydevd.settrace('localhost', stdoutToServer=True, stderrToServer=True)

import bromixbmc
__plugin__ = bromixbmc.Plugin()

import rtlinteractive
__now_client__ = rtlinteractive.now.Client(rtlinteractive.now.__CONFIG_VOX_NOW__)

__FANART__ = os.path.join(__plugin__.getPath(), "fanart.jpg")
__ICON_FAVOURITES__ = os.path.join(__plugin__.getPath(), "resources/media/favorites.png")
__ICON_NEWEST__ = os.path.join(__plugin__.getPath(), "resources/media/newest.png")
__ICON_HIGHLIGHTS__ = os.path.join(__plugin__.getPath(), "resources/media/highlight.png")
__ICON_LIBRARY__ = os.path.join(__plugin__.getPath(), "resources/media/library.png")
__ICON_SEARCH__ = os.path.join(__plugin__.getPath(), "resources/media/search.png")
__ICON_LIVE__ = os.path.join(__plugin__.getPath(), "resources/media/livestream.png")

__ACTION_SHOW_LIBRARY__ = 'showLibrary'
__ACTION_SHOW_TIPS__ = 'showTips'
__ACTION_SHOW_NEWEST__ = 'showNewest'
__ACTION_SHOW_TOP10__ = 'showTop10'
__ACTION_SHOW_EPISODES__ = 'showEpisodes'
__ACTION_SEARCH__ = 'search'
__ACTION_LIVE_STREAM__ = 'playLivestream'
__ACTION_SHOW_FAVS__ = 'showFavs'
__ACTION_ADD_FAV__ = 'addFav'
__ACTION_REMOVE_FAV__ = 'removeFav'
__ACTION_PLAY__ = 'play'

__SETTING_SHOW_FANART__ = __plugin__.getSettingAsBool('showFanart')
__SETTING_SHOW_PUCLICATION_DATE__ = __plugin__.getSettingAsBool('showPublicationDate')

def showIndex():
    if len(__plugin__.getFavorites())>0:
        params = {'action': __ACTION_SHOW_FAVS__}
        __plugin__.addDirectory("[B]"+__plugin__.localize(30008)+"[/B]", params = params, thumbnailImage=__ICON_FAVOURITES__, fanart=__FANART__)
        
    # add 'Sendungen A-Z'
    params = {'action': __ACTION_SHOW_LIBRARY__}
    __plugin__.addDirectory(__plugin__.localize(30000), params = params, thumbnailImage=__ICON_LIBRARY__, fanart=__FANART__)
    
    params = {'action': __ACTION_SHOW_NEWEST__}
    __plugin__.addDirectory(__plugin__.localize(30002), params = params, thumbnailImage=__ICON_NEWEST__, fanart=__FANART__)
    
    params = {'action': __ACTION_SHOW_TIPS__}
    __plugin__.addDirectory(__plugin__.localize(30001), params = params, thumbnailImage=__ICON_HIGHLIGHTS__, fanart=__FANART__)
    
    params = {'action': __ACTION_SHOW_TOP10__}
    __plugin__.addDirectory(__plugin__.localize(30003), params = params, thumbnailImage=__ICON_HIGHLIGHTS__, fanart=__FANART__)
    
    params = {'action': __ACTION_SEARCH__}
    __plugin__.addDirectory(__plugin__.localize(30004), params = params, thumbnailImage=__ICON_SEARCH__, fanart=__FANART__)
    
    params = {'action': __ACTION_LIVE_STREAM__}
    __plugin__.addVideoLink(__plugin__.localize(30005), params = params, thumbnailImage=__ICON_LIVE__, fanart=__FANART__)
    
    __plugin__.endOfDirectory()

def showLibrary():
    __plugin__.addSortMethod()
    
    shows = __now_client__.getShows()
    shows = shows.get('content', {})
    shows = shows.get('formatlist', {})
    
    for key, show in shows.items():
        title = show.get('formatlong', None)
        id = show.get('formatid', None)
        free_episodes = int(show.get('free_episodes', '0'))
        fanart = None
        if __SETTING_SHOW_FANART__:
            fanart = show.get('bigaufmacherimg', '')
            fanart = fanart.replace('/640x360/', '/768x432/')
            
        thumbnailImage = show.get('biggalerieimg', '')
        thumbnailImage = thumbnailImage.replace('/271x152/', '/768x432/')
        
        if free_episodes>=1 and title!=None and id!=None:
            params = {'action': __ACTION_SHOW_EPISODES__,
                      'id': id}
            
            contextParams = {'action': __ACTION_ADD_FAV__,
                             'id': id,
                             'title': title.encode('utf-8'),
                             'fanart': fanart,
                             'thumb': thumbnailImage}
            contextRun = 'RunPlugin('+__plugin__.createUrl(contextParams)+')'
            contextMenu = [("[B]"+__plugin__.localize(30006)+"[/B]", contextRun)]
            
            __plugin__.addDirectory(title, params=params, thumbnailImage=thumbnailImage, fanart=fanart, contextMenu=contextMenu)
    
    __plugin__.endOfDirectory()

def _listEpisodes(episodes, format_id, func={}, break_at_none_free_episode=True):
    __plugin__.setContent('episodes')
    
    episodes = episodes.get('content', {})
    page = episodes.get('page', '1')
    maxpage = episodes.get('maxpage', '1')
    episodes = episodes.get('filmlist', {})
        
    sorted_episodes = sorted(episodes.items(), key=func.get('sort_func', None), reverse=func.get('sort_reverse', True))
    
    show_next = False
    for item in sorted_episodes:
        if len(item)>=2:
            episode = item[1]
            title = func.get('title_func', None)(episode)
            id = episode.get('id', None)
            free = episode.get('free', '0')
            duration = episode.get('duration', '00:00:00')
            match = re.compile('(\d*)\:(\d*)\:(\d*)', re.DOTALL).findall(duration)
            if match!=None and len(match[0])>=3:
                hours = int(match[0][0])
                minutes = hours*60 + int(match[0][1]) 
                duration = str(minutes)

            year = ''
            aired = ''
            date = ''
            match = re.compile('(\d*)\-(\d*)\-(\d*) (\d*)\:(\d*)\:(\d*)', re.DOTALL).findall(episode.get('sendestart', '0000-00-00'))
            if match!=None and len(match[0])>=3:
                year = match[0][0]
                aired = match[0][0]+"-"+match[0][1]+"-"+match[0][2]
                date = match[0][2]+"."+match[0][1]+"."+match[0][0]
                if __SETTING_SHOW_PUCLICATION_DATE__:
                    date_format = bromixbmc.getFormatDateShort(match[0][0], match[0][1], match[0][2])
                    title = date_format+" - "+title
                
            fanart = None
            if __SETTING_SHOW_FANART__:
                fanart = episode.get('bigaufmacherimg', '')
                fanart = fanart.replace('/640x360/', '/768x432/')
                
            thumbnailImage = __now_client__.getEpisodeThumbnailImage(episode)

            infoLabels = {'duration': duration,
                          'plot': episode.get('articleshort', ''),
                          'episode': episode.get('episode', ''),
                          'season': episode.get('season', ''),
                          'year': year,
                          'date': date,
                          'aired': aired
                          }
                
            if free=='1' and title!=None and id!=None:
                params = {'action': __ACTION_PLAY__,
                          'id': id}
                __plugin__.addVideoLink(title, params=params, thumbnailImage=thumbnailImage, fanart=fanart, infoLabels=infoLabels)
                show_next = True
            elif free=='0':
                show_next = False
                
    if page<maxpage and show_next:
        params = {'action': __ACTION_SHOW_EPISODES__,
                  'id': format_id,
                  'page': str(page+1)
                  }
        __plugin__.addDirectory(__plugin__.localize(30009)+' ('+str(page+1)+')', params=params, fanart=__FANART__)
    
    __plugin__.endOfDirectory()

def showTips():
    def _sort_key(d):
        return d[0]
    
    def _get_title(d):
        return d.get('formatlong', '')+" - "+d.get('headlinelong', '')
    
    episodes = __now_client__.getTips()
    _listEpisodes(episodes, id, func={'sort_func': _sort_key,
                                  'sort_reverse': False,
                                  'title_func': _get_title}
                  )
    
def showNewest():
    def _sort_key(d):
        return d[0]
    
    def _get_title(d):
        return d.get('formatlong', '')+" - "+d.get('headlinelong', '')
    
    episodes = __now_client__.getNewest()
    _listEpisodes(episodes, id, func={'sort_func': _sort_key,
                                  'sort_reverse': False,
                                  'title_func': _get_title}
                  )
    
def showTop10():
    def _sort_key(d):
        return d[0]
    
    def _get_title(d):
        return d.get('formatlong', '')+" - "+d.get('headlinelong', '')
    
    episodes = __now_client__.getTop10()
    _listEpisodes(episodes, id, func={'sort_func': _sort_key,
                                  'sort_reverse': False,
                                  'title_func': _get_title}
                  )

def showEpisodes(id):
    def _sort_key(d):
        return d[1].get('sendestart', '').lower()
    
    def _get_title(d):
        return d.get('headlinelong', '')
    
    page = bromixbmc.getParam('page', '1')
    
    episodes = __now_client__.getEpisodes(id, page=page)
    _listEpisodes(episodes, id, func={'sort_func': _sort_key,
                                  'sort_reverse': True,
                                  'title_func': _get_title}
                  )
    
def search():
    success = False
    
    keyboard = bromixbmc.Keyboard(__plugin__.localize(30004))
    if keyboard.doModal():
        success = True
        
        search_string = keyboard.getText().replace(" ", "+")
        result = __now_client__.search(search_string)
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
        
    __plugin__.endOfDirectory(success)

def playLivestream():
    streams = __now_client__.getLivestreams()
    
    lsq = __plugin__.getSettingAsInt('liveStreamQuality')
    key = 'high_android4'
    if lsq==1:
        key='high_android4'
    elif lsq==0:
        key='high_android2'
    else:
        key='high_android4'
    
    url = streams.get(key, None)
    if url!=None:
        __plugin__.setResolvedUrl(url, isLiveStream=True)

def removeFav(id):
    __plugin__.removeFavorite(id)
    bromixbmc.executebuiltin("Container.Refresh");
    pass

def addFav(id):
    title = bromixbmc.getParam('title', '').decode('utf-8')
    fanart = bromixbmc.getParam('fanart', '')
    thumbnailImage = bromixbmc.getParam('thumb', '')
    
    if id!=None and title!='':
        newFav = {}
        newFav['title'] = title
        newFav['fanart'] = fanart
        newFav['thumbnailImage'] = thumbnailImage
        
        __plugin__.setFavorite(id, newFav)
    pass

def showFavs():
    def _sort_key(d):
        return d[1].get('title', "")
    
    _favs = __plugin__.getFavorites()
    favs = sorted(_favs, key=_sort_key, reverse=False)
    
    for fav in favs:
        if len(fav)==2:
            item = fav[1]
            params = {'action': __ACTION_SHOW_EPISODES__,
                      'id': fav[0]}
            title = item.get('title', None)
            if title!=None:
                contextParams = {'action': __ACTION_REMOVE_FAV__,
                                 'id': fav[0]
                                 }
                contextRun = 'RunPlugin('+__plugin__.createUrl(contextParams)+')'
                contextMenu = [("[B]"+__plugin__.localize(30007)+"[/B]", contextRun)]
                
                __plugin__.addDirectory(title, params=params, thumbnailImage=item.get('thumbnailImage', ''), fanart=item.get('fanart', ''), contextMenu=contextMenu)
                
    __plugin__.endOfDirectory()

def play(id):
    url = __now_client__.getEpisodeVideoUrl(id)
    if url!=None:
        __plugin__.setResolvedUrl(url) 

action = bromixbmc.getParam('action')
id = bromixbmc.getParam('id')

if action == __ACTION_SHOW_LIBRARY__:
    showLibrary()
elif action == __ACTION_SHOW_TIPS__:
    showTips()
elif action == __ACTION_SHOW_NEWEST__:
    showNewest()
elif action == __ACTION_SHOW_TOP10__:
    showTop10()
elif action == __ACTION_SHOW_EPISODES__ and id!=None:
    showEpisodes(id)
elif action == __ACTION_SEARCH__:
    search()
elif action == __ACTION_LIVE_STREAM__:
    playLivestream()
elif action == __ACTION_SHOW_FAVS__:
    showFavs()
elif action == __ACTION_ADD_FAV__ and id!=None:
    addFav(id)
elif action == __ACTION_REMOVE_FAV__ and id!=None:
    removeFav(id)
elif action == __ACTION_PLAY__ and id!=None:
    play(id)
else:
    showIndex()