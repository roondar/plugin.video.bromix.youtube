# -*- coding: utf-8 -*-

import client
from youtube.client import YouTubeClient

if __name__ == "__main__":
    __USERNAME__ = "YOUR_USERNAME"
    __PASSWORD__ = "YOUR_PASSWORD"
    
    __client__ = YouTubeClient(username=__USERNAME__, password=__PASSWORD__, maxResult=25)
    
    
    pass