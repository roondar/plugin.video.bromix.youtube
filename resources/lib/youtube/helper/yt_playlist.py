from resources.lib import kodion
from resources.lib.youtube.helper import v3

__author__ = 'bromix'


def _process_add_video(provider, context, re_match):
    playlist_id = context.get_param('playlist_id', '')
    if not playlist_id:
        raise kodion.KodimonException('Playlist/Remove: missing playlist_id')
    video_id = context.get_param('video_id', '')
    if not video_id:
        raise kodion.KodimonException('Playlist/Remove: missing video_id')

    json_data = provider.get_client(context).add_video_to_playlist(playlist_id=playlist_id, video_id=video_id)
    if not v3.handle_error(provider, context, json_data):
        return False

    return True


def _process_remove_video(provider, context, re_match):
    playlist_id = context.get_param('playlist_id', '')
    if not playlist_id:
        raise kodion.KodimonException('Playlist/Remove: missing playlist_id')
    video_id = context.get_param('video_id', '')
    if not video_id:
        raise kodion.KodimonException('Playlist/Remove: missing video_id')

    json_data = provider.get_client(context).remove_video_from_playlist(playlist_id=playlist_id, playlist_item_id=video_id)
    if not v3.handle_error(provider, context, json_data):
        return False

    context.get_ui().refresh_container()
    return True


def process(method, category, provider, context, re_match):
    if method == 'add' and category == 'video':
        return _process_add_video(provider, context, re_match)
    elif method == 'remove' and category == 'video':
        return _process_remove_video(provider, context, re_match)
    else:
        raise kodion.KodimonException("Unknown category '%s' or method '%s'" % (category, method))

    return True
