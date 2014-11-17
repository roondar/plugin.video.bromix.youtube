from resources.lib.kodion.utils import FunctionCache

__author__ = 'bromix'


class ChannelManager(object):
    def __init__(self, context, youtube_client):
        self._context = context
        self._youtube_client = youtube_client
        self._data = {}
        pass

    def _get_fanart(self, channel_id):
        return self._data.get(channel_id, '')

    def _update_channel_ids(self, channel_ids):
        if len(channel_ids) == 0:
            return {}

        result = {}

        json_data = self._youtube_client.get_channels(channel_ids)
        yt_items = json_data.get('items', [])
        for yt_item in yt_items:
            channel_id = yt_item['id']

            # set an empty url
            self._data[channel_id] = u''
            images = yt_item.get('brandingSettings', {}).get('image', {})
            banners = ['bannerTvMediumImageUrl', 'bannerTvLowImageUrl', 'bannerTvImageUrl']
            for banner in banners:
                image = images.get(banner, '')
                if image:
                    self._data[channel_id] = image
                    break
                pass

            # this will cache the url of the fanart and also work for our result
            result[channel_id] = self._context.get_function_cache().get(FunctionCache.ONE_WEEK, self._get_fanart, channel_id)
            pass

        return result

    def get_fanarts(self, channel_ids):
        result = {}

        channel_ids_to_update = []
        function_cache = self._context.get_function_cache()
        for channel_id in channel_ids:
            fanart = function_cache.get_cached_only(self._get_fanart, channel_id)
            if fanart is None:
                self._context.log_debug("No fanart for channel '%s' cached" % channel_id)
                channel_ids_to_update.append(channel_id)
                pass
            else:
                self._context.log_debug("Found cached fanart for channel '%s'" % channel_id)
                result[channel_id] = fanart
                pass
            pass

        result.update(self._update_channel_ids(channel_ids_to_update))

        return result

    pass
