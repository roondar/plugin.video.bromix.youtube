# -*- coding: utf-8 -*-

import urllib
import urllib2
import urlparse
import re

__ITAG_MAP__ = {'5': {'format': 'FLV', 'width': 320, 'height': 240, '3D': False},
                '17': {'format': '3GP', 'width': 176, 'height': 144, '3D': False},
                '18': {'format': 'MP4', 'width': 480, 'height': 360, '3D': False},
                '22': {'format': 'MP4', 'width': 1280, 'height': 720, '3D': False},
                '34': {'format': 'FLV', 'width': 480, 'height': 360, '3D': False},
                '35': {'format': 'FLV', 'width': 640, 'height': 480, '3D': False},
                '36': {'format': '3GP', 'width': 320, 'height': 240, '3D': False},
                '37': {'format': 'MP4', 'width': 1920, 'height': 1080, '3D': False},
                '38': {'format': 'MP4', 'width': 2048, 'height': 1080, '3D': False},
                '43': {'format': 'WEB', 'width': 480, 'height': 360, '3D': False},
                '44': {'format': 'WEB', 'width': 640, 'height': 480, '3D': False},
                '45': {'format': 'WEB', 'width': 1280, 'height': 720, '3D': False},
                '46': {'format': 'WEB', 'width': 1920, 'height': 1080, '3D': False},
                '82': {'format': 'MP4', 'width': 480, 'height': 360, '3D': True},
                '83': {'format': 'MP4', 'width': 640, 'height': 480, '3D': True},
                '84': {'format': 'MP4', 'width': 1280, 'height': 720, '3D': True},
                '85': {'format': 'MP4', 'width': 1920, 'height': 1080, '3D': True},
                '100': {'format': 'WEB', 'width': 480, 'height': 360, '3D': True},
                '101': {'format': 'WEB', 'width': 640, 'height': 480, '3D': True},
                '102': {'format': 'WEB', 'width': 1280, 'height': 720, '3D': True},
                '133': {'format': 'MP4', 'width': 320, 'height': 240, '3D': False, 'VO': True},
                '134': {'format': 'MP4', 'width': 480, 'height': 360, '3D': False, 'VO': True},
                '135': {'format': 'MP4', 'width': 640, 'height': 480, '3D': False, 'VO': True},
                '136': {'format': 'MP4', 'width': 1280, 'height': 720, '3D': False, 'VO': True},
                '137': {'format': 'MP4', 'width': 1920, 'height': 1080, '3D': False, 'VO': True},
                '160': {'format': 'MP4', 'width': 256, 'height': 144, '3D': False, 'VO': True},
                '242': {'format': 'WEB', 'width': 320, 'height': 240, '3D': False, 'VOX': True},
                '243': {'format': 'WEB', 'width': 480, 'height': 360, '3D': False, 'VOX': True},
                '244': {'format': 'WEB', 'width': 640, 'height': 480, '3D': False, 'VOX': True},
                '245': {'format': 'WEB', 'width': 640, 'height': 480, '3D': False, 'VOX': True},
                '246': {'format': 'WEB', 'width': 640, 'height': 480, '3D': False, 'VOX': True},
                '247': {'format': 'WEB', 'width': 1280, 'height': 720, '3D': False, 'VOX': True},
                '248': {'format': 'WEB', 'width': 1920, 'height': 1080, '3D': False, 'VOX': True},
                '264': {'format': 'MP4', 'width': 1920, 'height': 1080, '3D': False, 'VOX': True}
                }

class YTVideoStreamInfo():
    def __init__(self, url, itag, videoType, signature=None):
        self._url = url
        self._signature = signature
        self._itag = itag
        self._videoType = videoType
        pass
    
    def _getDecodeSignature(self, signature):
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
    
    def getUrl(self):
        if self._signature!=None:
            signature = self._getDecodeSignature(self._signature)
            if signature!=None and len(signature)>0:
                self._signature=None
                
                self._url = self._url+'&signature='+signature
                pass
            pass
        
        return self._url
    
    def getSize(self):
        width = self._itag.get('width', 0)
        height = self._itag.get('height', 0)
        return [width, height]
    
    def getType(self):
        return self._videoType
    
    def is3D(self):
        return self._itag.get('3D', False)
    pass

