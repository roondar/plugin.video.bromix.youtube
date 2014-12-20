__author__ = 'bromix'

from resources.lib import kodion


def append_add_video_to_playlist(context_menu, provider, context, video_id):
    context_menu.append((context.localize(provider.LOCAL_MAP['youtube.video.add_to_playlist']),
                         'RunPlugin(%s)' % context.create_uri(['playlist', 'select', 'playlist'],
                                                              {'video_id': video_id})))
    pass


def append_remove_playlist(context_menu, provider, context, playlist_id):
    context_menu.append((context.localize(provider.LOCAL_MAP['youtube.remove']),
                         'RunPlugin(%s)' % context.create_uri(['playlist', 'remove', 'playlist'],
                                                              {'playlist_id': playlist_id})))
    pass


def append_like_video(context_menu, provider, context, playlist_id, video_id):
    playlist_path = kodion.utils.create_path('channel', 'mine', 'playlist', playlist_id)
    if playlist_id and playlist_path != context.get_path():
        context_menu.append((context.localize(provider.LOCAL_MAP['youtube.like']),
                             'RunPlugin(%s)' % context.create_uri(['playlist', 'add', 'video'],
                                                                  {'playlist_id': playlist_id, 'video_id': video_id})))
        pass
    pass


def append_watch_later(context_menu, provider, context, playlist_id, video_id):
    playlist_path = kodion.utils.create_path('channel', 'mine', 'playlist', playlist_id)
    if playlist_id and playlist_path != context.get_path():
        context_menu.append((context.localize(provider.LOCAL_MAP['youtube.watch_later']),
                             'RunPlugin(%s)' % context.create_uri(['playlist', 'add', 'video'],
                                                                  {'playlist_id': playlist_id, 'video_id': video_id})))
        pass
    pass


def append_go_to_channel(context_menu, provider, context, channel_id, channel_name):
    text = context.localize(provider.LOCAL_MAP['youtube.go_to_channel']) % ('[B]%s[/B]' % channel_name)
    context_menu.append((text, 'Container.Update(%s)' % context.create_uri(['channel', channel_id])))
    pass


def append_related_videos(context_menu, provider, context, video_id):
    context_menu.append((context.localize(provider.LOCAL_MAP['youtube.related_videos']),
                         'Container.Update(%s)' % context.create_uri(['special', 'related_videos'],
                                                                     {'video_id': video_id})))
    pass


def append_subscribe_to_channel(context_menu, provider, context, channel_id, channel_name=u''):
    text = u''
    if channel_name:
        text = context.localize(provider.LOCAL_MAP['youtube.subscribe_to']).replace('%s', '[B]' + channel_name + '[/B]')
        context_menu.append(
            (text, 'RunPlugin(%s)' % context.create_uri(['subscriptions', 'add'], {'subscription_id': channel_id})))
        pass
    else:
        context_menu.append((context.localize(provider.LOCAL_MAP['youtube.subscribe']),
                             'RunPlugin(%s)' % context.create_uri(['subscriptions', 'add'],
                                                                  {'subscription_id': channel_id})))
        pass
    pass


def append_unsubscribe_from_channel(context_menu, provider, context, channel_id, channel_name=u''):
    context_menu.append((context.localize(provider.LOCAL_MAP['youtube.unsubscribe']),
                         'RunPlugin(%s)' % context.create_uri(['subscriptions', 'remove'],
                                                              {'subscription_id': channel_id})))
    pass