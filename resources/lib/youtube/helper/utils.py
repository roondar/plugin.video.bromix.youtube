__author__ = 'bromix'

import re

from resources.lib import kodion
from resources.lib.kodion import iso8601
from resources.lib.youtube.helper import yt_context_menu

def update_video_infos(provider, context, video_id_dict, playlist_item_id_dict=None):
    video_ids = list(video_id_dict.keys())
    if len(video_ids) == 0:
        return

    if not playlist_item_id_dict:
        playlist_item_id_dict = {}
        pass

    resource_manager = provider.get_resource_manager(context)
    video_data = resource_manager.get_videos(video_ids)

    my_related_playlists = {}
    if provider.is_logged_in():
        my_related_playlists = resource_manager.get_related_playlists(channel_id='mine')
        pass

    for video_id in video_data.keys():
        yt_item = video_data[video_id]
        video_item = video_id_dict[video_id]

        snippet = yt_item['snippet']  # crash if not conform

        """
        This is experimental. We try to get the most information out of the title of a video.
        This is not based on any language. In some cases this won't work at all.
        TODO: via language and settings provide the regex for matching episode and season.
        """
        video_item.set_season(1)
        video_item.set_episode(1)
        season_episode_regex = ['Part (?P<episode>\d+)',
                                '#(?P<episode>\d+)',
                                'Ep.[^\w]?(?P<episode>\d+)',
                                '\[(?P<episode>\d+)\]',
                                'S(?P<season>\d+)E(?P<episode>\d+)',
                                'Season (?P<season>\d+)(.+)Episode (?P<episode>\d+)',
                                'Episode (?P<episode>\d+)']
        for regex in season_episode_regex:
            re_match = re.search(regex, video_item.get_name())
            if re_match:
                if 'season' in re_match.groupdict():
                    video_item.set_season(int(re_match.group('season')))
                    pass

                if 'episode' in re_match.groupdict():
                    video_item.set_episode(int(re_match.group('episode')))
                    pass
                break
            pass

        # plot
        channel_name = snippet.get('channelTitle', '')
        description = kodion.utils.strip_html_from_text(snippet['description'])
        if channel_name:
            description = '[UPPERCASE][B]%s[/B][/UPPERCASE][CR][CR]%s' % (channel_name, description)
            pass
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
        thumbnail_sizes = ['high', 'medium']
        for thumbnail_size in thumbnail_sizes:
            image = thumbnails.get(thumbnail_size, {}).get('url', '')
            if image:
                video_item.set_image(image)
                break
            pass

        # update context menu
        channel_id = snippet.get('channelId', '')
        if channel_id and channel_name:
            context_menu = []
            # only if we are not in the channel provide to jump to the channel
            if kodion.utils.create_path('channel', channel_id) != context.get_path():
                context_menu.append((context.localize(provider.LOCAL_MAP['youtube.go_to_channel']).replace("%CHANNEL%",
                                                                                                           '[B]%s[/B]' % channel_name),
                                     'Container.Update(%s)' % context.create_uri(['channel', channel_id])))
                pass

            context_menu.append((context.localize(provider.LOCAL_MAP['youtube.related_videos']),
                                 'Container.Update(%s)' % context.create_uri(['special', 'relatedvideos'],
                                                                             {'video_id': video_id})))

            if provider.is_logged_in():
                """
                Add 'watch later' only if:
                - I'm logged in
                - this is not my 'watch later' playlist
                """
                watch_later_playlist = my_related_playlists.get('watchLater', '')
                if watch_later_playlist and kodion.utils.create_path('channel', 'mine', 'playlist',
                                                                     watch_later_playlist) != context.get_path():
                    context_menu.append((context.localize(provider.LOCAL_MAP['youtube.watch_later']),
                                         'RunPlugin(%s)' % context.create_uri(
                                             ['playlist', my_related_playlists['watchLater'], 'add', video_id])))
                    pass

                """
                Add 'like' only if:
                - I'm logged in
                - this is not my 'liked videos' playlist
                """
                liked_videos_playlist = my_related_playlists.get('likes', '')
                if liked_videos_playlist and kodion.utils.create_path('channel', 'mine', 'playlist',
                                                                      liked_videos_playlist) != context.get_path():
                    context_menu.append((context.localize(provider.LOCAL_MAP['youtube.like']),
                                         'RunPlugin(%s)' % context.create_uri(
                                             ['playlist', my_related_playlists['likes'], 'add', video_id])))
                    pass

                # subscribe to the channel of the video
                yt_context_menu.append_subscribe_to_channel(context_menu, provider, context, channel_id, channel_name)

                playlist_match = re.match('^/channel/mine/playlist/(?P<playlist_id>.*)/$', context.get_path())
                if playlist_match:
                    playlist_id = playlist_match.group('playlist_id')
                    playlist_item_id = playlist_item_id_dict.get(video_id, '')
                    if playlist_item_id:
                        context_menu.append((context.localize(provider.LOCAL_MAP['youtube.remove']),
                                             'RunPlugin(%s)' % context.create_uri(
                                                 ['playlist', playlist_id, 'remove', playlist_item_id])))
                        pass
                    pass
                pass

            if len(context_menu) > 0:
                video_item.set_context_menu(context_menu)
                pass
            pass
        pass

    pass


def update_channel_infos(provider, context, channel_id_dict):
    # at least we need one channel id
    channel_ids = list(channel_id_dict.keys())
    if len(channel_ids) == 0:
        return

    fanarts = provider.get_resource_manager(context).get_fanarts(channel_ids)

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
