import urllib

class SeachHistory(object):
    def __init__(self, plugin, size=10):
        self._plugin = plugin
        self._size = size
        pass
    
    def _getSearchItems(self):
        result = []
        data = self._plugin.getSettingAsString('bromix.search.history', '')
        if data!=None:
            items = data.split('|')
            for item in items:
                """
                If data exists the split method will at least create one item with no string.
                This will prevent any empty search items
                """
                if len(item)>0:
                    item = urllib.unquote(item)
                    result.append(item)
                    pass
                pass
            pass
        
        return result
    
    def removeItem(self, search):
         # get old items
        oldItems = self._getSearchItems()
        
        # remove the old item to move it up front
        if search in oldItems:
            index = oldItems.index(search)
            del oldItems[index]
            pass
        
        data = '|'.join(oldItems)
        self._plugin.setSettingAsString('bromix.search.history', data)
        pass
    
    def clear(self):
        self._plugin.setSettingAsString('bromix.search.history', '')
        pass
    
    def getSearchItems(self):
        return self._getSearchItems()
    
    def updateSearchItem(self, search):
        # get old items
        oldItems = self._getSearchItems()
        
        # remove the old item to move it up front
        if search in oldItems:
            index = oldItems.index(search)
            del oldItems[index]
            pass
        
        # create a new updated list with item 
        tmpList = [urllib.quote(search)]
        for oldItem in oldItems:
            tmpList.append(urllib.quote(oldItem))
            pass
        
        # create new list with correct size
        newItems = []
        count = min(self._size, len(tmpList))
        for i in range(count):
            newItems.append(tmpList[i])
            pass
        
        data = '|'.join(newItems)
        self._plugin.setSettingAsString('bromix.search.history', data)
        pass
    pass