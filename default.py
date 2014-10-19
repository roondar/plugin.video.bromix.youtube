from resources.lib import kodimon
from resources.lib import youtube

__provider__ = youtube.Provider()
kodimon.run(__provider__)