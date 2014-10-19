import hashlib

from storage import Storage

class SearchHistory(Storage):
    def __init__(self, filename, max_items=10):
        Storage.__init__(self, filename, max_item_count=max_items)
        pass

    def is_empty(self):
        return self._is_empty()

    def list(self):
        result = []

        for key in self._get_ids():
            item = self._get(key)
            if item is not None:
                # clean up old mistakes :)
                if not isinstance(item[0], basestring):
                    self._remove(key)
                    self.sync()
                else:
                    result.append(item)
                    pass
            pass

        def _sort(x):
            return x[1]

        # first sort the items based on their last timestamp
        result = sorted(result, key=_sort, reverse=True)
        # normalize the items by removing the timestamp
        for i in range(len(result)):
            result[i] = result[i][0]
            pass

        return result

    def clear(self):
        self._clear()
        pass

    def _make_id(self, search_text):
        m = hashlib.md5()
        m.update(search_text.encode('utf-8'))
        return m.hexdigest()

    def remove(self, search_text):
        self._remove(self._make_id(search_text))
        pass

    def update(self, search_text):
        self._set(self._make_id(search_text), search_text)
        pass

    pass