from resources.lib.kodion import runner
from resources.lib import _old_youtube

__provider__ = _old_youtube.Provider()
runner.run(__provider__)