from resources.lib.kodimon import DirectoryItem

__author__ = 'bromix'


def _process_browse_response(provider, json_data):
    contents = json_data.get('contents', {})
    section_list_renderer = contents.get('sectionListRenderer', {})
    contents = section_list_renderer.get('contents', [])

    pass


def process_response(provider, json_data):
    channel_map = {}
    result = []

    kind = json_data.get('kind', '')
    if kind=='youtubei#browseResponse':
        return _process_browse_response(provider, json_data)

    items = json_data.get('items', [])
    for item in items:
        # if kind=='youtubei#guideResponse'
        sub_items = item.get('guideSectionRenderer', {}).get('items', [])
        for sub_item in sub_items:
            guide_entry_renderer = sub_item.get('guideEntryRenderer', {})
            title = guide_entry_renderer['title']
            browse_id = guide_entry_renderer.get('navigationEndpoint', {}).get('browseEndpoint', {}).get('browseId',
                                                                                                         '')
            if browse_id:
                guide_item = DirectoryItem(title, provider.create_uri(['browse/tv', browse_id]))
                result.append(guide_item)

                channel_map[browse_id] = guide_item
                pass
            pass
        pass

    # we update the channels with the correct thumbnails and fanarts
    json_channel_data = provider.get_client().get_channels_v3(channel_id=list(channel_map.keys()))
    items = json_channel_data.get('items', [])
    for item in items:
        guide_item = channel_map[item['id']]  # should crash if something is missing

        image = item.get('snippet', {}).get('thumbnails', {}).get('medium', {}).get('url', '')
        guide_item.set_image(image)

        fanart = item.get('brandingSettings', {}).get('image', {}).get('bannerTvImageUrl', provider.get_fanart())
        guide_item.set_fanart(fanart)
        pass

    return result
