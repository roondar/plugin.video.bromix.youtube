from resources.lib import kodimon
from resources.lib.kodimon import KodimonException, VideoItem, DirectoryItem

__author__ = 'bromix'


def _update_video_infos(provider, video_item_dict):
    video_ids = list(video_item_dict.keys())

    json_data = provider.get_client().get_videos_v3(video_ids)
    items = json_data.get('items', [])
    for item in items:
        video_id = item['id']  # crash if not conform
        video_item = video_item_dict[video_id]

        snippet = item['snippet']  # crash if not conform

        # plot
        description = kodimon.strip_html_from_text(snippet['description'])
        video_item.set_plot(description)

        # date time
        published = kodimon.parse_iso_8601(snippet['publishedAt'])
        video_item.set_year(published['year'])
        video_item.set_aired(published['year'], published['month'], published['day'])
        video_item.set_premiered(published['year'], published['month'], published['day'])

        # duration
        duration = item.get('contentDetails', {}).get('duration', '')
        duration = kodimon.parse_iso_8601(duration)
        video_item.set_duration(hours=duration['hours'], minutes=duration['minutes'], seconds=duration['seconds'])

        # try to find a better resolution for the image
        thumbnails = snippet.get('thumbnails', {})
        image = thumbnails.get('standard', {}).get('url', video_item.get_image())
        video_item.set_image(image)
        pass

    pass


def _process_search_list_response(provider, path, params, json_data):
    video_item_dict = {}

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

                video_item_dict[video_id] = video_item
            elif sub_kind == 'youtube#channel':
                channel_id = item.get('id', {})['channelId']  # should crash if the API is not conform!
                snippet = item.get('snippet', {})
                title = snippet['title']  # should crash if the API is not conform!
                image = snippet.get('thumbnails', {}).get('medium', {}).get('url', '')

                playlist_item = DirectoryItem('[CH]'+title,
                                              provider.create_uri(['playlist', channel_id]),
                                              image=image)
                playlist_item.set_fanart(provider.get_fanart())
                result.append(playlist_item)
            elif sub_kind == 'youtube#playlist':
                playlist_id = item.get('id', {})['playlistId']  # should crash if the API is not conform!
                snippet = item.get('snippet', {})
                title = snippet['title']  # should crash if the API is not conform!
                image = snippet.get('thumbnails', {}).get('medium', {}).get('url', '')

                channel_item = DirectoryItem('[PL]'+title,
                                             provider.create_uri(['channel', channel_id]),
                                             image=image)
                channel_item.set_fanart(provider.get_fanart())
                result.append(channel_item)
            else:
                raise KodimonException("Unknown kind '%s' for youtube_v3" % sub_kind)
        else:
            raise KodimonException("Unknown kind '%s' for youtube_v3" % kind)
        pass

    _update_video_infos(provider, video_item_dict)

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
