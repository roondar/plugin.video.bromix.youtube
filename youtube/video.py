# -*- coding: utf-8 -*-

import urllib
import urllib2
import urlparse
import re

class YTVideoStreamInfo():
    def __init__(self, url, width, height, videoType, signature=None):
        self._url = url
        self._signature = signature
        self._width = width
        self._height = height
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
        return [self._width, self._height]
    
    def getType(self):
        return self._videoType
    pass

def _getVideoStreamInfosPerPageView(videoId):
    result = []
    sizeMap = {}
    
    opener = urllib2.build_opener()
    url = 'https://www.youtube.com/watch?v=%s' % (videoId)
    content = opener.open(url)
    
    html = content.read()
    
    fmtListMatch = re.compile('.+\"fmt_list\": \"(.+?)\".+').findall(html)
    if fmtListMatch!=None and len(fmtListMatch)>0 and len(fmtListMatch[0])>=1:
        valueString = fmtListMatch[0]
        values = valueString.split(',')
        
        for value in values:
            value = value.replace('\/', '|')
            
            try:
                attr = value.split('|')
                sizes = attr[1].split('x')
                sizeMap[attr[0]] =  {'width': int(sizes[0]), 'height': int(sizes[1])}
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
                    signature = attr.get('s', None)
                elif attr.get('sig', None)!=None:
                    signature = attr.get('sig', '')
                    url = url + '&signature='
                    url = url + signature
                
                itag = attr['itag']
                videoType = attr['type'].split(';')[0]
                
                size = sizeMap[itag]
                videoInfo = YTVideoStreamInfo(url, size.get('width', '0'), size.get('height', 0), videoType, signature)
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
    sizeMap = {}
    
    attr = dict(urlparse.parse_qsl( html ) )

    # first find the format list and create a map of the resolutions
    fmt_list = attr.get('fmt_list', None)
    if fmt_list!=None:
        fmt_list = fmt_list.split(',')
        for fmt in fmt_list:
            values = fmt.split('/')
            if len(values)>=5:
                sizes = values[1].split('x')
                sizeMap[values[0]] = sizes
                pass
            pass
        pass
    
    url_encoded_fmt_stream_map = attr.get('url_encoded_fmt_stream_map', None)
    if url_encoded_fmt_stream_map!=None:
        values = url_encoded_fmt_stream_map.split(',')
        for value in values:
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
            size = sizeMap[itag]
            videoInfo = YTVideoStreamInfo(url, int(size[0]), int(size[1]), videoType, signature)
            result.append(videoInfo)
            pass
        pass
    
    return result

def getBestFittingVideoStreamInfo(videoId=None, videoInfos=None, size=720):
    if videoId!=None:
        videoInfos = getVideoStreamInfos(videoId)
    
    result = None
    lastSize = 0
    for videoInfo in videoInfos:
        currentSize = videoInfo.getSize()[1]
        
        if currentSize>=lastSize and currentSize<=size:
            lastSize = currentSize
            result = videoInfo
        pass
        
    return result