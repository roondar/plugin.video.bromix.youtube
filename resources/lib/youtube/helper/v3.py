__author__ = 'bromix'

from resources.lib import kodion
from resources.lib.kodion import items, iso8601


def _update_video_infos(provider, context, video_id_dict):
    video_ids = list(video_id_dict.keys())
    if len(video_ids) == 0:
        return

    json_data = provider._get_client(context).get_videos(video_ids)
    yt_items = json_data.get('items', [])
    for yt_item in yt_items:
        video_id = yt_item['id']  # crash if not conform
        video_item = video_id_dict[video_id]

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


def _process_search_list_response(provider, context, json_data):
    video_id_dict = {}

    result = []

    yt_items = json_data.get('items', [])
    if len(yt_items) == 0:
        context.log_warning('List of search result is empty')
        return result

    for yt_item in yt_items:
        yt_kind = yt_item.get('kind', '')
        if yt_kind == 'youtube#searchResult':
            yt_kind = yt_item.get('id', {}).get('kind', '')
            if yt_kind == 'youtube#video':
                video_id = yt_item['id']['videoId']
                snippet = yt_item.get('snippet', {})
                title = snippet['title']  # should crash if the API is not conform!
                image = snippet.get('thumbnails', {}).get('medium', {}).get('url', '')
                video_item = items.VideoItem(title,
                                             context.create_uri(['play'], {'video_id': video_id}),
                                             image=image)
                video_item.set_fanart(provider._get_fanart(context))
                result.append(video_item)
                video_id_dict[video_id] = video_item
                pass
            else:
                raise kodion.KodimonException("Unknown kind '%s'" % yt_kind)
            pass
        else:
            raise kodion.KodimonException("Unknown kind '%s'" % yt_kind)
        pass

    _update_video_infos(provider, context, video_id_dict)
    return result


def response_to_items(provider, context, json_data):
    result = []

    kind = json_data.get('kind', '')
    if kind == 'youtube#searchListResponse':
        result.extend(_process_search_list_response(provider, context, json_data))
        pass
    else:
        raise kodion.KodimonException("Unknown kind '%s'" % kind)

    # next page
    yt_next_page_token = json_data.get('nextPageToken', '')
    if yt_next_page_token:
        new_params = {}
        new_params.update(context.get_params())
        new_params['page_token'] = yt_next_page_token

        current_page = int(context.get_param('page', 1))
        next_page_item = items.create_next_page_item(context, current_page)
        next_page_item.set_fanart(provider._get_fanart(context))
        result.append(next_page_item)
        pass

    return result