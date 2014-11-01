import urllib
import urlparse
import re
import requests

__author__ = 'bromix'


class VideoInfoExtractor(object):
    DEFAULT_ITAG_MAP = {'5': {'format': 'FLV', 'width': 320, 'height': 240},
                        '17': {'format': '3GP', 'width': 176, 'height': 144},
                        '18': {'format': 'MP4', 'width': 480, 'height': 360},
                        '22': {'format': 'MP4', 'width': 1280, 'height': 720},
                        '34': {'format': 'FLV', 'width': 480, 'height': 360},
                        '35': {'format': 'FLV', 'width': 640, 'height': 480},
                        '36': {'format': '3GP', 'width': 320, 'height': 240},
                        '37': {'format': 'MP4', 'width': 1920, 'height': 1080},
                        '38': {'format': 'MP4', 'width': 2048, 'height': 1080},
                        '43': {'format': 'WEB', 'width': 480, 'height': 360},
                        '44': {'format': 'WEB', 'width': 640, 'height': 480},
                        '45': {'format': 'WEB', 'width': 1280, 'height': 720},
                        '46': {'format': 'WEB', 'width': 1920, 'height': 1080},
                        '82': {'format': 'MP4', 'width': 480, 'height': 360, '3D': True},
                        '83': {'format': 'MP4', 'width': 640, 'height': 480, '3D': True},
                        '84': {'format': 'MP4', 'width': 1280, 'height': 720, '3D': True},
                        '85': {'format': 'MP4', 'width': 1920, 'height': 1080, '3D': True},
                        '100': {'format': 'WEB', 'width': 480, 'height': 360, '3D': True},
                        '101': {'format': 'WEB', 'width': 640, 'height': 480, '3D': True},
                        '102': {'format': 'WEB', 'width': 1280, 'height': 720, '3D': True},
                        '133': {'format': 'MP4', 'width': 320, 'height': 240, 'VO': True},
                        '134': {'format': 'MP4', 'width': 480, 'height': 360, 'VO': True},
                        '135': {'format': 'MP4', 'width': 640, 'height': 480, 'VO': True},
                        '136': {'format': 'MP4', 'width': 1280, 'height': 720, 'VO': True},
                        '137': {'format': 'MP4', 'width': 1920, 'height': 1080, 'VO': True},
                        '160': {'format': 'MP4', 'width': 256, 'height': 144, 'VO': True},
                        '242': {'format': 'WEB', 'width': 320, 'height': 240, 'VOX': True},
                        '243': {'format': 'WEB', 'width': 480, 'height': 360, 'VOX': True},
                        '244': {'format': 'WEB', 'width': 640, 'height': 480, 'VOX': True},
                        '245': {'format': 'WEB', 'width': 640, 'height': 480, 'VOX': True},
                        '246': {'format': 'WEB', 'width': 640, 'height': 480, 'VOX': True},
                        '247': {'format': 'WEB', 'width': 1280, 'height': 720, 'VOX': True},
                        '248': {'format': 'WEB', 'width': 1920, 'height': 1080, 'VOX': True},
                        '264': {'format': 'MP4', 'width': 1920, 'height': 1080, 'VOX': True}}

    """
    name of the method
    signature = (?P<cipher>.+\(.?\))


    """

    def __init__(self, youtube_client):
        self._youtube_client = youtube_client
        pass

    def _parse_java_script(self, java_script):
        def _get_helper_function(java_script, namespace):
            match = re.search('var %s={(?P<class_functions>.*?})};' % namespace, java_script)
            class_functions = match.group('class_functions')

            class_functions = class_functions.split('},')
            for class_function in class_functions:
                # normalize function
                if not class_function.endswith('}'):
                    class_function += '}'
                    pass
                match = re.match('(?P<name>[^:]*):function\((?P<parameter>[^)]*)\)\{(?P<body>[^}]+)\}', class_function)
                name = match.group('name')
                parameter = match.group('parameter')
                body = match.group('body').split(';')
                pass
            pass

        # first find the name of the cipher function
        match = re.search("signature=(?P<function_name>[$a-zA-Z]+)\([^)]\)", java_script)
        if not match:
            raise Exception('Could not find cipher function')

        function_name = match.group('function_name')

        # get the function body
        match = re.search('function %s\((?P<parameter_name>[^)]+?)\){(?P<function_body>[^}]+?)}' % function_name,
                          java_script)
        if not match:
            raise Exception('Could not find function body and parameter name')

        function_body = match.group('function_body')
        parameter_name = match.group('parameter_name')
        function_body = function_body.split(';')

        new_function_body = []
        for line in function_body:
            line = re.sub('%s[' ']*=[' ']*%s.split\(""\)' % (parameter_name, parameter_name),
                          '%s = list(%s)' % (parameter_name, parameter_name), line)

            line = re.sub('return %s.join\(""\)' % parameter_name,
                          "return ''.join(%s)" % parameter_name, line)

            match = re.match('(?P<namespace>[a-zA-Z]+)\.(?P<function_name>[a-zA-Z]+)(?P<parameter>\((.*)\))', line)
            if match:
                namespace = match.group('namespace')
                function_name = match.group('function_name')
                parameter = match.group('parameter')

                # ToDo: collect namespace and function name...after this call the helper_function to extract the other methods
                _get_helper_function(java_script, namespace)
                pass
            new_function_body.append(line)
            pass
        pass

    # TODO: can be improved
    def get_best_fitting_video_stream(self, video_id, video_height):
        streams = self._get_stream_infos_web(video_id)

        result = None
        last_size = 0
        for stream in streams:
            size = stream['format']['height']

            if size >= last_size and size <= video_height:
                last_size = size
                result = stream
                pass
            pass

        return result

    def get_stream_infos(self, video_id):
        methods = [self._get_stream_infos_tv, self._get_stream_infos_web]

        for method in methods:
            streams = method(video_id)
            if streams is not None:
                return streams
            pass

        return {}

    def _decipher_signature(self, signature):
        def _aJ(a, b):
            return a[::-1]

        def _KO(a, b):
            del a[:b]
            return a

        def _Gs(a, b):
            c = a[0]
            a[0] = a[b % len(a)]
            a[b] = c
            return a

        a = list(signature)  # a = a.split("");
        a = _KO(a, 2)
        a = _aJ(a, 52)
        a = _KO(a, 3)
        a = _aJ(a, 7)
        a = _KO(a, 3)
        a = _aJ(a, 4)
        a = _Gs(a, 2)

        return ''.join(a)

    def _get_stream_infos_web(self, video_id):
        stream_list = []

        headers = {'Host': 'www.youtube.com',
                   'Connection': 'keep-alive',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.36 Safari/537.36',
                   'Accept': '*/*',
                   'DNT': '1',
                   'Referer': 'https://www.youtube.com',
                   'Accept-Encoding': 'gzip, deflate',
                   'Accept-Language': 'en-US,en;q=0.8,de;q=0.6'}

        params = {'v': video_id}

        url = 'https://www.youtube.com/watch'

        result = requests.get(url, params=params, headers=headers, verify=False, allow_redirects=True)
        html = result.text

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

        itag_map = {}
        itag_map.update(self.DEFAULT_ITAG_MAP)
        re_match = re.match('.+\"fmt_list\": \"(?P<fmt_list>.+?)\".+', html)
        if re_match:
            fmt_list = re_match.group('fmt_list')
            fmt_list = fmt_list.split(',')

            for value in fmt_list:
                value = value.replace('\/', '|')

                try:
                    attr = value.split('|')
                    sizes = attr[1].split('x')
                    itag_map[attr[0]] = {'width': int(sizes[0]),
                                         'height': int(sizes[1])}
                except:
                    # do nothing
                    pass
                pass
            pass

        re_match = re.match('.+\"js\": \"(?P<js>.+?)\".+', html)
        js = ''
        if re_match:
            js = re_match.group('js').replace('\\', '').strip('//')
            pass

        re_match = re.match('.+\"url_encoded_fmt_stream_map\": \"(?P<url_encoded_fmt_stream_map>.+?)\".+', html)
        if re_match:
            url_encoded_fmt_stream_map = re_match.group('url_encoded_fmt_stream_map')
            url_encoded_fmt_stream_map = url_encoded_fmt_stream_map.split(',')

            for value in url_encoded_fmt_stream_map:
                value = value.replace('\\u0026', '&')
                attr = dict(urlparse.parse_qsl(value))

                try:
                    url = urllib.unquote(attr['url'])

                    signature = ''
                    if attr.get('s', ''):
                        signature = self._decipher_signature(attr.get('s', ''))
                    elif attr.get('sig', ''):
                        signature = attr.get('sig', '')
                        pass

                    if signature:
                        url += '&signature=%s' % signature
                        pass

                    video_stream = {'url': url,
                                    'format': itag_map[attr['itag']]}

                    stream_list.append(video_stream)
                except:
                    # do nothing
                    pass
                pass
            pass

        return stream_list

    def _get_stream_infos_tv(self, video_id):
        headers = {'Host': 'www.youtube.com',
                   'Connection': 'keep-alive',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.36 Safari/537.36',
                   'Accept': '*/*',
                   'DNT': '1',
                   'Referer': 'https://www.youtube.com/tv',
                   'Accept-Encoding': 'gzip, deflate',
                   'Accept-Language': 'en-US,en;q=0.8,de;q=0.6'}

        params = {'html5': '1',
                  'video_id': video_id,
                  'hl': self._youtube_client.get_language(),
                  'c': 'TVHTML5',
                  'cver': '4',
                  'cbr': 'Chrome',
                  'cbrver': '39.0.2171.36',
                  'cos': 'Windows',
                  'cosver': '6.1',
                  'ps': 'leanback',
                  'el': 'leanback'}

        url = 'https://www.youtube.com/get_video_info'

        result = requests.get(url, params=params, headers=headers, verify=False, allow_redirects=True)

        stream_list = []

        data = result.text
        params = dict(urlparse.parse_qsl(data))

        itag_map = {}
        itag_map.update(self.DEFAULT_ITAG_MAP)

        # update itag map
        fmt_list = params['fmt_list']
        fmt_list = fmt_list.split(',')
        for item in fmt_list:
            data = item.split('/')

            size = data[1].split('x')
            itag_map[data[0]] = {'width': int(size[0]),
                                 'height': int(size[1])}
            pass

        # extract streams from map
        url_encoded_fmt_stream_map = params['url_encoded_fmt_stream_map']
        url_encoded_fmt_stream_map = url_encoded_fmt_stream_map.split(',')
        for item in url_encoded_fmt_stream_map:
            stream_map = dict(urlparse.parse_qsl(item))

            url = stream_map['url']
            if 'sig' in stream_map:
                url += '&signature=%s' % stream_map['sig']
            elif 's' in stream_map:
                # fuck!!! in this case we must call the web page
                return self._get_stream_infos_web(video_id)

            video_stream = {'url': url,
                            'dashmpd': params['dashmpd'],
                            'probe_url': params['probe_url'],
                            'format': itag_map[stream_map['itag']]}

            stream_list.append(video_stream)
            pass

        return stream_list

    pass