def _getVideoStreamInfosPerPageView(videoId):
    result = []
    itagMap = {}
    
    opener = urllib2.build_opener()
    url = 'https://www.youtube.com/watch?v=%s' % (videoId)
    content = opener.open(url)
    
    html = content.read()
    
    """
    This will almost double the speed for the regular expressions, because we only must match
    a small portion of the whole html. And only if we find positions, we cut down the html.
    
    """
    pos = html.find('ytplayer.config')
    if pos:
        html2 = html[pos:]
        pos = html2.find('</script>')
        if pos:
            html = html2[:pos]
            pass
        pass
    
    fmtListMatch = re.compile('.+\"fmt_list\": \"(.+?)\".+').findall(html)
    if fmtListMatch!=None and len(fmtListMatch)>0 and len(fmtListMatch[0])>=1:
        valueString = fmtListMatch[0]
        values = valueString.split(',')
        
        for value in values:
            value = value.replace('\/', '|')
            
            try:
                attr = value.split('|')
                sizes = attr[1].split('x')
                itagMap[attr[0]] =  {'width': int(sizes[0]),
                                     'height': int(sizes[1]),
                                     '3D': False}
            except:
                # do nothing
                pass
            pass
        pass
    
    itagMap.update(__ITAG_MAP__)
    
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
                    signature = attr.get('s', None)
                elif attr.get('sig', None)!=None:
                    signature = attr.get('sig', '')
                    url = url + '&signature='
                    url = url + signature
                
                itag = attr['itag']
                videoType = attr['type'].split(';')[0]
                
                itag = itagMap[itag]
                videoInfo = YTVideoStreamInfo(url, itag, videoType, signature)
                result.append(videoInfo)
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

def getVideoStreamInfos(videoId):
    result = _getVideoStreamInfosPerPageView(videoId)
    if len(result)>0:
        return result
    
    #fallback
    opener = urllib2.build_opener()
    #url = ' https://www.youtube.com/get_video_info?video_id=%s&hl=en&gl=US&ptk=vevo&el=detailpage' % (videoId)
    url = ' https://www.youtube.com/get_video_info?video_id=%s&hl=en&gl=US&el=detailpage' % (videoId)
    content = opener.open(url)
    
    html = content.read()
    itagMap = {}
    
    attr = dict(urlparse.parse_qsl( html ) )

    # first find the format list and create a map of the resolutions
    fmt_list = attr.get('fmt_list', None)
    if fmt_list!=None:
        fmt_list = fmt_list.split(',')
        for fmt in fmt_list:
            values = fmt.split('/')
            if len(values)>=5:
                try:
                    sizes = values[1].split('x')
                    itagMap[values[0]] = {'width': int(sizes[0]),
                                          'height': int(sizes[1]),
                                          '3D': False
                                          }
                except:
                    #do nothing
                    pass
                
                pass
            pass
        pass
    
    itagMap.update(__ITAG_MAP__)
    
    url_encoded_fmt_stream_map = attr.get('url_encoded_fmt_stream_map', None)
    if url_encoded_fmt_stream_map!=None:
        values = url_encoded_fmt_stream_map.split(',')
        for value in values:
            
            try:
                attr = dict(urlparse.parse_qsl( value ) )
                
                url = attr.get('url', None)
                url = urllib.unquote(url)
                
                signature = None
                if attr.get('s', None)!=None:
                    signature = attr.get('s', None)
                elif attr.get('sig', None)!=None:
                    signature = attr.get('sig', '')
                    url = url + '&signature='
                    url = url + signature
                    
                videoType = attr['type'].split(';')[0]
                    
                itag = attr['itag']
                itag = itagMap[itag]
                videoInfo = YTVideoStreamInfo(url, itag, videoType, signature)
                result.append(videoInfo)
            except:
                # do nothing
                pass
            pass
        pass
    
    return result

def getBestFittingVideoStreamInfo(videoId=None, videoInfos=None, size=720, allow3D=False):
    if videoId!=None:
        videoInfos = getVideoStreamInfos(videoId)
    
    result = None
    lastSize = 0
    for videoInfo in videoInfos:
        # skip the one with 3D support
        if not allow3D and videoInfo.is3D():
            continue
        
        currentSize = videoInfo.getSize()[1]
        
        if currentSize>=lastSize and currentSize<=size:
            lastSize = currentSize
            result = videoInfo
        pass
        
    return result