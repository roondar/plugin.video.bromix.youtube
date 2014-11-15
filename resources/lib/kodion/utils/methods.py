__author__ = 'bromix'

__all__ = ['create_path', 'create_uri_path', 'strip_html_from_text', 'print_items']

import urllib
import re


def create_path(*args):
    comps = []
    for arg in args:
        if isinstance(arg, list):
            return create_path(*arg)

        comps.append(unicode(arg.strip('/').replace('\\', '/').replace('//', '/')))
        pass

    uri_path = '/'.join(comps)
    if uri_path:
        return u'/%s/' % uri_path

    return '/'


def create_uri_path(*args):
    comps = []
    for arg in args:
        if isinstance(arg, list):
            return create_uri_path(*arg)

        comps.append(arg.strip('/').replace('\\', '/').replace('//', '/').encode('utf-8'))
        pass

    uri_path = '/'.join(comps)
    if uri_path:
        return urllib.quote('/%s/' % uri_path)

    return '/'


def strip_html_from_text(text):
    """
    Removes html tags
    :param text: html text
    :return:
    """
    return re.sub('<[^<]+?>', '', text)


def print_items(items):
    """
    Prints the given test_items. Basically for tests
    :param items: list of instances of base_item
    :return:
    """
    if not items:
        items = []
        pass

    for item in items:
        print item
        pass
    pass