from resources.lib.kodimon import KodimonException, VideoItem, DirectoryItem

__author__ = 'bromix'


def _process_search_list_response(provider, path, params, json_data):
    result = []

    items = json_data.get('items', [])
    for item in items:
        kind = item.get('kind', '')
        if kind == 'youtube#searchResult':
            sub_kind = item.get('id', {}).get('kind', '')
            if sub_kind == 'youtube#video':
                video_id = item.get('id', {})['videoId']  # should crash if the API is not conform!
                snippet = item.get('snippet', {})
                title = snippet['title']  # should crash if the API is not conform!
                image = snippet.get('thumbnails', {}).get('medium', {}).get('url', '')

                video_item = VideoItem(title,
                                       provider.create_uri(['play'], {'video_id': video_id}),
                                       image=image)
                video_item.set_fanart(provider.get_fanart())
                result.append(video_item)
            elif sub_kind == 'youtube#channel':
                channel_id = item.get('id', {})['channelId']  # should crash if the API is not conform!
                snippet = item.get('snippet', {})
                title = snippet['title']  # should crash if the API is not conform!
                image = snippet.get('thumbnails', {}).get('medium', {}).get('url', '')

                playlist_item = DirectoryItem(title,
                                              provider.create_uri(['playlist', channel_id]),
                                              image=image)
                playlist_item.set_fanart(provider.get_fanart())
                result.append(playlist_item)
            elif sub_kind == 'youtube#playlist':
                playlist_id = item.get('id', {})['playlistId']  # should crash if the API is not conform!
                snippet = item.get('snippet', {})
                title = snippet['title']  # should crash if the API is not conform!
                image = snippet.get('thumbnails', {}).get('medium', {}).get('url', '')

                channel_item = DirectoryItem(title,
                                             provider.create_uri(['channel', channel_id]),
                                             image=image)
                channel_item.set_fanart(provider.get_fanart())
                result.append(channel_item)
            else:
                raise KodimonException("Unknown kind '%s' for youtube_v3" % sub_kind)
        else:
            raise KodimonException("Unknown kind '%s' for youtube_v3" % kind)

    return result


def process_response(provider, path, params, json_data):
    if not params:
        params = {}
        pass

    result = []

    kind = json_data.get('kind', '')
    if kind == 'youtube#searchListResponse':
        result.extend(_process_search_list_response(provider, path, params, json_data))
        pass
    else:
        raise KodimonException("Unknown kind '%s' for youtube_v3" % kind)

    # next page
    next_page_token = json_data.get('nextPageToken', '')
    if next_page_token:
        new_params = {}
        new_params.update(params)
        new_params['page_token'] = next_page_token

        page = int(params.get('page', '1'))
        next_page_item = provider.create_next_page_item(page, path, new_params)
        result.append(next_page_item)
        pass

    return result
