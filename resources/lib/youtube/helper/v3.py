from resources.lib.youtube.helper.resource_manager import ResourceManager

__author__ = 'bromix'

from resources.lib import kodion
from resources.lib.kodion import items, iso8601


def _update_video_infos(provider, context, video_id_dict):
    video_ids = list(video_id_dict.keys())
    if len(video_ids) == 0:
        return

    channel_manager = ResourceManager(context, provider.get_client(context))
    video_data = channel_manager.get_videos(video_ids)

    for key in video_data.keys():
        yt_item = video_data[key]
        video_item = video_id_dict[key]

        snippet = yt_item['snippet']  # crash if not conform

        # plot
        description = kodion.utils.strip_html_from_text(snippet['description'])
        video_item.set_plot(description)

        # date time
        datetime = iso8601.parse(snippet['publishedAt'])
        video_item.set_year(datetime.year)
        video_item.set_aired(datetime.year, datetime.month, datetime.day)
        video_item.set_premiered(datetime.year, datetime.month, datetime.day)

        # duration
        duration = yt_item.get('contentDetails', {}).get('duration', '')
        duration = iso8601.parse(duration)
        video_item.set_duration_from_seconds(duration.seconds)

        # try to find a better resolution for the image
        thumbnails = snippet.get('thumbnails', {})
        image = thumbnails.get('standard', {}).get('url', video_item.get_image())
        video_item.set_image(image)
        pass

    pass


def _update_channel_infos(provider, context, channel_id_dict):
    channel_ids = list(channel_id_dict.keys())
    if len(channel_ids) == 0:
        return

    channel_manager = ResourceManager(context, provider.get_client(context))
    fanarts = channel_manager.get_fanarts(channel_ids)

    for channel_id in channel_ids:
        channel_items = channel_id_dict[channel_id]
        for channel_item in channel_items:
            # only set not empty fanarts
            fanart = fanarts.get(channel_id, '')
            if fanart:
                channel_item.set_fanart(fanart)
                pass
            pass
        pass
    pass


def _process_list_response(provider, context, json_data):
    video_id_dict = {}
    channel_item_dict = {}

    result = []

    yt_items = json_data.get('items', [])
    if len(yt_items) == 0:
        context.log_warning('List of search result is empty')
        return result

    for yt_item in yt_items:
        yt_kind = yt_item.get('kind', '')
        if yt_kind == u'youtube#playlistItem':
            snippet = yt_item['snippet']
            video_id = snippet['resourceId']['videoId']
            title = snippet['title']
            image = snippet.get('thumbnails', {}).get('medium', {}).get('url', '')
            video_item = items.VideoItem(title,
                                         context.create_uri(['play'], {'video_id': video_id}),
                                         image=image)
            video_item.set_fanart(provider.get_fanart(context))
            result.append(video_item)
            video_id_dict[video_id] = video_item

            channel_id = snippet['channelId']
            if not channel_id in channel_item_dict:
                channel_item_dict[channel_id] = []
            channel_item_dict[channel_id].append(video_item)
            pass
        elif yt_kind == 'youtube#searchResult':
            yt_kind = yt_item.get('id', {}).get('kind', '')

            # video
            if yt_kind == 'youtube#video':
                video_id = yt_item['id']['videoId']
                snippet = yt_item['snippet']
                title = snippet['title']
                image = snippet.get('thumbnails', {}).get('medium', {}).get('url', '')
                video_item = items.VideoItem(title,
                                             context.create_uri(['play'], {'video_id': video_id}),
                                             image=image)
                video_item.set_fanart(provider.get_fanart(context))
                result.append(video_item)
                video_id_dict[video_id] = video_item

                channel_id = snippet['channelId']
                if not channel_id in channel_item_dict:
                    channel_item_dict[channel_id] = []
                channel_item_dict[channel_id].append(video_item)
                pass
            # playlist
            elif yt_kind == 'youtube#playlist':
                playlist_id = yt_item['id']['playlistId']
                snippet = yt_item['snippet']
                title = snippet['title']
                image = snippet.get('thumbnails', {}).get('medium', {}).get('url', '')

                playlist_item = items.DirectoryItem('[PL]' + title,
                                                    context.create_uri(['playlist', playlist_id]),
                                                    image=image)
                playlist_item.set_fanart(provider.get_fanart(context))
                result.append(playlist_item)
                channel_id = snippet['channelId']
                if not channel_id in channel_item_dict:
                    channel_item_dict[channel_id] = []
                channel_item_dict[channel_id].append(playlist_item)
                pass
            elif yt_kind == 'youtube#channel':
                channel_id = yt_item['id']['channelId']
                snippet = yt_item['snippet']
                title = snippet['title']
                image = snippet.get('thumbnails', {}).get('medium', {}).get('url', '')

                channel_item = items.DirectoryItem('[CH]' + title,
                                                   context.create_uri(['channel', channel_id]),
                                                   image=image)
                channel_item.set_fanart(provider.get_fanart(context))
                result.append(channel_item)

                if not channel_id in channel_item_dict:
                    channel_item_dict[channel_id] = []
                channel_item_dict[channel_id].append(channel_item)
                pass
            else:
                raise kodion.KodimonException("Unknown kind '%s'" % yt_kind)
            pass
        else:
            raise kodion.KodimonException("Unknown kind '%s'" % yt_kind)
        pass

    _update_video_infos(provider, context, video_id_dict)
    _update_channel_infos(provider, context, channel_item_dict)
    return result


def response_to_items(provider, context, json_data):
    result = []

    kind = json_data.get('kind', '')
    if kind == u'youtube#searchListResponse' or kind == u'youtube#playlistItemListResponse':
        result.extend(_process_list_response(provider, context, json_data))
        pass
    else:
        raise kodion.KodimonException("Unknown kind '%s'" % kind)

    # next page
    yt_next_page_token = json_data.get('nextPageToken', '')
    if yt_next_page_token:
        new_params = {}
        new_params.update(context.get_params())
        new_params['page_token'] = yt_next_page_token

        new_context = context.clone(new_params=new_params)

        current_page = int(new_context.get_param('page', 1))
        next_page_item = items.create_next_page_item(new_context, current_page)
        next_page_item.set_fanart(provider.get_fanart(new_context))
        result.append(next_page_item)
        pass

    return result