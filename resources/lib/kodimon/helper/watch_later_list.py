import datetime

__author__ = 'bromix'

from storage import Storage


class WatchLaterList(Storage):
    def __init__(self, filename):
        Storage.__init__(self, filename)
        pass

    def clear(self):
        self._clear()
        pass

    def list(self):
        from .. import json_to_item

        result = []

        for key in self._get_ids():
            data = self._get(key)
            if data is not None:
                item = data[0]

                # remove old stuff - we only want json data
                if not isinstance(item, dict):
                    self._remove(key)
                    pass

                # at this point we could react on api changes if the '_version' of
                # the base_item is different.
                item = json_to_item(item)
                result.append(item)
            pass

        from .. import sort_items_by_info_label, VideoItem

        return sort_items_by_info_label(result, VideoItem.INFO_DATEADDED)

    def add(self, base_item):
        now = datetime.datetime.now()
        base_item.set_date_added(now.year, now.month, now.day, now.hour, now.minute, now.second)

        from .. import item_to_json

        item_json_data = item_to_json(base_item)
        self._set(base_item.get_id(), item_json_data)
        pass

    def remove(self, base_item):
        self._remove(base_item.get_id())
        pass